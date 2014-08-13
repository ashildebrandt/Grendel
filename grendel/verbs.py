#	Verbs
#
#	Handles the creation of verbs.objects and sets up a couple generic verbs.objects common to most stories.

import items, locations, scripts, game

def Item(item): return items.Get(item)
def Location(location): return locations.Get(location)
def Game(): return game.Settings()

objects = []
directory = []

class InitVerb(object):
	def __init__(self, name, default, clarify = None, idclarify = None):
		self.name = name
		self.clarify = clarify
		self.idclarify = idclarify
		self.defaultResponse = default
		self.locationresponses = dict()
	def DefaultResponse(self):
		try:
			return self.locationresponses[items.Get("me").Location()]
		except:
			return self.defaultResponse
	def SetLocationAction(self, location, response):
		self.locationresponses[location] = response
	def RemoveLocationAction(self, location):
		del self.locationresponse[location]
	def Clarify(self):
		if self.clarify is None:
			return None
		else:
			return scripts.Capture(self.clarify, self.name+" %input%")
	def ClarifyIndirect(self, object):
		if self.idclarify is None:
			return None
		else:
			return scripts.Capture(self.idclarify, (self.name+" "+object+" to "+" %input%"))

def New(name, default = None, clarify = None, idclarify = None):
	if type(name) is str:
		directory.append(name)
		objects.append(InitVerb(name, default, clarify, idclarify))
	else:
		directory.append(name[0])
		objects.append(InitVerb(name[0], default, clarify, idclarify))
		output = ""
		for i in name:
			if i != name[0]:
				output += i+" "
				directory.append(i.lower())
				objects.append(name[0].lower())

def Get(word):
	word = word.lower()
	# Usage: object objects object object objectdirectory objects object. Seriously, I need to think of more distinguishing variable names.
	try:
		try:
			if type(objects[directory.index(word)]) is str:
				return Get(objects[directory.index(word)]) # Wow, that's a painful-looking line of code
			else:
				try: return objects[directory.index(word)]
				except: return None
		except:
			try: return objects[directory.index(word)]
			except: return None
	except:
		game.Log("Verb '"+word+"' does not exist.")