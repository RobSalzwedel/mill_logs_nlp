# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 11:53:13 2016

@author: robsalz

Description: Plan to read the mill logs from CSV to pd.dataframe and clean up data 
"""

# Have the raw data, but it is duplicated under different headings

import pandas as pd

# Units at duvha, removed '03' because it is offline indefinitely

units = ['01','02','04','05','06']
unit_index = {}
for i in units:
    unit_index[i] = data['date'][data['date'] == i].index[0]
