import random

from textAnalysis import *


def get_random_passage(passageLength):
	#  TODO ensure passage is only full sentences
	# TODO test this function (new)
	id = random.randint(52, 884)
	textQuery = "SELECT title, textString, authorName, textLength FROM texts WHERE textID = %s"
	vals = (id,)
	mycursor.execute(textQuery, vals)
	results = mycursor.fetchall()[0]
	title, text, author, length = results
	if length > passageLength:
		textLength = len(text.split())
		upperLimit = textLength - passageLength
		x = random.randint(0, upperLimit)
		passage = text.split()[x: x + passageLength]
		return author, title, passage, " ".join(passage)


wb = load_workbook("data/Latin Core Vocab.xlsx")
ws = wb.active
raw_dcc_list = [ws.cell(row=i, column=2).value for i in range(2, ws.max_row)]
dcc_list = [normalize_text(i) for i in raw_dcc_list]

mydb = SQL.connect(
	host="localhost",
	user="root",
	password="admin",
	database="corpus"
)

mycursor = mydb.cursor()
count = 0
while count < 9:
	passageLength = 200
	minPercentage = 80

	author, title, splitPassage, joinedPassage = get_random_passage(passageLength)
	print("\n\n", author, title)
	print("\n", splitPassage[0], " - ", splitPassage[-1])
	print("\n" + str(len(splitPassage)) + " words.")

	cleanPassage = normalize_text(joinedPassage)
	doc = analyse(cleanPassage)
	words = [w for w in doc.words if not ignore(w)]

	coverage = check_coverage(words, dcc_list)
	if coverage[0] < minPercentage:
		continue
	else:
		count += 1
		# print analysis
		NL = "\n"
		lemmaList = set([w.lemma for w in words])
		analysis = f"\n\nPassage no. {count}" \
				f"\n{author} {title}" \
				f"\n\nTotals" \
				f"\nTotal words in text: {len(words)}" \
				f"\nTotal number of lemmata: {len(lemmaList)}" \
				f"\n\nCoverage" \
				f"\nPercentage of words known: {coverage[0]:.2f}%" \
				f"\nPercentage of lemmata known: {coverage[1]:.2f}%" \
				f"\n\n{cleanPassage}\n" \
				f"\n{NL.join(coverage[2])}\n"
		print(analysis)

		with open("results/" + str(minPercentage) + "% passages.txt", "a", encoding="utf-8") as outfile:
			outfile.write(analysis)
