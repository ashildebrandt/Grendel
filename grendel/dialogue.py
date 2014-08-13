from xml.dom.minidom import *
import xml.parsers.expat as expat
import game, scripts, os

dialogue = {}
id = 0
xmldoc = None

def GetData(elem):
	import re
	data = elem.toxml().replace("&quot;", "\"").replace("\\\"", "\"").strip().replace("\t", "")
	data = re.compile(r'<'+elem.tagName+'.*?>').sub('', data)
	data = re.compile(r'</'+elem.tagName+'.*?>').sub('', data)
	return data

def ProcessOptions(tree, thisid = None, parent = ""):
	global id
	go = None
	speak = True
	if tree.tagName == "conversation":
		thisid = tree.attributes["name"].value
		parent = tree.attributes["name"].value
	options = []
	for i in tree.childNodes:
		try: 
			if i.tagName == "text":
				text = GetData(i)
			elif i.tagName == "option":
				try:
					options.append({i.attributes["text"].value: i.attributes["to"].value})
				except:
					try:
						child = i.attributes["name"].value
					except:
						id += 1
						child = "id"+str(id)
					options.append({i.attributes["text"].value: child})
					ProcessOptions(i, child, thisid)
			elif i.tagName == "go":
				try: go = i.attributes["to"].value
				except: raise
			elif i.tagName == "return":
				go = parent
			# if i.tagName in ["go", "return"]:
				# try: 
					# speak = i.attributes["speak"].value
					# if i.attributes["speak"].value.lower() == "false":
						# speak = False
				# except: pass
		except: pass
	dialogue[thisid] = {'id': thisid, 'parent': parent, 'text': text, 'options': options, 'go': go, 'speak': speak}

def Talk(key = None):
	continuecapture = False
	output = ""
	if key is None:
		try:
			oldkey = game.Settings().Current("input").lower().split(" ")[1]
			choice = game.Settings().Current("input").lower().split(" ")[2]
			result = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7, 'i':8, 'j':9}[choice]
			key = dialogue[oldkey]["options"][result].values()[0]
		except KeyError:
			output += "\nThat was an invalid option."
			key = oldkey
		except IndexError:
			output += "\nThat was an invalid option."
			key = oldkey
	try:
		output += "\n" + dialogue[key]["text"]
		if dialogue[key]["go"]:
			# if dialogue[key]["speak"]:
				# output += "\n" + dialogue[key]["text"]
			key = dialogue[key]["go"]
	except:
		raise
	if dialogue[key]["options"]:
		continuecapture = True
		output += "\n(Chose an option:)\n"
		keycount = 0
		alpha = "abcdefghij"
	for i in dialogue[key]["options"]:
		output += "     " + alpha[keycount] + ") " + i.keys()[0] + "\n"
		keycount += 1
	# output = output.encode("utf-8")
	if continuecapture:
		return scripts.Capture(output, "sys_talk " + key + " %input%")
	else:
		return output

def Init():
	try:
		xmldoc = parse(game.softdata["gamepath"] + game.softdata["storypath"] + "/" + game.softdata["storyfile"]+".dialogue.xml") # parse an XML file by name
		for i in xmldoc.getElementsByTagName('conversation'):
			if i.tagName == "conversation":
				ProcessOptions(i)
		xmldoc.unlink()
	except expat.ExpatError:
		print "\n'dialogue.xml' contains an XML formatting error\n"
		raise
	except IOError:
		game.Log("Failed to read file '"+game.softdata["gamepath"] + game.softdata["storyfile"]+".dialogue.xml'. Disregard this if you don't need it.")
	except:
		print "\nSomething went wrong:\n"
		raise
