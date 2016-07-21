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
        
        


## necessary variables
count_all = [count_mill, count_feeder, count_reject, count_lub, count_hydraulic,count_pa,count_pf]
N = len(count_all)
ind = np.arange(N)                # the x locations for the groups
width = .7                      # the width of the bars

#TODO: create a bar graph overview for each system
#TODO: create a bar graph of failures in each system
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xticks(ind + width/2)
ax.set_xticklabels(('Mill', 'Feeder', 'Reject', 'Lub','Hydr','PA','PF'))


## the bars
rects1 = plt.bar(ind, count_all, width,
                error_kw=dict(elinewidth=2,ecolor='blue'))
plt.style.use('seaborn-bright')


label_count_dict = dict(label_count)

#Create dictionaries to plot
pMill = {}
pFeeder = {}
pReject = {}
pPA = {}
pPF = {}
pHydraulic = {}
pLub = {}
#Create dictionary with label name : count
for lc in label_count_dict:
    for m in Mill:
        if lc == Mill[m]:
            pMill[m]=label_count_dict[lc]
    for f in Feeder:
        if lc == Feeder[f]:
            pFeeder[f]=label_count_dict[lc]
    for r in Reject:
        if lc == Reject[r]:
            pReject[r]=label_count_dict[lc]
    for pa in PA:
        if lc == PA[pa]:
            pPA[pa]=label_count_dict[lc]
    for pf in PF:
        if lc == PF[pf]:
            pPF[pf]=label_count_dict[lc]
    for h in Hydraulic:
        if lc == Hydraulic[h]:
            pHydraulic[h]=label_count_dict[lc]

def plot_dict(d,sort = False):
    '''Creates a bar graph for the dictionary d with xticks = d.keys() and 
    bar hight = dict.values()
    
    Parameters
    ----------
    d : dict
        Dictionary of key value pairs where the key is the category and the value
        is the category quantity
    sort : bool
        Boolean determines whether or not to sort the bar graph based on the 
        dictionary values
    '''
    X = np.arange(len(d))
    plt.bar(X, list(reversed(sorted(d.values()))), align='center', width=0.7)
    plt.xticks(X, list(reversed(sorted(d, key=d.get))),rotation='vertical')
    ymax = max(d.values()) + 1
    plt.ylim(0, ymax)
    plt.show()


import numpy as np
import matplotlib.pyplot as plt

from pylab import *

def click(event):
   """If the left mouse button is pressed: draw a little square. """
   tb = get_current_fig_manager().toolbar
   if event.button==1 and event.inaxes and tb.mode == '':
       x,y = event.xdata,event.ydata
       plot([x],[y],'rs')
       draw()

plot((arange(100)/99.0)**3)
gca().set_autoscale_on(False)
connect('button_press_event',click)
show()

# Plot time line of events
# Need to load in the full logs... something went wrong with the labelling process
import random
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv('mill_notifications_2015.csv')
data2 = pd.read_csv('mill_notifications_2014.csv')

#data = data['Title'].str.lower()
#data2 = data2['Title'].str.lower()
data2 = data2[100:-1]

logs = pd.concat((data,data2))
logs = logs.dropna()
logs = logs.reset_index(drop=True)

a  = logs['textbox19']
a.astype(str)

output = []
for x in a.tolist():
    if x not in output:
        output.append(x)
        print output
        
df = pd.DataFrame(data=a.tolist(), index=pandas.DatetimeIndex(logs['DateInitiated']), columns=['categories'])



cat_dict = dict(zip(output, range(1, len(output)+1)))
val_dict = dict(zip(range(1, len(output)+1), output))

df['plotval'] = df['categories'].apply(cat_dict.get)

fig, ax = plt.subplots()
df['plotval'].plot(ax=ax, style='.')
ax.margins(0.2)
