from __future__ import absolute_import, division, print_function

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

# Helper libraries
import json
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':

    class_names = ['error', 'info']
    priorities = {
        '0': emerg
        '1': alert
        '2': crit
        '3': err
        '4': warning
        '5': notice
        '6': info
        '7': debug
    }
    errorPriorities = ['0', '1', '2', '3', '4']

    prefixLogFile = '/home/flaviorissosakakibara/journalctl3'
    logFile = Path(prefixLogFile + '.json')
    logFileParsed = Path(prefixLogFile + '-parsed.json')
    logFileWithoutUnwanted = Path(prefixLogFile + '-wthout.json')

    print('\nStage 1: Preprocessing')
    print('\n\t Parsing...')
    retcode, parsedLogs = preprocessing.generateParsed(logFile, logFileParsed, 2891532)
    if retcode == -1:
        print('An error occurred!')
        raise
    print('\n\t Cleaning...')
    preprocessing.generateWithoutUnwanted(logFileParsed, logFileWithoutUnwanted)

    # Data exploration
    with open(logFileWithoutUnwanted, 'r') as infile:
        fullDataset = json.load(infile)
    print('Size of dataset: ', len(fullDataset))
