defolddocset
============

This Python script will download the reference documentation for the latest stable release of Defold and generate a docset for import to the [Dash API Documentation Browser](http://kapeli.com/dash).

requirements
------------
* Python 2.7

usage
-----
Run `./createdocset.py` from a terminal. This will create a complete defold.docset filestructure. If you have Dash installed it should be enough to double-click the defold.docset folder to import it to Dash.

todo
----
The script currently does not make any distinction between functions, messages and constants. All of the entries will be marked as functions in Dash.
