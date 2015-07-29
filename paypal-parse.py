import csv
from pprint import pprint
import locale
#locale._print_locale()
locale.setlocale(locale.LC_ALL, 'Dutch')
#locale.setlocale(locale.LC_ALL, '')
#locale._print_locale()

# gb_bank = 1110
gb_kruis = 1292
gb_kosten = 5561

with open('PayPal 2015-04.csv') as csvfile:
    with open('output.csv', 'wb') as output:
        writer = csv.writer(output, delimiter=',',quoting=csv.QUOTE_ALL)
        header = [h.lstrip() for h in csvfile.next().split(',')]
        reader = csv.DictReader(csvfile, fieldnames=header)
        for row in reader:
            factuur_nummer = row['Factuurnummer']
            omschrijving = row['Naam'] + ' ' + factuur_nummer + ' ' + row['Type']
            opmerking = row['Transactiereferentie'] + ' ' + omschrijving
            omschrijving = omschrijving[:60]
            opmerking = opmerking[:60]
            common = [row['Datum'], opmerking , omschrijving]

            bruto = locale.atof(row['Bruto'])
            fee = locale.atof(row['Kosten'])
            netto = locale.atof(row['Netto'])

            if factuur_nummer.startswith("10000") and bruto > 0 or row['Valuta'] != 'EUR':
                print "skipping :", common
                continue # skip ontvangen webshop betalingen

            writer.writerow(common + [bruto, gb_kruis])

            if fee != 0:
                writer.writerow(common + [fee, gb_kosten])