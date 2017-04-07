# -*- coding: UTF-8 -*-  

import xml.etree.ElementTree as ET
from operator import itemgetter
import numpy as np
import math
import sys
import parseXML
import json
import time
import argparse

def rocchioFeedBack(queryVector, rankingList):

	lengthOfList = len(rankingList)
	relatedNumber = int(lengthOfList * 0.15)
	scoreDict = {}
	useToSum = rankingList
	# Sort large to small
	for docId in rankingList:
		scoreDict[docId] = sum(useToSum[docId])
	sortedDict = list(sorted(scoreDict.items(), key=itemgetter(1), reverse=True))
	
	# related docs
	SumOfRelatedVec = np.array([0] * len(queryVector))
	for docId in sortedDict[:relatedNumber]: #docId ('id':value)
		SumOfRelatedVec =  SumOfRelatedVec + np.array(rankingList[docId[0]])

	# not related docs
	SumOfNotRelatedVec = np.array([0] * len(queryVector))
	for docId in sortedDict[-relatedNumber:]:
		SumOfNotRelatedVec =  SumOfNotRelatedVec + np.array(rankingList[docId[0]])

	# Three parameters
	a = 0.9
	b = 0.2
	c = 0.1

	Related = np.array(SumOfRelatedVec)
	NotRelated = np.array(SumOfNotRelatedVec)
	original = np.array(queryVector)

	newVec = (a * original) + (b * Related/relatedNumber) - (c * NotRelated/relatedNumber)
	return newVec


def searchBigram(queryTerms, queryID, isFeedBack):
	rankingList = {}
	queryVector = []
	queryTermsIndex = 0
	for key, elem in queryTerms.items():
		if key[0].encode('utf-8') in vocabList:
			if key[1].encode('utf-8') in vocabList:
				invertedIndex = str(vocabList.index(key[0].encode('utf-8')))+","+str(vocabList.index(key[1].encode('utf-8')))
				if invertedIndex in invertedFileDict: #Bigram in inverted-file.
					# Okapi/BM25 TF and Pivoted Document Lenhth Normalization
					BM25_K = 2.0
					SLOPE = 0.75
					
					queryVector.append(elem) # queryVector
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
						rankingList[docID][queryTermsIndex] = float(BIGRAMTF * IDF * elem) 
					queryTermsIndex += 1

	if isFeedBack:
		queryVector = rocchioFeedBack(queryVector, rankingList)

	bestResultList = calculateScoresAndSort(queryVector, rankingList)
	
	writeText = queryID + ","
	for docid in bestResultList:
		writeText += parseFileList[int(docid)]['id']
		writeText += ' '
	writeText += '\n'
	return writeText

def calculateScoresAndSort(queryvector, rankinglist):
	scoreDict = {}
	for docId in rankinglist:
		scoreDict[docId] = sum([x * y for x, y in zip(queryvector, rankinglist[docId])])

	sortedlistOfDoc = list(sorted(scoreDict.items(), key=itemgetter(1), reverse=True))
	returnList = []
	for index in range(len(sortedlistOfDoc)):
		returnList.append(sortedlistOfDoc[index][0]);
		if index == 99:
			break
	return returnList

def queryFile(path, isFeedBack, outPutFileName):
	writeText = "query_id,retrieved_docs\n"
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
			writeText += searchBigram(queryTerms, queryID, isFeedBack)
	ouputData = open(outPutFileName,"w")
	ouputData.write(writeText)

def main():
	global parseFileList, vocabList, invertedFileDict, avgDoc_len
	parser = argparse.ArgumentParser(description="Welcome!")
	parser.add_argument("-r", help="isFeedback", action="store_true", default=False)
	parser.add_argument("-i", help="Query File", type=str)
	parser.add_argument("-o", help="Rank List", type=str)
	parser.add_argument("-m", help="Model Dir", type=str)
	args = parser.parse_args()

	parseFileList = parseXML.readFileList(args.m)
	avgDoc_len = parseXML.getAvgDocLength(parseFileList)
	vocabList = parseXML.readVocab(args.m)
	parseXML.saveToPureInvertedFile(args.m)
	invertedFileDict = parseXML.parsePureInvertedFile()
	queryFile(args.i, args.r, args.o)
	
if __name__ == '__main__':
	main()