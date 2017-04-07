# -*- coding: UTF-8 -*-  

import xml.etree.ElementTree as ET
import numpy as numpy
import math
import sys
import parseXML
import json

def searchBigram(queryTerms):
	rankingList = {}
	# queryVector = []
	for key, elem in queryTerms.items():
		if key[0].encode('utf-8') in vocabList:
			if key[1].encode('utf-8') in vocabList:
				invertedIndex = str(vocabList.index(key[0].encode('utf-8')))+","+str(vocabList.index(key[1].encode('utf-8')))
				if invertedIndex in invertedFileDict: #Bigram in inverted-file.
					# Okapi/BM25 TF and Pivoted Document Lenhth Normalization
					BM25_K = 2.0
					SLOPE = 0.75
					
					# queryVector.append(elem) # queryVector
					bigramInDoc = invertedFileDict[invertedIndex]
					numberOfFile = int(bigramInDoc["numberOfFile"])
					docs = bigramInDoc["docs"]

					# Bigram's weight
					IDF = math.log((len(parseFileList)+1)/numberOfFile) 

					for doc in docs: # get document vector, then caculate IDF
						docID = int(doc['docID'])
						countInDoc = int(doc['countInDoc'])
						BIGRAMTF = ( BM25_K + 1 ) * countInDoc / ( countInDoc + BM25_K * ( 1 - SLOPE + SLOPE * len(docs) / avgDoc_len) )
						if docID not in rankingList:
							rankingList[docID] = [0] * len(queryTerms)
						rankingList[docID][key] = float(TF * IDF * elem) 
	print rankingList 
	return rankingList
	# listDocCount = 0
	# listOfDoc = list(sorted(scoreDict.items(), key=itemgetter(1)))
	# returnList = []
	# for index in xrange(len(listOfDoc)-1, 0, -1):
	# 	listDocCount+=1
	# 	returnList.append(listOfDoc[index][0]);
	# 	if listDocCount == 100:
	# 		break
	# return returnList

def queryFile(path):
	with open(path) as readFile:
		tree = ET.parse(path)
		root = tree.getroot()
		for topic in root.iter('topic'):
			queryID = topic.find("./number").text[-3:].strip()
			mainTitle = topic.find("./title").text.strip()
			mainConcepts = topic.find("./concepts").text.strip()

			puncs = [u'，', u'?', u'@', u'!', u'$', u'%', u'『', u'』', u'「', u'」', u'＼', u'｜', u'？', u' ', u'*', u'(', u')', u'~', u'.', u'[', u']', 'u\n',u'1',u'2',u'3',u'4',u'5',u'6',u'7',u'8',u'9',u'0', u'。']
			for punc in puncs:
				mainConcepts = mainConcepts.replace(punc,'')

			### Bigram
			queryTerms = {}
			for seg in mainConcepts.split(u'、'):
				if len(seg) % 2 == 0:
					for x in xrange(0,len(seg),2):
						if seg[x] + seg[x+1] not in queryTerms:
							queryTerms[seg[x] + seg[x+1]] = 1
						elif seg[x] + seg[x+1] in queryTerms:
							queryTerms[seg[x] + seg[x+1]] += 1
				else:
					for x in xrange(0,len(seg)-1):
						if seg[x]+seg[x+1] not in queryTerms:
							queryTerms[seg[x] + seg[x+1]] = 1
						elif seg[x] + seg[x+1] in queryTerms:
							queryTerms[seg[x] + seg[x+1]] += 1
			searchBigram(queryTerms)

def main():
	global parseFileList, vocabList, invertedFileDict, avgDoc_len
	parseFileList = parseXML.readFileList("model")
	avgDoc_len = parseXML.getAvgDocLength(parseFileList)
	vocabList = parseXML.readVocab("model")
	# 
	# invertedFileDict = parseXML.readInvertedFile("model")
	# parseXML.saveToPureInvertedFile("model")
	invertedFileDict = parseXML.parsePureInvertedFile()
	queryFile("./queries/query-train.xml")
	
if __name__ == '__main__':
	main()