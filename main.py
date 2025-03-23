from corporaScrape import *
from setup import *
from DB import *
from analyseText import *
from loggingSetup import *


# TODO organise files better- what is the purpose of each one, what are the entry points and what goes in main?
# TODO add stage selection for CLC
# TODO analyse the top words coming up that are still unknown on DCC and what words in DCC are not coming up. (Per author?)
# TODO how many words do you typically need before a word repeats in latin?
# TODO create normalised lists vocab for major textbooks
# TODO create frequency list for 90% coverage of common HS texts only, compare to textbook lists
# TODO Try to find the longest readable passage possible in a given text/author
# TODO add date and genre to database
# TODO texts are normalised when retrieved from database. If working with a user-entered text, need to add normalisation step
# TODO lowercase for all author & title variables
# TODO standardise naming formats for functions & variables


vocabLists = [
	("dcc", "data/vocab/Latin Core Vocab.xlsx"),
	("clc", "data/vocab/cambridge_latin_course.xlsx"),  # Missing some Bk5 vocab
	("llpsi", "data/vocab/lingua_latina.xlsx"),
	("olc", "data/vocab/oxford_latin_course.xlsx"),  # Only to Ch.22
	("ecrom", "data/vocab/ecce_romani.xlsx"),
	("sub", "data/vocab/suburani.xlsx"),
	("wheel", "data/vocab/wheelock.xlsx"),
	("newmil", "data/vocab/latin_for_the_new_millennium.xlsx")
]

works = [
	("Cicero", "In Catilinam"),
	("Cicero", "In Pisonem"),
	("Cicero", "In Q. Caecilium"),
	("Cicero", "In Sallustium [sp.]"),
	("Cicero", "In Vatinium"),
	("Cicero", "In Verrem"),
	("Cicero", "Pro Archia"),
	("Cicero", "Pro Balbo"),
	("Cicero", "Pro Caecina"),
	("Cicero", "Pro Caelio"),
	("Cicero", "Pro Cluentio"),
	("Cicero", "Pro Flacco"),
	("Cicero", "Pro Fonteio"),
	("Cicero", "Pro Lege Manilia"),
	("Cicero", "Pro Ligario"),
	("Cicero", "Pro Marcello"),
	("Cicero", "Pro Milone"),
	("Cicero", "Pro Murena"),
	("Cicero", "Pro Plancio"),
	("Cicero", "Pro Q. Roscio Comoedo"),
	("Cicero", "Pro Quinctio"),
	("Cicero", "Pro Rabirio Perduellionis Reo"),
	("Cicero", "Pro Rabirio Postumo"),
	("Cicero", "Pro Rege Deiotaro"),
	("Cicero", "Pro S. Roscio Amerino"),
	("Cicero", "Pro Scauro"),
	("Cicero", "Pro Sestio"),
	("Cicero", "Pro Sulla"),
	("Cicero", "Pro Tullio"),
	("Caesar", "de bello gallico"),
	("Catullus", "carmina"),
	("livius", "ab urbe condita"),
	("ovidius", "metamorphoses"),
	("ovidius", "amores"),
	("ovidius", "remedia amoris"),
	("ovidius", "Epistulae (vel Heroides)"),
	("plinius", "epistulae"),
	("vergilius", "aeneis")
]


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
	# TODO URGENT: pickle files are not in order, so the text is jumbled
	return combine_docs(docs)

def get_random_work():
	work = False
	while not work:
		mydb = SQL.connect(
			host="localhost",
			user="root",
			password="admin",
			database="corpus"
		)
		mycursor = mydb.cursor()
		print("\nGetting random text from database.")
		id = random.randint(52, 884)
		textQuery = "SELECT title, textString, authorName FROM texts WHERE textID = %s"
		vals = (id,)
		mycursor.execute(textQuery, vals)
		work = mycursor.fetchall()
	title, text, author = work[0]
	print(f"Collected {title} by {author}")
	return title, text, author


def get_random_passage(docObj, passageLength):
	if len(docObj["clean_words"]) < passageLength:
		print("Work too short.")
		return False
	else:
		print("Getting random passage from text.")
		sentences = docObj['sentences']
		if len(sentences) < 2:
			print("Not enough sentences.")
			return False
		start = 0
		end = 0
		passage_words = [w for w in docObj["words"] if start < w.index_sentence < end]
		wordcount = sum([1 for w in passage_words if w.upos != "PUNCT"])
		while wordcount < passageLength:
			start = random.randint(0, len(sentences)-1)
			for s in sentences[start:]:
				if wordcount + len(s.words) < passageLength * 1.1:
					passage_words += [w for w in s.words]
					wordcount = sum([1 for w in passage_words if w.upos != "PUNCT"])
				else:
					break
		print(f"Returning passage of {wordcount} words.")
		return " ".join([w.string for w in passage_words])

