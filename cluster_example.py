import numpy
from nltk.cluster import KMeansClusterer, GAAClusterer, euclidean_distance

job_titles = [
    'Not so skilled worker',
    'Skilled worker',
    'Banana picker',
    'Police officer',
    'Office worker',
    'Fireman',
    'IT consultant',
    'Rapist of old ladies',
    'Engineer',
    'Stupid bastard son',
    'Genious computer analyst',
    'Computer banana peeler',
    'Potato peeler',
    'CEO of a major business',
    'Business economist',
    'Data analyst',
    'Economist analyst bastard',
    'Psychologist data enumerator',
    'Psychologist genious',
    'Evil genious',
    'Murderer and rapist of cats',
    'Cat psychologist',
    'Top Software Engineer in IT with NLTK experience',
    'xim',
    'fission6'
]

words = set()
for title in job_titles:
    for word in title.split():
        words.add(word.lower())
words = list(words)

def vectorspaced(title):
    title_components = [word.lower() for word in title.split()]
    return numpy.array([word in title_components and 1 or 0 for word in words])

cluster = GAAClusterer(5, euclidean_distance)
cluster.cluster([vectorspaced(title) for title in job_titles])

# NOTE: This is inefficient, cluster.classify should really just be called when
# you are classifying previously unseen examples!
classified_examples = [
        cluster.classify(vectorspaced(title)) for title in job_titles
    ]

for cluster, title in sorted(zip(classified_examples, job_titles)):
    print cluster, title