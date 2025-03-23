from main import *
from setup import *
from DB import *
from analyseText import *


# # TODO Create 90% list for a given passage/work
#
# # Create frequency list
# # Add words to vocab until 90% coverage is reached.
#
# doc = load_from_pickles('Caesar', 'de bello gallico')
# with open(f"data/wordlists/dcc list.txt", 'rb') as file:
# 	vocab_list = list([x.strip().decode() for x in file.readlines()])
#
# passage = get_random_passage(doc, 130)
# tempDoc = analyseSmall(passage)
# print(passage)
#
# passageDoc = create_docObj(tempDoc)
# wordCoverage, lemmaCoverage, unknown = check_coverage(passageDoc["clean_words"], vocab_list)
# print(wordCoverage)
#
# freq = create_freq_list(passageDoc)
#
# num = 10
# voc_words = list(freq.keys())
# voc = voc_words[:num]
# coverage = wordCoverage
# while len(voc) < len(voc_words):
# 	num += 5
# 	voc = voc_words[:num]
# 	wordCoverage, lemmaCoverage, unknown = check_coverage(passageDoc["clean_words"], voc)
# 	print(str(num) + " words.")
# 	print(wordCoverage)
# 	if wordCoverage >= 90:
# 		print("90% coverage reached.")
# 		print(voc)
# 		break
# 	coverage = wordCoverage
import random

vocab = "dcc"
with open(f"data/wordlists/{vocab} list.txt", 'rb') as file:
	vocabList = list([x.strip().decode() for x in file.readlines()])
min = 20
max = 500
minCov = 80

author = "caesar"
titleFolders = os.listdir(f"./docs/{author}/")
T = random.randint(0, len(titleFolders)-1)
title = titleFolders[T]

docObj = load_from_pickles(author, title)

print("Getting random passage from text.")
sentences = docObj['sentences']

found = False

while not found:
	start = random.randint(0, len(sentences) - 2)
	# start at random sentence
	passage_words = []
	wordcount = sum([1 for w in passage_words if w.upos != "PUNCT"])

	for ind, s in enumerate(sentences[start:]):
		# check coverage of passage + sentence
		tempPassage = passage_words + s.words
		coverage = check_coverage(tempPassage, vocabList)[0]
		# if over target, add s to passage_words, continue to next s
		if coverage > minCov:
			if len(tempPassage) + len(sentences[ind + 1].words) > max:
				if len(tempPassage) > min:
					# return passage
					print(f"Returning passage of {wordcount} words.")
					print(" ".join(w.string for w in passage_words))
					found = True
				else:
					# 	choose new random start point
					break
			else:
				continue
				# Otherwise continue to next sentence
			passage_words += s.words
			wordcount = sum([1 for w in passage_words if w.upos != "PUNCT"])
			print(f'{ind}. {wordcount} words, {coverage :2f}.')
		else:
			if wordcount > min:
				print(f"Returning passage of {wordcount} words.")
				print(" ".join(w.string for w in passage_words))
				found = True
			else:
				# 	choose new random start point
				break

