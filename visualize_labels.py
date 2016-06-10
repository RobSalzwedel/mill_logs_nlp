# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 13:13:58 2016

@author: robsalz
"""

#TODO load notifications and labels 
import pandas as pd
import pickle

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
