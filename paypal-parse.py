import csv
#locale.setlocale(locale.LC_ALL, 'nl_NL')
#locale.setlocale(locale.LC_ALL, '')
#print(locale.getdefaultlocale(locale.LC_ALL))
#print(locale.locale_alias)
import time

#locale._print_locale()


# gb_bank = 1110
gb_kruis = 1292
gb_kosten = 5561

# note: add counter to start a new file every 50 transactions, so Exact Online does not time out.

omrekeningen = {}

previous_authorizations = '/home/elco/Dropbox/BrewPi/Administratie/PayPal/2020/2020_05_11-2020_07_28.CSV'
input = '/home/elco/Dropbox/BrewPi/Administratie/PayPal/2020/2020_07_28-2020_09_03.CSV'
output = input.rstrip(".csv") + "-exact-import.csv"
csvfilecopy = open(input, encoding='utf-8-sig')

authorized = {}

total_net = 0.0
total_fee = 0.0
total_gross = 0.0

# parse invoice numbers from previous month
with open(previous_authorizations, encoding='utf-8-sig') as previous_csv:
    reader = csv.DictReader(previous_csv)
    for row in reader:
        for key, value in row.items():
            row[key] = value.encode('iso-8859-1', 'ignore').decode('iso-8859-1') # replace characters that are not available in cp1252

        code = row["Transaction Event Code"]
        factuur_nummer = row['Invoice Number']
        referentie = row['Transaction ID']

        if code == 'T1300' or code == 'T1301': # authorization or re-authorization
            authorized[referentie] = factuur_nummer

# after parsing, in pycharm: file->file enconding->windows 1252->convert
with open(input, encoding='utf-8-sig') as csvfile:
    with open(output, 'w', newline='', encoding='utf-8-sig') as output:
        writer = csv.writer(output, delimiter=',',quoting=csv.QUOTE_ALL)
#       header = csv.reader(csvfile).next()        
#        header = [h.lstrip() for h in headerline.split(',')]
#        header = urllib.unquote(header)
        reader = csv.DictReader(csvfile)
        for row in reader:
            for key, value in row.items():
                row[key] = value.encode('iso-8859-1', 'ignore').decode('iso-8859-1') # replace characters that are not available in cp1252

            factuur_nummer = row['Invoice Number']
            referentie = row['Transaction ID']
            kruisreferentie = row['Reference Txn ID']
            dec_sep = "."
            thousands_sep = ","
            bruto = float(row['Gross'].replace(thousands_sep,"").replace(dec_sep,"."))
            fee = float(row['Fee'].replace(thousands_sep,"").replace(dec_sep,"."))
            netto = float(row['Net'].replace(',',"").replace(',',"."))
            code = row["Transaction Event Code"]
            date = time.strptime(row['Date'], '%d/%m/%Y')
            datestr = time.strftime("%d-%m-%Y", date)

            print(code)
            if code == 'T1300' or code == 'T1301': # authorization or re-authorization
                authorized[referentie] = factuur_nummer

            if code == 'T0006' and bruto > 0: # express checkout API of sale
                if not factuur_nummer:
                    if kruisreferentie: # recover invoice number from authorization
                        print(row)
                        factuur_nummer = authorized[kruisreferentie]

            if row['Balance Impact'] == 'Memo':
                continue # skip transactions not affecting balance

            omschrijving = row['Name'] + ' ' + factuur_nummer + ' ' + row['Type']
            omschrijving = omschrijving[:60]
            opmerking = referentie + ' ' + omschrijving
            opmerking = opmerking[:60]
            common = [datestr, opmerking , omschrijving]

            if row['Currency'] != 'EUR':
                bruto2 = None
                csvfilecopy.seek(0)
                reader2 = csv.DictReader(csvfilecopy)
                row2 = None
                if '%.2f' % fee != "0.00":
                    print(row)
                    print("\n\n\n\n",
                          "***********************",
                          "ERROR: vreemde valuta met fee niet nul in row 1. Please check and correct manually. Fee is ", fee,
                          "\n\n\n\n",
                          "***********************")

                for row2 in reader2:
                    if (row['Transaction ID'] == row2['Reference Txn ID'] or row['Reference Txn ID'] == row2['Reference Txn ID']) \
                            and row2['Currency'] == 'EUR' and row['Time'] == row2['Time']:
                        # euro bedrag gevonden
                        dec_sep = "."
                        thousands_sep = ","
                        bruto2 = float(row2['Gross'].replace(thousands_sep,"").replace(dec_sep,"."))
                        fee2 = float(row2['Fee'].replace(thousands_sep,"").replace(dec_sep,"."))
                        print("Vreemde valuta conversie: ", common, bruto, bruto2, fee, fee2)

                        if '%.2f' % fee2 != "0.00":
                            print(str(row2))
                            print("ERROR: vreemde valuta met fee niet nul in row 2, skipping. Please correct manually")
                        break
                origineel_bedrag = " ({0} {1})".format(bruto, row['Currency'])
                omschrijving = omschrijving[:(60-len(origineel_bedrag))] + origineel_bedrag
                fee_eur = fee / bruto * bruto2
                bruto = bruto2
                netto = bruto2 - fee_eur
                common = [datestr, opmerking , omschrijving]
                if bruto2 is None:
                    print("Probleem met row1 " + str(row) + "en row2 " + str(row2))

                if '%.2f' % fee != "0.00":
                    print("\n\n\n\n",
                          "***********************",
                          "Trying to convert to EUR.", fee, "->", fee_eur,
                          "\n\n\n\n",
                          "***********************")
                    csvline = common + [fee_eur, gb_kosten]
                    # print(csvline)
                    writer.writerow(csvline)

            if 'Conversion' in row['Type'] or 'valutaomrekening' in row['Type']:
                continue

            csvline = common + [bruto, gb_kruis]
            print(csvline)
            writer.writerow(csvline)
            total_net = total_net + netto
            total_fee = total_fee + fee
            total_gross = total_gross + bruto

            if '%.2f' % fee != "0.00":
                csvline = common + [fee, gb_kosten]
                # print(csvline)
                writer.writerow(csvline)

print("Total gross: ", total_gross)
print("Total net: ", total_net)
