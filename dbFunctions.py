import mysql.connector as SQL



def getText(title, author):
	'''
	Get full text from DB
	:param string title: Title of work
	:return: string of text, string of author
	'''
	title = title.lower()
	textQuery = "SELECT textString, authorName FROM texts WHERE LOWER(title) = %s"
	vals = (title,)
	mycursor.execute(textQuery, vals)
	results = mycursor.fetchall()
	if len(results) < 1:
		print("No text by that name found in the database.")
		print(author)
		print(title)
		return False
	if len(results) > 1:
		res = list(filter(lambda x: x[1].lower() == author.lower(), results))
		text = res[0][0]
		author = res[0][1]
	else:
		text = results[0][0]
		author = results[0][1]
	print("Text: {} by {} successfully collected".format(title, author))
	return text, author


def DBgetAuthor(fullname):
	# get author ID for text
	val = (fullname,)
	sql = "SELECT authorID, authorName FROM authors WHERE fullName = %s"
	mycursor.execute(sql, val)
	results = mycursor.fetchall()
	return results[0][0], results[0][1]


def textExists(text):
	CHECKsql = "SELECT * FROM texts WHERE title = %s AND authorID = %s"
	val = (text["title"], text["authorID"])
	mycursor.execute(CHECKsql, val)
	searchResult = mycursor.fetchall()
	return searchResult if searchResult else False


def searchDB(table, ret, prop, val):
	sql = f'SELECT {ret} FROM {table} WHERE {prop} == {val}'
	mycursor.execute(sql)
	results = mycursor.fetchall()
	return results


if __name__ == "__main__":
	mydb = SQL.connect(
		host="localhost",
		user="root",
		password="admin",
		database="corpus"
	)
	mycursor = mydb.cursor()

