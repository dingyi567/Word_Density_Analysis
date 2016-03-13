import scrapy
import json
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
import lxml.etree
import lxml.html
import string
from nltk.corpus import stopwords
from collections import OrderedDict

def removePunctuation(inputString):
    table = string.maketrans("","")
    return inputString.translate(table, string.punctuation)

# Bigrams
def getBigrams(inputList, isList):
    outputList = []
    if not isList:
        inputList = inputList.splitlines()
    for item in inputList:
        itemList = item.split(' ')
        itemList = [i for i in itemList if i!=""]
        for i in range(len(itemList)-1):
            outputList.append(itemList[i] + " " + itemList[i+1])
    return outputList

# Trigrams
def getTrigrams(inputList, isList):
    outputList = []
    if not isList:
        inputList = inputList.splitlines()
    for item in inputList:
        itemList = item.split(' ')
        itemList = [i for i in itemList if i!=""]
        for i in range(len(itemList)-2):
            outputList.append(itemList[i] + " " + itemList[i+1] + " " + itemList[i+2])
    return outputList


def generateDict(inputList, dictionary):
    for key in inputList:
        if key not in dictionary:
            dictionary[key] = 1
        else:
            dictionary[key] += 1
    return dictionary

def cleanList(inputList):
    outputList = []
    table = string.maketrans("","")
    for item in inputList:
       item = item.strip(' \t\n\r')
       if item != "" :
        item = str(item).translate(table, string.punctuation)
        item = removeStopWords(item)
        outputList.append(item)
    return outputList

def cleanText(inputText):
    outputText = ""
    table = string.maketrans("","")
    for line in inputText.splitlines():
        if line.rstrip():
            line = line.translate(table, string.punctuation)
            line = removeStopWords(line)
            outputText += line + "\n"
    return outputText

def removeStopWords(inputText):
	cachedStopWords = stopwords.words("english")
	inputText = ' '.join([word for word in inputText.split() if word not in cachedStopWords])
	return inputText


def generateCompareItemList(inputKeyDict, inputTextDict):
    all_CompareItem = []
    for k, v1 in inputKeyDict.iteritems():
        v2 = 0
        if k in inputTextDict.keys():
            v2 = inputTextDict[k]
        all_CompareItem.append(CompareItem(k, v1, v2))
    all_CompareItem = sorted(all_CompareItem, key=lambda x: (x.keyCount, x.textCount), reverse=True)
    return all_CompareItem

def getTop3grams(inputList):
    n = len(inputList)
    if n > 3:
        n = 3
    inputList = inputList[:n]
    outputList = []
    for item in inputList:
        outputList.append(item.value)
    return outputList


class PageItem(scrapy.Item):
    html = scrapy.Field()
    text = scrapy.Field()
    keywords = scrapy.Field()

    keywords_bigrams = scrapy.Field()
    keywords_trigrams = scrapy.Field()

    text_bigrams = scrapy.Field()
    text_trigrams = scrapy.Field()

    result_bigrams = scrapy.Field()
    result_trigrams = scrapy.Field()

    top3_bigrams = scrapy.Field()
    top3_trigrams = scrapy.Field()

class CompareItem(object):
    def __init__(self, value, keyCount, textCount):
        self.value = value
        self.keyCount = keyCount
        self.textCount = textCount


class BrightEdgeSpider(scrapy.Spider):
    name = "BrightEdge1"
    # start_urls = ["http://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster"]
    # start_urls = ["http://blog.rei.com/camp/how-to-introduce-your-indoorsy-friend-to-the-outdoors/"]
    start_urls = ["http://www.cnn.com/2013/06/10/politics/edward-snowden-profile/"]
    
    def parse(self,response): 
    	pageItem = PageItem()
    	pageItem['html'] = response.body

    	root = lxml.html.fromstring(response.body)
        lxml.etree.strip_elements(root, lxml.etree.Comment, "script", "style", "head")
        pageItem['text'] = lxml.html.tostring(root, method="text", encoding='utf-8')
        pageItem['text'] = cleanText(pageItem['text'])
        pageItem['text_bigrams'] =  getBigrams(pageItem['text'], False)
        pageItem['text_trigrams'] =  getTrigrams(pageItem['text'], False)

        dictText_bigrams = {}
        dictText_bigrams = generateDict(pageItem['text_bigrams'], dictText_bigrams)
        dictText_trigrams = {}
        dictText_trigrams = generateDict(pageItem['text_trigrams'], dictText_trigrams)



        list1= response.xpath('//head/meta[contains(@name, "title")]/@content').extract()  
        list2 = response.xpath('//head/title/text()').extract()
        pageItem['keywords'] = list1 + list2
        pageItem['keywords'] += response.xpath('//head/meta[contains(@name, "keywords")]/@content').extract()
        pageItem['keywords'] += response.xpath('//body//h1/text()').extract()

        allKeywords = cleanList(pageItem['keywords'])

        pageItem['keywords_bigrams'] = getBigrams(allKeywords, True)
        pageItem['keywords_trigrams'] = getTrigrams(allKeywords, True)

        dictKey_bigrams = {}
        dictKey_bigrams = generateDict(pageItem['keywords_bigrams'], dictKey_bigrams)
        dictKey_trigrams = {}
        dictKey_trigrams = generateDict(pageItem['keywords_trigrams'], dictKey_trigrams)
 


        result_bigrams = generateCompareItemList(dictKey_bigrams, dictText_bigrams)
        pageItem['result_bigrams'] = result_bigrams
        result_trigrams = generateCompareItemList(dictKey_trigrams, dictText_trigrams)
        pageItem['result_trigrams'] = result_trigrams

        top3_bigrams = getTop3grams(result_bigrams)
        pageItem['top3_bigrams'] = top3_bigrams
        top3_trigrams = getTop3grams(result_trigrams)
        pageItem['top3_trigrams'] = top3_trigrams


        print top3_bigrams
        print "-----"
        print top3_trigrams

    



