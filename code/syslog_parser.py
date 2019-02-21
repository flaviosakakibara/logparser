from pathlib import Path
import json
from os import listdir

if __name__ == '__main__':

    listOfFiles = []
    rootFolder = '/home/flaviorissosakakibara/datasets'
    listOfFolders = [
                    '/home/flaviorissosakakibara/datasets',
                     ]

    for folder in listOfFolders:
        for file in listdir(folder):
            listOfFiles.append(folder+'/'+file)

    # Parsing single file with multiple dicts into
    # single file with a list of dict.
    for folder in listOfFolders:
        print('Folder: ', folder)
        parsedFolder = Path(folder+'/parsed')
        for log in listdir(folder):
            logFile = Path(folder+'/'+log)
            if logFile.is_file():
                parsedLogFile = Path(folder+'/parsed/'+log)
                print('File: ', logFile)
                print('Parsed: ', parsedLogFile)
                array = []
                with open(logFile, 'r') as inFile:
                    for line in inFile:
                        try:
                            array.append(eval(line))
                        except NameError:
                            continue
                print('Len of parsed: ', len(array))
                with open(parsedLogFile, 'w') as outFile:
                    json.dump(array, outFile)
            else:
                continue
        consolidatedLog = Path(folder+'/consolidated.json')
        consolidated = []
        for log in listdir(parsedFolder):
            parsedLogFile = Path(folder+'/parsed/'+log)
            with open(parsedLogFile, 'r') as inFile:
                consolidated.extend(json.load(inFile))
        print('Consolidated: ', len(consolidated))
        with open(consolidatedLog, 'w') as outFile:
            json.dump(consolidated, outFile)
