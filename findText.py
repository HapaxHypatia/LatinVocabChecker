from analyseText import *
from setup import *
from dbFunctions import *
from cltk.sentence.lat import LatinPunktSentenceTokenizer

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


def get_random_passage(text, passageLength):
	# TODO remove numbers here?
	if len(text.split()) < passageLength:
		print("Work too short.")
		return False
	else:
		print("Getting random passage from text.")
		splitter = LatinPunktSentenceTokenizer()
		sentences = splitter.tokenize(text)
		if len(sentences) < 2:
			print("Not enough sentences.")
			return False
		passage = ""
		while len(passage.split()) < passageLength:
			start = random.randint(0, len(sentences)-1)
			for s in sentences[start:]:
				wordcount = len([w for w in passage.split() if w != "."])
				if wordcount + len(s.split()) < passageLength * 1.1:
					passage = passage + s + " "
				else:
					break
		print(f"Returning passage of {len(passage.split())} words.")
		return passage


def isReadable(passage, minPercentage, vocablist):
	"""
	:param passage: str. passage to be checked.
	:param percentage: int. Vocab coverage needed.
	:param vocablist: list. List of known vocab.
	:return: bool
	"""
	print("Checking readability.")
	doc = analyseSmall(passage)
	words = [w for w in doc.words if not ignore(w)]
	word_coverage, lemmaCoverage, unknown_words = check_coverage(words, vocablist)
	if word_coverage >= minPercentage:
		print(f"Found passage with {word_coverage:.2f}% coverage.")
		return word_coverage, lemmaCoverage, unknown_words
	else:
		print(f"Passage did not meet minimum coverage. Coverage was {word_coverage:.2f}%.")
		return False

