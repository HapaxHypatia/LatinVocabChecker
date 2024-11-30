from cltk import NLP
from cltk.alphabet.lat import remove_macrons, JVReplacer
import mysql.connector as SQL


def normalize_text(text):
	replacer = JVReplacer()
	text = remove_macrons(text)	text = replacer.replace(text)
	return text.lower()


mydb = SQL.connect(
	host="localhost",
	user="root",
	password="admin",
	database="corpus"
)
mycursor = mydb.cursor()


def getText(title, author):
	textQuery = "SELECT textString, textLength FROM texts WHERE authorName = %s AND title = %s"
	vals = (author, title)
	mycursor.execute(textQuery, vals)
	results = mycursor.fetchall()
	length = results[0][1]
	text = results[0][0]
	print("Text: {} by {} successfully collected ({} words)".format(title, author, length))
	return text


def analyse(text):
	cltk = NLP(language="lat", suppress_banner=True)
	doc = cltk.analyze(text)
	print("finished analysing")
	return doc


def isFeatureInstance(word, feature, value):
	keys = [str(key) for key in word.features.keys()]
	if feature in keys:
		if word.features[feature] == value or value in word.features[feature]:
			return True
		else:
			return False


text = getText("Fabulae", "Hyginus")
doc = analyse(text[0:30000])
subjunctives = [w.string for w in doc if isFeatureInstance(w, "Mood", "subjunctive")]
ablatives = [w.string for w in doc if isFeatureInstance(w, "Case", "ablative")]



