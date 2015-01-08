defolddocset
============

This Python script will scrape http://doc.defold.com and generate a docset for import to the [Dash API Documentation Browser](http://kapeli.com/dash).

requirements
------------
* Python 2.7
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)

usage
-----
Run `./createdocset.py` from a terminal. This will create a complete defold.docset filestructure. If you have Dash installed it should be enough to double-click the defold.docset folder to import it to Dash.
