import json
import ijson
import multiprocessing as mp
from nltk.corpus import stopwords
import os
from pathlib import Path
from time import sleep
from tqdm import tqdm


def fileLen(file):

    with open(file) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def generateParsed(logFile, logFileParsed):

    if logFile.is_file():
        if logFileParsed.is_file():
            print("Log file already parsed... Moving on.")
            return 0
        else:
            retCode, parsedLogs = logParser(logFile)
            with open(logFileParsed, 'w') as outfile:
                json.dump(parsedLogs, outfile)
            return 1
    else:
        print("Log file to parse not found. Please inform a valid one")
        return -1


def generateWithoutUnwanted(logFileParsed, logFileWithoutUnwanted):

    if logFileWithoutUnwanted.is_file():
        print("Unwanted logs already removed... Moving on.")
        return 0
    else:
        retCode, withoutUnwantedLogs = removeUnwantedLogs(logFileParsed)
        with open(logFileWithoutUnwanted, 'w') as outfile:
            json.dump(withoutUnwantedLogs, outfile)


def logParser(logFile):

    en_stopwords = stopwords.words('english')
    isReading = False
    numParsedLogs = 0
    parsedLogs = []
    parsedLog = {
        'message': '',
        'priority': ''
    }

    print('Starting log parsing...')
    with open(logFile) as inFile:

        try:
            # defining progress bar
            with tqdm(
                    postfix=["Logs", dict(value=0)]
                    ) as t:
                parser = ijson.parse(inFile)
                for event, prefix, value in tqdm(parser):
                    # updating progress bar
                    numParsedLogs += 1
                    t.postfix[1]['value'] = numParsedLogs
                    t.update()
                    if prefix == 'start_array':
                        continue
                    elif prefix == 'map_key':
                        continue
                    elif prefix == 'number':
                        continue
                    elif prefix == 'end_array':
                        continue
                    elif prefix == 'null':
                        continue
                    elif prefix == 'start_map':
                        isReading = True
                        continue
                    elif prefix == 'end_map':
                        isReading = False
                        parsedLogs.append(parsedLog.copy())
                        parsedLog = {
                            'message': '',
                            'priority': ''
                        }
                    elif prefix == 'string':
                        if event == 'item.MESSAGE':
                            value = value.split()
                            value = [word
                                     for word in value
                                     if word not in en_stopwords]
                            value = ' '.join(value)
                            parsedLog['message'] = value
                        elif event == 'item.PRIORITY':
                            parsedLog['priority'] = value
                        else:
                            continue
                    else:
                        print('Encountered an error while parsing..')
                        print('\nWrong prefix: ', prefix)
                        return -1, prefix
                return 1, parsedLogs
        except TypeError:
            print('\nAn error occurred...',
                  '\n\tPrefix: ', prefix,
                  '\n\tEvent: ', event,
                  '\n\tValue: ', value,
                  '\n\tParsedLog: ',
                  parsedLog['message'],
                  parsedLog['priority'])
        except KeyboardInterrupt:
            print('\nBye')


def processLogFile(prefixLogFile):
    # Top level funcion that coordinates other preprocessing activities

    logFile = Path(prefixLogFile + '.json')
    logFileParsed = Path(prefixLogFile + '-parsed.json')
    logFileWithoutUnwanted = Path(prefixLogFile + '-wthout.json')
    retcode = generateParsed(logFile, logFileParsed)
    if retcode == -1:
        print('An error occurred!')
        raise
    generateWithoutUnwanted(logFileParsed, logFileWithoutUnwanted)


def removeUnwantedLogs(logFileParsed):

    print('\nStarting unwanted logs removal...')
    unwantedMessages = [
        'i2c_hid i2c-ELAN1010:00: i2c_hid_get_input: incomplete report (14/65535)'
    ]
    with open(logFileParsed, 'r') as infile:

        parsedLogs = json.load(infile)
        try:
            logsWithoutUnwanted = [log
                                   for log in parsedLogs
                                   if log['message'] not in unwantedMessages]
        except TypeError:
            print('Log: ', log)

    return 1, logsWithoutUnwanted


if __name__ == '__main__':

    prefixLogFile = '/home/flaviorissosakakibara/datasets/parsed/dataset'
    # processLogFile(prefixLogFile)
    p1 = mp.Process(target=processLogFile,
                    args=(prefixLogFile,),
                    name='Process1')

    prefixLogFile = '/home/flaviorissosakakibara/datasets/parsed/dataset_head'
    # processLogFile(prefixLogFile)
    p2 = mp.Process(target=processLogFile,
                    args=(prefixLogFile,),
                    name='Process2')

    prefixLogFile = '/home/flaviorissosakakibara/datasets/parsed/dataset_tail'
    # processLogFile(prefixLogFile)
    p3 = mp.Process(target=processLogFile,
                    args=(prefixLogFile,),
                    name='Process2')
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()