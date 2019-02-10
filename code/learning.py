from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import re
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
    table = str.maketrans('', '', string.punctuation)
    list_of_words = []

    # print('Files\' lines ammount: ', file_len(logFile)) 5kk lines
    with open(logFile, mode='r') as file:

        for line in file:
            line = line.split()
            line = [word for word in line if word.isalpha() and word not in enStopWords]
            list_of_words.append(line)

    # Defining a list of words in the log file
    # [
    #  [],
    #  [],
    # ]

    print(list_of_words[:10])
