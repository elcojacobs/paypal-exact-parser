__author__ = 'Elco'

import re

factuurnummer_prev = 0

with open('invoice-list.txt', 'r') as inputfile:
    for line in inputfile:
        factuurnummer = re.findall("Factuur #([0-9]*)", line)
        if factuurnummer:
            factuurnummer = factuurnummer[0]
            print factuurnummer
            if int(factuurnummer) != int(factuurnummer_prev) + 1:
                print "missing in between", factuurnummer_prev, factuurnummer
            factuurnummer_prev = factuurnummer

