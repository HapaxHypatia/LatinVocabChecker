from setup import *


if __name__ == "__main__":

	with open("data/tusc.txt", 'r', encoding='utf-8') as file:
		text = "".join(x.strip() for x in file.readlines())

	res = normalize_text(text)

	# Split text if long then analyse each chunk
	# Store analysed chunks in shared variable
	length = len(text.split())
	print("Text length: {}".format(length))
	num = length // 2000
	manager = multiprocessing.Manager()
	docs = manager.list()
	if num > 1:
		chunks = splitText(text, min(10, num))
		start_time = time.time()
		# NOTE: multiprocessing must be done in __main__
		processes = [Process(target=analyseLarge, args=(ch, docs)) for ch in chunks]
		for process in processes:
			process.start()
		for process in processes:
			process.join()
		print("Analysis took {} minutes.".format(round((time.time() - start_time) / 60), 2))

	words = [word for doc in docs for word in doc.words]
	for i in range(0, 500):
		try:
			print(words[i].string)
			print(words[i].upos)
		except UnicodeEncodeError:
			continue
#  TODO cltk analyser seems to removes the <> around the numbers and split them at full stops. Need to somehow extract references before analysing, split text at references, create dictionary with references as keys

