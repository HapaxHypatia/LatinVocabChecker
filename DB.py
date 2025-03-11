def connect(func):

	def wrapper(*args, **kwargs):
		import mysql.connector as SQL
		mydb = SQL.connect(
			host="localhost",
			user="root",
			password="admin",
			database="corpus"
		)
		cursor = mydb.cursor()
		result = func(cursor, *args)
		cursor.close()
		return result

	return wrapper


@connect
def getText(cursor, title, author):
	"""
	:param title: string
	:param author: string
	:return:
	"""
	title = title.lower()
	textQuery = "SELECT textString, authorName FROM texts WHERE LOWER(title) = %s"
	vals = (title,)
	cursor.execute(textQuery, vals)
	results = cursor.fetchall()
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
	return text


@connect
def DBgetAuthor(cursor, name):
	# get author ID for text
	val = (name,)
	sql = "SELECT authorID, fullName FROM authors WHERE LOWER(authorName) = %s"
	cursor.execute(sql, val)
	results = cursor.fetchall()
	if len(results) > 1:
		print('Multiple authors found.')
		for i, r in enumerate(results):
			print(f'{str(i+1)}. {r[1]}')
		choice = input('Select the author you want: ')
		return results[int(choice)-1][0], results[int(choice)-1][1]
	else:
		return results[0][0], results[0][1]


@connect
def textExists(cursor, text):
	CHECKsql = "SELECT * FROM texts WHERE title = %s AND authorID = %s"
	val = (text["title"], text["authorID"])
	cursor.execute(CHECKsql, val)
	searchResult = cursor.fetchall()
	return searchResult if searchResult else False


@connect
def getTextList(cursor, authorID):
	CHECKsql = "SELECT title FROM texts WHERE authorID = %s"
	val = (authorID,)
	cursor.execute(CHECKsql, val)
	searchResult = cursor.fetchall()
	if searchResult:
		return searchResult
	else:
		return False


@connect
def searchDB(cursor, table, ret, prop, val):
	sql = f'SELECT {ret} FROM {table} WHERE {prop} == {val}'
	cursor.execute(sql)
	results = cursor.fetchall()
	return results
