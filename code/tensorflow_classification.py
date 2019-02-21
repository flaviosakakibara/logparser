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


def adjustPriority(priority, errorPriorities):

    if priority in errorPriorities:
        return 0
    else:
        return 1


def createWordDict(fullDataset):

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
    saveWordDict(wordDictionary, wordDictionaryFile)

    return wordDictionary, wordNumber


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


def generateTensor(listOfMessages):

    maxLen = 1100
    padValue = 1
    tensor = keras.preprocessing.sequence.pad_sequences(listOfMessages,
                                                        value=padValue,
                                                        padding='post',
                                                        maxlen=maxLen)
    return tensor


def loadWordDict(wordDictionaryFile):

    with open(wordDictionaryFile, 'r') as infile:
        return json.load(infile)


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

    dataset = 'dataset_tail'
    epochs = 20
    prefixLogFile = '/home/flaviorissosakakibara/datasets/parsed/'+dataset
    logFileWithoutUnwanted = Path(prefixLogFile + '-wthout.json')
    wordDictionaryFile = dataset+'.dict.json'

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
    wordDictionary, wordNumber = createWordDict(fullDataset)

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

    # print(encodedLearningDs[:10])
    # print(encodedTestingDs[:10])

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
    learningData = generateTensor(encLearningDsMessages)
    testingData = generateTensor(encTestingDsMessages)

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
                        epochs=epochs,
                        batch_size=512,
                        validation_data=(valMessages, valPriorities),
                        verbose=1)

    print('\nStage 7: Model evaluation')
    # Getting the results
    results = model.evaluate(testingData, encTestingDsPriority)
    print('\nResults: ', results)

    # Saving the model
    modelFile = dataset+'-'+str(epochs)+'.hdf5'
    model.save(modelFile,
               overwrite=True,
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
    plt.plot(epochs, loss, 'bo', label='Perda - treinamento')
    # b is for "solid blue line"
    plt.plot(epochs, val_loss, 'b', label='Perda - validação')
    plt.title('Treinamento e validação: perda')
    plt.xlabel('Epochs')
    plt.ylabel('Perda')
    plt.legend()

    plt.show()

    plt.clf()   # clear figure

    plt.plot(epochs, acc, 'bo', label='Acurácia - treinamento')
    plt.plot(epochs, val_acc, 'b', label='Acurácia - validação')
    plt.title('Treinamento e validação: Acurácia')
    plt.xlabel('Epochs')
    plt.ylabel('Acurácia')
    plt.legend()

    plt.show()
