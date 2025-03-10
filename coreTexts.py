from analyseText import *


def reduce_fraction(x,y):
	result = min(x, y)
	div = 1
	while div <= min(x, y):
		if x % div == 0 and y % div == 0:
			result = div
		div += 1
	return x/result, y/result


if __name__ == "__main__":
	authors ={
		"Cicero": {
			"In Catilinam": "",
			"In Pisonem": "",
			"In Q. Caecilium": "",
			"In Sallustium [sp.]": "",
			"In Vatinium": "",
			"In Verrem": "",
			"Pro Archia": "",
			"Pro Balbo": "",
			"Pro Caecina": "",
			"Pro Caelio": "",
			"Pro Cluentio": "",
			"Pro Flacco": "",
			"Pro Fonteio": "",
			"Pro Lege Manilia": "",
			"Pro Ligario": "",
			"Pro Marcello": "",
			"Pro Milone": "",
			"Pro Murena": "",
			"Pro Plancio": "",
			"Pro Q. Roscio Comoedo": "",
			"Pro Quinctio": "",
			"Pro Rabirio Perduellionis Reo": "",
			"Pro Rabirio Postumo": "",
			"Pro Rege Deiotaro": "",
			"Pro S. Roscio Amerino": "",
			"Pro Scauro": "",
			"Pro Sestio": "",
			"Pro Sulla": "",
			"Pro Tullio": ""
		},
		"Caesar": {"de bello gallico": ""},
		"Catullus": {"carmina": ""},
		"Livius": {"ab urbe condita": ""},
		"Ovidius": {
			"metamorphoses": "",
			"amores": "",
			"remedia amoris": "",
			"Heroides": ""
		},
		"Plinius": {"epistulae": ""},
		"Vergilius": {"aeneis": ""}
	}

	for A in authors.keys():
		#string of author name
		for ind, T in enumerate(authors[A]):
			#list of texts
			docfiles = getPickles(A, T)
			docs = list([deserialize(pickle) for pickle in docfiles])
			# can skip if docs are combined before pickling
			doc = combine_docs(docs)
			authors[A][T] = doc

		# Total length
		words = []
		sent_lengths = []
		for text, doc in authors[A].items():
			words += [x for x in doc['words']]
			sent_lengths += [len(s) for s in doc['sentences']]

		print(f'\n\n{A}:')
		verbforms, cases, pos = set_lists(words)
		clean_words = [x for x in words if not ignore(x)]
		total_length = len(clean_words)
		total_lemmata = len(set(w.lemma for w in clean_words))
		avg_sent_length = sum([x for x in sent_lengths])/len(sent_lengths)
		num, dem = reduce_fraction(total_lemmata, total_length)
		lex_density = num/dem

		print(f'Total wordcount: {total_length:,} words')
		print(f'Total lemmata: {total_lemmata:,}')
		print(f'Average sentence length: {round(avg_sent_length)} words')
		print(f'Lexical density: {lex_density:.1%}')

		# No. words required for 90% (Overall and on average on random passages)

		# Grammatical complexity: frequency of advanced grammatical forms

# Nested list comprehension
# [x for y in ylist for x in xlist (if x ....)]

# RESULTS
# Caesar has quite low lexical density
# Virgil slightly high
# Catullus very high
