# kml2csv
a quick and dirty python script to convert Google Maps KML export to CSV

- grabs _name_, _latitude_, _longitude_, and any extra columns added to the data table
- converts boolean options in the data table to 'x' or '' for true/false, respectively

with help from [mciantyre/KmlToCsv.py](https://gist.github.com/mciantyre/32ff2c2d5cd9515c1ee7)

## usage
install requirements

```
$ python3 kml2csv.py input.kml output.csv
```
