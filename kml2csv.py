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
        self.styleColumns = []
        self.indexFolder = 0
        self.indexRow = 0
        self.inputFile = inputFile
        self.options = options
        self.rows = []
        self.styleMap = {}

    def camelCase(self, text):
        text = text.replace('_', ' ')
        index = text.find(' ')
        if (index > -1):
            text = text[0:index] + string.capwords(text[index::]).replace(' ','')
        return text

    def sanitize_column_name(self, prefix, name):
        name = self.camelCase(name)
        return '{}{}'.format(prefix + '_' if bool(prefix) else '', name)

    def map_folder_columns(self, data, prefix, columns, level):
        if (not bool(data.contents)):
            return columns

        level += 1
        key = data.name
        if (key == 'Data'):
            prefix = prefix + '_Data'
            key = data['name']

        column_name = self.sanitize_column_name(prefix, key)

        if (key == 'styleUrl' and not self.options['styles']):
            pass
        elif key == 'styleUrl':
            style = data.string.replace('#','')
            row = self.rows[self.indexFolder][self.indexRow]
            self.rows[self.indexFolder][self.indexRow] = { **self.styleMap[style], **row }
        elif (column_name == 'Folder_name'):
            self.folders.append(data.string)
        elif (len(data.contents) > 1):
            if level == 2:
                self.rows[self.indexFolder].append({})
                self.indexRow = len(self.rows[self.indexFolder]) - 1
            for item in data.contents:
                if (item.name is not None):
                    columns = self.map_folder_columns(item, column_name, columns, level)
        else:
            column_name = self.sanitize_column_name(prefix, key)
            self.rows[self.indexFolder][self.indexRow][column_name] = data.string
            if column_name not in columns:
                columns.append(column_name)

        return columns

    def map_style_columns(self, data, prefix, columns, level, key, variant):
        level += 1
        if (not bool(data.contents)):
            return columns

        col = data.name
        if (level == 1):
            key = data['id']
            variant = key.split('-')[-1]
            key = key.replace(f'-{variant}', '')
            if not key in self.styleMap:
                self.styleMap[key] = {}

        column_name = self.sanitize_column_name(prefix, col)

        if (len(data.contents) > 1):
            for item in data.contents:
                if (item.name is not None):
                    columns = self.map_style_columns(item, column_name, columns, level, key, variant)
        else:
            column = f'{self.sanitize_column_name(prefix, col)}_{variant}'
            self.styleMap[key][column] = data.string

            if column not in self.styleColumns:
                columns.append(column)

        return columns

    def convert(self):
        with open(self.inputFile, 'r') as f:
            kml = BeautifulSoup(f, 'xml')

            if (self.options['styles']):
                styles = kml.find_all('Style')
                for index, style in enumerate(styles):
                    styleColumns = self.map_style_columns(style, '', [], 0, '', '')
                    self.styleColumns = [*styleColumns, *self.styleColumns]

            folders = kml.find_all('Folder')
            for index, folder in enumerate(folders):
                self.indexRow = 0
                columns = self.styleColumns if self.options['styles'] else []
                self.columns.append(columns)
                self.rows.append([])
                self.columns[self.indexFolder] = self.map_folder_columns(folder, '', columns, 0)
                self.indexFolder += 1

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
