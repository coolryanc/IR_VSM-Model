# -*- coding: UTF-8 -*-  

import xml.etree.ElementTree as ET
import sys
import time
import mmap
import json
import string


def readVocab(modelDir):
	parseVocabList = []
	print "\nParse vocab.all now."
	with open(modelDir + "/vocab.all") as readFile:
		keyWord = readFile.read().splitlines()
		for wordCount, word in enumerate(keyWord):
			print "\rparse vocab.all: "+ str(wordCount+1) + " vocab",
			sys.stdout.flush()
			parseVocabList.append(word)
	print "\n"
	return parseVocabList

def readFileList(modelDir):
	parseFileList = []
	print "\nParse file-list now."
	with open(modelDir + "/file-list") as readFile:
		DocPath = readFile.read().splitlines()
		for pathCount, path in enumerate(DocPath):
			print "\rparse file-list: "+ str(pathCount+1) + " Doc",
			sys.stdout.flush()
			docInfo = {} # dictionary to save date
			tree = ET.parse(path)
			root = tree.getroot()
			docInfo['id'] = root.find('./doc/id').text.lower()
			docInfo['date'] = root.find('./doc/date').text
			if not root.find('./doc/title').text:
				docInfo['title'] = ""
			else:
				docInfo['title'] = root.find('./doc/title').text.strip()
			textInDoc = ""
			for p in root.iter('p'):
				textInDoc += p.text.strip()
			docInfo['content'] = textInDoc
			parseFileList.append(docInfo)
	print "\n"
	return parseFileList

def getAvgDocLength(parseFileList):
	avgDoc_len = 0
	for doc in parseFileList:
		avgDoc_len += len(doc['content'])
	print "avg:"+str(avgDoc_len/float(len(parseFileList)))
	return avgDoc_len/float(len(parseFileList))

# def readInvertedFile(modelDir): #TODO
# 	# id2 = -1, unigram
# 	invertedFileLineIndex = 0
# 	t1 = time.time()
# 	parseInvertedFileList = {}
# 	currentIndex = ""
# 	print "\nParse inverted-file now..."
# 	for chunk in read_in_chunks(modelDir + "/inverted-file"):
# 		chunkLineIndex = 0
# 		while chunkLineIndex < len(chunk):
# 			print "\rparse inverted-file: "+ str(invertedFileLineIndex),
# 			fields = chunk[chunkLineIndex].split(" ")
# 			if len(fields) == 3:
# 				if fields[1] == "-1":
# 					chunkLineIndex += int(fields[2])
# 					chunkLineIndex += 1
# 				elif fields[1] != "-1":
# 					currentIndex = fields[0]+","+fields[1]
# 					parseInvertedFileList[currentIndex] = {"numberOfFile":fields[2], "docs": []}
# 					# parseInvertedFileList[currentIndex] = {"numberOfFile":fields[2], "invertedFileLineIndex":invertedFileLineIndex}
# 					chunkLineIndex += 1
# 			elif len(fields) == 2:
# 				parseInvertedFileList[currentIndex]["docs"].append({"docID":fields[0], "countInDoc":fields[1]})
# 				chunkLineIndex += 1
# 			invertedFileLineIndex += 1

# 	ouputData = open("bigramData.txt","w")
# 	ouputData.write(json.dumps(parseInvertedFileList))
# 	t2 = time.time()
# 	print "\n"
# 	print t2-t1
# 	return parseInvertedFileList

def saveToPureInvertedFile(modelDir):
	# id2 = -1, unigram
	invertedFileLineIndex = 0
	t1 = time.time()
	parseInvertedFileList = ""
	currentIndex = ""
	print "\nParse inverted-file now..."
	for chunk in read_in_chunks(modelDir + "/inverted-file"):
		chunkLineIndex = 0
		while chunkLineIndex < len(chunk):
			print "\rparse inverted-file: "+ str(invertedFileLineIndex),
			fields = chunk[chunkLineIndex].split(" ")
			if len(fields) == 3:
				if fields[1] == "-1":
					chunkLineIndex += int(fields[2])
					chunkLineIndex += 1
				elif fields[1] != "-1":
					parseInvertedFileList += chunk[chunkLineIndex].strip()
					parseInvertedFileList += '\n'
					chunkLineIndex += 1
			elif len(fields) == 2:
				parseInvertedFileList += chunk[chunkLineIndex].strip()
				parseInvertedFileList += '\n'
				chunkLineIndex += 1
			invertedFileLineIndex += 1

	ouputData = open("PurebigramData.txt","w")
	ouputData.write(parseInvertedFileList)
	t2 = time.time()
	print "\n"
	print t2-t1

def parsePureInvertedFile():
	# id2 = -1, unigram
	invertedFileLineIndex = 0
	t1 = time.time()
	parseInvertedFileList = {}
	currentIndex = ""
	print "\nParse inverted-file now..."
	for chunk in read_in_chunks("./PurebigramData.txt"):
		for lineindex, line in enumerate(chunk):
			invertedFileLineIndex += 1
			print "\rparse inverted-file: "+ str(invertedFileLineIndex),
			fields = line.split(" ")
			if len(fields) == 3:
				currentIndex = fields[0]+","+fields[1]
				parseInvertedFileList[currentIndex] = {"numberOfFile":fields[2], "docs": []}
			else:
				parseInvertedFileList[currentIndex]["docs"].append({"docID":fields[0], "countInDoc":fields[1]})
		
	t2 = time.time()
	print "\n"
	print t2-t1
	return parseInvertedFileList

def read_in_chunks(filePath, chunk_size=1024*1024):
	file_object = open(filePath,'r')
	while True:
		chunk_data = file_object.readlines(chunk_size)
		if not chunk_data:
			break
		yield chunk_data

# def readJsonInvertedFile():
# 	print "Read BigramData..."
# 	readfile = open("./bigramData.txt",'r')
# 	jsonData = json.loads(readfile.read())
# 	return jsonData