import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
#Load the embeddgings from file
embeddings = np.load('final_embeddings.npy')
print np.shape(embeddings)

reverse_dictionary = pickle.load(open( "reverse_dictionary.dict", "rb" ))

# Need to evaluate the cosine distance between all embeddings and each other
# 5000 * 5000 distances, then find thos that are the closest together
num_embed = np.shape(embeddings)[0]
cosine_dist = np.empty([num_embed,2])
print cosine_dist.shape

#Similarity matrix (num_words*num_words
sim_matrix = cosine_similarity(embeddings,embeddings)
print sim_matrix.shape
# Step 1: Find the most similar words to the top 100

sim_matrix[2]
closest_k=10
ind = np.empty([100,closest_k],dtype=int)
for i in xrange(100):
    ind[i] = np.argsort(sim_matrix[i])[-closest_k:][::-1]

for i in xrange(100):
    # Look up the word from reverse dictionary, given sampled example from
    # the head of the distribution

    nearest = ind[i]
    log_str = "Nearest to %s:" % reverse_dictionary[i]
    for k in xrange(1,closest_k):
        close_word = reverse_dictionary[nearest[k]]
        log_str = "%s %s," % (log_str, close_word)
    print log_str

for i in xrange(num_embed):
    for idx, similarity in enumerate(sim_matrix[i]):
        if similarity>= 0.45 and similarity <=0.999:
            print reverse_dictionary[i] + ', '+ reverse_dictionary[idx]
