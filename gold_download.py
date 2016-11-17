#!/usr/bin/env python2
import sys

assert sys.version_info[0] == 2, "the script requires Python 2"


__author__ = "Juan Miguel Cejuela (@juanmirocks)"


help = """
Download organism records from GOLD (Genomes Online Database,
http://www.genomesonline.org/cgi-bin/GOLD/index.cgi)

Use:     %s [--help|--lowercase] (goldcard)*

Example: %s Gc00001 Gc00002 ...


The script will download all records to the **current directory**. Each record
is downloaded as an xml file. The syntax is straightforward. For example,
compare the xml output for Gc00001 with
http://www.genomesonline.org/cgi-bin/GOLD/GOLDCards.cgi?goldstamp=Gc00001

Note: GOLD does not provide xml records. This script fetches the html from the
webpage and tries its best to parse it. The html itself is malformed so the
parsing can go wrong. Report problems to @jmcejuela

OPTIONS
    --lowercase    down case all field names and values. This can be useful
                   to normalize records that perhaps use a different case
"""

def printhelp():
    print help  % (sys.argv[0], sys.argv[0])
    sys.exit()

import requests, re, codecs, sys
from bs4 import BeautifulSoup
from bs4 import element
from lxml import etree

def record_url(goldcard): return "http://www.genomesonline.org/cgi-bin/GOLD/GOLDCards.cgi?goldstamp=" + goldcard

def case(x): return x

def record_html_soup(recordUrl):
    req = requests.get(recordUrl)
    soup = BeautifulSoup(req.content)
    return soup

def parse_table(table):
    section = etree.Element("section")
    section.set("name", case(table.thead.tr.th.string.strip()))
    for row in table('tr')[1:]:
        field = etree.Element("field")
        field.set("name", case(row.select('> th')[1].get_text().strip()))
        rootValueNodes = row.td
        if rootValueNodes:
            values = []
            for child in rootValueNodes.children:
                if isinstance(child, element.NavigableString):
                    c = child.strip()
                else:
                    c = child.get_text().strip()
                if c:
                    values.append(c)
            if values:
                field.set("value", case(", ".join(values)))

        mgi = row.th.get_text().strip()
        if mgi:
            field.set("migs", case(mgi))
        section.append(field)
    return section

def create_ElementTree(goldcard):
    url = record_url(goldcard)
    soup = record_html_soup(url)
    # print soup.prettify() #for debugging

    root = etree.Element("organism")
    etree.SubElement(root, "goldcard").text = goldcard
    etree.SubElement(root, "name").text = soup.h2.string
    etree.SubElement(root, "url").text = url
    etree.SubElement(root, "mci").text = soup.h4.string.partition(")=")[2]
    sections = etree.SubElement(root, "sections")

    for table in soup.find_all('table'):
        sections.append(parse_table(table))

    return etree.ElementTree(root)

def download_record(goldcard):
    xml = create_ElementTree(goldcard)
    filename = goldcard + ".xml"
    file = codecs.open(filename, "w", "utf-8")
    xml.write(file, pretty_print=True)
    file.close()
    return filename

###############################################################################

if len(sys.argv) <= 1:
    printhelp()
elif sys.argv[1].startswith("--"):
    flag = sys.argv[1]
    if flag == "--lowercase":
        def case(x): return x.lower()
    elif flag == "--help":
        printhelp()
    else:
        print "wrong argument: " + flag
        printhelp()
    goldcards = sys.argv[2:]
else:
    goldcards = sys.argv[1:]

for goldcard in goldcards:
    print "gold card: " + goldcard
    try:
        download_record(goldcard)
    except Exception as e:
        print "   Oops! Couldn't download the record. Report this to @jmcejuela\nStack:\n\n"
        print str(e)
