# -*- coding: utf-8 -*-

import requests
import json
import nltk
from nltk.tokenize import LineTokenizer
import csv
import time
import pprint
from unidecode import unidecode
import matplotlib
import pandas
import codecs
import cStringIO

#UnicodeWriter from http://docs.python.org/2/library/csv.html#examples
class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

#/end UnicodeWriter

devkey = (open('dev_key.txt','r')).read()

text = codecs.open('keywords.txt','a')
for y in range(2013, 2014):
    for m in range(1,4): # first number is starting month, last number needs to be one more than final month
        url = 'http://labs.adsabs.harvard.edu/adsabs/api/search/?q=bibgroup:cfa,pubdate:'+str(y)+'-'+str(m)+'&rows=200&fl=keyword&fmt=json&dev_key='+str(devkey)
        print url
        content = requests.get(url)
        k=content.json()
        #pprint.pprint(k)
        docs = k['results']['docs']        
        for i in docs:
            try:
                mywords=i['keyword']
                myList = list(set(mywords)) #magic line that removes exact duplicates from an articles keywords
                cleanList = u' '.join(myList)
                unicode_list = (str(y)+'|'+str(m)+'|')+u'**'.join(myList)
                clean_unicode = '\n'+unicode_list.replace('**','\n'+str(y)+'|'+str(m)+'|')
                #print thisisatest
                text.write(clean_unicode.encode('utf-8'))
            except KeyError:
                pass
        time.sleep(1)
text.close()
print 'finished getting keywords'

text = open('keywords.txt','r').read()
freqlist = open('freqlist.txt','wb')
lowertext = text.lower()
lines = LineTokenizer(blanklines='discard').tokenize(lowertext)
freq = nltk.FreqDist(lines)
#print freq
writer = csv.writer(freqlist, delimiter='|', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerows(freq.items())
freqlist.close()
print 'finished getting frequency distribution'

fileout = codecs.open('frequency.csv', 'wb')

csv_out = csv.writer(fileout, lineterminator='\n', delimiter=',')
wr = UnicodeWriter(fileout,lineterminator='\n', delimiter=',', dialect='excel',quoting=csv.QUOTE_ALL)

wr.writerow(["Year","Month","Keyword","Frequency"])
f = codecs.open('freqlist.txt')
for line in f:
    vals = line.split('|')
    words = [v.replace('\n', '') for v in vals]
    words1 = [v.replace('"', '') for v in words]
    #print words1
    csv_out.writerow((words1[0], words1[1], words1[2], words1[3]))
f.close()
fileout.close()
print 'finished writing csv file'