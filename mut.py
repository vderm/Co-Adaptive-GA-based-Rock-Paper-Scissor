#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Created on Mar 23 2016

@author: Vasken Dermardiros
ID: 26049516

Final project for COEN6321: Evolutionary Systems
Professor Nawwaf Kharma

mutations
---------
1. Rule bit flip:           {'100': '0'} --> {'101': '0'}
2. Rule bit to wildcard:    {'100': '0'} --> {'1.0': '0'}, the "." is a wildcard
3. Rule order shuffle:      {'100': '0'} --> {'010': '0'}
4. Rule add bits:           {'100': '0'} --> {'01010': '0'}
5. Rule flip output bit:    {'100': '0'} --> {'100': '1'}
6. Rulebook add rule:       {'100': '0'} --> {'100': '0', '11': '1'}
"""
# Import dependencies
import numpy as np
import random

# Pick a random rule from the rulebook and flip a bit
def bitFlip(rulebook):
    rd = random.randint(0, len(rulebook)-1) # '-1' due to indexing
    rule, output = rulebook.items()[rd]
    rulebook.pop(rule)         # remove rule from rulebook
    ruleAsList = list(rule)
    rdb = random.randint(0, len(ruleAsList)-1)
    # If the chosen bit is a wildcard, stop this mutation
    if ruleAsList[rdb] == '.': return rulebook.update({rule: output})
    ruleAsList[rdb] = str((int(ruleAsList[rdb]) + 1) % 2)
    modifiedRule = ''.join(ruleAsList)
    return rulebook.update({modifiedRule: output})

# Pick a random rule from the rulebook and add a wildcard
def bitWild(rulebook):
    rd = random.randint(0, len(rulebook)-1) # '-1' due to indexing
    rule, output = rulebook.items()[rd]
    rulebook.pop(rule)         # remove rule from rulebook
    ruleAsList = list(rule)
    rdb = random.randint(0, len(ruleAsList)-1)
    ruleAsList[rdb] = '.'
    modifiedRule = ''.join(ruleAsList)
    return rulebook.update({modifiedRule: output})

# Pick a random rule from the rulebook and shuffle the bits
def shuffle(rulebook):
    rd = random.randint(0, len(rulebook)-1) # '-1' due to indexing
    rule, output = rulebook.items()[rd]
    rulebook.pop(rule)         # remove rule from rulebook
    ruleAsList = list(rule)
    random.shuffle(ruleAsList) # shuffle
    modifiedRule = ''.join(ruleAsList)
    return rulebook.update({modifiedRule: output})

# Pick a random rule from the rulebook, add a bit
def addBit(rulebook):
    rd = random.randint(0, len(rulebook)-1) # '-1' due to indexing
    rule, output = rulebook.items()[rd]
    rulebook.pop(rule) # remove rule from rulebook
    rule = str(random.randint(0, 1)) + rule
    return rulebook.update({rule: output})

# Pick a random rule from the rulebook and flip its output
def flipOutput(rulebook):
    rd = random.randint(0, len(rulebook)-1) # '-1' due to indexing
    rulebook[rulebook.keys()[rd]] = str((int(rulebook.values()[rd]) + 1) % 2)
    return rulebook.update()

# Add a random rule to the rulebook
def addRule(rulebook):
    newRule = createRule(len(max(rulebook.keys())))
    return rulebook.update(newRule)

# same function from "functions.py" file
# copied here to avoid circular referencing...
def createRule(ruleLength):
	# based on a Poisson distribution for actual length
    actualLength = np.random.poisson(ruleLength-1, 1) + 1 # can't be 0
    rule = np.random.randint(2, size=actualLength) # this is a list
    rule = ''.join(map(str, rule))                 # this is a string
    output = str(np.random.randint(2, size=1)[0])  # this is also a string
    return {rule: output}
