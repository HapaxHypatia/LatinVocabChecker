import time
import mysql.connector as SQL
from _mysql_connector import MySQLInterfaceError
from mysql.connector import DatabaseError
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from DB import *
import re
from setup import normalize_text

# TODO update DB calls to new functions


if __name__ == "__main__":
	mydb = SQL.connect(
		host="localhost",
		user="root",
		password="admin",
		database="corpus"
	)

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
			# TODO fix calls to database functions, including returning named properties from them.
			# findText = textExists(textdata)
			# if findText:
			# 	length = getTextByID(findText[0])[5]
			# 	if length > 1000:
			# 		continue

			text = ""
			page_count = 1
			while True:
				# Add reference to array
				# Add text segments to array
				# Click next button
				tableRows = driver.find_elements(by=By.TAG_NAME, value='tr')
				for r in tableRows:
					cells = r.find_elements(by=By.TAG_NAME, value='td')
					textstring = cells[0].text
					number = cells[1].text

					# Add text segments to array
					try:
						if number:
							# Add line numbers before line. If mid-sentence, move to start.
							textSegments = re.split(r"((?:\.\s?){1,3}|(?:\?)|(?:;):|(?:-\s?){1,3})", textstring)
							if textSegments[-1] == "":
								textSegments = textSegments[:-1]
							segs = len(textSegments)
							match segs:
								case 1:
									text += f" {number} {textSegments[0]}"
								case 2:
									text += f" {number} {textSegments[0]}{textSegments[1]}"
								case 3:
									text += f" {textSegments[0]}{textSegments[1]} {number} {textSegments[2]}"
								case 4:
									text += f" {textSegments[0]}{textSegments[1]} {number} {textSegments[2]} {textSegments[3]}"

						else:
							text += textstring + " "
					except StaleElementReferenceException:
						print(driver.current_url)
						print(textdata)
						continue
				next_button = driver.find_element(By.ID, value="next")
				if next_button.get_attribute("href") == "":
					break
				before_click = driver.current_url
				next_button.click()
				page_count += 1
				time.sleep(2)
				if before_click == driver.current_url:
					print('Reached end of {} after {} pages'.format(textdata['title'], page_count))
					break

			textdata["length"] = len(textdata["fulltext"])
			textdata["fulltext"] = " ".join(text)
			textdata["fulltext"] = normalize_text(text)
			texts.append(textdata)
			try:
				DBaddText(textdata)
			except (MySQLInterfaceError, DatabaseError) as e:
				continue

