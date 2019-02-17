import json
import numpy as np
from pathlib import Path
import preprocessing
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import sklearn.metrics as metrics

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

    print('\nStage 3: Defining and Fiting DBSCAN model')
    epsilon = 1.0
    minimunSamples = 10
    db = DBSCAN(eps=epsilon,
                min_samples=minimunSamples).fit(scoredLogs)

    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)

    print('Estimated number of clusters: %d' % n_clusters_)
    print('Estimated number of noise points: %d' % n_noise_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(scoredLogs, labels))

    for i in range(10):
        print('Line: ', logsMessages[i], 'Label: ', labels[i])

    for label in set(labels):
        print('Label: ', label, ' ammount: ', list(labels).count(label))
