import sys
import re
import csv
import urllib
import urllib2
from lxml import etree
from pprint import pprint

items = []
sys.argv.pop(0)

def hasLetter(inputString):
    for char in inputString:
        if not char.isdigit():
            return True
    return False

def getPage(page,pageData):
    body = {'auction':'bcl'+str(auctionID),'page':'p'+str(page),'p'+str(page):pageData}
    form_data = urllib.urlencode(body)
    response = urllib2.urlopen('http://bid.bclauction.com/cgi-bin/mnlist.cgi', form_data)
    #print response.read()
    newHtml = etree.HTML(response.read())
    rows = newHtml.xpath('//table[@id="DataTable"]/tr')
    for r in rows[1:]:
        if not hasLetter(str(r.attrib['id'])):
            values = r.xpath('td/text()')
            headers = r.xpath('td/strong/text()')
            for header in headers:
                newheader = re.sub(r'\W+', '', header)
                if newheader not in csvheaders:
                    csvheaders.append(newheader)
            itemDict = {}
            for i,c in enumerate(headers):
                itemDict[re.sub(r'\W+', '', headers[i])] = values[i].encode('utf-8')
            itemDict['HIGHBIDDER'] = values[(len(values)-3)].encode('utf-8')
            itemDict['CURRENTPRICE'] = values[(len(values)-2)].encode('utf-8')
            itemDict['ITEMID'] = unicode(r.attrib['id'])
            items.append(itemDict)
            
for x,auction in enumerate(sys.argv):
    items = []
    auctionID = auction
    initialResponse = urllib2.urlopen('http://bid.bclauction.com/cgi-bin/mnlist.cgi?bcl' + auctionID + '/category/ALL')
    html = etree.HTML(initialResponse.read())
    pagesTable = html.xpath('//table')[4]
    inputs = pagesTable.xpath('tr/td/form/input')
    numPages = 0
    pages = []
    csvheaders = ['ITEMID', 'CURRENTPRICE', 'HIGHBIDDER']
    for i in inputs:
        if 'pages' in i.attrib['name']:
            numPages = i.attrib['value']
        elif ('p' in i.attrib['name']) and not ('a' in i.attrib['name']):
            pages.append(i.attrib['value'])
    getPage(1, pages[0])
    if(numPages >= 2):
        for x in range(2, int(numPages)+1):
            getPage(x,pages[x-1])
    for item in items:
        if item['HIGHBIDDER'] == '207533':
            if 'DESCRIPTION' in item:
                print item['DESCRIPTION'] + ' '
            print item['CURRENTPRICE'] + '\n'
    for x in csvheaders:
        print x
    with open('items.csv', 'w+') as f:
        w = csv.DictWriter(f, fieldnames=csvheaders)
        w.writerows(items)
            
            







