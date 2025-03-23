import random
from setup import *


def getPickles(author, title):
	res = []
	for filename in os.listdir(f"docs/{author}/{title}"):
		res.append(f"docs/{author}/{title}/{filename}")
	return res


def deserialize(filename):
	# Open the file in binary mode
	with open(filename, 'rb') as file:
		# Call load method to deserialze
		doc = pickle.load(file)
		return doc


def create_docObj(nlpDoc):
	clean_words = [x for x in nlpDoc.words if not ignore(x)]

	docObject = {'embeddings': nlpDoc.embeddings,
				 'lemmata': nlpDoc.lemmata,
				 'morphosyntactic_features': nlpDoc.morphosyntactic_features,
				 'pos': nlpDoc.pos,
				 'sentences': nlpDoc.sentences,
				 'sentences_strings': nlpDoc.sentences_strings,
				 'sentences_tokens': nlpDoc.sentences_tokens,
				 'stems': nlpDoc.stems, 'tokens': nlpDoc.tokens,
				 'tokens_stops_filtered': nlpDoc.tokens_stops_filtered,
				 'words': nlpDoc.words, 'raw': nlpDoc.raw,
				 'normalized_text': nlpDoc.normalized_text,
				 'token_count': len(nlpDoc.tokens),
				 'sentence_count': len(nlpDoc.sentences),
				 'word_count': sum([1 for w in nlpDoc.words if w.upos != "PUNCT"]),
				 'unique': set(w.lemma for w in clean_words)}

	docObject['density'] = len(docObject['unique']) / docObject['word_count']
	docObject['token_count'] = len(docObject['tokens'])
	docObject['sentence_count'] = len(docObject['sentences'])
	docObject['clean_words'] = [x for x in docObject['words'] if not ignore(x)]
	docObject['word_count'] = len(docObject['clean_words'])
	docObject['unique'] = set(w.lemma for w in docObject['clean_words'])

	return docObject

def combine_docs(doclist):
	"""
	combine several nlpdocs into one doc object
	:param doclist:
	:return:
	"""
	docObject = {
		'embeddings': [],
		'lemmata': [],
		'morphosyntactic_features': [],
		'pos': [],
		'sentences': [],
		'sentences_strings': [],
		'sentences_tokens': [],
		'stems': [],
		'tokens': [],
		'tokens_stops_filtered': [],
		'words': [],
		'raw': '',
		'normalized_text': '', }

	for doc in doclist:
		for ATT in docObject.keys():
			val = getattr(doc, ATT)
			try:
				if ATT == 'words' and len(docObject['words']) > 0:
					highestSentence = docObject['words'][-1].index_sentence
					for w in val:
						w.index_sentence += highestSentence + 1
				docObject[ATT] += val
			except Exception as e:
				print(e)
				continue
	docObject['token_count'] = len(docObject['tokens'])
	docObject['sentence_count'] = len(docObject['sentences'])
	docObject['clean_words'] = [x for x in docObject['words'] if not ignore(x)]
	docObject['word_count'] = len(docObject['clean_words'])
	docObject['unique'] = set(w.lemma for w in docObject['clean_words'])
	docObject['density'] = len(docObject['unique'])/docObject['word_count']
	return docObject

def ignore(wordObject):
	"""
	Ignore words which are punctuation, empty strings, proper nouns, or (English) numbers
	:param wordObject:
	:return:
	"""
	if wordObject.upos == "PUNCT" or wordObject.upos == "X" or wordObject.upos == "PROPN" or wordObject.upos == "SYM":
		return True
	if wordObject.string == "":
		return True
	for char in wordObject.string:
		# TODO inaccurate because of the words that have numbers attached.
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
	"""
	:param wordList: list of word objects
	:return: 3 dictionaries
	"""
	gerundives = []
	participles = []
	for w in wordList:
		if isFeatureInstance(w, "VerbForm", "participle"):
			if 'nd' in w.string:
				gerundives.append((w.string, w.index_char_start))
			else:
				participles.append((w.string, w.index_char_start))

	# TODO not finding any gerunds, supines
	verbforms = {
				"subjunctives": [(w.string, w.index_sentence, w.index_token) for w in wordList
									if isFeatureInstance(w, "Mood", "subjunctive")],
				"imperatives": [(w.string, w.index_sentence, w.index_token) for w in wordList
							 		if isFeatureInstance(w, "Mood", "imperative")],
				"gerundives": gerundives,
				# "gerunds": [(w.string, w.index_sentence, w.index_token) for w in wordList
				# 		 			if isFeatureInstance(w, "VerbForm", "gerund")],
				# "supines": [(w.string, w.index_sentence, w.index_token) for w in wordList
				# 		 			if isFeatureInstance(w, "VerbForm", "supine")],
				"participles": participles,
				"AbAbs": [(w.string, w.index_sentence, w.index_token) for w in wordList
					   				if isFeatureInstance(w, "VerbForm", "participle") and isFeatureInstance(w, "Case", "ablative")],
				"infinitives": [(w.string, w.index_sentence, w.index_token) for w in wordList
							 		if isFeatureInstance(w, "VerbForm", "infinitive")],
				"finite verbs": [(w.string, w.index_sentence, w.index_token) for w in wordList
							  		if isFeatureInstance(w, "VerbForm", "finite")]}

	cases = {
		"ablatives": [(w.string, w.index_sentence, w.index_token) for w in wordList if isFeatureInstance(w, "Case", "ablative")],
		"datives": [(w.string, w.index_sentence, w.index_token) for w in wordList if isFeatureInstance(w, "Case", "dative")],
		"genitives": [(w.string, w.index_sentence, w.index_token) for w in wordList if isFeatureInstance(w, "Case", "genitive")],
		"locatives": [(w.string, w.index_sentence, w.index_token) for w in wordList if isFeatureInstance(w, "Case", "locative")],
		"vocatives": [(w.string, w.index_sentence, w.index_token) for w in wordList if isFeatureInstance(w, "Case", "vocative")]}

	# TODO not finding interjections

	pos = {
		"verbs": [w for w in wordList if str(w.pos) == "verb"],
		"nouns": [w for w in wordList if str(w.pos) == "noun"],
		"proper nouns": [w for w in wordList if str(w.upos) == "PROPN"],
		"adjectives": [w for w in wordList if str(w.pos) == "adjective"],
		"pronouns": [w for w in wordList if str(w.pos) == "pronoun"],
		"prepositions": [w for w in wordList if str(w.pos) == "adposition"],
		"adverbs": [w for w in wordList if str(w.pos) == "adverb"],
		"conjunctions": [w for w in wordList if
						 str(w.pos) == "subordinating_conjunction" or str(w.pos) == "coordinating_conjunction"],
		"particles": [w for w in wordList if str(w.pos) == "particle"],
		"determiners": [w for w in wordList if str(w.pos) == "determiner"],
		"interjections": [w for w in wordList if str(w.upos) == "INTJ"]
	}
	pos["verbs"] += [w for w in wordList if str(w.pos) == "auxiliary"]
	pos["adjectives"] += [w for w in wordList if str(w.pos) == "numeral"]

	return verbforms, cases, pos

def create_freq_list(docobj):
	words = [w for w in docobj['words'] if not ignore(w)]
	result = {}
	for w in words:
		if w.lemma in result.keys():
			result[w.lemma] += 1
		else:
			result[w.lemma] = 1
	result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
	return result

def avg_sentence_length(docObj):
	sent_lengths = [len(s) for s in docObj['sentences']]
	return sum(x for x in sent_lengths)/len(sent_lengths)


if __name__ == "__main__":
	pass
