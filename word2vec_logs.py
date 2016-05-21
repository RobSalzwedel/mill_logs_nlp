from clean_logs import clean_data

import re
import math
import random
import collections
import sys
import nltk

import numpy as np
import tensorflow as tf
import pandas as pd

from six.moves import xrange  # pylint: disable=redefined-builtin

reload(sys)
sys.setdefaultencoding("UTF-8")

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





#Tokenize, remove numbers, punctuation, and split string into a list of words
#NB excludes alphanum eg. 2A and '1A is kept as a word
#TODO: Remove all numbers and punctuation from alphanums
#def tokenize_only(text):
#    from nltk import RegexpTokenizer
#    #Tokenize using a regular expression,
#    #We use consecutive letters (exclude punction and numbers)
#    tokenizer = RegexpTokenizer(r"""([A-Za-z]+[/|-|\][A-Za-z]+|[A-Za-z]+)""")
#    tokens = [word.lower() for word in tokenizer.tokenize(text)]
#    return tokens

def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens

# Loop through log strings, convert to list of words (log_i_words)
# Extend the words list
# TODO: Consider zero padding before and after each log.
words = []
for i in logs:
    log_i_words = tokenize_only(i)
    words.extend(log_i_words)

print('Data size', len(words))

# Step 2: Build the dictionary and replace rare words with UNK token.
vocabulary_size = 3715

def build_dataset(words):
  #Sort words from most common to least common and store in count
  count = [['UNK', -1]]
  count.extend(collections.Counter(words).most_common(vocabulary_size - 1))
  dictionary = dict()
  for word, _ in count:
    dictionary[word] = len(dictionary)
    data = list()
  unk_count = 0
  for word in words:
    if word in dictionary:
      index = dictionary[word]
    else:
      index = 0  # dictionary['UNK']
      unk_count += 1
    data.append(index)
  count[0][1] = unk_count
  # reverse_dictionary{key = index in count, value = word}
  reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
  # data: list of word indexes
  # count: list of tuples (word = str, count = int)
  # dictionary: dict {key = word, value = index in count}
  # reverse_dictionary: dict {key = index in count, value = word}
  return data, count, dictionary, reverse_dictionary

data, count, dictionary, reverse_dictionary = build_dataset(words)
del words  # Hint to reduce memory.
print('Most common words (+UNK)', count[:5])
print('Sample data', data[:10])

data_index = 0


