# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 11:53:13 2016

@author: robsalz

Description: Plan to read the mill logs from CSV to pd.dataframe and clean up data
"""

## Raw data processing and manipulations

# Have the raw data, but it is duplicated under different headings

import pandas as pd

#Read data
DATA = pd.read_csv('mill_logs_2015.csv')

# Step 1. Remove NaN's i
def delete_nan(data, column=''):
    """Removes all the rows from data where a NaN appears in the specified column """

    for i in data.index:
        if isinstance(data[column][i], float):
            data = data.drop([i])
    #Reset indices after dropping rows
    data = data.reset_index().ix[:, 1:]

    return data

def find_index(data, unit, column):
    """Finds the row where the specified unit appears in the data"""
    unit_index = data[column][data[column] == unit].index[0]
    return unit_index

# Units at duvha, removed '03' because it is offline indefinitely
#units = ['01','02','04','05','06','1 & 2', '3 & 4', '5 & 6', 'EOD', 'OP']

def clean_data(data):
    """Takes the origingal CSV file and returns a standardized DataFrame"""

    #Step 1: Move additional information to the correct columns.
    #Additional information incorrectly appears in the 'date' column in raw_data.csv
    for i in data.index:
        if  data['date'][i] == 'Additional Information':
            data['type'][i] = 'Additional Information'
            data['date'][i] = data['date'][i-1]
            data['description'][i] = data['date'][i+1]

    #Step 2: Find all the units in the date column and create a list
    units = []
    for unit in data['date']:
        if isinstance(unit, str) and len(unit) < 8:
            units.append(unit)

    #Step 3: Create a new column with the unit responsible for each log.
    #Locate the index of each units mill logs in, it incorrectly appears in the 'date' 
    unit_index = {}
    for unit in units:
        unit_index[unit] = find_index(data, unit, 'date')

    #Create new column called unit
    data['unit'] = ''

    #Assign the correct unit based on the index located in the date columns
    for i in range(0, len(units)-1):
        data['unit'][unit_index[units[i]]:unit_index[units[i+1]]] = units[i]
    data['unit'][0:unit_index[units[0]]] = 'all'
    data['unit'][unit_index[units[-1]]:] = 'OP' # Need to clean this up (hacked)

    #Step 3. Remove all of the NaN's from the data
    data = delete_nan(data, 'type')
    data = delete_nan(data, 'description')
    data = delete_nan(data, 'date')

    # Final index of each unit once all the NaNs are removed
    unit_index = {}
    for unit in units:
        unit_index[unit] = find_index(data, unit, 'unit')

    return data, unit_index

# Step 1: Import raw data and clean up into a usable dataframw
data = pd.read_csv('mill_logs_2015.csv')
unit_indices = {}
data, unit_indices = clean_data(data)

# Only select the data for grouped for the units, it is duplicated under all, 1&2, etc...
data = data[unit_indices['01']:unit_indices['1 & 2']]


# Find the number of loged events per online unit
#num_logs = np.empty([5,1],int)
#num_logs[0] = unit_index['02']-unit_index['01']
#num_logs[1] =unit_index['04']-unit_index['02']
#num_logs[2] =unit_index['05']-unit_index['04']
#num_logs[3] =unit_index['06']-unit_index['05']
#num_logs[4] =unit_index['1 & 2']-unit_index['06']
#total_logs = num_logs.sum()
