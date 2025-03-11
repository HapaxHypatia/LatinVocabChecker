from corporaScrape import *
from setup import *
from DB import *
from analyseText import *
from findText import *
from loggingSetup import *


# TODO organise files better- what is the purpose of each one, what are the entry points and what goes in main?
# TODO add stage selection for CLC
# TODO analyse the top words coming up that are still unknown on DCC and what words in DCC are not coming up. (Per author?)
# TODO how many words do you typically need before a word repeats in latin?
# TODO create normalised lists vocab for major textbooks
# TODO create frequency list for 90% coverage of common HS texts only, compare to textbook lists
#  DCC definitely gives the best coverage, compared to clc and llpsi, but still only 69%
# TODO Try to find the longest readable passage possible in a given text/author
# TODO add date and genre to database
# TODO texts are normalised when retrieved from database. If working with a user-entered text, need to add normalisation step

def load_from_file(filename):
	"""
	loads text from a textfile and normalises it
	:param filename: string of filepath
	:return: string of normalised text
	"""
	with open(filename, 'r', encoding='utf-8') as file:
		text = "".join(x.strip() for x in file.readlines())
	return normalize_text(text)


def load_from_pickles(author, title):
	"""
	loads analysed texts from pickle files
	:param author: string
	:param title: string
	:return: docObj (not a real nlp doc)
	"""
	docfiles = getPickles(author, title)
	docs = list([deserialize(pickle) for pickle in docfiles])
	return combine_docs(docs)


if __name__ == "__main__":
	'''
	Text input options:
	 - from textfile
	 - from stored pickles
	 - from database
	 - random from database
	'''

	author = input("Please enter author's name: ")
	id = DBgetAuthor(author)[0]
	texts = getTextList(id)
	if not texts:
		print("Could not find that author in our database. Check your spelling or try another author.")
	else:
		for ind, T in enumerate(texts):
			print(f"{str(ind)}. {T}")
		choice = input("Please select title from list: ")
		title = texts[int(choice)][0]

	if pickleExists(title, author):
		doc = load_from_pickles(author, title)
	else:
		text = getText(title, author)

		# Split text if long then analyse each chunk
		length = len(text.split())
		print("Text length: {}".format(length))

		num = length//2000
		manager = multiprocessing.Manager()
		docs = manager.list()

		if num > 1:
			chunks = splitText(text, min(10, num))
			start_time = time.time()
			# NOTE: multiprocessing must be done in __main__
			processes = [Process(target=analyseLarge, args=(ch, docs)) for ch in chunks]
			for process in processes:
				process.start()
			for process in processes:
				process.join()
			print("Analysis took {} minutes.".format(round((time.time() - start_time) / 60), 2))
		else:
			start_time = time.time()
			docs.append(analyseSmall(text))
			print("Analysis took {} minutes.".format(round((time.time() - start_time) / 60), 2))

		if len(docs) > 1:
			doc = combine_docs(docs)
		else:
			doc = create_docObj(docs[0])

	# get lists of text features
	lemmalist = doc["unique"]
	verbforms, cases, pos = set_lists(doc["words"])

	for ind, name in enumerate(vocabLists.keys()):
		print(f"{ind}. {name}")
	vocab = input("Select which list you would like to use: ")

	with open(f"data/wordlists/{vocab} list.txt", 'rb') as file:
		vocab_list = list([x.strip().decode() for x in file.readlines()])

	# print analysis

	# basic details
	print(f"\n{title} by {author}")
	print("\nTotals")
	print("Total words in text: {}".format(doc['word_count']))
	print("Total number of lemmata: {}".format(len(lemmalist)))

	#  readability
	wordCoverage, lemmaCoverage, unknown = check_coverage(doc["clean_words"], vocab_list)
	print("\nCoverage")
	print("Percentage of lemmata known: {:.2f}%".format(lemmaCoverage))
	print("Percentage of words known: {:.2f}%".format(wordCoverage))
	print("\n")

	# average sentence length
	average = avg_sentence_length(doc)
	print(f"Average sentence length: {average} words")
	# lexical density
	print(f"Lexical density (unique words : total words): {doc['density']:.1%}")

	print("Verb Forms")
	for k in verbforms.keys():
		print("Number of {} in text: {}".format(k, len(verbforms[k])))
	print("\n")

	print("Noun Cases")
	for k in cases.keys():
		print("Number of {} in text: {}".format(k, len(cases[k])))
	print("\n")

	print("Parts of Speech")
	for k in pos.keys():
		print("Number of {} in text: {}".format(k, len(pos[k])))


	# # Get 10 random readable passages from a given text
	# percentage = 80
	# passageLength = 50
	# vocab = "dcc"
	# number = 10
	#
	# file = f"results/{number}x{passageLength} words at {percentage}%.txt"
	# vocab = getVocab('dcc')
	#
	# passages = []
	# while len(passages) < number:
	# 	work = get_random_work()
	# 	title, text, author = work
	# 	passage = get_random_passage(text, passageLength)
	# 	if not passage:
	# 		continue
	# 	else:
	# 		doc = analyseSmall(passage)
	# 		word_coverage, lemmaCoverage, unknown_words = check_coverage(doc.words, vocab)
	#
	# 		details = {
	# 			"author": author,
	# 			"text": text,
	# 			"passage": passage,
	# 			"Coverage": word_coverage,
	# 			"Unknown": unknown_words
	# 		}
	# 		if word_coverage >= percentage:
	# 			colour = '\033[32m'
	# 		else:
	# 			colour = '\033[31m'
	# 		print(colour)
	# 		logger.info(f"{author}, {title}: {word_coverage:.2f}%")
	# 		print("\x1b[0m")
	# 		if word_coverage > percentage:
	# 			passages.append(details)
	# 			with open(file, 'a') as f:
	# 				for k, v in details.items():
	# 					f.write(f"{k}: {v}\n")
	# 				f.write('\n')

	# def isReadable(passage, minPercentage, vocablist):
	# 	"""
	# 	:param passage: str. passage to be checked.
	# 	:param percentage: int. Vocab coverage needed.
	# 	:param vocablist: list. List of known vocab.
	# 	:return: bool
	# 	"""
	# 	print("Checking readability.")
	# 	doc = analyseSmall(passage)
	# 	words = [w for w in doc.words if not ignore(w)]
	# 	word_coverage, lemmaCoverage, unknown_words = check_coverage(words, vocablist)
	# 	if word_coverage >= minPercentage:
	# 		print(f"Found passage with {word_coverage:.2f}% coverage.")
	# 		return word_coverage, lemmaCoverage, unknown_words
	# 	else:
	# 		print(f"Passage did not meet minimum coverage. Coverage was {word_coverage:.2f}%.")
	# 		return False



	# RESULTS
	# Caesar has quite low lexical density
	# Virgil slightly high
	# Catullus very high


	# Sentence Splitting
	# from cltk.sentence.lat import LatinPunktSentenceTokenizer
	# splitter = LatinPunktSentenceTokenizer()
	# sentences = splitter.tokenize(text)

	# Nested list comprehension
	# [x for y in ylist for x in xlist (if x ....)]
