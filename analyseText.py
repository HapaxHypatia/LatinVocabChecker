import random
from setup import *

works = [
	("Cicero", 'Pro S. Roscio Amerino'),
	("apuleius", "metamorphoses"),
	("gellius", "noctes atticae"),
	("Caesar", "de bello gallico"),
	("Catullus", "carmina"),
	("Cicero", "de legibus"),
	("Cicero", "de officiis"),
	("Cicero", "de legibus"),
	("Cicero", "Pro Q. Roscio Comoedo"),
	("Cicero", "Pro Lege Manilia"),
	("Cicero", "Pro Rabirio Perduellionis Reo"),
	("Cicero", "Pro Murena"),
	("Cicero", "Pro Sulla"),
	("Cicero", "Pro Archia"),
	("Cicero", "Pro Caelio"),
	("Cicero", "Pro Milone"),
	("Cicero", "in verrem"),
	("Cicero", "in catilinam"),
	# ("iuvenalis", "saturae"),
	# ("livius", "ab urbe condita"),
	# ("lucretius", "de rerum natura"),
	# ("ovidius", "metamorphoses"),
	# ("ovidius", "amores"),
	# ("ovidius", "remedia amoris"),
	# ("ovidius", "Epistulae (vel Heroides)"),
	# ("plinius", "epistulae"),
	# ("tacitus", "annales"),
	# ("tibullus", "elegiae"),
	# ("virgilius", "aeneis"),
	# ("virgilius", "georgica")
]


def getPickles(author, title):
	res = []
	for filename in os.listdir(f"docs/{author}"):
		if re.search(rf"{title}\d.pickle", filename):
			res.append(f"docs/{author}/{filename}")
	return res


def deserialize(filename):
	# Open the file in binary mode
	with open(filename, 'rb') as file:
		# Call load method to deserialze
		doc = pickle.load(file)
		return doc


def ignore(wordObject):
	"""
	Ignore words which are punctuation, empty strings, proper nouns, or (English) numbers
	:param wordObject:
	:return:
	"""
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


def isFeatureInstance(wordObject, feature, value):
	keys = [str(key) for key in wordObject.features.keys()]
	if feature in keys:
		featureValue = str(wordObject.features[feature][0])
		if featureValue == value or value in featureValue:
			return True
		else:
			return False


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


def set_lists(wordList):
	# TODO not finding any gerundives, gerunds, supines
	verbforms = {"subjunctives": [(w.string, w.index_char_start) for w in wordList
								  if isFeatureInstance(w, "Mood", "subjunctive")],
				 "imperatives": [(w.string, w.index_char_start) for w in wordList
								 if isFeatureInstance(w, "Mood", "imperative")],
				 "gerundives": [(w.string, w.index_char_start) for w in wordList
								if isFeatureInstance(w, "VerbForm", "gerundive")],
				 "gerunds": [(w.string, w.index_char_start) for w in wordList
							 if isFeatureInstance(w, "VerbForm", "gerund")],
				 "supines": [(w.string, w.index_char_start) for w in wordList
							 if isFeatureInstance(w, "VerbForm", "supine")],
				 "participles": [(w.string, w.index_char_start) for w in wordList
								 if isFeatureInstance(w, "VerbForm", "participle")],
				 "AbAbs": [(w.string, w.index_char_start) for w in wordList
						   if
						   isFeatureInstance(w, "VerbForm", "participle") and isFeatureInstance(w, "Case", "ablative")],
				 "infinitives": [(w.string, w.index_char_start) for w in wordList
								 if isFeatureInstance(w, "VerbForm", "infinitive")],
				 "finite verbs": [(w.string, w.index_char_start) for w in wordList
								  if isFeatureInstance(w, "VerbForm", "finite")]}

	# TODO not finding vocatives
	cases = {
		"ablatives": [(w.string, w.index_char_start) for w in wordList if isFeatureInstance(w, "Case", "ablative")],
		"datives": [(w.string, w.index_char_start) for w in wordList if isFeatureInstance(w, "Case", "dative")],
		"genitives": [(w.string, w.index_char_start) for w in wordList if isFeatureInstance(w, "Case", "genitive")],
		"locatives": [(w.string, w.index_char_start) for w in wordList if isFeatureInstance(w, "Case", "locative")],
		"vocatives": [(w.string, w.index_char_start) for w in wordList if isFeatureInstance(w, "Case", "vocative")]}

	# TODO not finding proper nouns, interjections

	pos = {
		"verbs": [w for w in wordList if str(w.pos) == "verb"],
		"nouns": [w for w in wordList if str(w.pos) == "noun"],
		"proper nouns": [w for w in wordList if str(w.pos) == "proper_noun"],
		"adjectives": [w for w in wordList if str(w.pos) == "adjective"],
		"pronouns": [w for w in wordList if str(w.pos) == "pronoun"],
		"prepositions": [w for w in wordList if str(w.pos) == "adposition"],
		"adverbs": [w for w in wordList if str(w.pos) == "adverb"],
		"conjunctions": [w for w in wordList if
						 str(w.pos) == "subordinating_conjunction" or str(w.pos) == "coordinating_conjunction"],
		"particles": [w for w in wordList if str(w.pos) == "particle"],
		"determiners": [w for w in wordList if str(w.pos) == "determiner"],
		"interjections": [w for w in wordList if str(w.pos) == "interjection"]
	}
	pos["verbs"] += [w for w in wordList if str(w.pos) == "auxiliary"]
	pos["adjectives"] += [w for w in wordList if str(w.pos) == "numeral"]

	return verbforms, cases, pos


if __name__ == "__main__":
	# get pickle file from disk or db
	# deserialize
	# author, title = random.choice(works)
	author = "Vergilius"
	title = "aeneis"

	docfiles = getPickles(author, title)
	docs = list([deserialize(pickle) for pickle in docfiles])

	# get lists of text features
	words = [word for doc in docs for word in doc.words if not ignore(word)]
	lemmalist = set([w.lemma for w in words])
	verbforms, cases, pos = set_lists(words)

	with open("data/wordlists/dcc list.txt", 'rb') as file:
		dcc_list = list([x.strip().decode() for x in file.readlines()])

	# print analysis
	print(f"\n{title} by {author}")
	print("\nTotals")
	print("Total words in text: {}".format(len(words)))
	print("Total number of lemmata: {}".format(len(lemmalist)))
	wordCoverage, lemmaCoverage, unknown = check_coverage(words, dcc_list)
	print("\nCoverage")
	print("Percentage of lemmata known: {:.2f}%".format(lemmaCoverage))
	print("Percentage of words known: {:.2f}%".format(wordCoverage))
	print("\n")

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


