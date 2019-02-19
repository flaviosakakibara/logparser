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


def adjustPriority(priority, errorPriorities):

    if priority in errorPriorities:
        return 0
    else:
        return 1


def loadWordDict(wordDictionaryFile):

    with open(wordDictionaryFile, 'r') as infile:
        return json.load(infile)


def saveWordDict(wordDictionary, wordDictionaryFile):

    with open(wordDictionaryFile, 'w') as outfile:
        json.dump(wordDictionary, outfile)

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
        'testing': 0.3,
        'validating': 0.5
    }

    prefixLogFile = '/home/flaviorissosakakibara/journalctl3_1'
    logFileWithoutUnwanted = Path(prefixLogFile + '-wthout.json')
    wordDictionaryFile = 'word_dictionary.json'

    print('\nStage 1: Preprocessing')
    retcode = preprocessing.processLogFile(prefixLogFile)

    print('\nStage 2: Data preparation')
    # Data exploration
    with open(logFileWithoutUnwanted, 'r') as infile:
        fullDataset = json.load(infile)
    fullDatasetSize = len(fullDataset)
    learningDatasetSize = ceil(fullDatasetSize * ratio['learning'])
    testingDatasetSize = floor(fullDatasetSize * ratio['testing'])
    validationSize = floor(learningDatasetSize * ratio['validating'])
    print('Size of dataset: ', fullDatasetSize,
          '\nLearning dataset size: ', learningDatasetSize,
          '\nTesting dataset size: ', testingDatasetSize)
    learningDataset = fullDataset.copy()[:learningDatasetSize]
    testingDataset = fullDataset.copy()[:learningDatasetSize-1:-1]

    # Adjusting priorities to error labels
    learningDataset = [{'priority': adjustPriority(item['priority'],
                                                   errorPriorities),
                        'message': item['message']}
                       for item in learningDataset]
    testingDataset = [{'priority': adjustPriority(item['priority'],
                                                  errorPriorities),
                       'message': item['message']}
                      for item in testingDataset]

    print('Stage 3: Creating word dictionary')
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
    wordDictionary['UNK'] = 0
    wordDictionary['PAD'] = 1
    wordDictionary = {word: index
                      for index, word in enumerate(listOfDistinctWords, 2)}
    wordNumber = len(wordDictionary)
    saveWordDict(wordDictionary, wordDictionaryFile)

    print('\nStage 4: Encoding datasets with dict')
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
    print('\nStage 5: Creating tensors')
    # Creating tensors
    learningData = keras.preprocessing.sequence.pad_sequences(encLearningDsMessages,
                                                              value=wordDictionary['PAD'],
                                                              padding='post',
                                                              maxlen=1000)
    testingData = keras.preprocessing.sequence.pad_sequences(encTestingDsMessages,
                                                             value=wordDictionary['PAD'],
                                                             padding='post',
                                                             maxlen=1000)

    # Defining model
    # Labels: 0 or 1 i.e error or not error
    print('\nStage 6: Model definition and training')
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
    valMessages = learningData[:validationSize]
    partialValMessages = learningData[validationSize:]
    valPriorities = encLearningDsPriority[:validationSize]
    partialValPriorities = encLearningDsPriority[validationSize:]

    print('\n', valMessages[:10])
    print('\n', partialValMessages[:10])
    print('\n', valPriorities[:10])
    print('\n', partialValPriorities[:10])

    # Training the model
    history = model.fit(partialValMessages,
                        partialValPriorities,
                        epochs=10,
                        batch_size=512,
                        validation_data=(valMessages, valPriorities),
                        verbose=1)

    print('\nStage 7: Model evaluation')
    # Getting the results
    results = model.evaluate(testingData, encTestingDsPriority)
    print(results)

    # Saving the model
    modelFile = 'model10ep.hdf5'
    model.save(modelFile,
               overwrite=False,
               include_optimizer=True)

    # Accuracy over time
    history_dict = history.history
    history_dict.keys()

    acc = history_dict['acc']
    val_acc = history_dict['val_acc']
    loss = history_dict['loss']
    val_loss = history_dict['val_loss']

    epochs = range(1, len(acc) + 1)

    # "bo" is for "blue dot"
    plt.plot(epochs, loss, 'bo', label='Training loss')
    # b is for "solid blue line"
    plt.plot(epochs, val_loss, 'b', label='Validation loss')
    plt.title('Training and validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    plt.show()

    plt.clf()   # clear figure

    plt.plot(epochs, acc, 'bo', label='Training acc')
    plt.plot(epochs, val_acc, 'b', label='Validation acc')
    plt.title('Training and validation accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.show()