# Step 3: Function to generate a training batch for the skip-gram model.
def generate_batch(batch_size, num_skips, skip_window):
  global data_index
  assert batch_size % num_skips == 0
  assert num_skips <= 2 * skip_window
  batch = np.ndarray(shape=(batch_size), dtype=np.int32)
  labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
  span = 2 * skip_window + 1 # [ skip_window target skip_window ]
  buffer = collections.deque(maxlen=span)
  for _ in range(span):
    buffer.append(data[data_index])
    data_index = (data_index + 1) % len(data)
  for i in range(batch_size // num_skips):
    target = skip_window  # target label at the center of the buffer
    targets_to_avoid = [ skip_window ]
    for j in range(num_skips):
      while target in targets_to_avoid:
        target = random.randint(0, span - 1)
      targets_to_avoid.append(target)
      batch[i * num_skips + j] = buffer[skip_window]
      labels[i * num_skips + j, 0] = buffer[target]
    buffer.append(data[data_index])
    data_index = (data_index + 1) % len(data)
  return batch, labels


batch, labels = generate_batch(batch_size=8, num_skips=2, skip_window=1)
for i in range(8):
  print(batch[i], '->', labels[i, 0])
  print(reverse_dictionary[batch[i]], '->', reverse_dictionary[labels[i, 0]])

# Step 4: Build and train a skip-gram model.

batch_size = 128
embedding_size = 128  # Dimension of the embedding vector.
skip_window = 4       # How many words to consider left and right.
num_skips = 2         # How many times to reuse an input to generate a label.

# We pick a random validation set to sample nearest neighbors. Here we limit the
# validation samples to the words that have a low numeric ID, which by
# construction are also the most frequent.
valid_size = 16     # Random set of words to evaluate similarity on.
valid_window = 100  # Only pick dev samples in the head of the distribution.
valid_examples = np.random.choice(valid_window, valid_size, replace=False)
num_sampled = 64    # Number of negative examples to sample.

graph = tf.Graph()

with graph.as_default():

  # Input data.
  train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
  train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
  valid_dataset = tf.constant(valid_examples, dtype=tf.int32)

  # Ops and variables pinned to the CPU because of missing GPU implementation
  with tf.device('/cpu:0'):
    # Look up embeddings for inputs.
    embeddings = tf.Variable(
        tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))
    embed = tf.nn.embedding_lookup(embeddings, train_inputs)

    # Construct the variables for the NCE loss
    nce_weights = tf.Variable(
        tf.truncated_normal([vocabulary_size, embedding_size],
                            stddev=1.0 / math.sqrt(embedding_size)))
    nce_biases = tf.Variable(tf.zeros([vocabulary_size]))

  # Compute the average NCE loss for the batch.
  # tf.nce_loss automatically draws a new sample of the negative labels each
  # time we evaluate the loss.
  loss = tf.reduce_mean(
      tf.nn.nce_loss(nce_weights, nce_biases, embed, train_labels,
                     num_sampled, vocabulary_size))

  # Construct the SGD optimizer using a learning rate of 1.0.
  optimizer = tf.train.GradientDescentOptimizer(1.0).minimize(loss)

  # Compute the cosine similarity between minibatch examples and all embeddings.
  norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
  normalized_embeddings = embeddings / norm
  valid_embeddings = tf.nn.embedding_lookup(
  normalized_embeddings, valid_dataset)
  similarity = tf.matmul(
  valid_embeddings, normalized_embeddings, transpose_b=True)

# Step 5: Begin training.
num_steps = 6001

with tf.Session(graph=graph) as session:
  # We must initialize all variables before we use them.
  tf.initialize_all_variables().run()
  print("Initialized")

  average_loss = 0
  for step in xrange(num_steps):
    batch_inputs, batch_labels = generate_batch(
        batch_size, num_skips, skip_window)
    feed_dict = {train_inputs : batch_inputs, train_labels : batch_labels}

    # We perform one update step by evaluating the optimizer op (including it
    # in the list of returned values for session.run()
    _, loss_val = session.run([optimizer, loss], feed_dict=feed_dict)
    average_loss += loss_val

    if step % 2000 == 0:
      if step > 0:
        average_loss /= 2000
      # The average loss is an estimate of the loss over the last 2000 batches.
      print("Average loss at step ", step, ": ", average_loss)
      average_loss = 0

    # Note that this is expensive (~20% slowdown if computed every 500 steps)
    if step % 10000 == 0:
      sim = similarity.eval()
      for i in xrange(valid_size):
        # Look up the word from reverse dictionary, given sampled example from
        # the head of the distribution
        valid_word = reverse_dictionary[valid_examples[i]]
        top_k = 8 # number of nearest neighbors
        nearest = (-sim[i, :]).argsort()[1:top_k+1]
        log_str = "Nearest to %s:" % valid_word
        for k in xrange(top_k):
          close_word = reverse_dictionary[nearest[k]]
          log_str = "%s %s," % (log_str, close_word)
        print(log_str)
  final_embeddings = normalized_embeddings.eval()

# Step 6: Visualize the embeddings.
# TODO: Clean up the visualization, reduce overlap, select specific words
# TODO: Save a text file with words closest to eachother (within threshhold)
# TODO: Cluster the words, and print out word clusters
# can think about using cosine distance
# Plot with labels
def plot_with_labels(low_dim_embs, labels, filename='tsne_logs.eps'):
  assert low_dim_embs.shape[0] >= len(labels), "More labels than embeddings"
  plt.figure(figsize=(18, 18))  #in inches
  for i, label in enumerate(labels):
    x, y = low_dim_embs[i,:]
    plt.scatter(x, y)
    plt.annotate(label,
                 xy=(x, y),
                 xytext=(5, 2),
                 textcoords='offset points',
                 ha='right',
                 va='bottom')

  plt.savefig(filename, format='eps')

