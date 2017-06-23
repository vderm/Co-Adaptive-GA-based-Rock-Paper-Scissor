#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Created on Mar 24 2016

@author: Vasken Dermardiros
ID: 26049516

Final project for COEN6321: Evolutionary Systems
Professor Nawwaf Kharma


individual
----------
rulebook: {'1':'0', '0':'1', '1010':'1'}
allowance: {1000 - rulebook length}
fit: val (fitness of individual)
# best individual: (1) maximizes 'fit'; and, (2) maximizes 'allowance'

population
----------
nI = population size
predictorPopulation = Pindividual1, Pindividual2, Pindividual3, ...
generatorPopulation = Gindividual1, Gindividual2, Gindividual3, ...
...Parents: parent population
...Children: children population spawned from parents
...Family: combined parent and children populations
...Population: survivor population which becomes the next round's population

generatedPattern / predictedPattern / initialPattern
----------------------------------------------------
Newest bit of pattern is on the far left: "new ...1010111001101 old"
Initial pattern is only used by the generator to create the generatedPattern.
The predictedPattern is generated from the initialPattern and the previous
round's generatedPattern sequence.
Over time, the oldest generatedPattern bit is transfered to the initialPattern
and the oldest initialPattern bit is deleted.

Ex.:
{history = 10, prehistory = 5}

** == [ Round 10 ] == **
generatedPattern | initialPattern   | old/deleted
len = history    | len = prehistory |
-------------------------------------------------
      1010110101 | 10101   -->      | 10
       11000?1?1 |         -->      |
-------------------------------------------------
predictedPattern |                  |

** == [ Round 11 ] == **
generatedPattern | initialPattern   | old/deleted
len = history    | len = prehistory |
-------------------------------------------------
      0101011010 | 11010   -->      | 110
       111000?1? |         -->      |
-------------------------------------------------
predictedPattern |                  |


Process
-------
0. Evolution Configuration
1. Initialize Population
2. Play On! {
    3. Get New Champions
    4. Generate/Predict a Bit
    5. Evaluate Population Fitness
    6. Parent Selection, Breed Children, Evaluate Children, Combine Populations
    7. Survivor Selection
    8. Display Progress, Track Progress
    }
9. Plot Results

