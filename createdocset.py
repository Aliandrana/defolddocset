#!/usr/bin/env python
import os
import re
import sqlite3
import shutil
import urllib
import urllib2
from bs4 import BeautifulSoup, NavigableString, Tag


INFO_PLIST = """<!DOCTYPE plist SYSTEM "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
<key>CFBundleIdentifier</key>
<string>defold</string>
<key>CFBundleName</key>
<string>Defold</string>
<key>DocSetPlatformFamily</key>
<string>defold</string>
<key>isDashDocset</key>
<true/>
<key>dashIndexFilePath</key>
<string>index.html</string>
</dict>
</plist>
"""



# path definitions
docset_path = "defold.docset"
contents_path = os.path.join(docset_path, "Contents")
resources_path = os.path.join(contents_path, "Resources")
documents_path = os.path.join(resources_path, "Documents")
index_path = os.path.join(documents_path, "index.html")
ref_path = os.path.join(documents_path, "ref")
db_path = os.path.join(resources_path, "docSet.dsidx")


def parse_ref(url, local_path, db_cursor):
	print("  Parsing " + local_path)
	urllib.urlretrieve(url, local_path)
	soup = BeautifulSoup(open(local_path).read())

	# remove stuff we don't want
	for div in soup.findAll('div', 'navbar'):
		div.extract()
	for div in soup.findAll('div', 'span3'):
		div.extract()
	for footer in soup.findAll('footer'):
		footer.extract()

	for link in soup.find_all('a'):
		href = str(link.get("href"))
		if "#" in href:
			function_name = href.split('#')[1]
			if "." in function_name:
				function_name = function_name.split(".")[1]
			path = local_path.replace(documents_path + "/", "") + href
			db_cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (function_name, 'Function', path))
			print("    Adding documentation for " + function_name)

	# update file with the changes made (removed divs etc)
	with open(local_path, "wb") as file:
		file.write(soup.prettify("utf-8"))


# create all paths
if os.path.exists(ref_path):
	shutil.rmtree(ref_path)
os.makedirs(ref_path)

# create Info.plist
with open(os.path.join(contents_path, "Info.plist"), "w") as file:
	file.write(INFO_PLIST)

# copy icon
shutil.copyfile("icon.tiff", os.path.join(docset_path, "icon.tiff"))

# create sqlite db
with sqlite3.connect(db_path) as db:
	cursor = db.cursor()

	try: cursor.execute('DROP TABLE searchIndex;')
	except: pass
	# create db table
	cursor.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
	# make sure duplicates are ignored
	#cursor.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

	# scrape doc.defold.com, download index page and all /ref pages
	urllib.urlretrieve("http://doc.defold.com", index_path)
	soup = BeautifulSoup(open(index_path).read())

	# remove stuff we don't want
	for div in soup.findAll('div', 'navbar'):
		div.extract()
	for div in soup.findAll('div', 'page-header'):
		div.extract()
	for div in soup.findAll('div', 'ue-tab-container'):
		div.extract()
	for div in soup.findAll('div', 'well-blue'):
		div.extract()
	for div in soup.findAll('div', 'well-orange'):
		div.extract()
	for footer in soup.findAll('footer'):
		footer.extract()

	#urllib.urlretrieve("http://doc.defold.com/", index_path)
	#soup = BeautifulSoup(open(index_path).read())
	for link in soup.find_all('a'):
		href = str(link.get("href"))
		if "/ref/" in href:
			class_name = href.split("/")[2]
			class_path = "." + href + ".html"
			print("Adding documentation for " + class_name + " from " + class_path)
			cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (class_name, 'Class', class_path))
			parse_ref("http://doc.defold.com" + href, documents_path + href + ".html", cursor)
			link["href"] = class_path

	# write updated index file
	with open(index_path, "wb") as file:
		file.write(soup.prettify("utf-8"))
