import os
from analyseText import deserialize, ignore
from setup import normalize_text


def create_freq_list():
	all_words = []
	for folder in os.listdir("docs"):
		for file in os.listdir("docs/"+folder):
			doc = deserialize(f"docs/{folder}/{file}")
			words = [w for w in doc.lemmata if not ignore(w)]
			all_words+=words
	result = {}
	for w in all_words:
		if w in result.keys():
			result[w] += 1
		else:
			result[w] = 1
	result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
	return result


# TODO test how many words from senior freq list are needed to reach 90% coverage on a random passage of a given author