def get_readable_passage(docObj, vocabList, min = 20, max = None, minCov = 90):
	print("Getting random passage from text.")
	if len(docObj["clean_words"]) < min:
		print("Work too short.")
		return False
	sentences = docObj['sentences']
	if len(sentences) < 2:
		print("Not enough sentences.")
		return False
	if max == None:
		max = len(docObj["clean_words"])

	start = random.randint(0, len(sentences)-2)
	end = start
	passage_words = []
	wordcount = sum([1 for w in passage_words if w.upos != "PUNCT"])
	while len(passage_words) < max:
		# start at random sentence
		for s, ind in enumerate(sentences[start:]):
			# check coverage of passage + sentence
			tempPassage = passage_words + s.words
			coverage = check_coverage(tempPassage, vocabList)[0]
			# if over target, add s to passage_words, continue to next s
			if coverage > minCov:
				if len(tempPassage) + len(sentences[ind + 1].words) > max:
					if len(tempPassage) > min:
						# return passage
						print(f"Returning passage of {wordcount} words.")
						return " ".join(w.string for w in passage_words)
					else:
						# 	choose new random start point
						break
				# Otherwise continue to next sentence
				passage_words += s.words
				wordcount = sum([1 for w in passage_words if w.upos != "PUNCT"])
			else:
				if wordcount > min:
					print(f"Returning passage of {wordcount} words.")
					return " ".join(w.string for w in passage_words)
				else:
					# 	choose new random start point
					break

def load_and_analyse():
	# Get author & text
	author = input("Please enter author's name: ")
	id = DBgetAuthor(author)[0]
	texts = getTextList(id)
	if not texts:
		print("Could not find that author in our database. Check your spelling or try another author.")
	else:
		for ind, T in enumerate(texts):
			print(f"{str(ind+1)}. {T}")
		choice = input("Please select title from list: ")
		title = texts[int(choice)-1][0]

	# get choice of vocab list
	for ind, name in enumerate(vocabLists):
		print(f"{ind+1}. {name}")
	choice = input("Select which list you would like to use: ")
	vocab = vocabLists[int(choice)-1][0]
	with open(f"data/wordlists/{vocab} list.txt", 'rb') as file:
		vocab_list = list([x.strip().decode() for x in file.readlines()])

	# Load & Analyse text
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

	# Forms
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


if __name__ == "__main__":
	'''
	Text input options:
	 - from textfile
	 - from stored pickles DONE
	 - from database DONE
	 - random from database
	'''
	"""
	Get readable passage from saved docs
	"""
	# Define vocab list
	# for ind, name in enumerate(vocabLists):
	# 	print(f"{ind + 1}. {name[0]}")
	# choice = input("Select which list you would like to use: ")
	# vocab = vocabLists[int(choice) - 1][0]
	vocab = "dcc"
	with open(f"data/wordlists/{vocab} list.txt", 'rb') as file:
		vocabList = list([x.strip().decode() for x in file.readlines()])

	# Optional settings: min and max word counts, preferred author/work/genre/date
	# min = int(input("Minimum Word Count: "))
	# max = int(input("Maximum Word Count: "))
	# minCov = int(input("Minimum Coverage: "))
	min = 20
	max = 500
	minCov = 80

	# # Get random author, work
	# authorFolders = os.listdir("./docs/")
	# A = random.randint(0, len(authorFolders)-1)
	# author = authorFolders[A]

	author = "caesar"
	titleFolders = os.listdir(f"./docs/{author}/")
	T = random.randint(0, len(titleFolders)-1)
	title = titleFolders[T]

	# Get random passage
	docObj = load_from_pickles(author, title)
	print(get_readable_passage(docObj, vocabList, 20, 500, 80))



	# RESULTS
	# Caesar has quite low lexical density
	# Virgil slightly high
	# Catullus very high
	#  DCC definitely gives the best coverage, compared to clc and llpsi, but still only 69%

	#There are no 2 consecutive sentences in DBG where dcc gives 80% coverage.


# Sentence Splitting
	# from cltk.sentence.lat import LatinPunktSentenceTokenizer
	# splitter = LatinPunktSentenceTokenizer()
	# sentences = splitter.tokenize(text)

	# Nested list comprehension
	# [x for y in ylist for x in xlist (if x ....)]
