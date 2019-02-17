import json
from pathlib import Path
import preprocessing
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

if __name__ == '__main__':

    prefixLogFile = '/home/flaviorissosakakibara/journalctl3_1'
    logFileWithoutUnwanted = Path(prefixLogFile + '-wthout.json')

    print('\nStage 1: Preprocessing')
    preprocessing.processLogFile(prefixLogFile)

    print('\nStage 2: Scoring logs with TFIDF')
    with open(logFileWithoutUnwanted, 'r') as infile:
        logs = json.load(infile)
    logsMessages = [log['message'] for log in logs]
    vectorizer = TfidfVectorizer()
    scoredLogs = vectorizer.fit_transform(logsMessages)
    print(scoredLogs[:10])
    print(scoredLogs.shape)

    print('\nStage 3: Defining and Fiting K-means model')
    n_clusters = 2
    model = KMeans(n_clusters=n_clusters, init='k-means++',
                   max_iter=100, n_init=1)
    model.fit(scoredLogs)
    print("Top terms per cluster:")
    order_centroids = model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()
    for i in range(n_clusters):
        print("Cluster %d:" % i)
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind]),
        print
