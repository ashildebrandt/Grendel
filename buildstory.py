#	Build Story
#
#	An XML -> GRN (Grendel's native file format) compiler

version = .1

import sys, gzip, os, cPickle
from textwrap import wrap
from xml.dom.minidom import *
import grendel

output = ""

def Main(storyfile):
	try: 
		xmldoc = parse("stories/"+storyfile+".story.xml") # parse an XML file by name
		Collect("\n###################################\n#\tImports\n")
		Collect("def Item(item):\n\treturn grendel.items.Get(item)")
		Collect("def Verb(verb):\n\treturn grendel.verbs.Get(verb)")
		Collect("def Location(location):\n\treturn grendel.locations.Get(location)")
		storyscripts = ProcessScripts(xmldoc.getElementsByTagName('scripts'))
		ProcessGame(xmldoc.getElementsByTagName('game'))
		ProcessLocations(xmldoc.getElementsByTagName('location'))
		ProcessItems(xmldoc.getElementsByTagName('item'))
		xmldoc.unlink()
	except xml.parsers.expat.ExpatError:
		print "\n'"+storyfile+".story.xml' contains an XML formatting error\n"
		raise
	except IOError:
		print "\nFailed to read file '"+storyfile+".story.xml'\n"
		raise
	except:
		print "\nSomething went wrong:\n"
		raise
	try:
		if "/nodefaults" in sys.argv:
			print "Compiling story (without default verbs and objects -- this is currently NOT IMPLEMENTED)...",
		else:
			print "Compiling story...",
		from grendel import defaults
		exec output in globals()
		print "done processing '" + grendel.game.Settings().name + "'"
		if "/debug" in sys.argv:
			print "Debug > Writing Python intermediate to '"+storyfile+".debug-*.py'...",
			try:
				file = open(os.getcwd()+"/stories/"+storyfile+".debug-story.py", 'w')
				file.write(output)
				file.close
				file = open(os.getcwd()+"/stories/"+storyfile+".debug-scripts.py", 'w')
				file.write(storyscripts)
				file.close
				print "done"
			except:
				print "oops. Something went wrong."
				raise
		print "Pickling results...",
		try:
			pickles = {
				'game': grendel.game.game,
				'items_objects': grendel.items.objects,
				'items_directory': grendel.items.directory,
				'verbs_objects': grendel.verbs.objects,
				'verbs_directory': grendel.verbs.directory,
				'locations_objects': grendel.locations.objects,
				'locations_directory': grendel.locations.directory,
				'storyscripts': storyscripts
			}
			jar = gzip.open(os.getcwd()+"/stories/"+storyfile+".grn", 'wb')
			cPickle.dump(pickles, jar, 2)
			jar.close()
		except:
			print "Failed to properly pickle:"
			raise
		print "saved as '" + storyfile + ".grn'"
		print
		print "If your story includes dialogue trees, remember to include "+storyfile+".dialogue.xml"
	except:
		raise

def Collect(string):
	global output
	# output += str(string) + "\n"
	output += string + "\n"

def GetData(elem):
	import re
	data = elem.toxml().replace("&quot;", "\"").replace("\"", "\\\"").strip().replace("\t", "").replace("\n", "\\n").replace(" \\n", "\\n")
	data = re.compile(r'<'+elem.tagName+'.*?>').sub('', data)
	return re.compile(r'</'+elem.tagName+'.*?>').sub('', data)
	# Old method follows: fails to strip tags when they have arguments
	# return elem.toxml().replace("<"+elem.tagName+">", "").replace("</"+elem.tagName+">", "").replace("&quot;", "\"").replace("\"", "\\\"").strip().replace("\t", "").replace("\n", "\\n").replace(" \\n", "\\n")

def ProcessGame(game):
	Collect("\n###################################\n#\tGame settings\n")
	for i in game:
		for j in i.childNodes:
			if j.nodeType == j.ELEMENT_NODE:
				if j.tagName == "intro": tag = "Intro"
				if j.tagName == "name": tag = "Name"
				if j.tagName == "author": tag = "Author"
				if j.tagName == "maxpoints": tag = "MaxPoints"
				if j.tagName == "startroom": tag = "StartRoom"
				try: Collect("grendel.game.Settings()." + tag + "(\"" + GetData(j) + "\")")
				except: pass
	
