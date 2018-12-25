import random
import time

class Selfish_Mining:

	def __init__(self, nb_simulations, alpha, gamma):
		self.__nb_simulations = nb_simulations
		self.__delta = 0 # advance of selfish miners on honests'ones
		self.__private_chain_length = 0 # length of private chain RESET at each validation
		self.__public_chain_length = 0 # length of public chain RESET at each validation
		self.__blocked_validated_for_honests = 0
		self.__blocked_validated_for_selfish = 0
		self.__revenue = None
		self.__counter = 1

		# Setted Parameters
		self.__alpha = alpha
		self.__gamma = gamma


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
			### UNCOMMENT BELOW THOSE 3 LINES TO GET DISPLAY OF EVOLUTION ###
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


new = Selfish_Mining(130000, 0.39, 0)
new.Simulate()