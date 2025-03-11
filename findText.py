from analyseText import *
from setup import *
from DB import *

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


def get_random_passage(docobj, passageLength):
	# TODO remove numbers here?

	if len(docobj["tokens"]) < passageLength:
		print("Work too short.")
		return False
	else:
		print("Getting random passage from text.")
		sentences = docobj['sentences']
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
