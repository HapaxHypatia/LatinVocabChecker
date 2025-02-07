import pickle


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
	("virgilius", "georgica")
]

def deserialize(author, title):
	# Open the file in binary mode
	filepath = f"docs/{author}/{title}.pickle"
	with open(filepath, 'rb') as file:
		# Call load method to deserialze
		doc = pickle.load(file)
		return doc


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
	cases = {}
	pos = {}
	verbforms = {}

	# TODO not finding any gerundives, gerunds, supines
	verbforms["subjunctives"] = [(w.string, w.index_char_start) for w in wordList if
								 isFeatureInstance(w, "Mood", "subjunctive")]
	verbforms["imperatives"] = [(w.string, w.index_char_start) for w in wordList if
								isFeatureInstance(w, "Mood", "imperative")]
	verbforms["gerundives"] = [(w.string, w.index_char_start) for w in wordList if
							   isFeatureInstance(w, "VerbForm", "gerundive")]
	verbforms["gerunds"] = [(w.string, w.index_char_start) for w in wordList if
							isFeatureInstance(w, "VerbForm", "gerund")]
	verbforms["supines"] = [(w.string, w.index_char_start) for w in wordList if
							isFeatureInstance(w, "VerbForm", "supine")]
	verbforms["participles"] = [(w.string, w.index_char_start) for w in wordList if
								isFeatureInstance(w, "VerbForm", "participle")]
	verbforms["AbAbs"] = [(w.string, w.index_char_start) for w in wordList if
						  isFeatureInstance(w, "VerbForm", "participle") and isFeatureInstance(w, "Case", "ablative")]
	verbforms["infinitives"] = [(w.string, w.index_char_start) for w in wordList if
								isFeatureInstance(w, "VerbForm", "infinitive")]
	verbforms["finite verbs"] = [(w.string, w.index_char_start) for w in wordList if
								 isFeatureInstance(w, "VerbForm", "finite")]

	# TODO not finding vocatives
	cases["ablatives"] = [(w.string, w.index_char_start) for w in wordList if isFeatureInstance(w, "Case", "ablative")]
	cases["datives"] = [(w.string, w.index_char_start) for w in wordList if isFeatureInstance(w, "Case", "dative")]
	cases["genitives"] = [(w.string, w.index_char_start) for w in wordList if isFeatureInstance(w, "Case", "genitive")]
	cases["locatives"] = [(w.string, w.index_char_start) for w in wordList if isFeatureInstance(w, "Case", "locative")]
	cases["vocatives"] = [(w.string, w.index_char_start) for w in wordList if isFeatureInstance(w, "Case", "vocative")]

	# TODO not finding proper nouns, interjections
	pos["verbs"] = [w for w in wordList if str(w.pos) == "verb"]
	pos["verbs"] += [w for w in wordList if str(w.pos) == "auxiliary"]
	pos["nouns"] = [w for w in wordList if str(w.pos) == "noun"]
	pos["proper nouns"] = [w for w in wordList if str(w.pos) == "proper_noun"]
	pos["adjectives"] = [w for w in wordList if str(w.pos) == "adjective"]
	pos["adjectives"] += [w for w in wordList if str(w.pos) == "numeral"]
	pos["pronouns"] = [w for w in wordList if str(w.pos) == "pronoun"]
	pos["prepositions"] = [w for w in wordList if str(w.pos) == "adposition"]
	pos["adverbs"] = [w for w in wordList if str(w.pos) == "adverb"]
	pos["conjunctions"] = [w for w in wordList if
						   str(w.pos) == "subordinating_conjunction" or str(w.pos) == "coordinating_conjunction"]
	pos["particles"] = [w for w in wordList if str(w.pos) == "particle"]
	pos["determiners"] = [w for w in wordList if str(w.pos) == "determiner"]
	pos["interjections"] = [w for w in wordList if str(w.pos) == "interjection"]

	return verbforms, cases, pos


if __name__ == "__main__":

	docs = []
	# get pickle file from disk or db
	# deserialize
	#

	# get lists of text features
	words = [word for doc in docs for word in doc.words if not ignore(word)]
	lemmalist = set([w.lemma for w in words])
	verbforms, cases, pos = set_lists(words)

	# print analysis
	print("\n Totals")
	print("Total words in text: {}".format(len(words)))
	print("Total number of lemmata: {}".format(len(lemmalist)))
	wordCoverage, lemmaCoverage, unknown = check_coverage(words, dcc_list)
	print("\n Coverage")
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
