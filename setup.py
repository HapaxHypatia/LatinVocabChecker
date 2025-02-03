import multiprocessing
import os
from multiprocessing import Process
from cltk import NLP
from cltk.alphabet.lat import remove_macrons, JVReplacer
import mysql.connector as SQL
from openpyxl.reader.excel import load_workbook
import time
from semantic_text_splitter import TextSplitter
import pickle

# TODO create pickle files for all common senior texts
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
		return False
	if len(results) > 1:
    res = list(filter(lambda x: x[1] ==author, results))    
		text = res[0]
		author = res[1]
	else:
		text = results[0][0]
		author = results[0][1]
	print("Text: {} by {} successfully collected".format(title, author))
	return text, author


def splitText(text, num):
	splitter = TextSplitter(len(text) // num - 1)
	chunks = splitter.chunks(text)
	return chunks


def analyse(text, return_list=None):
	cltk = NLP(language="lat", suppress_banner=True)
	print("Beginning analysis. Please wait.")
	doc = cltk.analyze(text)
	print("Finished analysing")
	if return_list:
		return_list.append(doc)
	else:
		return doc


def store_data(title, author, nlp_doc):
	print("Storing data for {} by {}".format(title, author))
	if not os.path.isdir(f'docs/{author}'):
		os.mkdir(f'docs/{author}')
	with open(f'docs/{author}/{title}.pickle', 'wb') as handle:
		pickle.dump(nlp_doc, handle, protocol=pickle.HIGHEST_PROTOCOL)
		print("{} by {} successfully saved to {}.".format(title, author, handle))


def normalize_text(text):
	replacer = JVReplacer()
	text = remove_macrons(text)
	text = replacer.replace(text)
	replace_strings = ["- ", "-", "†"]
	for r in replace_strings:
		text = text.replace(r, "")
	# TODO still not catching all hyphenated words
	return text.lower()


def ignore(wordObject):
	'''
	Ignore words which are punctuation, empty strings, proper nouns, or (English) numbers
	:param wordObject:
	:return:
	'''
	if wordObject.upos == "PUNCT" or wordObject.upos == "X" or wordObject.upos == "PROPN":
		return True
	if wordObject.string == "":
		return True
	for char in wordObject.string:
		if char in "0123456789":
			return True
	return False


def deduplicate(items):
	seen = set()
	for item in items:
		if item.lemma not in seen:
			seen.add(item.lemma)
			yield item


def set_wordlist(name, listSource):
	"""

	:param listSource: either a filepath to a spreadsheet
	 					or a list object
	Latin terms must be in first column of spreadsheet
	:return: normalised version of list
	"""
	if os.path.exists(listSource):
		wb = load_workbook(listSource)
		ws = wb.active
		raw_list = [ws.cell(row=i, column=1).value for i in range(2, ws.max_row)]
		result = [normalize_text(i) for i in raw_list]
	elif type(listSource) == list:
		result = [normalize_text(i) for i in listSource]
	filename = f'data/wordlists/{name} list.txt'
	with open(filename, "a") as f:
		for item in result:
			f.write(item)
		f.close()
	return result


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
  titles = [
    "aeneis",
    "de bello gallico",
    "metamorphoses",
    "ab urbe condita",
    "pro caelio",
    "in catilinam",
    "in verrem",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
  ]

  for title in titles:
		text, author = getText(title)

	# Split text if long then analyse each chunk
	# Store analysed chunks in shared variable
	length = len(text.split())
	num = length//1500
	if num > 2:
		chunks = splitText(text, num)
		start_time = time.time()
		manager = multiprocessing.Manager()
		docs = manager.list()
		processes = [Process(target=analyse, args=(ch, docs)) for ch in chunks]
		for process in processes:
			process.start()
		for process in processes:
			process.join()
		print("Analysis took {} minutes.".format(round((time.time() - start_time) / 60), 2))
	else:
		start_time = time.time()
		analyse(text)
		print("Analysis took {} minutes.".format(round((time.time() - start_time) / 60), 2))

	# pickle & store
	# TODO save in database
	for i in range(len(docs)):
		store_data(title + str(i), author, docs[i])
		# TODO didn't store pickle files, but no error

  # set vocab lists
  vocabLists = [
    ("dcc", "data/Latin Core Vocab.xlsx"),
    ("clc", "data/CLC Vocab Pool.xlsx"),
    ("llpsi", ""),
    ("ecrom", ""),
    ("olc", ""),
    ("sub", ""),
  ]
  
  for v in vocabLists:
    set_wordlist(v[0], v[1])
