from bs4 import BeautifulSoup
from os import path, makedirs
import csv
import string
import sys

class Colors:
    HEADER = '\033[95m'
    LTBLUE = '\033[94m'
    LTGREEN = '\033[92m'
    DKGREEN = '\033[32m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class Kml2Csv:
    def __init__(self, options, inputFile):
        self.folders = []
        self.columns = []
        self.indexFolder = 0
        self.indexRow = 0
        self.inputFile = inputFile
        self.options = options
        self.rows = []

    def camelCase(self, text):
        text = text.replace('_', ' ')
        index = text.find(' ')
        if (index > -1):
            text = text[0:index] + string.capwords(text[index::]).replace(' ','')
        return text

    def sanitize_column_name(self, prefix, name):
        name = self.camelCase(name)
        return '{}{}'.format(prefix + '_' if bool(prefix) else '', name)

    def parse_data(self, data, prefix, columns, level):
        level += 1
        if (not bool(data.contents)):
            return columns

        key = data.name
        if (key == 'Data'):
            prefix = prefix + '_Data'
            key = data['name']

        if (not self.options['styles'] and key in ['Style', 'StyleMap', 'styleUrl']):
            return columns

        column_name = self.sanitize_column_name(prefix, key)
        if (column_name == 'Folder_name'):
            self.folders.append(data.string)
            return columns

        if (len(data.contents) > 1):
            if level == 2:
                self.rows[self.indexFolder].append({})
                self.indexRow = len(self.rows[self.indexFolder]) - 1
            for item in data.contents:
                if (item.name is not None):
                    columns = self.parse_data(item, column_name, columns, level)
        else:
            column = self.sanitize_column_name(prefix, key)
            self.rows[self.indexFolder][self.indexRow][column] = data.string
            if column not in columns:
                columns.append(column)

        return columns

    def convert(self):
        with open(self.inputFile, 'r') as f:
            kml = BeautifulSoup(f, 'xml')

            folders = kml.find_all('Folder')
            for index, folder in enumerate(folders):
                self.indexFolder = index
                self.indexRow = 0
                self.columns.append([])
                self.rows.append([{}])
                self.columns[index] = self.parse_data(folder, '', [], 0)

            for index, folder in enumerate(self.folders):
                filename = '{}_{}.csv'.format(self.camelCase(folder), index)
                outputFile = path.join(self.options['outputDir'], filename)
                with open(outputFile, 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, self.columns[index])
                    writer.writeheader()
                    for row in self.rows[index]:
                        writer.writerow(row)
                print(f'{Colors.LTGREEN}created: {Colors.ENDC}{outputFile}')

if __name__ == "__main__":
    inputFile = sys.argv[1]

    options = {
        'outputDir': input(f'{Colors.LTGREEN}specify the destination folder {Colors.DKGREEN}(./output): {Colors.ENDC}') or './output',
        'styles': input(f'{Colors.LTGREEN}include styles? {Colors.DKGREEN}(y/N): {Colors.ENDC}') == 'y',
    }

    try:
        makedirs(options['outputDir'], exist_ok=True)
    except:
        print('Error: unable to create directory: %s', options['outputDir'])

    result = Kml2Csv(options, inputFile)
    result.convert()
