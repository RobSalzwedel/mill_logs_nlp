# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 11:53:13 2016

@author: robsalz

Description: Plan to read the mill logs from CSV to pd.dataframe and clean up data
"""

## Raw data processing and manipulations

# Have the raw data, but it is duplicated under different headings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import math

#Read data
data = pd.read_csv('mill_logs_2015.csv')

# Clean up data
#delete NaN rows in dates columns, can't use math.isnan because other fields
#are of type string
count = 0
for i in data.index:
    if type(data['date'][i])==float:
        data = data.drop([i])
        
        

# Units at duvha, removed '03' because it is offline indefinitely
units = ['01','02','04','05','06','1 & 2']

#Locate the index of each units mill logs in
unit_index = {}
for i in units:
    unit_index[i] = data['date'][data['date'] == i].index[0]

# Find the number of loged events per online unit
num_logs = np.empty([5,1],int)
num_logs[0] = unit_index['02']-unit_index['01']
num_logs[1] =unit_index['04']-unit_index['02']
num_logs[2] =unit_index['05']-unit_index['04']
num_logs[3] =unit_index['06']-unit_index['05']
num_logs[4] =unit_index['1 & 2']-unit_index['06']

total_logs = num_logs.sum()