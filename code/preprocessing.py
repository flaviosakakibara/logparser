import json
import ijson
import os
import tqdm


def generateParsed(logFile, logFileParsed):

    if ~ os.path.isfile(logFile):
        print("Log file to parse not found. Please inform a valid one")
        return -1
    elif os.path.isfile(logFileParsed):
        print("Log file already parsed... Moving on.")
        return 0
    else:
        logParser(logFile)
        return 1


if __name__ == '__main__':

    logFile = '/home/flaviorissosakakibara/journalctl3.json'
    logFileParsed = '/home/flaviorissosakakibara/journalctl3-parsed.json'
    logFileWithoutUnwanted = '/home/flaviorissosakakibara/journalctl3-wthout.json'

    generateParsed(logFile, logFileParsed)
