#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Created on Mar 19 2016

@author: Vasken Dermardiros
ID: 26049516

Final project for COEN6321: Evolutionary Systems
Professor Nawwaf Kharma

"""
# Import dependencies
import numpy as np
import re
import random
from operator import itemgetter
import xover, mut # user-defined functions for crossover and mutation

# rulebook = {'1':'0','0':'1','1010':'1'} # use a "." as a wildcard in "re" package
# xover = [0., 1.]
# mut = [0.125, 0.125, 0.250, 0.500]
# fit = 1.300
# indiv = {'rulebook': rulebook,
#          'xover': xover,
#          'mut': mut,
#          'fit': fit}

# TODO: relook at generatePattern code for predictor; how to handle generator and initial pattern?
def initializePopulation(nI, initialPattern, championTerm = 10, ruleLength = 2, rulebookLength = 2, displayResults = False):
    predictorPopulation = []
    generatorPopulation = []
    for i in range(nI):
        predictorPopulation.append(createIndividual(ruleLength, rulebookLength))
        generatorPopulation.append(createIndividual(ruleLength, rulebookLength))
    # Pick a generator champion, randomly; and output pattern
    generatorChampion = random.choice(generatorPopulation)
    generatedPattern = generatePattern(generatorChampion['rulebook'], initialPattern, championTerm)
    # Evaluate fitness of predictors
    for i in range(nI):
        predictorPopulation[i]['fit'] = evaluatePredictor(predictorPopulation[i]['rulebook'], initialPattern, generatedPattern)
    # Pick a predictor champion, ranked; and output the predicted pattern
    predictorChampion = max(predictorPopulation, key=itemgetter('fit','allowance'))
    predictedPattern = predictPattern(predictorChampion['rulebook'], initialPattern, generatedPattern)
    # Evaluate fitness of generators
    for i in range(nI):
        generatorPopulation[i]['fit'] = evaluateGenerator(generatorPopulation[i]['rulebook'], initialPattern, predictedPattern)
    # Print initialization results
    if displayResults == True:
        print "initial pattern: %s" % initialPattern
        print "generator champion chosen randomly!"
        print "generator rulebook: %s" % generatorChampion['rulebook']
        print "generated pattern: %s" % generatedPattern
        print "predicted pattern: %s" % predictedPattern
        print "predictor fitness: %s" % predictorChampion['fit']
        print "predictor rulebook: %s" % predictorChampion['rulebook']
    return predictorPopulation, generatorPopulation

def createRule(ruleLength):
	# based on a Poisson distribution for actual length
    actualLength = np.random.poisson(ruleLength-1, 1) + 1 # can't be 0
    rule = np.random.randint(2, size=actualLength) # this is a list
    rule = ''.join(map(str, rule))                 # this is a string
    output = str(np.random.randint(2, size=1)[0])  # this is also a string
    return {rule: output}

def createRulebook(ruleLength, rulebookLength):
	# based on a Poisson distribution for actual length
    actualLength = np.random.poisson(rulebookLength-1, 1) + 1 # can't be 0
    rulebook = {}
    for i in range(actualLength): rulebook.update(createRule(ruleLength))
    # housekeeping!
    # Well, a python dictionary can't have duplicate keys,
    # so no need to perform "housekeeping" after all
    # ".update()" will replace the value of the duplicate key
    # rulebook = housekeeping(rulebook)
    return rulebook

def createIndividual(ruleLength, rulebookLength):
    rulebook = createRulebook(ruleLength, rulebookLength)
    ruleAllowance = 1000 - len(rulebook)
    return {'rulebook': rulebook, 'fit': 0, 'allowance': ruleAllowance} #, 'xover' = xover, 'mut' = mut}

def rulebookIndividual(rulebook):
    ruleAllowance = 1000 - len(rulebook)
    return {'rulebook': rulebook, 'fit': 0, 'allowance': ruleAllowance}

#=============================================================================#
# Newest member of pattern is on far left
def generatePattern(rulebook, initialPattern, patternLength):
    pattern = initialPattern
    for p in range(patternLength):
        nextBit = readRulebook(rulebook, pattern)
        if (nextBit == -1): nextBit = pattern[0] # Confused generator
        pattern = nextBit + pattern # insert in front
    return pattern[0:patternLength]

def predictPattern(rulebook, initialPattern, generatedPattern):
    # generated pattern's newest member is not used!
    pattern = ''
    inputPattern = generatedPattern + initialPattern
    invPattern = inputPattern[::-1] # flip pattern, to start with oldest
    for p in range(len(initialPattern), len(invPattern)):
        slicePattern = invPattern[0:p] # slice pattern
        nextBit = readRulebook(rulebook, slicePattern[::-1]) # flip it back
        # print slicePattern[::-1], nextBit # check
        if (nextBit == -1): nextBit = '?' # Confused predictor
        pattern = nextBit + pattern
    return pattern

# to predict just 1 bit, use:
# nextBit = readRulebook(rulebook, previouslyGeneratedPattern)

# Go through rulebook to find matching patterns
def readRulebook(rulebook, pattern):
    matches = []
    for rule in rulebook:
        if len(rule) > len(pattern): continue # not necessary, does it save significant time?
        if re.match(re.compile(rule), pattern): matches.append(rule)
    if matches == []: return -1 # if no matches, break out!
    # keep only longest matching rules (can be more than 1)
    longest = len(max(matches, key=len))
    reducedMatch = [match for match in matches if len(match) == longest]
    # filter matched rules
    # if number of matches > 1, use one with the most wildcards
    if len(reducedMatch) > 1:
        wild = [reducedMatch[i].count('.') for i in range(len(reducedMatch))]
        longestWild = max(wild)
        wildIndex = [i for i,j in enumerate(wild) if j == longestWild]
        # if number of matches > 1, take a random one between results
        if len(wildIndex) > 1:
            randIndex = random.randint(0, len(wildIndex)-1) # '-1' for indexing reasons
            useRule = reducedMatch[wildIndex[randIndex]]
        else: # use the longest rule that has the most wildcards
            useRule = reducedMatch[wildIndex[0]]
    else: # if only 1 long rule exists, use it
        useRule = reducedMatch[0]
    return rulebook[useRule]

#=============================================================================#
def evaluateFitness(generatedPattern, predictedPattern):
    correctMatches = [g == p for (g,p) in zip(generatedPattern, predictedPattern)].count(True)
    # TODO: correct final fitness output
    # Necessary?
    return correctMatches

def evaluatePredictor(rulebook, initialPattern, generatedPattern):
    predictedPattern = predictPattern(rulebook, initialPattern, generatedPattern)
    fitness = evaluateFitness(generatedPattern, predictedPattern)
    return fitness

def evaluateGenerator(rulebook, initialPattern, predictedPattern):
    generatedPattern = generatePattern(rulebook, initialPattern, len(predictedPattern))
    fitness = len(predictedPattern) - evaluateFitness(generatedPattern, predictedPattern)
    return fitness

def evaluatePredictorPopulation(predictorPopulation, initialPattern, generatedPattern):
    # A better way to do this?
    for i in range(len(predictorPopulation)):
        rulebook = predictorPopulation[i]['rulebook']
        predictorPopulation[i]['fit'] = evaluatePredictor(rulebook, initialPattern, generatedPattern)
    return predictorPopulation

def evaluateGeneratorPopulation(generatorPopulation, initialPattern, predictedPattern):
    # A better way to do this?
    for i in range(len(generatorPopulation)):
        rulebook = generatorPopulation[i]['rulebook']
        generatorPopulation[i]['fit'] = evaluateGenerator(rulebook, initialPattern, predictedPattern)
    return generatorPopulation
#=============================================================================#
def tournamentSelection(population, thePit): # without replacement
    random.shuffle(population) # randomize population order
    survivors = []
    for i in range(0, len(population), thePit):
        survivors.append(max(population[i:i+thePit], key=itemgetter('fit','allowance')))
    return survivors

#=============================================================================#
def breedChildren(parentPopulation, pXover=0.45, pMut=0.45, pPass=0.03, pNew=0.07,
                  pMutType = [0.15, 0.15, 0.15, 0.15, 0.20, 0.20], ratio=3):
    # ratio is 3:1 children:parent by default
    nC = len(parentPopulation)*ratio # Number of children
    pSum = np.cumsum([0, pXover, pMut, pPass, pNew])
    childrenPopulation = []
    while (len(childrenPopulation) < nC): # Breed children until the good Lord tells us to stop
        rd = random.random()
        if (pSum[0] <= rd and rd < pSum[1]):
        # Crossover
            rdmom = random.randint(0, len(parentPopulation)-1)
            rddad = random.randint(0, len(parentPopulation)-1)
            while rdmom == rddad: # just in case they end being the same, say no to cloning
                rddad = random.randint(0, len(parentPopulation)-1)
            momRulebook = parentPopulation[rdmom]['rulebook']
            dadRulebook = parentPopulation[rddad]['rulebook']
            sisRulebook, broRulebook = xover.uniform(momRulebook, dadRulebook)
            childrenPopulation.append(rulebookIndividual(sisRulebook))
            childrenPopulation.append(rulebookIndividual(broRulebook))
        elif (pSum[1] <= rd and rd < pSum[2]):
        # Mutation
            mSum = np.cumsum([0] + pMutType)
            rdind = random.randint(0, len(parentPopulation)-1) # chose random individual
            mutantRulebook = parentPopulation[rdind]['rulebook']
            rdmut = random.random()
            if (mSum[0] <= rdmut and rdmut < mSum[1]): mut.addRule(mutantRulebook)
            if (mSum[1] <= rdmut and rdmut < mSum[2]): mut.flipOutput(mutantRulebook)
            if (mSum[2] <= rdmut and rdmut < mSum[3]): mut.addBit(mutantRulebook)
            if (mSum[3] <= rdmut and rdmut < mSum[4]): mut.shuffle(mutantRulebook)
            if (mSum[4] <= rdmut and rdmut < mSum[5]): mut.bitWild(mutantRulebook)
            if (mSum[5] <= rdmut and rdmut <=mSum[6]): mut.bitFlip(mutantRulebook)
            childrenPopulation.append(rulebookIndividual(mutantRulebook))
        elif (pSum[2] <= rd and rd < pSum[3]):
        # Pass through
            rdpass = random.randint(0, len(parentPopulation)-1)
            childrenPopulation.append(parentPopulation[rdpass])
        # elif (pSum[3] <= rd and rd <= pSum[4]):
        else:
        # Fresh Meat!
            longestRulebook = 1000 - min(parentPopulation, key = itemgetter('allowance'))['allowance']
            childrenPopulation.append(createIndividual(4, longestRulebook))
    return childrenPopulation[0:nC]

#=============================================================================#
# CODE GRAVEYARD
#=============================================================================#
# # Returns fittest and leanest individual
# def getFittest(population):
#     # Sort population with fittest first
#     sortedPopulation = sorted(population, key=itemgetter('fit'), reverse=True)
#     best = max(population, key=itemgetter('fit'))
#     best = max(population, key=itemgetter('fit','allowance'))
# # newlist = sorted(list_to_be_sorted, key=itemgetter('name'))

# def tournamentSelection(population, thePit): # without replacement
#     random.shuffle(population) # randomize population order
#     survivors = []
#     for i in range(0, len(population), thePit):
#         # silly implementation, TODO: improve this!
#         for j in range(thePit):
#             if j == 0:
#                 champion = population[i+j]
#             if (j != 0 and champion['fit'] < population[i+j]['fit']):
#                 champion = population[i+j]
#         survivors.append(champion)
#         champion = {}
#     return survivors

# Test generator
# rulebook = {'1':'0','0':'1','1010':'1'}
# pattern = '1'
# generatePattern(rulebook, pattern, 10)

# # After a xover or mutation, make sure there are no repeated rules
# # if there are, select 1 randomly and delete the rest
# def housekeeping(rulebook):
#     # delete all duplicated but 1, randomly
#     return 0
