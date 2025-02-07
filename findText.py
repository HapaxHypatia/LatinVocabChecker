import random
from analyseText import *
from setup import *
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt_tab')

def get_random_passage(passageLength):
	id = random.randint(52, 884)
	textQuery = "SELECT title, textString, authorName, textLength FROM texts WHERE textID = %s"
	vals = (id,)
	mycursor.execute(textQuery, vals)
	results = mycursor.fetchall()
	if not results:
		print("database fetch failed")
		return False
	title, text, author, length = results[0]
	if length > passageLength:
		text = normalize_text(text)
		sentences = sent_tokenize(text)
		passage = ""
		start = random.randint(1, len(sentences))
		for s in sentences[start:]:
			wordcount = len([w for w in passage.split() if w != "."])
			if wordcount + len(s.split()) < passageLength*1.1:
				passage = passage + s + " "
			else:
				break
		if len(passage.split()) < passageLength:
			return False
		return author, title, passage.split(), passage
	else:
		return False


wb = load_workbook("data/Latin Core Vocab.xlsx")
ws = wb.active
with open("data/wordlists/dcc list.txt", 'rb') as file:
	dcc_list = list([x.strip() for x in file.readlines()])
with open("data/wordlists/clc list.txt", 'rb') as file:
	clc_list = list([x.strip() for x in file.readlines()])

mydb = SQL.connect(
	host="localhost",
	user="root",
	password="admin",
	database="corpus"
)

mycursor = mydb.cursor()

def findReadablePassage(passageLength, minPercentage, vocablist):
	"""
	:param length: int. Approximate number of words
	:param percentage: int. Vocab coverage needed.
	:param vocablist: list. List of known vocab
	:return: None
	"""
	isReadable = False
	while not isReadable:
		title = None
		while not title:
			results = get_random_passage(passageLength)
			if results:
				author, title, splitPassage, joinedPassage = results
		print("\n\n", author, title)
		print(str(len(splitPassage)) + " words.")

		cleanPassage = normalize_text(joinedPassage)
		doc = analyseSmall(cleanPassage)
		words = [w for w in doc.words if not ignore(w)]
		word_coverage, lemmaCoverage, unknown_words = check_coverage(words, vocablist)
		if word_coverage >= minPercentage:
			isReadable = True
		else:
			print("Coverage minimum not met.")
	NL = "\n"
	lemmaList = set([w.lemma for w in words])
	analysis = f"\n{author} {title}" \
			   f"\n\nTotals" \
			   f"\nTotal words in text: {len(words)}" \
			   f"\nTotal number of lemmata: {len(lemmaList)}" \
			   f"\n\nCoverage" \
			   f"\nPercentage of words known: {word_coverage:.2f}%" \
			   f"\nPercentage of lemmata known: {lemmaCoverage:.2f}%" \
			   f"\n\n{cleanPassage}\n" \
			   f"\n{NL.join(unknown_words)}\n"
	return analysis


# Get 10 random readable passages
count = 0
length = 90
percentage = 80
vocab = dcc_list
file = "results/" + str(percentage) + "% passages.txt"
while count < 10:
	results = findReadablePassage(length, percentage, vocab)
	with open(file, "a", encoding="utf-8") as outfile:
		outfile.write(results)
