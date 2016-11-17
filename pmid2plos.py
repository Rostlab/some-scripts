#!/usr/bin/env python3
import sys

assert sys.version_info[0] == 3, "the script requires Python 3"


__author__ = "Juan Miguel Cejuela (@juanmirocks)"


help = """
Download PLOS (http://www.plos.org/) xml articles given a list of pmids (PubMed ids).
The script assumes that the given pmids correspond to public PLOS articles.
If that's not the case, the pmid is ignored but this is reported.

Use:     %s (pmid)*

Example  %s 21245904
"""

def printhelp():
    print(help  % (sys.argv[0], sys.argv[0]))
    sys.exit()

import requests, re, codecs, sys

def dxplos(pmid):
    url = "http://www.ncbi.nlm.nih.gov/pubmed/" + pmid
    req = requests.get(url)
    match = re.search('href="(http://dx.plos.org/10.1371/[^"]+)"', req.text)
    if match: return match.group(1)
    else: None

def urlplos(dxplos):
    # http://dx.plos.org/10.1371/journal.pone.0028106
    req = requests.get(dxplos)
    return req.history[-1].headers['location']

def urlxml(urlplos):
    # http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0028106
    m = re.search('(.*/)(info.*)', urlplos)
    return m.group(1) + 'fetchObjectAttachment.action?uri=' + m.group(2) + '&representation=XML'

def fetch(urlxml):
    # http://www.plosone.org/article/fetchObjectAttachment.action?uri=info%3Adoi%2F10.1371%2Fjournal.pone.0028106&representation=XML
    req = requests.get(urlxml)
    req.encoding = "utf-8"
    filename = re.search('filename="([^"]*)"', req.headers['content-disposition']).group(1)
    file = codecs.open(filename, "w", "utf-8")
    file.write(req.text)
    file.close()
    return filename

###############################################################################

if len(sys.argv) <= 1:
    printhelp()

for pmid in sys.argv[1:]:
    print("PMID: " + pmid)
    dx = dxplos(pmid)
    if not dx:
        print("  no plos article found!")
    else:
        try:
            print("  " + fetch(urlxml(urlplos(dx))))
        except:
            print("  oops! couldn't fetch the xml (network problems on their/yours side?)")
