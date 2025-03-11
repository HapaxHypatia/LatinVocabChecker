def connect(func):
	print("inside connect")
	def wrapper(*args, **kwargs):
		print("inside wrapper")
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
def DBgetAuthor(cursor, fullname):
	print("inside get author function")
	# get author ID for text
	val = (fullname,)
	sql = "SELECT authorID, authorName FROM authors WHERE LOWER(fullName) = %s"
	cursor.execute(sql, val)
	results = cursor.fetchall()
	return results[0][0], results[0][1]


DBgetAuthor("Cicero")
