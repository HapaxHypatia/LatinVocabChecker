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


def getTextByID(cursor, id):
	sql = "SELECT textLength FROM texts WHERE textID = %s"
	val = (id,)
	cursor.execute(sql, val)
	return cursor.fetchall()


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
	# TODO return a dictionary of named keys and values, so I don't have to code which index to grab. Consider doing this for all DB functions.
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

@connect
def DBaddText(cursor, text):
	# insert text
	authorID, authorName = DBgetAuthor(text["author"])
	values = {
		'title': text["title"],
		'length': text["length"],
		'text': text["fulltext"],
		'author': authorID,
		'authorName': authorName
	}
	findText = textExists(text)
	# TODO missed Pliny NH somehow - because of multiple authors with same name?
	if not findText:
		#If text does not already exist in db
		#  TODO need to normalise text before entering. Fix hyphenated words, line numbers in middle of words.
		print("Adding text: {} by {}".format(text['title'], text['author']))
		add_text = ("INSERT INTO texts "
					"(title, textLength, textString, authorID) "
					"VALUES (%(title)s, %(length)s, %(text)s, %(author)s)")
		cursor.execute(add_text, values)
		print("Text added.")
	else:
		textID = findText[0][0]
		# TODO Skip this check to refresh database with new version of texts.
		check_length = "SELECT textLength FROM texts WHERE textID=%s"
		cursor.execute(check_length, (textID,))
		current_length = cursor.fetchall()
		if current_length[0][0] != text['length']:
			# if text is not complete
			update_text = 'UPDATE texts SET textLength=%s, textString=%s WHERE textID = %s'
			values = (text['length'], text['fulltext'], textID)
			cursor.execute(update_text, values)
			print("Text updated.")


@connect
def DBaddAuthor(cursor, name, fullname):
	# insert author
	val = (name, fullname)
	CHECKsql = "SELECT * FROM authors WHERE authorName = %s AND fullName = %s"
	cursor.execute(CHECKsql, val)
	if not cursor.fetchall():
		print("Adding author: {},{}".format(name, fullname))
		ADDsql = "INSERT INTO authors (authorName, fullName) VALUES (%s, %s)"
		cursor.execute(ADDsql, val)
		print("Author added.")


@connect
def DBgetAuthor(cursor, fullname):
	# get author ID for text
	val = (fullname,)
	sql = "SELECT authorID, authorName FROM authors WHERE fullName = %s"
	cursor.execute(sql, val)
	results = cursor.fetchall()
	return results[0][0], results[0][1]


@connect
def textExists(cursor, text):
	CHECKsql = "SELECT * FROM texts WHERE title = %s AND authorID = %s"
	val = (text["title"], text["authorID"])
	cursor.execute(CHECKsql, val)
	searchResult = cursor.fetchall()
	return searchResult if searchResult else False
