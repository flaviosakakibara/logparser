from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
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
            line = [word for word in line if word.isalpha()
                    and word not in enStopWords]
            line = str(line)
            list_of_words.append(line)

    scoredLogs = vectorizer.fit_transform(list_of_words[:1000])

    # Defining and fitting model
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
