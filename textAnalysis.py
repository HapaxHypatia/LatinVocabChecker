from cltk import NLP
from cltk.alphabet.lat import remove_macrons, JVReplacer
import mysql.connector as SQL


def normalize_text(text):
	replacer = JVReplacer()
	text = remove_macrons(text)
	text = replacer.replace(text)
	return text.lower()


mydb = SQL.connect(
	host="localhost",
	user="root",
	password="admin",
	database="corpus"
)
mycursor = mydb.cursor()


def getText(title):
	'''
	Get full text from DB
	:param string title: Title of work
	:return: string of text
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
		print("There are {} texts by that name.".format(len(results)))
		for i in range(len(results)):
			print("{}. {} {}".format(i, results[i][1], title))
		selection = int(input("Please type the number of the text you want."))
		text = results[selection][0]
		author = results[selection][1]
	else:
		text = results[0][0]
		author = results[0][1]
	print("Text: {} by {} successfully collected".format(title, author))
	return text

def analyse(text):
	cltk = NLP(language="lat", suppress_banner=True)
	print("Beginning analysis. Please wait.")
	doc = cltk.analyze(text)
	print("Finished analysing")
	return doc


def isFeatureInstance(wordObject, feature, value):
	keys = [str(key) for key in wordObject.features.keys()]
	if feature in keys:
		featureValue = str(wordObject.features[feature][0])
		if featureValue == value or value in featureValue:
			return True
		else:
			return False


def ignore(wordObject):
	if wordObject.upos == "PUNCT" or wordObject.upos =="X":
		return True
	for char in wordObject.string:
		if char.isdigit():
			return True
	return False

if __name__ == "__main__":
	print("Starting...")
	while True:
		title = input("Enter title of text: ")
		text = getText(title)
		if not text:
			title = input("Enter title of text: ")
		else:
			break

	doc = analyse(text[0:30000])

	words = [w for w in doc.words if not ignore(w)]
	lemmalist = set([w.lemma for w in words])

	cases = {}
	pos = {}
	verbforms = {}

	verbforms["subjunctives"] = [(w.string, w.index_char_start) for w in doc.words if
								 isFeatureInstance(w, "Mood", "subjunctive")]
	verbforms["imperatives"] = [(w.string, w.index_char_start) for w in doc.words if
								isFeatureInstance(w, "Mood", "imperative")]
	verbforms["gerundives"] = [(w.string, w.index_char_start) for w in doc.words if
							   isFeatureInstance(w, "VerbForm", "gerundive")]
	verbforms["gerunds"] = [(w.string, w.index_char_start) for w in doc.words if
							isFeatureInstance(w, "VerbForm", "gerund")]
	verbforms["supines"] = [(w.string, w.index_char_start) for w in doc.words if
							isFeatureInstance(w, "VerbForm", "supine")]
	verbforms["participles"] = [(w.string, w.index_char_start) for w in doc.words if
								isFeatureInstance(w, "VerbForm", "participle")]
	verbforms["AbAbs"] = [(w.string, w.index_char_start) for w in doc.words if
						  isFeatureInstance(w, "VerbForm", "participle") and isFeatureInstance(w, "Case", "ablative")]
	verbforms["infinitives"] = [(w.string, w.index_char_start) for w in doc.words if
								isFeatureInstance(w, "VerbForm", "infinitive")]
	verbforms["finite verbs"] = [(w.string, w.index_char_start) for w in doc.words if
								 isFeatureInstance(w, "VerbForm", "finite")]

	cases["ablatives"] = [(w.string, w.index_char_start) for w in doc.words if isFeatureInstance(w, "Case", "ablative")]
	cases["datives"] = [(w.string, w.index_char_start) for w in doc.words if isFeatureInstance(w, "Case", "dative")]
	cases["genitives"] = [(w.string, w.index_char_start) for w in doc.words if isFeatureInstance(w, "Case", "genitive")]
	cases["locatives"] = [(w.string, w.index_char_start) for w in doc.words if isFeatureInstance(w, "Case", "locative")]
	cases["vocatives"] = [(w.string, w.index_char_start) for w in doc.words if isFeatureInstance(w, "Case", "vocative")]

	pos["verbs"] = [w for w in doc.words if str(w.pos) == "verb"]
	pos["verbs"] += [w for w in doc.words if str(w.pos) == "auxiliary"]
	pos["nouns"] = [w for w in doc.words if str(w.pos) == "noun"]
	pos["proper nouns"] = [w for w in doc.words if str(w.pos) == "proper_noun"]
	pos["adjectives"] = [w for w in doc.words if str(w.pos) == "adjective"]
	pos["adjectives"] += [w for w in doc.words if str(w.pos) == "numeral"]
	pos["pronouns"] = [w for w in doc.words if str(w.pos) == "pronoun"]
	pos["prepositions"] = [w for w in doc.words if str(w.pos) == "adposition"]
	pos["adverbs"] = [w for w in doc.words if str(w.pos) == "adverb"]
	pos["conjunctions"] = [w for w in doc.words if
						   str(w.pos) == "subordinating_conjunction" or str(w.pos) == "coordinating_conjunction"]
	pos["particles"] = [w for w in doc.words if str(w.pos) == "particle"]
	pos["determiners"] = [w for w in doc.words if str(w.pos) == "determiner"]
	pos["interjections"] = [w for w in doc.words if str(w.pos) == "interjection"]

	# print analysis
	print("Total words in text: {}".format(len(words)))
	print("Total number of lemmata: {}".format(len(lemmalist)))

	for k in verbforms.keys():
		print("Number of {} in text: {}".format(k, len(verbforms[k])))

	for k in cases.keys():
		print("Number of {} in text: {}".format(k, len(verbforms[k])))

	for k in pos.keys():
		print("Number of {} in text: {}".format(k, len(verbforms[k])))

