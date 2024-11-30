import time

import mysql.connector as SQL
from _mysql_connector import MySQLInterfaceError
from mysql.connector import DatabaseError
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

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


def DBaddText(text):
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
	if not findText:
		#If text does not already exist in db
		print("Adding text: {} by {}".format(text['title'], text['author']))
		add_text = ("INSERT INTO texts "
					"(title, textLength, textString, authorID) "
					"VALUES (%(title)s, %(length)s, %(text)s, %(author)s)")
		mycursor.execute(add_text, values)
		mydb.commit()
		print("Text added.")
	else:
		textID = findText[0][0]
		check_length = "SELECT textLength FROM texts WHERE textID=%s"
		mycursor.execute(check_length, (textID,))
		current_length = mycursor.fetchall()
		if current_length[0][0] != text['length']:
			# if text is not complete
			update_text = 'UPDATE texts SET textLength=%s, textString=%s WHERE textID = %s'
			values = (text['length'], text['fulltext'], textID)
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
			"authorID": 0
		}
		driver.get(text)
		textdata["author"] = driver.find_element(By.ID, value='author').text
		textdata["title"] = driver.find_element(By.ID, value='work').text
		textdata["authorID"] = DBgetAuthor(textdata["author"])[0]
		findText = textExists(textdata)
		if findText:
			sql = "SELECT textLength FROM texts WHERE textID = %s"
			val = (findText[0][0],)
			mycursor.execute(sql, val)
			length = mycursor.fetchall()[0][0]
			if length > 1000:
				continue

		count = 0
		text = []
		while True:
			count += 1
			tableCells = driver.find_elements(by=By.TAG_NAME, value='td')
			try:
				text += list([cell.text for cell in tableCells])
			except StaleElementReferenceException:
				print(driver.current_url)
				print(textdata)
				continue
			# click next button until full text is gathered
			next_button = driver.find_element(By.ID, value="next")
			if next_button.get_attribute("href") == "":
				break
			before_click = driver.current_url
			next_button.click()
			time.sleep(2)
			if before_click == driver.current_url:
				print('Reached end of {} after {} pages'.format(textdata['title'], count))
				break

		textdata["fulltext"] = " ".join(text)
		textdata["length"] = len(textdata["fulltext"].split(" "))
		texts.append(textdata)
		try:
			DBaddText(textdata)
		except (MySQLInterfaceError, DatabaseError) as e:
			continue

