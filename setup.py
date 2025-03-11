import multiprocessing
import os
from multiprocessing import Process
import mysql.connector as SQL
from openpyxl.reader.excel import load_workbook
import time
from semantic_text_splitter import TextSplitter
import pickle
import re
from unidecode import unidecode
from cltk.data.fetch import FetchCorpus
from cltk.tokenizers.lat.lat import LatinWordTokenizer
from cltk import NLP


def getCorpora():
	corpus_downloader = FetchCorpus(language="lat")
	corpora = corpus_downloader.list_corpora
	for c in corpora:
		try:
			corpus_downloader.import_corpus(c)
			print(f"{c} successfully downloaded.")
		except Exception as e:
			print(c)
			print(e)
			continue


def getText(title, author):
	"""
	Get full text from DB
	:param string title: Title of work
	:return: string of text, string of author
	"""
	title = title.lower()
	textQuery = "SELECT textString, authorName FROM texts WHERE LOWER(title) = %s"
	vals = (title,)
	mycursor.execute(textQuery, vals)
	results = mycursor.fetchall()
	if len(results) < 1:
		print("No text by that name found in the database.")
		print(author)
		print(title)
		return False
	if len(results) > 1:
		res = list(filter(lambda x: x[1].lower() == author.lower(), results))
		text = res[0][0]
		author = res[0][1]
	else:
		text = results[0][0]
		author = results[0][1]
	print("\nText: {} by {} successfully collected".format(title, author))
	text = normalize_text(text)
	return text, author


def splitText(text, num):
	print(f"Splitting Text into {num} parts")
	splitter = TextSplitter(len(text) // num - 1)
	chunks = splitter.chunks(text)
	print(f"Returning {len(chunks)} chunks.")
	return chunks


def analyseLarge(text, return_list):
	cltk = NLP(language="lat", suppress_banner=True)
	print("Beginning analysis. Please wait.")
	doc = cltk.analyze(text)
	print("Finished analysing")
	return_list.append(doc)


def analyseSmall(text):
	cltk = NLP(language="lat", suppress_banner=True)
	print("Beginning analysis. Please wait.")
	doc = cltk.analyze(text)
	print("Finished analysing")
	return doc


def store_data(title, author, nlp_doc):
	if not os.path.isdir(f'docs/{author}'):
		os.mkdir(f'docs/{author}')
	with open(f'docs/{author}/{title}.pickle', 'wb') as handle:
		pickle.dump(nlp_doc, handle, protocol=pickle.HIGHEST_PROTOCOL)
		print("{} by {} successfully saved".format(title, author))


def normalize_text(text):
	"""
	Removes macrons
	Replaces Vs and Js
	Removes punctuation in the middle of words
	:param text: string of a passage
	:return: string
	"""
	if type(text) != str:
		text = str(text)
	text = text.lower()

	# replace macrons
	macrons = {
		'ā': 'a',
		'ē': 'e',
		'ō': 'o',
		'ī': 'I',
		'ū': 'u',
		'ȳ': 'y'
	}
	for k, v in macrons.items():
		text.replace(k, v)

	# replace Js and Vs
	jv = {
		'ja': 'ia',
		'je': 'ie',
		'ji': 'ii',
		'jo': 'io',
		'ju': 'iu',
		'va': 'ua',
		've': 'ue',
		'vi': 'ui',
		'vo': 'uo',
		'vu': 'uu',
	}
	for k, v in jv.items():
		text.replace(k, v)

	# join words that split over line break
	text = text.replace("-  ", "")
	text = text.replace("- ", "")

	# TODO move numbers when they occur inside words like this: multi4.1 tudo

	# # Replace numbers
	# res = ""
	# word_tokenizer = LatinWordTokenizer()
	# tokens = word_tokenizer.tokenize(text)
	# for t in tokens:
	# 	for num in '0123456789':
	# 		if num in t:
	# # 			move number to front of word
	#
	#
	#
	# print("Returning normalised text.")
	return text

def set_wordlist(name, listSource):
	"""
	:param name: string.
	:param listSource: either a filepath to a spreadsheet	 					or a list object
	Latin terms must be in first column of spreadsheet
	:return: normalised version of list
	"""
	if os.path.exists(listSource):
		wb = load_workbook(listSource)
		ws = wb.active
		raw_list = list([ws.cell(row=i, column=1).value for i in range(2, ws.max_row)])
		result = [normalize_text(i) for i in raw_list]
	elif type(listSource) == list:
		result = [normalize_text(i) for i in listSource]
	filename = f'data/wordlists/{name} list.txt'
	with open(filename, "a", encoding="utf-8") as f:
		for item in result:
			if not item:
				continue
			if len(item.split()) > 1:
				item = unidecode(item.split()[0])
			else:
				item = unidecode(item)
			f.write(item)
			f.write("\n")
		f.close()
	return result


def pickleExists(title, author):
	if os.path.isdir(f"docs/{author}"):
		for filename in os.listdir(f"docs/{author}"):
			if re.search(rf"{title.lower()}\d.pickle", filename):
				return True
	else:
		return False


def getVocab(name):
	with open(f"data/wordlists/{name} list.txt", 'r', encoding='utf-8') as f:
		vocab = [x.strip() for x in f.readlines()]
		return vocab


if __name__ == "__main__":
	print("Starting...\n")

	# getCorpora()


	# connect to database
	mydb = SQL.connect(
		host="localhost",
		user="root",
		password="admin",
		database="corpus"
	)
	mycursor = mydb.cursor()
	print("Connected to database.\n")

	# set vocab lists
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


	# get senior texts
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
		("virgilius", "aeneis")
	]

	for title in works:
		text, author = getText(title[1], title[0])
		#
		if pickleExists(title[1], author):
			print("Text analysis already stored.")
			continue

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

		# pickle & store
		# TODO save in database
		for i in range(len(docs)):
			store_data(title[1] + str(i), author, docs[i])

	# for k, v in vocabLists.items():
	# 	set_wordlist(v[0], v[1])

