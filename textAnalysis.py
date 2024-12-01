from cltk import NLP
from cltk.alphabet.lat import remove_macrons, JVReplacer
import mysql.connector as SQL
from openpyxl.reader.excel import load_workbook


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


def normalize_text(text):
	replacer = JVReplacer()
	text = remove_macrons(text)
	text = replacer.replace(text)
	text.replace("- ", "").replace("-", "")
	return text.lower()


def ignore(wordObject):
	'''
	Ignore words which are punctuation, empty strings, proper nouns, or (English) numbers
	:param wordObject:
	:return:
	'''
	if wordObject.upos == "PUNCT" or wordObject.upos =="X" or wordObject.upos=="PROPN":
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


def compare_lists(wordlist1, wordlist2):
	sharedWords = [w for w in wordlist1 if w in wordlist2]
	return sharedWords


def combine_lists(wordlist1, wordlist2):
	return set(wordlist1 + wordlist2)


def check_coverage(word_objects, vocablist):
	totalWords = len(word_objects)
	total_sharedWords = sum(1 for w in word_objects if w.lemma in vocablist)
	if total_sharedWords < 1:
		word_coverage = 0
	else:
		word_coverage = (total_sharedWords / totalWords) * 100

	lemmaList = set([w.lemma for w in word_objects])
	totalLemmata = len(lemmaList)
	sharedLemmata = compare_lists(lemmaList, vocablist)
	lemmaCoverage = (len(sharedLemmata) / totalLemmata) * 100

	unknown_words = [w.string for w in word_objects if w.lemma not in vocablist]

	return word_coverage, lemmaCoverage, unknown_words


if __name__ == "__main__":
	print("Starting...\n")
	mydb = SQL.connect(
		host="localhost",
		user="root",
		password="admin",
		database="corpus"
	)
	mycursor = mydb.cursor()
	print("Connected to database.\n")

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
	pos["conjunctions"] = [w for w in doc.words if str(w.pos) == "subordinating_conjunction" or str(w.pos) == "coordinating_conjunction"]
	pos["particles"] = [w for w in doc.words if str(w.pos) == "particle"]
	pos["determiners"] = [w for w in doc.words if str(w.pos) == "determiner"]
	pos["interjections"] = [w for w in doc.words if str(w.pos) == "interjection"]

	# print analysis
	print("\n Totals")
	print("Total words in text: {}".format(len(words)))
	print("Total number of lemmata: {}".format(len(lemmalist)))
	print("\n\n")
	print("Verb Forms")
	for k in verbforms.keys():
		print("Number of {} in text: {}".format(k, len(verbforms[k])))
	print("\n\n")
	print("Noun Cases")
	for k in cases.keys():
		print("Number of {} in text: {}".format(k, len(cases[k])))
	print("\n\n")
	print("Parts of Speech")
	for k in pos.keys():
		print("Number of {} in text: {}".format(k, len(pos[k])))

	wb = load_workbook("data/Latin Core Vocab.xlsx")
	ws = wb.active
	raw_dcc_list = [ws.cell(row=i, column=2).value for i in range(2, ws.max_row)]
	dcc_list = [normalize_text(i) for i in raw_dcc_list]

	wordCoverage, lemmaCoverage = check_coverage(words, dcc_list)
	print("\n\n Coverage")
	print("Percentage of lemmata known: {:.2f}%".format(lemmaCoverage))
	print("Percentage of words known: {:.2f}%".format(wordCoverage))

