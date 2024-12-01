import csv

from textAnalysis import *

# Get freq vocab of common prescribed texts
# Cicero Forensic Speeches
# Y Virgil Aeneid
# Y Catullus
# Livy
# Lucretius
# Ovid (
# metmorphoses,
# Y amores,
# Y heroides)
# Y Pliny
# Y Tacitus (annales)

#
# 'Livius' 'Ab Urbe Condita'
# 'Lucretius' 'De Rerum Natura'
# 'Ovidius' 'Metamorphoses'

mydb = SQL.connect(
	host="localhost",
	user="root",
	password="admin",
	database="corpus"
)

mycursor = mydb.cursor()

sql = "SELECT title, textString FROM texts WHERE authorName = 'Cicero'"
mycursor.execute(sql)
results = mycursor.fetchall()

for r in results:
	title, text = r
	if title.startswith("In ") or title.startswith('Pro '):
		print(title)
		doc = analyse(text)
		textWords = [w for w in doc.words if not ignore(w)]
		freqList = []
		exists = [freqList.index(wordDict) for wordDict in freqList if wordDict['lemma'] == w.lemma]
		for w in textWords:
			if len(exists) < 1:
				freqList.append({
					"lemma": w.lemma,
					"pos": str(w.pos),
					"freq": 1
				})
			else:
				index = exists[0]
				freqList[index]["freq"] += 1
		with open("results/senior/Cicero_" + title + ".csv", 'w', newline='') as csvfile:
			headerRow = ["lemma", "pos", "freq"]
			writer = csv.DictWriter(csvfile, fieldnames=headerRow)
			writer.writeheader()
			writer.writerows(freqList)
