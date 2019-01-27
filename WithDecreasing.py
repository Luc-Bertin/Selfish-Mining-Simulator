import random
import time
import sys
import numpy as np
import collections 

"""
    Rather than taking 1 iteration for 1 block to be found, let's take 1 iteration each time unit (min)
    * Sn0:    Time before difficulty adjustement
    * Tho0:   Theorical average time for a block to be mined => 10 min (Bitcoin protocol)
    * n0:     Number of blocks to be mined before difficulty adjustment
    * B:      Correction factor 'miniLambda' : B = Sn0 / (n0*Tho0)
    * Difficulty adjustement occurs when 2016 blocks have been mined => normally 2 weeks
    * t is the 'break time' or time before profitability for Selfish miners
        -> as Selfish miners now decided to invest more ressources than honest miners
        -> so that difficulty decreases and they could mine even quicker afterwards
    We seek to find t
    
    PnL = R - C
    compare PnL for honest vs selfish miners
    
    __nb.simmulations become number of blocks to be mined
    but they can be mined in T time
    p, q follow exponential distribution probability
"""

class Selfish_Mining:

	def __init__(self, **d):
		self.__nb_simulations = d['nb_simulations']
		self.__delta = 0 # advance of selfish miners on honests'ones
		self.__privateChain = 0 # length of private chain RESET at each validation
		self.__publicChain = 0 # length of public chain RESET at each validation
		self.__honestsValidBlocks = 0
		self.__selfishValidBlocks = 0
		self.__counter = 1

		# Setted Parameters
		self.__alpha = d['alpha']
		self.__gamma = d['gamma']
		
		# For results
		self.__RevenueRatio = None
		self.__orphanBlocks = 0
		self.__totalValidatedBlocks = 0

		# For difficulty adjustment
		self.__Tho = 10
		self.__n0 = 2016
		#self.__breaktime = None
		self.__Sn0 = None
		self.__B = 1
		self.__currentTimestamp = 0
		self.__allBlocksMined = []
		self.__lastTimestampDAchanged = 0

		# Writing down results?
		self.__write = d.get('write', False)
		# Display to console results?
		self.__display = d.get('display', False)

	def write_file(self):
		stats_result = [self.__alpha, self.__gamma, self.__nb_simulations, self.__currentTimestamp,\
						self.__totalValidatedBlocks, self.__honestsValidBlocks, self.__selfishValidBlocks,\
						self.__counter, self.__alpha*self.__currentTimestamp/10]
		if self.__Sn0 is not None:
			stats_result.extend([self.__Sn0, 20160*100/self.__Sn0])
			#stats_result.extend([self.__TimeRevenueSM, self.__TimeRevenueHM, self.__TimeRevenueSMifHM,\
			#	self.__Sn0, 20160*100/self.__Sn0])
		else:
			#stats_result.extend(['NA', 'NA', 'NA', 'NA', 'NA'])
			stats_result.extend(['NA', 'NA'])
		with open('results_final15.txt', 'a', encoding='utf-8') as f:
			f.write(','.join([str(x) for x in stats_result]) + '\n')

	def Simulate(self):
		# Time to FIND a block : lambda is the rate so alpha => for each 10 min
		# Simulting all times where blocks have been found since starting t=0
		# \\considering extreme case where all blocks have been found by one party
		# *10 for minutes units | or without for 10 min units
		SepBlocksEach2016 = [2016 for x in range(0, self.__nb_simulations//2016)] + [self.__nb_simulations%2016]

		for i in range(0, len(SepBlocksEach2016)):
			TimesBlocksFoundSM = map(lambda x: x+self.__currentTimestamp, list(np.cumsum(np.random.exponential(1/(self.__alpha)*10/self.__B, SepBlocksEach2016[i]))))
			TimesBlocksFoundHM = map(lambda x: x+self.__currentTimestamp, list(np.cumsum(np.random.exponential(1/(1-self.__alpha)*10/self.__B, SepBlocksEach2016[i]))))
			# marking HM/SM found blocks and times, merging them together and ordering by timestamps
			TimesBlocksFoundSM = {x:'SM' for x in TimesBlocksFoundSM}
			TimesBlocksFoundHM = {x:'HM' for x in TimesBlocksFoundHM}
			TimesAllBLocks = {**TimesBlocksFoundSM, **TimesBlocksFoundHM}
			TimesAllBLocks = collections.OrderedDict(sorted(TimesAllBLocks.items()))
			# This is the time (by 10min unit) when the 2016th block has been found 
			# Takes the number of total blocks found ( <=> self.__nb_simulations)
			TimesAllBLocks = list(TimesAllBLocks.items())
			#TimesAllBLocks = [(a,b) for (a,b) in zip(TimesAllBLocks, range(1,self.__nb_simulations+1))]
			TimesAllBLocks = [(a,b) for (a,b) in zip(TimesAllBLocks, range(0,SepBlocksEach2016[i]*2))]

			for ((currentTimestamp, who), block_number) in TimesAllBLocks:
				## Case when the simulation ended (nb of blocks exceeded actual nb of blocks to mine)
				if self.__counter > self.__nb_simulations:
					break
				self.__counter += 1

				self.__currentTimestamp = currentTimestamp
				if who == 'SM':
					self.On_Selfish_Miners() # found by Selfish Miners
				else:
					self.On_Honest_Miners() # found by Honest Miners
				## to minimize file size, just write block validations by group of 100
				if self.__write and self.__totalValidatedBlocks % 200 == 0:
					self.write_file()
				# NOT REALLY ALL VALIDATED BLOCK BUT ALSO ALL MINED BLOCK THAT DIDN'T LEAD TO VALIDATION UNTIL
				# VALIDATION OCCURS
				#self.__allBlocksMined.append((currentTimestamp, who, block_number))
				
				## Case when totalValidated blocks exceed 2016 in number and difficulty changes
				if self.__totalValidatedBlocks // ((i+1)*2016) > 0:
					self.actualize_results(ChangeDifficulty=True)
					break

		# Publishing private chain if not empty when total nb of simulations reached
		self.__delta = self.__privateChain - self.__publicChain
		if self.__delta > 0:
			self.__selfishValidBlocks += self.__privateChain
			self.__publicChain, self.__privateChain = 0,0
		self.actualize_results()
		if self.__display:
			print(self)
		#print(self.__allBlocksMined)


	def On_Selfish_Miners(self):
		self.__delta = self.__privateChain - self.__publicChain
		self.__privateChain += 1
		if self.__delta == 0 and self.__privateChain == 2:
			self.__privateChain, self.__publicChain = 0,0
			self.__selfishValidBlocks += 2
			# Publishing private chain reset both public and private chains lengths to 0
		self.actualize_results()

	def On_Honest_Miners(self):
		self.__delta = self.__privateChain - self.__publicChain
		self.__publicChain += 1
		if self.__delta == 0:
			# if 1 block is found => 1 block validated as honest miners take advance
			self.__honestsValidBlocks += 1
			# If there is a competition though (1-1) considering gamma,
			# (Reminder: gamma = ratio of honest miners who choose to mine on pool's block)
			# --> either it appends the private chain => 1 block for each competitor in RevenueRatio
			# --> either it appends the honnest chain => 2 blocks for honnest miners (1 more then)
			s = random.uniform(0, 1)
			if self.__privateChain > 0 and s <= float(self.__gamma):
				self.__selfishValidBlocks += 1
			elif self.__privateChain > 0 and s > float(self.__gamma):
				self.__honestsValidBlocks += 1
			#in all cases (append private or public chain) all is reset to 0
			self.__privateChain, self.__publicChain = 0,0
		
		elif self.__delta == 2:
			self.__selfishValidBlocks += self.__privateChain
			self.__publicChain, self.__privateChain = 0,0
		self.actualize_results()

	def actualize_results(self, ChangeDifficulty=False):
		# Total Blocks Mined
		self.__totalValidatedBlocks = self.__honestsValidBlocks + self.__selfishValidBlocks

		# Orphan Blocks 
		self.__orphanBlocks = self.__nb_simulations - self.__totalValidatedBlocks
		# Revenue
		if self.__honestsValidBlocks or self.__selfishValidBlocks:
			self.__RevenueRatio = 100*round(self.__selfishValidBlocks/(self.__totalValidatedBlocks),3)

		# B needs to be not be set back to 1, otherwise it will regenerate the first case
		# B needs to be constant even after the correction
		if ChangeDifficulty:
			self.__Sn0 = self.__currentTimestamp - self.__lastTimestampDAchanged
			self.__B = self.__B*self.__Sn0/(self.__n0*self.__Tho)
			self.__lastTimestampDAchanged = self.__currentTimestamp
			#print(self)

	def __str__(self):
		if self.__counter <= self.__nb_simulations:
			simulation_message = '\nSimulation ' + str(self.__counter) + ' out of ' + str(self.__nb_simulations) + '\n'
			current_stats = 'Private chain : ' + '+ '*int(self.__privateChain) + '\n'\
			'public chain : ' + '+ '*int(self.__publicChain) + '\n'
		else:
			simulation_message = '\n\n' + str(self.__nb_simulations) + ' Simulations Done // publishing private chain if non-empty\n'
			current_stats = ''

		choosen_parameters = 'Alpha : ' + str(self.__alpha) + '\t||\t' +'Gamma : ' + str(self.__gamma) +'\n'

		selfish_vs_honests_stats = \
			'Blocks validated by honest miners : ' + str(self.__honestsValidBlocks) + '\n'\
			'Blocks validated by selfish miners : ' + str(self.__selfishValidBlocks) + '\n'\
            'Expected if they were honests : ' + str(int(self.__alpha * self.__nb_simulations)) + '\n'\
			'Number of total blocks mined : ' + str(self.__totalValidatedBlocks) + '\n'\
			'Number of Orphan blocks : ' + str(self.__orphanBlocks) + '\n'\
			'Revenue ratio = PoolBlocks / TotalBlocks : ' + str(self.__RevenueRatio) + '%\n'

		if self.__Sn0 is not None:
			considering_time_stats = \
				'Sn0 : ' +str(int(self.__Sn0))+ ' minutes \n'\
				'Difficulty adjustment Coefficient after 2016 blocks \n'\
				'=> will change to : ' +str(round(20160/self.__Sn0,4)*100)+ '% of initial value \n'
				#'Revenue by unit time for SM : '+ str(round(self.__TimeRevenueSM, 4)) +'\n'\
				#'Revenue by unit time for HM : '+ str(round(self.__TimeRevenueHM, 4)) +'\n'\
				#'Revenue by unit time expected for SM if HM: '+ str(round(self.__TimeRevenueSMifHM, 4)) +'\n'
		else:
			considering_time_stats = ''
	
		return simulation_message + current_stats + choosen_parameters + selfish_vs_honests_stats + considering_time_stats

if len(sys.argv)==4:
    dico = {'nb_simulations':int(sys.argv[1]), 'alpha':float(sys.argv[2]), 'gamma':float(sys.argv[3]), 'display':True}
    new = Selfish_Mining(**dico)
    new.Simulate()

if len(sys.argv)==1:
    ### TO SAVE MULTIPLE VALUES IN FILE ###
    start = time.time()
    alphas = list(i/100 for i in range(1, 50, 1)) #range(1, 50, 1) | 50 => 0, 0.5, 0.01
    gammas = list(i/100 for i in range(1, 100, 5)) #range(1, 100, 1) | 100 => 0, 1, 0.01
    count = 0 #pourcentage done
    for alpha in alphas:
        for gamma in gammas:
        	## Before and after Difficulty Adjustment (whole time range)
            new = Selfish_Mining(**{'nb_simulations':150000, 'alpha':alpha, 'gamma':gamma, 'write':True})
            new.Simulate()
        count += 1/len(alphas)
        print("progress :" + str(round(count,2)*100) + "%\n")
    duration = time.time()-start
    print("Tooks " + str(round(duration,2)) + " seconds")
