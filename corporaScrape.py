import time

import mysql.connector as SQL
from selenium import webdriver
from selenium.webdriver.common.by import By

mydb = SQL.connect(
	host="localhost",
	user="root",
	password="admin",
	database="corpus"
)
mycursor = mydb.cursor()


def DBaddAuthor(name, fullname):
	# insert author
	val = (name, fullname)
	CHECKsql = "SELECT * FROM authors WHERE authorName = %s AND fullName = %s"
	mycursor.execute(CHECKsql, val)
	if not mycursor.fetchall():
		print("Adding author: {},{}".format(name, fullname))
		ADDsql = "INSERT INTO authors (authorName, fullName) VALUES (%s, %s)"
		mycursor.execute(ADDsql, val)
		mydb.commit()
		print("Author added.")

def DBgetAuthor(fullname):
	# get author ID for text
	val = (fullname,)
	sql = "SELECT authorID FROM authors WHERE fullName = %s"
	mycursor.execute(sql, val)
	return mycursor.fetchall()


def DBaddText(text):
	# insert text
	authorID = DBgetAuthor(text["author"])
	values = {
		'title': text["title"],
		'length': text["length"],
		'text': text["fulltext"],
		'author': authorID[0][0]
	}
	val = (text["title"], authorID[0][0])
	CHECKsql = "SELECT * FROM texts WHERE title = %s AND authorID = %s"
	mycursor.execute(CHECKsql, val)
	searchresult = mycursor.fetchall()
	if not searchresult:
		print("Adding text: {} by {}".format(text['title'], text['author']))
		add_text = ("INSERT INTO texts "
				   "(title, textLength, textString, authorID) "
				   "VALUES (%(title)s, %(length)s, %(text)s, %(author)s)")
		mycursor.execute(add_text, values)
		mydb.commit()
		print("Text added.")
	else:
		textID = searchresult[0][0]
		check_length = "SELECT textLength FROM texts WHERE textID=%s"
		mycursor.execute(check_length, (textID,))
		current_length = mycursor.fetchall()
		if current_length[0][0] != text['length']:
			values = {
				'length': text["length"],
				'text': text["fulltext"],
				'id': textID
			}
			update_text = ("UPDATE texts SET textLength=%s, textString=%s WHERE textID = %s ) "
					   "VALUES (%(length)s, %(text)s, %(id)s)")
			mycursor.execute(update_text, values)
			mydb.commit()
			print("Text updated.")


driver = webdriver.Chrome()
driver.set_page_load_timeout(60)

driver.get("https://latin.packhum.org/browse")
print("Connected to site")
checkbox = driver.find_element(By.CSS_SELECTOR, value='#showall')
checkbox.click()
texts = []
authorElements = driver.find_elements(By.CSS_SELECTOR, value='.authors li a')
for item in authorElements:
	name = item.find_element(By.CSS_SELECTOR, value='span b').text
	fullname = item.find_element(By.CSS_SELECTOR, value='span').text
	# DBaddAuthor(name, fullname)
author_links = [x.get_attribute("href") for x in authorElements]
for author in author_links:
	driver.get(author)
	time.sleep(2)
	textElements = driver.find_elements(By.CSS_SELECTOR, value='li.work a')
	textlist = [x.get_attribute("href") for x in textElements]
	text_count = 0
	for text in textlist:
		textdata = {
			"title": "",
			"date": "",
			"length": 0,
			"genre": "",
			"fulltext": "",
			"author": "",
		}
		driver.get(text)
		textdata["author"] = driver.find_element(By.ID, value='author').text
		textdata["title"] = driver.find_element(By.ID, value='work').text
		tablecells = driver.find_elements(by=By.TAG_NAME, value='td')
		# TODO click next button until full text is gathered
		textdata["fulltext"] = " ".join(cell.text for cell in tablecells)
		textdata["length"] = len(textdata["fulltext"].split(" "))
		texts.append(textdata)
		DBaddText(textdata)
