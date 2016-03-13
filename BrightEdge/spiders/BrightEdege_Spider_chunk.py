import scrapy
import json
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.selector import HtmlXPathSelector
import lxml.etree
import lxml.html
import string
import nltk, re, pprint


# Using NLTK to process data, get useful trunks
def preprocess(document):
    # Sentence segmentation
    sentences = nltk.sent_tokenize(document) 
    # Word tokenization
    sentences = [nltk.word_tokenize(sent) for sent in sentences] 
    # Add part-of-speeching tags
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    # Define the rule that when one of the following patterns safisfied, then the NP trunk should be formed
    patterns = """
        NP: {<DT|PP\$>?<JJ>*<NN>}
            {<NNP>+}
            {<NN>+}
            {<NNS>+}
        """
    # Create a chunk parser
    NPChunker = nltk.RegexpParser(patterns) 
    outputList = []
    # Test it on each sentence and get a tree structure result; extract leaves which have "NP" label, then concate the leaves by a whitespace
    for sentence in sentences:
        tree = NPChunker.parse(sentence) 
        for subtree in tree.subtrees():
            if subtree.label() == 'NP': 
                words = [theTuple[0] for theTuple in subtree.leaves()]
                string = ' '.join(words)
                outputList.append(string)
    return outputList

# Group repeated items and compute count for each item
def generateDict(inputList):
    dictionary = {}
    for key in inputList:
        if key not in dictionary:
            dictionary[key] = 1
        else:
            dictionary[key] += 1
    return dictionary

# Sort all the keywords in inputKeyDict by comparing counts which are both in inputKeyDict and inputTextDict
def generateCompareItemList(inputKeyDict, inputTextDict):
    all_CompareItem = []
    if bool(inputKeyDict):
        for k, v1 in inputKeyDict.iteritems():
            v2 = 0
            if k in inputTextDict.keys():
                v2 = inputTextDict[k]
            all_CompareItem.append(CompareItem(k, v1, v2))
        all_CompareItem = sorted(all_CompareItem, key=lambda x: (x.keyCount, x.textCount), reverse=True)
    else:
        for k, v2 in inputTextDict.iteritems():
            v1 = 0
            all_CompareItem.append(CompareItem(k, v1, v2))
        all_CompareItem = sorted(all_CompareItem, key=lambda x: (x.keyCount, x.textCount), reverse=True)
    return all_CompareItem

# Remove empty lines, strip whitespaces and tabs from the beginning and the end of the string in the list
def cleanList(inputList):
    outputList = []
    for item in inputList:
       item = item.strip(' \t\n\r')
       if item != "" :
        outputList.append(str(item))
    return outputList

# Remove empty lines in plain body text
def cleanText(inputText):
    outputText = ""
    for line in inputText.splitlines():
        if line.rstrip():
            outputText += line + "\n"
    return outputText

# Return the top 6 representative strings
def getTop6(inputList):
    n = len(inputList)
    if n > 6:
        n = 6
    inputList = inputList[:n]
    outputList = []
    for item in inputList:
        outputList.append(item.value)
    return outputList

def printResult(inputList):
    print "----------Result------------"
    print inputList
    print "----------------------------"

class PageItem(scrapy.Item):
    html = scrapy.Field()

    text = scrapy.Field()
    keywords = scrapy.Field()

    text_dict = scrapy.Field()
    key_dict = scrapy.Field()

    result_list = scrapy.Field()
    top6list = scrapy.Field()

# Define this class for sorting function generateCompareItemList
# "keyCount" represents times that "value" occurs in keywords dictionary
# "textCount" represents times that "value" occurs in text dictionary
class CompareItem(object):
    def __init__(self, value, keyCount, textCount):
        self.value = value
        self.keyCount = keyCount
        self.textCount = textCount


class BrightEdgeSpider(scrapy.Spider):
    name = "BrightEdge"

    # Get url arguments through terminal
    def __init__(self, url=""):
        try:
            self.start_urls = ["%s" % url]
        except ValueError:
            print "Invalid URL"


    def parse(self,response): 
    	pageItem = PageItem()
    	pageItem['html'] = response.body

        # Get plain text of this webpage by removing comment, script, style and head tags, as well as empty lines
    	root = lxml.html.fromstring(response.body)
        lxml.etree.strip_elements(root, lxml.etree.Comment, "script", "style", "head")
        pageItem['text'] = lxml.html.tostring(root, method="text", encoding=unicode)
        pageItem['text'] = cleanText(pageItem['text'])
        # Get useful trunks you want through NLTK for the plain body text
        text_outputList = preprocess(pageItem['text'])
        # Group trunks and compute counts for each trunk
        text_dict = generateDict(text_outputList)
        

        # Get titles from head and meta tags
        list1= response.xpath('//head/meta[contains(@name, "title")]/@content').extract()  
        list2 = response.xpath('//head/title/text()').extract()
        pageItem['keywords'] = list1 + list2
        # Get keywords from meta tags
        pageItem['keywords'] += response.xpath('//head/meta[contains(@name, "keywords")]/@content').extract()
        # Get text from h1 tags
        pageItem['keywords'] += response.xpath('//body/h1/text()').extract()
        # Remove empty lines, strip whitespaces and tabs from the beginning and the end of the string in the list
        pageItem['keywords'] = cleanList(pageItem['keywords'])
        # Get useful trunks you want through NLTK for all the collected keywords 
        key_outputList = []
        for item in pageItem['keywords']:
            outputList = preprocess(item)
            key_outputList += outputList
        # Group trunks and compute counts for each trunk
        key_dict = generateDict(key_outputList)
        

        # Sort all the keywords in key_dict by comparing counts in key_dict and text_dict
        result_list = generateCompareItemList(key_dict, text_dict)
        # Get the top 6 keywords
        top6list = getTop6(result_list)


        # Print result
        printResult(top6list)

        pageItem['text_dict'] = text_dict
        pageItem['key_dict'] = key_dict
        pageItem['result_list'] = result_list
        pageItem['top6list'] = top6list

        

