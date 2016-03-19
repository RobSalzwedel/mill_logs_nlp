# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 11:53:13 2016

@author: robsalz

Description: Plan to read the mill logs from CSV to pd.dataframe and clean up data
"""

## Raw data processing and manipulations

# Have the raw data, but it is duplicated under different headings

import pandas as pd
import matplotlib.pyplot as plt 

data = pd.read_csv('mill_logs_2015.csv')

# Units at duvha, removed '03' because it is offline indefinitely

units = ['01','02','04','05','06','1 & 2']

#Locate the index of each units mill logs in
unit_index = {}
for i in units:
    unit_index[i] = data['date'][data['date'] == i].index[0]

# Find the number of loged events per online unit
num_logs = {}
num_logs[1] = unit_index['02']-unit_index['01']
num_logs[2] =unit_index['04']-unit_index['02']
num_logs[4] =unit_index['05']-unit_index['04']
num_logs[5] =unit_index['06']-unit_index['05']
num_logs[6] =unit_index['1 & 2']-unit_index['06']

