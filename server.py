#!/usr/bin/python

#	Server
#
#	A simple Grendel server

print "content-type: text/plain"
print

import cgitb, cgi, sys
cgitb.enable()
# cgitb.enable(display=0, logdir="/tmp")

def Main():
	import os, grendel
	pathinfo = os.environ.get('PATH_INFO')
	form = cgi.FieldStorage()
	if not pathinfo:
		print "<p>Python version " + sys.version.replace(" \n", " / ") + "</p>"
		print "<p>Nothing to do</p>"
		print str(grendel.game.softdata).replace("{", "<p>").replace(", ", ",<br/>").replace("}", "</p>")
	elif "/NewSession" in pathinfo:
		if "storyfile" in form:
			storyfile = form.getvalue("storyfile")
			grendel.game.softdata["storyfile"] = storyfile
			grendel.game.LoadGRN(grendel.game.softdata["storyfile"])
			grendel.game.Settings().Session(BuildSession()) # Creates and loads a new session ID
			grendel.StartGame()
			print grendel.game.Settings().Session() + "\n" # Returns the session ID to the client
			ProcessOutput(grendel.game.Settings().Response())
			grendel.game.SaveSession()
		else:
			print "Error: No storyfile"
	elif "/Submit" in pathinfo:
		if not ("input" in form and "session" in form and "storyfile" in form):
			if not "input" in form:
				print "Excuse me?"
			elif not "session" in form:
				print "Error: No session"
			elif not "storyfile" in form:
				print "Error: No storyfile"
		else:
			storyfile = form.getvalue("storyfile")
			session = form.getvalue("session")
			input = form.getvalue("input")
			grendel.game.softdata["storyfile"] = storyfile
			grendel.game.game = grendel.game.InitGame()
			grendel.game.LoadGRN(grendel.game.softdata["storyfile"])
			grendel.StartGame()
			grendel.game.Settings().Session(session)
			grendel.Parse(input)
			if "html" in form:
				ProcessOutput(grendel.game.Settings().Response(), True)
			else:
				ProcessOutput(grendel.game.Settings().Response())
			grendel.game.SaveSession()
	else:
		print "Invalid call"

def BuildSession():
	import md5, time, base64, random
	m = md5.new()
	m.update(str(time.time())) # Timestamped!
	m.update(str(random.randint(0, 10000000))) # Randomed!
	return base64.encodestring(m.digest()).replace("==", "").replace("\n", "").replace("\\", "0").replace("/", "0").replace("+", "0")

def ProcessOutput(text, html = False):
	if html:
		text = text.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;").replace("<center>", "<p class='center'>").replace("</center>", "</p>").replace("<br>", "<br/>").replace("<big>", "<span class='big'>").replace("</big>", "</span>").replace("<medium>", "<span class='medium'>").replace("</medium>", "</span>").split("\n")
		for i in text:
			if i is not "":
				print "\t\t\t<p>"+i+"</p>\n"
	else:
		for i in text.split("\n"):
			if i is not "":
				print i+"\n"

Main()