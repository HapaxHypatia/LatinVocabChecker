import multiprocessing
import os
from multiprocessing import Process
from cltk import NLP
import mysql.connector as SQL
from openpyxl.reader.excel import load_workbook
import time
from semantic_text_splitter import TextSplitter
import pickle
import re
from unidecode import unidecode


# TODO create normalised lists of all common latin textbooks


def getText(title, author):
	'''
	Get full text from DB
	:param string title: Title of work
	:return: string of text, string of author
	'''
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
	return text, author


def splitText(text, num):
	print(f"Splitting Text into {num} parts")
	splitter = TextSplitter(len(text) // num - 1)
	chunks = splitter.chunks(text)
	return chunks


def analyseLarge(text, return_list):
	cleanText = normalize_text(text)
	cltk = NLP(language="lat", suppress_banner=True)
	print("Beginning analysis. Please wait.")
	doc = cltk.analyze(text)
	print("Finished analysing")
	return_list.append(doc)


def analyseSmall(text):
	cleanText = normalize_text(text)
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
	if type(text) != str:
		text = str(text)
	else:
		text = text.lower()
		macrons = {
			'ā': 'a',
			'ē': 'e',
			'ō': 'o',
			'ī': 'I',
			'ū': 'u',
			'ȳ': 'y'
		}

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
		for k, v in macrons.items():
			text.replace(k, v)
		for k, v in jv.items():
			text.replace(k, v)
		punctuation = ",;:'\"()[]_-<>?†"
		# TODO need to remove full stops etc only if inside a word
		for p in punctuation:
			text = text.replace(p, "")
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
			if re.search(rf"{title}\d.pickle", filename):
				return True
	else:
		return False


def getVocab(name):
	with open(f"data/wordlists/{name} list.txt", 'r', encoding='utf-8') as f:
		vocab = [x.strip() for x in f.readlines()]
		return vocab


if __name__ == "__main__":
	print("Starting...\n")

	# connect to database
	mydb = SQL.connect(
		host="localhost",
		user="root",
		password="admin",
		database="corpus"
	)
	mycursor = mydb.cursor()
	print("Connected to database.\n")

	# get senior texts
	works = [
		("Cicero", "de legibus"),
		("Cicero", "Pro Archia"),
		("Cicero", "Pro Caelio"),
		("apuleius", "metamorphoses"),
		("gellius", "noctes atticae"),
		("Caesar", "de bello gallico"),
		("Catullus", "carmina"),
		("Cicero", "de officiis"),
		("Cicero", "de legibus"),
		("Cicero", "Pro Q. Roscio Comoedo"),
		("Cicero", "Pro Lege Manilia"),
		("Cicero", "Pro Rabirio Perduellionis Reo"),
		("Cicero", "Pro Murena"),
		("Cicero", "Pro Sulla"),
		("Cicero", "Pro Milone"),
		("Cicero", "in verrem"),
		("Cicero", "in catilinam"),
		("iuvenalis", "saturae"),
		("livius", "ab urbe condita"),
		("lucretius", "de rerum natura"),
		("ovidius", "metamorphoses"),
		("ovidius", "amores"),
		("ovidius", "remedia amoris"),
		("ovidius", "Epistulae (vel Heroides)"),
		("plinius", "epistulae"),
		("tacitus", "annales"),
		("tibullus", "elegiae"),
		("virgilius", "aeneis"),
		("virgilius", "georgica"),
		("Cicero", 'Pro S. Roscio Amerino')

	]

	# TODO run this setup again ensuring normalisation of text before analysis
	# for title in works:
	# 	text, author = getText(title[1], title[0])
	#
	# 	if pickleExists(title[1], author):
	# 		print("Text analysis already stored.")
	# 		continue
	#
	# 	# Split text if long then analyse each chunk
	# 	# Store analysed chunks in shared variable
	# 	length = len(text.split())
	# 	print("Text length: {}".format(length))
	# 	num = length//2000
	# 	manager = multiprocessing.Manager()
	# 	docs = manager.list()
	# 	if num > 1:
	# 		chunks = splitText(text, min(10, num))
	# 		start_time = time.time()
	# 		processes = [Process(target=analyseLarge, args=(ch, docs)) for ch in chunks]
	# 		for process in processes:
	# 			process.start()
	# 		for process in processes:
	# 			process.join()
	# 		print("Analysis took {} minutes.".format(round((time.time() - start_time) / 60), 2))
	# 	else:
	# 		start_time = time.time()
	# 		docs.append(analyseSmall(text))
	# 		print("Analysis took {} minutes.".format(round((time.time() - start_time) / 60), 2))
	#
	# 	# pickle & store
	# 	# TODO save in database
	# 	for i in range(len(docs)):
	# 		store_data(title[1] + str(i), author, docs[i])

	# set vocab lists
	vocabLists = [
		("dcc", "data/Latin Core Vocab.xlsx"),
		("clc", "data/CLC Vocab Pool.xlsx"),  # Missing some Bk5 vocab
		("llpsi", "data/LLPSI vocab.xlsx"),
		("olc", "data/Oxford Book 1 Vocab.xlsx"),  # Only to Ch.22
		# ("ecrom", ""),
		# ("sub", ""),
	]

	for v in vocabLists:
		set_wordlist(v[0], v[1])
