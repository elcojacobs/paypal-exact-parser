import csv
import locale
#locale._print_locale()

#locale.setlocale(locale.LC_ALL, 'nl_NL')

#locale.setlocale(locale.LC_ALL, '')
locale.setlocale(locale.LC_ALL, 'Dutch')
#print(locale.getdefaultlocale(locale.LC_ALL))
#print(locale.locale_alias)

# gb_bank = 1110
gb_kruis = 1292
gb_kosten = 5561

# note: add counter to start a new file every 50 transactions, so Exact Online does not time out.

omrekeningen = {}

input = 'PayPal 2016-03.csv'
output = input.rstrip(".csv") + "-exact-import.csv"
csvfilecopy = open(input, encoding='utf8')

with open(input, encoding='utf8') as csvfile:
    with open(output, 'w', newline='', encoding='iso-8859-1') as output:
        writer = csv.writer(output, delimiter=',',quoting=csv.QUOTE_ALL)
        headerline = csvfile.readline()
        header = [h.lstrip() for h in headerline.split(',')]
        reader = csv.DictReader(csvfile, fieldnames=header)
        for row in reader:
            for key, value in row.items():
                row[key] = value.encode('iso-8859-1', 'ignore').decode('iso-8859-1') # replace characters that are not available in cp1252
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
                csvfilecopy.seek(0)
                reader2 = csv.DictReader(csvfilecopy, fieldnames=header)
                row2 = None
                if fee != 0:
                    print("ERROR: vreemde valuta met fee niet nul")
                    exit(1)
                for row2 in reader2:
                    if (row['Transactiereferentie'] == row2['Ref.-id transactie'] or row['Ref.-id transactie'] == row2['Ref.-id transactie']) \
                            and row2['Valuta'] == 'EUR' and row['Tijd'] == row2['Tijd']:
                        # euro bedrag gevonden
                        bruto2 = locale.atof(row2['Bruto'])
                        fee2 = locale.atof(row2['Kosten'])
                        if fee2 != 0:
                            print("ERROR: vreemde valuta met fee niet nul")
                            exit(1)
                        break
                origineel_bedrag = " ({0} {1})".format(bruto, row['Valuta'])
                omschrijving = omschrijving[:(60-len(origineel_bedrag))] + origineel_bedrag
                bruto = bruto2
                common = [row['Datum'], opmerking , omschrijving]
                if bruto2 is None:
                    print("Probleem met row1 " + str(row) + "en row2 " + str(row2))
                    continue

            if 'Omrekening' in row['Type']:
                continue

            csvline = common + [bruto, gb_kruis]
            # print(csvline)
            writer.writerow(csvline)
            if fee != 0:
                csvline = common + [fee, gb_kosten]
                # print(csvline)
                writer.writerow(csvline)