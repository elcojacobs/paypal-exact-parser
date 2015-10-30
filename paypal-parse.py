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


omrekeningen = {}

input = 'PayPal transacties 2015-09.csv'
output = input.rstrip(".csv") + "-exact-import.csv"

with open(input) as csvfile:
    with open(output, 'wb', encoding='utf-8') as output:
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

            # if factuur_nummer.startswith("10000") and bruto > 0:
            #    print "skipping :", common
            #    continue # skip ontvangen webshop betalingen
            if row['Valuta'] != 'EUR':
                bruto2 = None
                reader2 = reader
                if fee != 0:
                    print "ERROR: vreemde valuta met fee niet nul"
                    exit(1)
                for row2 in reader2:
                    if row['Transactiereferentie'] == row2['Ref.-id transactie'] and row2['Valuta'] == 'EUR':
                        # euro bedrag gevonden
                        bruto2 = locale.atof(row2['Bruto'])
                        fee2 = locale.atof(row2['Kosten'])
                        if fee2 != 0:
                            print "ERROR: vreemde valuta met fee niet nul"
                            exit(1)
                        break
                omschrijving = omschrijving + " ({0} {1})".format(bruto, row['Valuta'])
                bruto = bruto2
                common = [row['Datum'], opmerking , omschrijving]
                if bruto2 is None:
                    print "Probleem met row1 " + row + "en row2 " + row2
                    continue



            writer.writerow(common + [bruto, gb_kruis])
            if fee != 0:
                writer.writerow(common + [fee, gb_kosten])