"""
# Import dependencies
import numpy as np
from functions import * # User-defined functions for Project
from operator import itemgetter
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib as mpl
# import plotTemplate

#===========================
# STEP -1: Search Space Run
#===========================
import itertools
range_nI = np.array([180, 360, 720, 1440])
range_term = np.array([1, 2, 4, 8])
range_prehistory = np.array([4, 8, 16])
space_search = list(itertools.product(range_nI, range_term, range_prehistory))
# print space_search
# print len(space_search)

for nI, championTerm, prehistory in space_search:

	#=================================
	# STEP 0: Evolution Configuration
	#=================================
	# Population Size, initialization parameters, champions' duty term
	# nI = 240          # number of individuals in the population, kept constant
	initialPattern = '0'
	# championTerm = 5  # for how many rounds do the champions serve their rightful duty?
	ruleLength = 2
	rulebookLength = 5

	# SCM probabilities
	ratio = 8         # Ratio of children to parents,
					  # if 3, use multiples of 2 for nI; if 8, multiples of 3
	pXover = 0.25     # Crossover (uniform)
	pMut = 0.55       # Mutation
	pMutType = [0.20, # 1. Add rule
				0.10, # 2. Flip output
				0.15, # 3. Add bit
				0.10, # 4. Shuffle
				0.25, # 5. Make wildcard
				0.20] # 6. Flip bit
	pPass = 0.00      # Pass through
	pNew = 0.20       # New (random) individual
	if abs(pXover+pMut+pPass+pNew-1) > 1e-7: print "Probabilities don't sum to 1!"
	if abs(np.sum(pMutType)-1) > 1e-7: print "Mutation probabilities don't sum to 1!"

	# Tournament selection parameters
	thePit = int(np.sqrt(1+ratio)) # tournament bag size to be used for parent and
								   # survivor selection

	# History length
	history = championTerm    # number of bits used to evaluate fitness of individuals
	# prehistory = 15 # number of bits that become the "initial pattern",
					# bits after are deletes

	# Stopping criteria
	totalRounds = 120
	# fitness stagnating; not really happening...
	# loss of diversity? TODO: speciation?

	# Fix a champion?
	fixPredictor = False
	fixGenerator = False

	#===============================
	# STEP 1: Initialize Population
	#===============================
	predictorPopulation, generatorPopulation = initializePopulation(nI, initialPattern,
																	championTerm, ruleLength,
																	rulebookLength)

	#==================
	# STEP 2: Play On!
	#==================
	predictedPattern = '' # Actual patterns that champions are producing and the
	generatedPattern = '' # rest of the population is being evaluated against!
	predictorPerformance = np.zeros((totalRounds, 3)) # Fitness (best/avg), Allowance (avg)
	generatorPerformance = np.zeros((totalRounds, 3)) # Fitness (best/avg), Allowance (avg)

	for currentRound in range(totalRounds):

		#============================
		# STEP 3: Get New Champions!
		#============================
		# Copy them "deeply" to break referencing
		if currentRound % championTerm == 0:
			print "\n**----  The New Champs are Here!  ----**"
			if fixPredictor == False or currentRound == 0:
				# predictorChampion = rulebookIndividual({'1':'0','0':'1', '0.':'0', '1.':'1'})
				predictorChampion = deepcopy(max(predictorPopulation,
												 key=itemgetter('fit','allowance')))
			if fixGenerator == False or currentRound == 0:
				# generatorChampion = rulebookIndividual({'1':'0', '0':'1'})
				generatorChampion = deepcopy(max(generatorPopulation,
												 key=itemgetter('fit','allowance')))
			# print "Predictor Champ Rulebook: %s" % predictorChampion['rulebook']
			# print "Generator Champ Rulebook: %s" % generatorChampion['rulebook']

		#================================
		# STEP 4: Generate/Predict a Bit
		#================================
		# Predict a new (single) bit, using only previous generated pattern
		predictedPattern = predictPattern(predictorChampion['rulebook'], generatedPattern +
										  initialPattern, '.') + predictedPattern
		# Generate a new (single) bit
		generatedPattern = generatePattern(generatorChampion['rulebook'], generatedPattern +
										   initialPattern, 1) + generatedPattern

		# Truncate pattern according to history length
		# or, rewrite fitness function to put a greater weight on more recent rounds
		predictedPattern = predictedPattern[0:history]
		initialPattern = generatedPattern[history::] + initialPattern
		initialPattern = initialPattern[0:prehistory]
		generatedPattern = generatedPattern[0:history]

		#=====================================
		# STEP 5: Evaluate Population Fitness
		#=====================================
		predictorPopulation = evaluatePredictorPopulation(predictorPopulation, initialPattern,
														  generatedPattern)
		generatorPopulation = evaluateGeneratorPopulation(generatorPopulation, initialPattern,
														  predictedPattern)

		#==================================================================================
		# STEP 6: Parent Selection, Breed Children, Evaluate Children, Combine Populations
		#==================================================================================
		# Parent Selection
		predictorParents = tournamentSelection(predictorPopulation, thePit)
		generatorParents = tournamentSelection(generatorPopulation, thePit)
		predictorParentsNonRef = deepcopy(predictorParents)
		generatorParentsNonRef = deepcopy(generatorParents)
		del predictorPopulation, generatorPopulation
		# Breed Children
		predictorChildren = breedChildren(predictorParents, ratio=ratio)
		generatorChildren = breedChildren(generatorParents, ratio=ratio)
		# Evaluate Children
		predictorChildren = evaluatePredictorPopulation(predictorChildren, initialPattern,
														generatedPattern)
		generatorChildren = evaluateGeneratorPopulation(generatorChildren, initialPattern,
														predictedPattern)
		# Gather Individuals
		predictorFamily = deepcopy(predictorParentsNonRef) + deepcopy(predictorChildren)
		generatorFamily = deepcopy(generatorParentsNonRef) + deepcopy(generatorChildren)
		del predictorParents, predictorParentsNonRef, predictorChildren
		del generatorParents, generatorParentsNonRef, generatorChildren

		#============================
		# STEP 7: Survivor Selection
		#============================
		predictorPopulation = tournamentSelection(predictorFamily, thePit)
		generatorPopulation = tournamentSelection(generatorFamily, thePit)

		#==========================================
		# STEP 8: Display Progress, Track Progress
		#==========================================
		if currentRound % championTerm == 0:
			print "Round %s" % currentRound
			print "Generator Champ Rulebook: %s" % generatorChampion['rulebook']
			print "Predictor Champ Rulebook: %s" % predictorChampion['rulebook']
			print "Generated Pattern: %s%s (older)" % (generatedPattern, initialPattern)
			print "Predicted Pattern: %s" % predictedPattern
			print "Fittest Generator: %s" % max(generatorPopulation,
												key=itemgetter('fit','allowance'))['fit']
			print "Fittest Predictor: %s" % max(predictorPopulation,
												key=itemgetter('fit','allowance'))['fit']

		# Track best/average fitnesses, track rulebook size {1000-'allowance'}
		avgPredictorFit = float(sum([predictorPopulation[i]['fit'] for i in range(nI)]))/nI
		avgPredictorAllowance = float(sum([predictorPopulation[i]['allowance'] for i in range(nI)]))/nI
		avgGeneratorFit = float(sum([generatorPopulation[i]['fit'] for i in range(nI)]))/nI
		avgGeneratorAllowance = float(sum([generatorPopulation[i]['allowance'] for i in range(nI)]))/nI
		# Insert in matrix
		predictorPerformance[currentRound, 0] = max(predictorPopulation, key=itemgetter('fit'))['fit']
		predictorPerformance[currentRound, 1] = avgPredictorFit
		predictorPerformance[currentRound, 2] = 1000 - avgPredictorAllowance
		generatorPerformance[currentRound, 0] = max(generatorPopulation, key=itemgetter('fit'))['fit']
		generatorPerformance[currentRound, 1] = avgGeneratorFit
		generatorPerformance[currentRound, 2] = 1000 - avgGeneratorAllowance

		# TODO: Show the genotype of the fittest over time also their fitnesses.

	#======================
	# STEP 9: Plot Results
	#======================
	# Timestamp, font size configuration
	from time import time
	stamp = str(int(time()))
	param_stamp = '_nI_' + str(nI) + '_term_' + str(championTerm) + '_hist_' + str(prehistory)
	
	font = {'size': 16}
	mpl.rc('font', **font)

	# Fitnesses
	plt.figure()
	plt.plot(predictorPerformance[:, 1], 'r', label='Predictor')
	plt.plot(generatorPerformance[:, 1], 'k', label='Generator')
	plt.xlabel('Round')
	plt.ylabel('Average Fitness')
	plt.legend(loc='lower right', fontsize=14)
	filename = 'Figures/' + stamp + param_stamp + '_fitness.png'
	plt.savefig(filename, dpi=300, bbox_inches='tight')
	#plt.show()

	# Complexity
	plt.figure()
	plt.plot(predictorPerformance[:, 2], 'r', label='Predictor')
	plt.plot(generatorPerformance[:, 2], 'k', label='Generator')
	plt.xlabel('Round')
	plt.ylabel('Average Rulebook Size')
	plt.legend(loc='best', fontsize=14)
	filename = 'Figures/' + stamp + param_stamp + '_rulebook.png'
	plt.savefig(filename, dpi=300, bbox_inches='tight')
	#plt.show()


	# Notes

	# why is predictor always more complex?
	# transfer to rock paper scissor

	# The imitation game
	# Rock paper scissor
	#   R P S; rules based on player 1 v. player 2
		 # +--------+
		 # | 0|+1|-1|
		 # |-1| 0|+1|
		 # |+1|-1| 0|
		 # +--------+
	#
	# 0-2, 3-5, 6-8
	# L, D, W
	#
	# R
	# P
	# becomes "1"
	# and is linked to the payoff function
	# history: 1 3 2 7
