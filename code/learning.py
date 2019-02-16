from nltk.corpus import stopwords
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
import string


# Function to return the amount of lines of a file
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


if __name__ == '__main__':

    logFile = '/mnt/data/logs/journalctl'
    enStopWords = stopwords.words('english')
    ptStopWords = stopwords.words('portuguese')
    list_of_words = []
    vectorizer = TfidfVectorizer()

    # print('Files\' lines ammount: ', file_len(logFile)) 5kk lines
    with open(logFile, mode='r') as file:

        for line in file:
            line = line.split()
            # removing not alpha chars and "stop words"
            line = [word for word in line[4:] if word.isalpha()
                    and word not in enStopWords]
            line = str(line)
            list_of_words.append(line)

    scoredLogs = vectorizer.fit_transform(list_of_words)
    print(scoredLogs[:10])

    print(scoredLogs.shape)
    # Defining and fitting model
    # n_clusters = 2
    # model = KMeans(n_clusters=n_clusters, init='k-means++',
    #            #    max_iter=100, n_init=1)
    # model.fit(scoredLogs)
    # print("Top terms per cluster:")
    # order_centroids = model.cluster_centers_.argsort()[:, ::-1]
    # terms = vectorizer.get_feature_names()
    # for i in range(n_clusters):
    #     print("Cluster %d:" % i)
    #     for ind in order_centroids[i, :10]:
    #         print(' %s' % terms[ind]),
    #     print

    # ###### DBSCAN
    epsilon = 1.0
    minimunSamples = 10
    db = DBSCAN(eps=epsilon, min_samples=minimunSamples).fit(
        scoredLogs[:10000])

    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)

    print('Estimated number of clusters: %d' % n_clusters_)
    print('Estimated number of noise points: %d' % n_noise_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(scoredLogs[:10000], labels))

    for i in range(10):
        print('Line: ', list_of_words[i], 'Label: ', labels[i])

    for label in set(labels):
        print('Label: ', label, ' ammount: ', list(labels).count(label))
