import random
import time
import sys

class Selfish_Mining:

	#def __init__(self, nb_simulations, alpha, gamma):
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
		self.__revenue = None
		self.__orphanBlocks = 0
		self.__totalMinedBlocks = 0

	def write_file(self):
		stats_result = [self.__alpha, self.__gamma, self.__nb_simulations,\
						self.__honestsValidBlocks, self.__selfishValidBlocks,\
						self.__revenue, self.__orphanBlocks, self.__totalMinedBlocks]
		with open('results.txt', 'a', encoding='utf-8') as f:
			f.write(','.join([str(x) for x in stats_result]) + '\n')

	def Simulate(self):
		while(self.__counter <= self.__nb_simulations):
			# Mining power does not mean the block is actually found
			# there is a probability p to find it
			r = random.uniform(0, 1) # random number for each simulation
			self.__delta = self.__privateChain - self.__publicChain
			if r <= float(self.__alpha):
				self.On_Selfish_Miners()
			else:
				self.On_Honest_Miners()
			### COPY-PASTE THE 3 LINES BELOW IN THE IF/ELSE TO GET EACH ITERATION RESULTS ###
			#self.actualize_results()
			#print(self)
			#time.sleep(1)
			self.__counter += 1

		# Publishing private chain if not empty when total nb of simulations reached
		self.__delta = self.__privateChain - self.__publicChain
		if self.__delta > 0:
			self.__selfishValidBlocks += self.__privateChain
			self.__publicChain, self.__privateChain = 0,0
		self.actualize_results()
		print(self)

	def On_Selfish_Miners(self):
		self.__privateChain += 1
		if self.__delta == 0 and self.__privateChain == 2:
			self.__privateChain, self.__publicChain = 0,0
			self.__selfishValidBlocks += 2
			# Publishing private chain reset both public and private chains lengths to 0

	def On_Honest_Miners(self): 
		self.__publicChain += 1
		if self.__delta == 0:
			# if 1 block is found => 1 block validated as honest miners take advance
			self.__honestsValidBlocks += 1
			# If there is a competition though (1-1) considering gamma,
			# (Reminder: gamma = ratio of honest miners who choose to mine on pool's block)
			# --> either it appends the private chain => 1 block for each competitor in revenue
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

	def actualize_results(self):
		# Total Blocks Mined
		self.__totalMinedBlocks = self.__honestsValidBlocks + self.__selfishValidBlocks
		# Orphan Blocks 
		self.__orphanBlocks = self.__nb_simulations - self.__totalMinedBlocks
		# Revenue
		if self.__honestsValidBlocks or self.__selfishValidBlocks:
			self.__revenue = 100*round(self.__selfishValidBlocks/(self.__totalMinedBlocks),3)

	# Show message
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
			'Number of total blocks mined : ' + str(self.__totalMinedBlocks) + '\n'\
			'Number of Orphan blocks : ' + str(self.__orphanBlocks) + '\n'\
			'Revenue ratio = PoolBlocks / TotalBlocks : ' + str(self.__revenue) + '%\n'
		return simulation_message + current_stats + choosen_parameters + selfish_vs_honests_stats

if len(sys.argv)==4:
    dico = {'nb_simulations':int(sys.argv[1]), 'alpha':float(sys.argv[2]), 'gamma':float(sys.argv[3])}
    new = Selfish_Mining(**dico)
    new.Simulate()

if len(sys.argv)==1:
    ### TO SAVE MULTIPLE VALUES IN FILE ###
    start = time.time()
    alphas = list(i/100 for i in range(0, 50, 1)) #50 => 0, 0.5, 0.01
    gammas = list(i/100 for i in range(0, 100, 1)) #100 => 0, 1, 0.01
    count = 0 #pourcentage done
    for alpha in alphas:
        for gamma in gammas:
            new = Selfish_Mining(**{'nb_simulations':200000, 'alpha':alpha, 'gamma':gamma})
            new.Simulate() # took 113 seconds | 155 Ko
            new.write_file()
        count += 1/len(alphas)
        print("progress :" + str(round(count,2)*100) + "%\n")
    duration = time.time()-start
    print("Tooks " + str(round(duration,2)) + " seconds")
