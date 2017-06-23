#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Created on Mar 23 2016

@author: Vasken Dermardiros
ID: 26049516

Final project for COEN6321: Evolutionary Systems
Professor Nawwaf Kharma

crossover
---------
1. uniform crossover
"""
# Import dependencies
import random
import numpy as np

# break individuals in two and combine them together to make two children
def uniform(motherRulebook, fatherRulebook):
    sisterRulebook = {}
    brotherRulebook = {}
    for k, v in motherRulebook.iteritems():
        if random.randint(0,1) == 0:
            sisterRulebook.update({k:v})
        else:
            brotherRulebook.update({k:v})
    for k, v in fatherRulebook.iteritems():
        if random.randint(0,1) == 0:
            sisterRulebook.update({k:v})
        else:
            brotherRulebook.update({k:v})
    # If either resulting rulebook is empty, add a random rule
    if len(sisterRulebook) == 0: sisterRulebook = createRule(3)
    if len(brotherRulebook) == 0: brotherRulebook = createRule(3)
    return sisterRulebook, brotherRulebook

# same function from "functions.py" file
# copied here to avoid circular referencing...
def createRule(ruleLength):
	# based on a Poisson distribution for actual length
    actualLength = np.random.poisson(ruleLength-1, 1) + 1 # can't be 0
    rule = np.random.randint(2, size=actualLength) # this is a list
    rule = ''.join(map(str, rule))                 # this is a string
    output = str(np.random.randint(2, size=1)[0])  # this is also a string
    return {rule: output}

#=============================================================================#
# CODE GRAVEYARD
#=============================================================================#
# popitem() is reference based. It's destroying the original rulebook
# # break individuals in two and combine them together to make two children
# def uniform(motherRulebook, fatherRulebook):
#     sisterRulebook = {}
#     brotherRulebook = {}
#     for i in range(len(motherRulebook)):
#         k, v = motherRulebook.popitem()
#         if random.randint(0,1) == 0:
#             sisterRulebook.update({k:v})
#         else:
#             brotherRulebook.update({k:v})
#     for i in range(len(fatherRulebook)):
#         k, v = fatherRulebook.popitem()
#         if random.randint(0,1) == 0:
#             sisterRulebook.update({k:v})
#         else:
#             brotherRulebook.update({k:v})
#     return sisterRulebook, brotherRulebook
