# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 13:13:58 2016

@author: robsalz
"""

#TODO load notifications and labels 
import pandas as pd
import pickle
import matplotlib.pyplot as plt

try:
    clusters_df = pd.read_csv('clusters_not_df.csv', index_col = 0)
except IOError:
    print 'There the data csv is not specified'
    quit

try:
    labels_df = pd.read_csv('labels_not_df_all.csv', index_col = 0)
    df = pd.concat([clusters_df, labels_df], axis=1, join_axes=[clusters_df.index])
except IOError:
    print 'data missing'

#Load the lables dictionary
try:
    labels = pickle.load( open( "all_labels.p", "rb" ) )
except IOError:
    print 'data missing'

#Count label occurences 
label_count = df['label'].value_counts()

#Split the dictionary into sub dict based on the system 
#System dictionaries
Mill = {}
Feeder = {}
Reject = {}
PA = {}
PF = {}
Hydraulic = {}
Lub = {}

#TODO decide if elif is better
for l in labels:
    if 'Mill' in l:
        Mill[l]= labels[l]
    if 'Feeder' in l:
        Feeder[l]= labels[l]    
    if 'Reject' in l:
        Reject[l]= labels[l]  
    if 'PA' in l:
        PA[l]= labels[l]
    if 'Hydraulic' in l:
        Hydraulic[l]= labels[l]
    if 'Lub' in l:
        Lub[l]= labels[l]
        
count_mill = 0
count_feeder = 0
count_reject = 0
count_lub = 0
count_hydraulic = 0
count_pa = 0
count_pf = 0

for label in labels_df['label']:
    if sum(l in label for l in Mill.values()):
        count_mill+=1
    if sum(l in label for l in Feeder.values()):
        count_feeder+=1
    if sum(l in label for l in Reject.values()):
        count_reject+=1
    if sum(l in label for l in Lub.values()):
        count_lub+=1
    if sum(l in label for l in Hydraulic.values()):
        count_hydraulic+=1
    if sum(l in label for l in PA.values()):
        count_pa+=1
    if sum(l in label for l in PA.values()):
        count_pf+=1