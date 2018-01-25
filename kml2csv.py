from bs4 import BeautifulSoup
import csv
from re import sub
import sys



def add_data_columns(kml):
    columns = ['address','lat','lng'] #default columns
    
    for pm in kml.find_all('Placemark',limit=1): #other data columns
        for child in pm.contents[7].find_all('Data'):
            columns.append(child['name'])

    return columns

def populate_data(kml,writer):
    for pm in kml.find_all('Placemark'):
        data = []
        coords = pm.contents[9].coordinates.string
        coords = sub(r'(\n|\s)+','',coords).split(',')
    
        data.append(pm.contents[1].string) # address
        data.append(coords[1]) # lat
        data.append(coords[0]) # lng

        for child in pm.contents[7].find_all('Data'): #other data
            val = child.find('value').string
            if val == None or val == '' or val == '0':
                val = ''
            elif val == '1' or val == 'x' or val.lower() == 'yes' or val.lower() == 'true':
                val = 'x'
            data.append(val)

        writer.writerow([unicode(d).encode("utf-8") for d in data])

def main(inputfile,outputfile):
    with open(inputfile, 'r') as f:
        kml = BeautifulSoup(f, 'xml')
        with open(outputfile, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(add_data_columns(kml))

            populate_data(kml,writer)

if __name__ == "__main__":
    inputfile = sys.argv[1] 
    outputfile = sys.argv[2]

    main(inputfile,outputfile)