def ProcessLocations(locations):
	Collect("\n###################################\n#\tLocations")
	for i in locations:
		Collect("\n# Location (" + i.attributes["name"].value + ")")
		Collect("grendel.locations.New(\"" + i.attributes["name"].value + "\")")
		for j in i.childNodes:
			if j.nodeType == j.ELEMENT_NODE:
				if j.tagName == "desc":
					for k in j.childNodes:
						if k.nodeType == k.ELEMENT_NODE:
							Collect("Location(\"" + i.attributes["name"].value + "\").Description(\"" + k.tagName + "\", \"" + GetData(k) + "\")")
				if j.tagName == "connections":
					for k in j.childNodes:
						if k.nodeType == k.ELEMENT_NODE:
							Collect("Location(\"" + i.attributes["name"].value + "\").SetConnection(\"" + k.tagName + "\", \"" + GetData(k) + "\")")
				if j.tagName == "block":
					for k in j.childNodes:
						if k.nodeType == k.ELEMENT_NODE:
							Collect("Location(\"" + i.attributes["name"].value + "\").BlockConnection(\"" + k.tagName + "\", \"" + GetData(k) + "\")")
				if j.tagName == "actions":
					for k in j.childNodes:
						if k.nodeType == k.ELEMENT_NODE:
							Collect("Verb(\"" + k.tagName + "\").SetLocationAction(\"" + i.attributes["name"].value + "\", \"" + GetData(k) + "\")")
							try: # Untested
								for l in k.attributes["alt"].value.encode('ascii').split(", "):
									Collect("Verb(\"" + l + "\").SetLocationAction(\"" + i.attributes["name"].value + "\", \"" + GetData(k) + "\")")
							except:
								pass
				if j.tagName == "decoration":
					name = i.attributes["name"].value + "_" + j.attributes["name"].value
					Collect("\n# Decoration (" + name + ")")
					output = "grendel.items.New(\"" + name + "\""
					try:	output += ", [\""+j.attributes["name"].value+"\", \"" + j.attributes["alt"].value.replace(", ", "\", \"") + "\"]"
					except: output += ", \""+j.attributes["name"].value+"\""
					try:	output += ", \"" + j.attributes["adj"].value + "\""
					except: pass
					Collect(output + ")")
					Collect("Item(\"" + name + "\").isSilent = True")
					Collect("Item(\"" + name + "\").Description(\"short\", \"" + j.attributes["name"].value + "\")")
					Collect("Item(\"" + name + "\").Location(\"" + i.attributes["name"].value + "\")")
					for k in j.childNodes:
						if k.nodeType == k.ELEMENT_NODE:
							Collect("Item(\"" + name + "\").Description(\"" + k.tagName + "\", \"" + GetData(k) + "\")")

def ProcessItems(items):
	Collect("\n###################################\n#\tItems")
	for i in items:
		name = i.attributes["name"].value
		Collect("\n# Item (" + name + ")")
		
		output = "grendel.items.New(\"" + name + "\""
		try:	output += ", " + str(i.attributes["alt"].value.encode('ascii').split(", "))
		except: pass
		try:	output += ", \"" + i.attributes["adj"].value + "\""
		except: pass
		Collect(output + ")")

		try:	Collect("Item(\"" + name + "\").Location(\"" + i.attributes["location"].value + "\")")
		except: pass
		
		for j in i.attributes.keys():
			if j != "location" and j != "name" and j != "alt" and j != "adj":
				value = i.attributes[j].value.encode('ascii')
				if j != "grammar":
					value = value.capitalize()
				try:
					if value in ["True", "False"]:
						Collect("Item(\"" + name + "\")." + j + " = " + value)
					else:
						Collect("Item(\"" + name + "\")." + j + " = \"" + value + "\"")
				except: pass
		
		for j in i.childNodes:
			if j.nodeType == j.ELEMENT_NODE:
				if j.tagName == "desc":
					for k in j.childNodes:
						if k.nodeType == k.ELEMENT_NODE:
							Collect("Item(\"" + name + "\").Description(\"" + k.tagName + "\", \"" + GetData(k) + "\")")
				if j.tagName == "actions":
					for k in j.childNodes:
						if k.nodeType == k.ELEMENT_NODE:
							try: 
								Collect("Item(\"" + name + "\").SetAction(\"" + k.tagName + "\", \"" + GetData(k) + "\", \""+k.attributes["with"].value+"\")")
							except: Collect("Item(\"" + name + "\").SetAction(\"" + k.tagName + "\", \"" + GetData(k) + "\")")
							try:
								for l in k.attributes["alt"].value.encode('ascii').split(", "):
									try: 
										Collect("Item(\"" + name+ "\").SetAction(\"" + l + "\", \"" + GetData(k) + "\", \""+k.attributes["with"].value+"\")")
									except: Collect("Item(\"" + name + "\").SetAction(\"" + l + "\", \"" + GetData(k) + "\")")
							except:
								pass

def ProcessScripts(scripts):
	storyscripts = "\n###################################\n#\tGame logic"
	# Collect("\n###################################\n#\tGame logic")
	storyscripts = "\nclass StoryScripts:"
	# Collect("\nclass StoryScripts:") # THIS WILL FAIL if there aren't any scripts
	for i in scripts.item(0).childNodes:
		if i.nodeType == i.CDATA_SECTION_NODE:
			scripts = i.data
			tabcount = 0
			search = "\n"
			if scripts[0] == "\n":
				while 1:
					if scripts[tabcount + 1] != "\t": break
					else: 
						tabcount += 1
						search += "\t"
			storyscripts += scripts.replace(search, "\n\t")
			# Collect(scripts.replace(search, "\n\t"))
	while True:
		if storyscripts[-1] == "\n" or storyscripts[-1] == "\t":
			 storyscripts = storyscripts[:-1]
		else:
			break
	return storyscripts

print
print "Grendel story compiler"
print "Version " + str(version)
print

try:
	if sys.argv[1]:
		pass
except:
	print "Usage:\n\tpython buildstory.py storyname"
	print
	sys.exit()

Main(sys.argv[1])