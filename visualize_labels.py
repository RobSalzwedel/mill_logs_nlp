# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 13:13:58 2016

@author: robsalz
"""

#TODO load notifications and labels 
import numpy as np
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


#TODO create a list of labels and counts


#Split the dictionary into sub dict based on the system 
#System dictionaries
Mill = {}
Feeder = {}
Reject = {}
PA = {}
PF = {}
Hydraulic = {}
Lub = {}


#Create a dictionary for each system label name : label
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



#Count the labelled occurences for  each system (NB must follow labelling 
#naming convention)
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
        
        
#TODO: create a bar graph overview for each system
#TODO: create a bar graph of failures in each system
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xticks(ind + width/2)
ax.set_xticklabels(('Mill', 'Feeder', 'Reject', 'Lub','Hydr','PA','PF'))
count_all = [count_mill, count_feeder, count_reject, count_lub, count_hydraulic,count_pa,count_pf]
N = len(count_all)

## necessary variables
ind = np.arange(N)                # the x locations for the groups
width = .7                      # the width of the bars

## the bars
rects1 = ax.bar(ind, count_all, width,
                error_kw=dict(elinewidth=2,ecolor='blue'))
plt.style.use('seaborn-bright')


label_count_dict = dict(label_count)

Mill2 = {}
#Create dictionary with label name : count
for lc in label_count_dict:
    for m in Mill:
        if lc == Mill[m]:
            Mill2[m]=lc[lc]
