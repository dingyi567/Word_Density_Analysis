#Word Density Analysis

##Implementation

Language: Python

Tools: Scrapy

External library: NLTK, lxml


I collected keywords from meta, title and h1 tags for each page. In case of most of them are sentences, the program trunks all the key sentences into key phrases and selects useful trunks by defined patterns using NLTK, and then group and compute counts for each selected key phrase.


For the plain body text of webpage, the program removes head, styles and scripts and all other html tags. And then the program also uses NLTK to select useful trunks, as well as grouping and computing counts for each selected key phrase.


For selecting final result, the program sorts key phrase in keywords by comparing the counts in keywords dictionary firstly, and counts in body text dictionary secondly. Finally, return the top 6 key phrases.


##Execution

You need to install Scrapy 1.0.5, lxml 3.5.0, nltk 3.2 and Python 2.7

###Commands:

```
scrapy crawl BrightEdge -a url="http://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster"

scrapy crawl BrightEdge -a url="http://blog.rei.com/camp/how-to-introduce-your-indoorsy-friend-to-the-outdoors/"

scrapy crawl BrightEdge -a url="http://www.cnn.com/2013/06/10/politics/edward-snowden-profile/"
```

##Results for the 3 URLs

1. http://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster
	
	['White', 'Compact Plastic Toaster', 'Conair Cuisinart CPT-122', 'Amazon.com', 'Kitchen', 'Dining']


2. http://blog.rei.com/camp/how-to-introduce-your-indoorsy-friend-to-the-outdorrs/
 	
 	['Indoorsy Friend', 'Outdoors', 'REI Blog']


3. http://www.cnn.com/2013/06/10/politics/edward-snowden-profile/
	
	['NSA', 'privacy', 'leaks', 'Man', 'CNNPolitics.com', 'liberty']



