import random
import time

class Selfish_Mining:

	#def __init__(self, nb_simulations, alpha, gamma):
	def __init__(self, **d):
		self.__nb_simulations = d['nb_simulations']
		self.__delta = 0 # advance of selfish miners on honests'ones
		self.__private_chain_length = 0 # length of private chain RESET at each validation
		self.__public_chain_length = 0 # length of public chain RESET at each validation
		self.__blocked_validated_for_honests = 0
		self.__blocked_validated_for_selfish = 0
		self.__revenue = None
		self.__counter = 1

		# Setted Parameters
		self.__alpha = d['alpha']
		self.__gamma = d['gamma']
		
		self.__end_result = None

	def write_file(self):
		with open('results.txt', 'a', encoding='utf-8') as f:
			f.write(','.join(self.__end_result) + '\n')

	def Simulate(self):
		while(self.__counter <= self.__nb_simulations):
			# Mining power does not mean the block is actually found
			# there is a probability p to find it
			r = random.uniform(0, 1) # random number for each simulation
			self.__delta = self.__private_chain_length - self.__public_chain_length
			if r <= float(self.__alpha):
				self.On_Selfish_Miners()
			else:
				self.On_Honest_Miners()
			### COPY-PASTE THE 3 LINES BELOW IN THE IF/ELSE TO GET EACH ITERATION RESULTS ###
			#self.__revenue = self.compute_revenue()
			#print(self)
			#time.sleep(1)
			self.__counter += 1

		#must take into account when private chain is not empty and simulation ends
		self.__delta = self.__private_chain_length - self.__public_chain_length
		if self.__delta > 0:
			self.__blocked_validated_for_selfish += self.__private_chain_length
			self.__public_chain_length, self.__private_chain_length = 0,0
		self.__revenue = self.compute_revenue()
		
		result = [self.__alpha, self.__gamma, self.__nb_simulations, self.__blocked_validated_for_honests,\
		 self.__blocked_validated_for_selfish, self.__revenue]
		self.__end_result = [str(x) for x in result]
		print(self)

	def On_Selfish_Miners(self):
		self.__private_chain_length += 1
		if self.__delta == 0 and self.__private_chain_length == 2:
			self.__private_chain_length, self.__public_chain_length = 0,0
			self.__blocked_validated_for_selfish += 2
			#don't forget to retrieve money 
			#publishing the private chain reset both public and private chain length

	def On_Honest_Miners(self): 
		self.__public_chain_length += 1
		if self.__delta == 0:
			self.__blocked_validated_for_honests += 1
			#in all cases either, bloc mined by honest will be validated anyway
			# 1) if it appends private chain from delta=0 => validated in the revenue
			# 2) if it appends public chain from delta=0 => validated de facto
			#if self.__private_chain_length == 0: 
			#	self.__blocked_validated_for_honests += 1
			# gamma will matter in this case only (competitive case)
			# Reminder: gamma = ratio of honest miners who choose to mine on pool's block
			if self.__private_chain_length > 0 and random.uniform(0, 1) <= float(self.__gamma):
				self.__blocked_validated_for_selfish += 1
				#g = random.uniform(0, 1)
				#if g <= float(self.__gamma):
				
			#in all cases (append private or public chain) all is reset to 0
			self.__private_chain_length, self.__public_chain_length = 0,0
		
		elif self.__delta == 2:
			self.__blocked_validated_for_selfish += self.__private_chain_length
			self.__public_chain_length, self.__private_chain_length = 0,0

	def compute_revenue(self):
		if self.__blocked_validated_for_honests or self.__blocked_validated_for_selfish:
			return(round(self.__blocked_validated_for_selfish/(self.__blocked_validated_for_selfish +
			 self.__blocked_validated_for_honests),2))

	#show message
	def __str__(self):
		if self.__counter <= self.__nb_simulations:
			simulation_message = '\nSimulation ' + str(self.__counter) + ' out of ' + str(self.__nb_simulations) + '\n'
		else:
			simulation_message = '\n' + str(self.__nb_simulations) + ' Simulations Done // publishing private chain if non-empty\n'
		choosen_parameters = 'alpha : ' + str(self.__alpha) + '\t||\t' +'gamma : ' + str(self.__gamma) +'\n'
		private_public_results = \
			'private chain : ' + '+ '*int(self.__private_chain_length) + '\n'\
			'public chain : ' + '+ '*int(self.__public_chain_length) + '\n'\
			'blocks validated by honests miners : ' + str(self.__blocked_validated_for_honests) + '\n'\
			'blocks validated by selfish miners : ' + str(self.__blocked_validated_for_selfish) + '\n'\
			'delta was before this : ' + str(self.__delta) + '\n'\
			'current revenue ratio \n\t Rpool = rpool / (rpool + rothers) : ' + str(self.__revenue) + '\n'		
		return simulation_message + choosen_parameters + private_public_results

dico = {'nb_simulations':200000, 'alpha':0.5, 'gamma':0.4}
new = Selfish_Mining(**dico)
new.Simulate()

"""
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
"""