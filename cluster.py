# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 12:31:08 2016

@author: robsalz

Script to generate cluster information from your vector representations.
"""
import os

import tensorflow as tf
import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile, join
import numpy as np
import tensorflow
from sklearn.cluster import KMeans
from sklearn.externals import joblib

flags = tf.app.flags
flags.DEFINE_string("file", 'mill_logs.csv', "Input csv file")
flags.DEFINE_string("field", 'description', "The field in the csv file that has natural language logs")
flags.DEFINE_string("method", 'kmeans', "Vectorization Method")


#KMEANS FLAGS
flags.DEFINE_integer('num_clusters', 100, 'The number of clusters for KMEANs algorithm')
FLAGS = flags.FLAGS

class Cluster(object):
    '''Base class for all the vectorization classes
    Attributes
    file: (string) Path to the log file.csv
    field: (string) Field containg natural language data in file.csv
    tk: (int) Option to set the tokenization method 
    data: (pd.DataFrame) Data frame of the CSV file
    text: (pd.Series) Series of document strings
    '''
    def __init__(self):
        self.file = FLAGS.file
        self.field = FLAGS.field
        self._read_file()
        self.vocab = {}
        self.inv_vocab = []
        
#        self._build_vocab()
#        self._word2id()
    
    def _read_file(self):
        'Function to read file.csv to pd.DataFrame and pd.Series of text'
        self.data = pd.read_csv(self.file)
        self.text = self.data[self.field]
        
    #TODO load cluster for visualization from file, 
    #def load_clusters(self):
    def cluster_list(self):
        '''Generates the cluster lists from the documents labelled with the cluster'''
        self.cluster_list = []
        cluster_list = []
        for i in xrange (self.cluster_list):
            self.cluster_list.append([])
        
        for idx, cluster in enumerate(self.clusters):
            self.cluster_list[cluster].append(self.text[idx])

class KM (Cluster):
    
    def generate_clusters(self):
        '''Generates the cluster assignments for each vector representations 
        available for a given file name and writes to to a new file cluster_foo.csv
        with the field given the title of the hyper parameters used to generate the 
        cluster, as well as the cluster centers.
        '''
        
        km = KMeans(n_clusters=FLAGS.num_clusters)
        
        #TODO, read all the file names that match the 
        # Run through the current directory to find all vector representations 
        #for the file name concerned, load and cluster the array, save 
        mypath = os.getcwd() 
        files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        count = 0 #Count clusters for labelling purposes
        for file_ in files:
            if self.file and 'tfidf' in file_ and 'pkl' not in file_:
                count+=1
                #Numpy array of document vectors  
                vec = np.load(file_)
                file_ = file_.replace('.npy','')
                #Cluster the array 
                km.fit(vec)
                
                #Save the cluster object and load when needed
                cluster_file = file_+'_KM_%d'%FLAGS.num_clusters
                save_path = os.path.join(mypath,'clusters',cluster_file)
                joblib.dump(km, save_path)
                
                #Write clusters allocations to new csv file
                data_cluster_df = self.data
                data_cluster_df['C%d:'%count+cluster_file] = km.labels_.tolist()
        data_cluster_df.to_csv(os.path.join(mypath, 'clusters', 'clustered_' + self.file))

                                
    