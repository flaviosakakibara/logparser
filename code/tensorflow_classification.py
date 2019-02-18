from __future__ import absolute_import, division, print_function

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

# Helper libraries
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
        '^::1',
        ''
    ]

    for pattern in listOfPatterns:

        pat = re.compile(pattern)
        listOfWords = [word
                       for word in listOfWords
                       if not pat.match(word)]

    return listOfWords

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
    
    for index, word in enumerate(listOfDistinctWords):
        print('Index: ', index, ' Word: ', word)
