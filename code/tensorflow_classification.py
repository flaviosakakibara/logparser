from __future__ import absolute_import, division, print_function

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

# Helper libraries
from collections import Counter
import json
from math import floor, ceil
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import preprocessing
import re


def removeUnwantedPatterns(listOfWords):

    listOfPatterns = [
        # IPV4
        '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
        # Localhost IPV6
        '^::1'
    ]

    for pattern in listOfPatterns:

        pat = re.compile(pattern)
        listOfWords = [word
                       for word in listOfWords
                       if not pat.match(word)]

    return listOfWords


def encodeMessage(message, wordDictionary):

    encodedList = [encodeWord(word, wordDictionary)
                   for word in message.split(' ')]

    return encodedList


def encodeWord(word, wordDictionary):

    try:
        encodedWord = wordDictionary[word]
        return encodedWord
    except KeyError:
        return 0


if __name__ == '__main__':

    class_names = ['error', 'info']
    priorities = {
        '0': 'emerg',
        '1': 'alert',
        '2': 'crit',
        '3': 'err',
        '4': 'warning',
        '5': 'notice',
        '6': 'info',
        '7': 'debug'
    }
    errorPriorities = ['0', '1', '2', '3', '4']
    ratio = {
        'learning': 0.7,
        'testing': 0.3
    }

    prefixLogFile = '/home/flaviorissosakakibara/journalctl3_1'
    logFileWithoutUnwanted = Path(prefixLogFile + '-wthout.json')

    print('\nStage 1: Preprocessing')
    print('\n\t Parsing...')
    retcode = preprocessing.processLogFile(prefixLogFile)

    print('\nStage 2: Data preparation')
    # Data exploration
    with open(logFileWithoutUnwanted, 'r') as infile:
        fullDataset = json.load(infile)
    fullDatasetSize = len(fullDataset)
    learningDatasetSize = ceil(fullDatasetSize * ratio['learning'])
    testingDatasetSize = floor(fullDatasetSize * ratio['testing'])
    print('Size of dataset: ', fullDatasetSize,
          '\nLearning dataset size: ', learningDatasetSize,
          '\nTesting dataset size: ', testingDatasetSize)
    learningDataset = fullDataset.copy()[:learningDatasetSize]
    testingDataset = fullDataset.copy()[:learningDatasetSize-1:-1]

    # Extracting the messages from the dataset
    # and spliting them into words
    onlyMessages = [message
                    for log in fullDataset
                    for message in log['message'].split(' ')
                    ]
    onlyMessages = removeUnwantedPatterns(onlyMessages)
    listOfDistinctWords = set(onlyMessages)
    print('Messages: ', len(onlyMessages),
          ' Distinct: ', len(listOfDistinctWords))

    # Creating the word dictionary
    wordDictionary = {word: index
                      for index, word in enumerate(listOfDistinctWords, 2)}
    wordDictionary['UNK'] = 0
    wordDictionary['PAD'] = 1
    wordNumber = len(wordDictionary)

    # Encoding Learning and Testing datasets
    encodedLearningDs = [{'priority': item['priority'],
                         'message': encodeMessage(item['message'],
                                                  wordDictionary)}
                         for item in learningDataset]
    encodedTestingDs = [{'priority': item['priority'],
                        'message': encodeMessage(item['message'],
                                                 wordDictionary)}
                        for item in testingDataset]

    maxLearningMessage = max([len(item['message'])
                              for item in learningDataset])
    maxTestingMessage = max([len(item['message'])
                             for item in testingDataset])

    print(encodedLearningDs[:10])
    print(encodedTestingDs[:10])

    encLearningDsMessages = [item['message']
                             for item in encodedLearningDs]
    encLearningDsPriority = [item['priority']
                             for item in encodedLearningDs]
    encTestingDsMessages = [item['message']
                            for item in encodedTestingDs]
    encTestingDsPriority = [item['priority']
                            for item in encodedTestingDs]

    print('Max learning message: ', maxLearningMessage)  # 798
    print('Max testing message: ', maxTestingMessage)  # 991
    # print(Counter([len(item['message']) for item in learningDataset]))
    # using a max size of 1000
    learningData = keras.preprocessing.sequence.pad_sequences(encLearningDsMessages,
                                                              value=wordDictionary['PAD'],
                                                              padding='post',
                                                              maxlen=1000)
    print(learningData[0], learningData[1])

    # Defining model
    # Labels: 0 or 1 i.e error or not error

    model = keras.Sequential()
    model.add(keras.layers.Embedding(wordNumber, 16))
    model.add(keras.layers.GlobalAveragePooling1D())
    model.add(keras.layers.Dense(16, activation=tf.nn.relu))
    model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))

    model.summary()

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    # Generating validation data
    x_val = 
