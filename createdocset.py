#!/usr/bin/env python
import os
import re
import sqlite3
import shutil
import urllib
import urllib2
import json
import zipfile


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
ref_path = os.path.join(documents_path, "ref")


DOC_ZIP = "ref-doc.zip"
JSON_PATH = "json"

def get_defold_sha1():
	info_url = "http://d.defold.com/stable/info.json"
	info_file = urllib.urlopen(info_url)
	info = json.loads(info_file.read())
	info_file.close()
	return info["sha1"]

def get_ref_doc():
	sha1 = get_defold_sha1()
	if os.path.exists(DOC_ZIP):
		os.remove(DOC_ZIP)
	urllib.urlretrieve("http://d.defold.com/archive/" + sha1 + "/engine/share/ref-doc.zip", DOC_ZIP)

def cleanup():
	if os.path.exists(JSON_PATH):
		shutil.rmtree(JSON_PATH)
	if os.path.exists(DOC_ZIP):
		os.remove(DOC_ZIP)

def unzip_ref_doc():
	if os.path.exists(JSON_PATH):
		shutil.rmtree(JSON_PATH)

	with zipfile.ZipFile(DOC_ZIP) as zf:
		zf.extractall(JSON_PATH)


def create_docset():
	# create all paths
	if os.path.exists(ref_path):
		shutil.rmtree(ref_path)
	os.makedirs(ref_path)

	# create Info.plist
	with open(os.path.join(contents_path, "Info.plist"), "w") as file:
		file.write(INFO_PLIST)

	# copy icon
	shutil.copyfile("icon.png", os.path.join(docset_path, "icon.png"))

	# create sqlite db
	with sqlite3.connect(os.path.join(resources_path, "docSet.dsidx")) as db:
		cursor = db.cursor()

		try: cursor.execute('DROP TABLE searchIndex;')
		except: pass

		# create db table
		cursor.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
		# make sure duplicates are ignored
		#cursor.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

		index_html = ""
		for root, dir, files in os.walk(JSON_PATH):
			for file in files:
				with open(os.path.join(root, file), "r") as fh:
					if file.endswith(".json"):
						class_name = file.replace("_doc.json", "")
						class_path = class_name + ".html"
						class_doc = ""
						for element in json.load(fh)["elements"]:
							function_name = element["name"]
							function_path = class_path + "#" + function_name
							class_doc = class_doc + "<h1><a name='" + function_name + "'>" + function_name + "</a></h1>"
							class_doc = class_doc + "<p>" + element["brief"] + "</p>"
							if element["description"] != "":
								class_doc = class_doc + "<p>" + element["description"] + "</p>"
							if len(element["parameters"]) > 0:
								class_doc = class_doc + "<h3>PARAMETERS</h3>"
								for parameter in element["parameters"]:
									class_doc = class_doc + "<p>" + parameter["name"] + " - "  + parameter["doc"] + "</p>"
							if element["return_"] != "":
								class_doc = class_doc + "<h3>RETURN</h3>"
								class_doc = class_doc + "<p>" + element["return_"] + "</p>"
							if element["examples"] != "":
								class_doc = class_doc + "<h3>EXAMPLES</h3>"
								class_doc = class_doc + "<p>" + element["examples"] + "</p>"

							type = "Function"
							if element["type"] == "VARIABLE":
								type = "Variable"
							elif element["type"] == "MESSAGE":
								type = "Variable"
							cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (function_name, 'Function', "ref/" + function_path))

						index_html = index_html + "<a href='ref/" + class_path + "'>" + class_name + "</a></br>"
						with open(os.path.join(ref_path, class_path), "w") as out:
							out.write(class_doc)

						cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (class_name, 'Module', "ref/" + class_path))

		with open(os.path.join(documents_path, "index.html"), "w") as out:
			out.write(index_html)

get_ref_doc()
unzip_ref_doc()
create_docset()
cleanup()
