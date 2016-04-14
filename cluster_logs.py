# Cluster the logs based on the semantic meaning
# Need a standardized output for multiple techniques that will allow ease of
# evaluation. this should not be allowed with pep 3
from clean_logs import clean_data

import numpy as np
import pandas as pd
import pickle

# Cluster 1: BOW
def cluster_logs(logs):
    '''
    This function does nothing yet
    Args:

    Return:

    '''
    print logs


# Cluster 2: TfIdf
def tfidf_log_cluster(logs):
    '''
    This function does nothing yet



    '''
    print logs

# Cluster 3: Embedded Representation (Various option)

def emb_vectorizer(logs, dictionary, embeddings):
    """Embedded vectorizer takes word embeddings, dictionary and sentence representing
    mth log

    Args:
        logs = pd.DataFrame(columns=[log_id,log_description])
        dictionary = dict[word:word_id]
        embeddings = word embedding matrix that matches the dict

    Returns:
    np.array (shape = [n,m]): n features, m samples

    """

    pass

embeddings = np.load('final_embeddings.npy')
reverse_dictionary = pickle.load(open( "reverse_dictionary.dict", "rb" ))

# Step 1: Import raw data and clean up into a usable dataframw
data = pd.read_csv('mill_logs_2015.csv')
unit_indices = {}
data, unit_indices = clean_data(data)

# Only select the data for grouped for the units, it is duplicated under all, 1&2, etc...
data = data[unit_indices['01']:unit_indices['1 & 2']]


# Step 1: Create the raw format for training, ie list of words from descriptions

# Create a list of logs
logs = data['description']

del data         #Save memory

emb_vectorizer(logs=logs, dictionary=reverse_dictionary,embeddings=embeddings)