#Method ensures dependancies are available
try:
  from sklearn.manifold import TSNE
  import matplotlib.pyplot as plt

  tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000)
  plot_only = 500
  low_dim_embs = tsne.fit_transform(final_embeddings[:plot_only,:])
  labels = [reverse_dictionary[i] for i in xrange(plot_only)]
  plot_with_labels(low_dim_embs, labels)

except ImportError:
  print("Please install sklearn and matplotlib to visualize embeddings.")

## Step 7: Save to file
#save = True
#if save:
#    import pickle
#    np.save('final_embeddings',final_embeddings)
#    pickle.dump(reverse_dictionary, open( "reverse_dictionary.dict", "wb" ) )

tokenized_logs = []
for idx, log in enumerate(logs):
   tokenized_logs.append(tokenize_only(log))

embedded_logs = []
embedded_log_arrays=[]
embedded_log_vecs = []
for idx, tokenized_log in enumerate(tokenized_logs):
    embedded_log = []
    for token in tokenized_log:
         embedding = final_embeddings[dictionary[token],:]
         embedded_log.append(embedding)
    embedded_logs.append(embedded_log)
    embedded_log_arrays.append(np.stack(embedded_log,axis=0))
    embedded_log_vecs.append(np.sum(np.stack(embedded_log,axis=0),axis=0))

embsum_matrix = np.stack(embedded_log_vecs)

# Step 8: Clustter the logs based on the feauture array built from word embeddings
from sklearn.cluster import KMeans
num_clusters = 1000

km = KMeans(n_clusters = num_clusters, verbose = True)
km.fit(embsum_matrix)

clusters = km.labels_.tolist()

#Create a list of descriptions grouped by cluster
cluster_list = []
for i in xrange (num_clusters):
    cluster_list.append([])

for idx, cluster in enumerate(clusters):
    cluster_list[cluster].append(logs[idx+12813])


#Export latest cluster to csv
#################################
#clusters_df = pd.DataFrame(logs)
#clusters_df['cluster'] = clusters
#clusters_df.to_csv('clusters_df.csv')
#################################
#import numpy as np
#
#from sklearn.cluster import DBSCAN
#from sklearn import metrics
#from sklearn.datasets.samples_generator import make_blobs
#from sklearn.preprocessing import StandardScaler
#
## Compute DBSCAN
#db = DBSCAN(eps=0.3, min_samples=10).fit(embsum_matrix)
#core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
#core_samples_mask[db.core_sample_indices_] = True
#labels = db.labels_
#
## Number of clusters in labels, ignoring noise if present.
#n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
#
#print('Estimated number of clusters: %d' % n_clusters_)
#print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
#print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
#print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
#print("Adjusted Rand Index: %0.3f"
#      % metrics.adjusted_rand_score(labels_true, labels))
#print("Adjusted Mutual Information: %0.3f"
#      % metrics.adjusted_mutual_info_score(labels_true, labels))
#print("Silhouette Coefficient: %0.3f"
#      % metrics.silhouette_score(X, labels))

### Use Regex to create clusters

# Oil Burners in service 1000
pattern = 'oil burners'
pattern2 = 'shut down|shutdown'
a = []
for i in logs:
    match1 = re.search(pattern,i)
    match2 = re.search(pattern2,i)
    if match1 and match2:
        a.append(i)
  
# Mill X in service      
pattern = '(?=mill\s+(\w+|"\w+")\s+(in\s+service|i/s))'
a = []
for i in logs:
    match1 = re.search(pattern,i)
    if match1:
        a.append(i)
        
# Mill X in shutdown      
pattern = '(?=mill\s+(\w+|"\w+")\s+(shut\s+down|shutdown|s/d))'
a = []
for i in logs:
    match1 = re.search(pattern,i)
    if match1:
        a.append(i)