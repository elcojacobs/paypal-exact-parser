import csv

gb_cc = 1294

input = '/home/elco/Downloads/CSV_CC_20210426_131441.csv'
output = input.rstrip(".csv") + "-exact-import.csv"

with open(input, encoding='utf-8-sig') as csvfile:
    with open(output, 'w', newline='', encoding='utf-8-sig') as output:
        writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_ALL)
        reader = csv.DictReader(csvfile)
        for row in reader:
            for key, value in row.items():
                # replace characters that are not available in cp1252
                row[key] = value.encode(
                    'iso-8859-1', 'ignore').decode('iso-8859-1')

            omschrijving = row['Omschrijving']
            referentie = row['Transactiereferentie']
            bedrag = row['Bedrag']
            datum = row['Datum']

            csvline = [referentie, bedrag, omschrijving, datum, 1294]
            print(csvline)
            writer.writerow(csvline)
