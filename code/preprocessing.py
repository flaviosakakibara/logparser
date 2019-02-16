import json
import ijson
import os
from pathlib import Path
import tqdm


def generateParsed(logFile, logFileParsed):

    if logFile.is_file():
        if logFileParsed.is_file():
            print("Log file already parsed... Moving on.")
            return 0
        else:
            retCode, parsedLogs = logParser(logFile)
            print(parsedLogs)
            return 1
    else:
        print("Log file to parse not found. Please inform a valid one")
        return -1


def logParser(logFile):

    isReading = False
    parsedLogs = []
    parsedLog = {
        'message': '',
        'priority': ''
    }

    print('Starting log parsing...')
    with open(logFile) as inFile:

        parser = ijson.parse(inFile)

        for event, prefix, value in parser:

            print('\nevent: ', event, 'prefix: ', prefix, 'value: ', value)
            if prefix == 'start_array':
                continue
            elif prefix == 'start_map':
                isReading = True
                continue
            elif prefix == 'map_key':
                continue
            elif prefix == 'end_map':
                isReading = False
                parsedLogs.append(parsedLog.copy())
            elif prefix == 'string':
                if event == 'item.MESSAGE':
                    parsedLog['message'] = value
                elif event == 'item.PRIORITY':
                    parsedLog['priority'] = value
                else:
                    continue
            elif prefix == 'end_array':
                return 0, parsedLogs
            else:
                return -1, prefix

if __name__ == '__main__':

    prefixLogFile = '/home/flaviorissosakakibara/journalctl_teste'
    logFile = Path(prefixLogFile + '.json')
    logFileParsed = Path(prefixLogFile + '-parsed.json')
    logFileWithoutUnwanted = Path(prefixLogFile + '-wthout.json')

    generateParsed(logFile, logFileParsed)
