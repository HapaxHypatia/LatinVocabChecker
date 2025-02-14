from corporaScrape import *
from setup import *
from dbFunctions import *
from analyseText import *
from findText import *
from frequency import *
from loggingSetup import *

# TODO add stage selection for CLC
# TODO analyse the top words coming up that are still unknown on DCC and what words in DCC are not coming up. (Per author?)
# TODO how many words do you typically need before a word repeats in latin?
# TODO create normalised lists vocab for major textbooks
# TODO create frequency list for 90% coverage of common HS texts only, compare to textbook lists
#  DCC definitely gives the best coverage, compared to clc and llpsi, but still only 69%
# TODO Try to find the longest readable passage possible in a given text/author
# TODO add date and genre to database


if __name__ == "__main__":
	# freqdict = create_freq_list()
	# with open("data/wordlists/senior list.txt", "a", encoding="utf-8") as outfile:
	# 	count = 0
	# 	for key, val in freqdict.items():
	# 		count += 1
	# 		outfile.write(f"{count}, {key}, {val}\n")

	#
	# Get 10 random readable passages from a given text

	# set parameters
	# author = "Vergilius"
	# title = "aeneis"
	# docfiles = getPickles(author, title)
	# docs = list([deserialize(pickle) for pickle in docfiles])
	# text = " ".join([token for doc in docs for token in doc.tokens])

	percentage = 80
	passageLength = 50
	vocab = "dcc"
	number = 10

	file = f"results/{number}x{passageLength} words at {percentage}%.txt"
	vocab = getVocab('dcc')

	passages = []
	while len(passages) < number:
		work = get_random_work()
		title, text, author = work
		passage = get_random_passage(text, passageLength)
		if not passage:
			continue
		else:
			cleanPassage = normalize_text(passage)
			doc = analyseSmall(cleanPassage)
			word_coverage, lemmaCoverage, unknown_words = check_coverage(doc.words, vocab)

			details = {
				"author": author,
				"text": text,
				"passage": passage,
				"Coverage": word_coverage,
				"Unknown": unknown_words
			}
			if word_coverage >= percentage:
				colour = '\033[32m'
			else:
				colour = '\033[31m'
			print(colour)
			logger.info(f"{author}, {title}: {word_coverage:.2f}%")
			print("\x1b[0m")
			if word_coverage > percentage:
				passages.append(details)
				with open(file, 'a') as f:
					for k, v in details.items():
						f.write(f"{k}: {v}\n")
					f.write('\n')





# average lemmata in a 130 word passage
# lemmacounts = []
#
# for work in works:
# 	author = work[0]
# 	title = work[1]
# 	docfiles = getPickles(author, title)
# 	docs = list([deserialize(pickle) for pickle in docfiles])
# 	words = [word for doc in docs for word in doc.words if not ignore(word)]
# 	num = len(words)//130
# 	index = 0
# 	for i in range(num):
# 		passage = words[index:index+130]
# 		wordcount = len(passage)
# 		if wordcount != 130:
# 			continue
# 		else:
# 			lemmacount = len(set([w.lemma for w in passage]))
# 			lemmacounts.append(lemmacount)
# 			index+=130
