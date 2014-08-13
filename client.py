#	Client
#
#	A simple Grendel front-end

version = "1.6.5"

import sys, cPickle, gzip, os
from textwrap import wrap

def Main(storyfile):

	# Load in the game data
	import grendel
	grendel.game.softdata["storyfile"] = storyfile
	grendel.game.LoadGRN(grendel.game.softdata["storyfile"])
	grendel.game.Settings().Session("local")
	grendel.StartGame() # Finishes up

	while not ("<quit" in grendel.game.Settings().Response()): # Response should have been originally set by grendel/init
		ProcessOutput(grendel.game.Settings().Response())
		if debug:
			for i in grendel.game.Log():
				print i
			grendel.game.ClearLog()
		input = raw_input("> ")
		
		if input == "q" or input == "quit":
			grendel.game.Settings().Response("<quit>")
		else:
			grendel.Parse(input)
	print
	print "Thanks for playing "+grendel.game.Settings().Name()
	sys.exit()

def ProcessOutput(text):
	import msvcrt
	text = text.decode("utf-8")
	print
	text = text.replace("<b>", "").replace("</b>", "").replace("<medium>", "").replace("</medium>", "").replace("<big>", "").replace("</big>", "").replace("<center>", "\n").replace("</center>", "\n").split("\n")
	for i in text:
		if i:
			if i.find("<pause/>") is -1 and i.find("<clear/>") is -1:
				for j in wrap(i, 79):
					print j.replace("<br/>", "\n").replace("\n\n", "\n")
				print
			elif i.find("<pause/>") is not -1: # Pause
				split = i.partition("<pause/>")
				if split[0] is not "":
					for j in wrap(split[0], 79):
						print j.replace("<br/>", "\n")
					print
				print "(Press any key to continue...)"
				char = 0
				while not char:
					char = msvcrt.getch()
				if split[2]:
					ProcessOutput(split[2])
				else:
					print
			elif i.find("<clear/>") is not -1: # Clear the screen
				split = i.partition("<clear/>")
				if split[0] is not "":
					ProcessOutput(split[0])
				print " --- "
				print
				if split[2]:
					ProcessOutput(split[2])

print
print "Grendel client"
print "Version " + str(version)
print

try:
	storyfile = sys.argv[1]
except:
	print "Usage:\n\tpython client.py storyname [/debug]"
	print
	sys.exit()

if "/debug" in sys.argv:
	debug = True
	print "(Debug mode)"
else:
	debug = False
	
Main(storyfile)