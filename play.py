from main import *
from setup import *
from DB import *
from analyseText import *


# # TODO Create 90% list for a given passage/work (This currently seems to work, needs to be incorporated)
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
# TODO testing minimal code- no adding of sentences
vocab = "dcc"
with open(f"data/wordlists/{vocab} list.txt", 'rb') as file:
	vocabList = list([x.strip().decode() for x in file.readlines()])
min_words = 20
max_words = 500
target = 70

author = "caesar"
titleFolders = os.listdir(f"./docs/{author}/")
T = random.randint(0, len(titleFolders)-1)
title = titleFolders[T]

docObj = load_from_pickles(author, title)

print("Getting random passage from text.")
sentences = docObj['sentences']
covPC = []
found = False
count = 0
while not found:
	count += 1
	if count >= len(sentences):
		print(f"Tried {count} random start points.")
		break
	start = random.randint(0, len(sentences) - 3)
	# start at random sentence
	passage_words = [w for w in docObj["words"] if start <= w.index_sentence <= start+2]
	wordcount = sum([1 for w in passage_words if w.upos != "PUNCT"])

	coverage = check_coverage(passage_words, vocabList)[0]
	covPC.append(coverage)
	# TODO add start index and don't try the same one again
	# print(f'{start}. {wordcount} words, {coverage :.2f}%.')
	if coverage > target:
		if wordcount > min_words:
			print(f"Returning passage of {wordcount} words.")
			print(" ".join(w.string for w in passage_words))
			found = True

print(f'Highest coverage found: {max(x for x in covPC)}.')
print(f'Average coverage: {sum(x for x in covPC)/len(covPC)}')

# uncomment to test adding to the length
# for ind, s in enumerate(sentences[start+4:]):
	# 	# check coverage of passage + sentence
	# 	tempPassage = passage_words + s.words
	# 	coverage = check_coverage(tempPassage, vocabList)[0]
	# 	print(f'{ind}. {len(tempPassage)} words, {coverage :.2f}%.')
	# 	# if over target, add s to passage_words, continue to next s
	# 	if coverage > minCov:
	# 		if len(tempPassage) + len(sentences[ind + 1].words) > max:
	# 			if len(tempPassage) > min:
	# 				# return passage
	# 				passage_words = tempPassage
	# 				wordcount = sum([1 for w in passage_words if w.upos != "PUNCT"])
	# 				print(f"Returning passage of {wordcount} words.")
	# 				print(" ".join(w.string for w in passage_words))
	# 				found = True
	# 				break
	# 			else:
	# 				# 	choose new random start point
	# 				break
	# 		prevCov = True
	# 		passage_words = tempPassage
	# 		wordcount = sum([1 for w in passage_words if w.upos != "PUNCT"])
	# 		print(" ".join(w.string for w in passage_words))
	# 	else:
	# 		if prevCov == True:
	# 			if wordcount > min:
	# 				print(f"Returning passage of {wordcount} words.")
	# 				print(" ".join(w.string for w in passage_words))
	# 				found = True
	# 				break
	# 		else:
	# 			# 	choose new random start point
	# 			break

print('finished')
