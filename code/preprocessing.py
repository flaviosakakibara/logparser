import json
import ijson
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
    logFileLen = fileLen(logFile)

    print('Starting log parsing...')
    with open(logFile) as inFile:

        # defining progress bar
        with tqdm(
                  #   bar_format="{postfix[0]} {postfix[1][value]:>8.10g}/{postfix[1][total]} {percentage:3.0f}%",
                  postfix=["Logs", dict(value=0)]
                  ) as t:
            parser = ijson.parse(inFile)
            for event, prefix, value in tqdm(parser):
                numParsedLogs += 1
                t.postfix[1]['value'] = numParsedLogs
                t.update()
                if prefix == 'start_array':
                    continue
                elif prefix == 'start_map':
                    isReading = True
                    continue
                elif prefix == 'map_key':
                    continue
                elif prefix == 'number':
                    continue
                elif prefix == 'end_array':
                    continue
                elif prefix == 'null':
                    continue
                elif prefix == 'end_map':
                    isReading = False
                    # print(parsedLog)
                    parsedLogs.append(parsedLog.copy())
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


def removeUnwantedLogs(logFileParsed):

    unwantedMessages = [
        'i2c_hid i2c-ELAN1010:00: i2c_hid_get_input: incomplete report (14/65535)'
    ]
    with open(logFileParsed, 'r') as infile:

        parsedLogs = json.load(infile)
        logsWithoutUnwanted = [log
                               for log in parsedLogs
                               if log['message'] not in unwantedMessages]

    return 1, logsWithoutUnwanted


if __name__ == '__main__':

    prefixLogFile = '/home/flaviorissosakakibara/journalctl3'
    logFile = Path(prefixLogFile + '.json')
    logFileParsed = Path(prefixLogFile + '-parsed.json')
    logFileWithoutUnwanted = Path(prefixLogFile + '-wthout.json')

    retcode, parsedLogs = generateParsed(logFile, logFileParsed)
    if retcode == -1:
        print('An error occurred!')
        raise
    generateWithoutUnwanted(logFileParsed, logFileWithoutUnwanted)
