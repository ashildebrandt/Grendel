#	Items
#
#	Handles object creation and sets up default verbs and scripts to interact with them. Also creates the default player.

import locations, verbs, scripts, game
def Location(location): return locations.Get(location)
def Verb(verb): return verbs.Get(verb)
def Game(): return game.Settings()

ignoreautotake = ["look", "get", "touch"]

objects = []
directory = []
adjectives = []

class InitObject(object):
	def __init__(self, sDesc, adjective):
		self.name = sDesc # Should never change after creation
		self.description = {"short": sDesc, "long": None, "smell": None, "sound": None, "touch": None, "initial": None, "follow": None}
		self.adjective = adjective
		self.isSilent = False
		self.canTake = False
		self.canDrop = True
		self.canOpen = True
		self.canClose = True
		self.isContainer = False
		self.followPlayer = False
		self.nounType = "singular" # Can be "singular", "plural", "proper", or "collective"
		self.gender = None
		self.announceContents = True
		self.isSurface = False
		self.isOpen = True
		self.autoTake = True
		self.location = ""
		self.contents = []
		self.verbs = []
		self.actions = []
		self.idobjects = []
		self.flags = {}
	def Grammar(self, type):
		if type == "a":
			if self.nounType == "singular":
				if self.Description("short")[0] in ["a", "e", "i", "o", "u"]:
					return "an"
				else:
					return "a"
			else:
				return ""
		if type == "the":
			return "the" if self.nounType in ["singular", "plural", "collective"] else ""
		if type == "it":
			return "them" if self.nounType in ["plural"] else "it"
	def Flag(self, id, value = None):
		if value is not None:
			self.flags.update({id: value})
		else:
			try:
				return self.flags[id]
			except:
				return None
	def Description(self, type, description = 0):
		if description is not 0:
			self.description[type] = description
		else:
			return self.description[type]
	def Location(self, location = None):
		if location is not None:
			success = 0
			try:
				del locations.Get(self.location).contents[locations.Get(self.location).contents.index(self.name)]
			except:
				pass
			try:
				del Get(self.location).contents[Get(self.location).contents.index(self.name)]
			except:
				pass
			try:
				locations.Get(location).contents.append(self.name)
				self.location = location
				success = 1
			except:
				pass
			try:
				if Get(location).isContainer or Get(location).isSurface:
					Get(location).contents.append(self.name)
					self.location = location
					success = 1
			except: 
				pass
			if self.name == "me" and location == "startroom":
				# Yeah, we'll just go ahead and ignore that
				success = 1
			if success == 0:
				game.Log("Can't move item '" + self.name + "', location '" + location + "' does not exist.")
			return self.location
		else:
			return self.location
	def SetAction(self, verb, action, idobject = None):
		if type(verb) is str:
			verb = [verb]
		if type(idobject) is str or idobject is None:
			idobject = [idobject]
		for i in verb:
			for j in idobject:
				try:
					if type(verbs.objects[verbs.directory.index(i)]) is str:
						i = verbs.objects[verbs.directory.index(i)]
				except:
					game.Log(self.name + " > Verb '" + i + "' does not exist -- it will be automatically created. Be warned, though, that it won't have a default response.")
					verbs.New(verb)
				try: # Delete the previous action, if set
					matches = Indices(self.verbs, i)
					foundmatch = False
					for k in matches:
						if self.idobjects[k] == j:
							foundmatch = k
					if foundmatch is not False:
						# Match found -- delete it
						del self.actions[foundmatch]
						del self.verbs[foundmatch]
						del self.idobjects[foundmatch]
				except:
					# No matches, we're in the clear
					pass
				self.verbs.append(i)
				self.actions.append(action)
				self.idobjects.append(j)
	def Adjective(self, adjective = None):
		if adjective is not None:
			self.adjective = adjective
		else:
			return self.adjective
	def RemoveAction(self, verb, idobject = None):
		if type(verbs.objects[verbs.directory.index(verb)]) is str:
			verb = verbs.objects[verbs.directory.index(verb)]
		try:
			matches = Indices(self.verbs, verb)
			foundmatch = False
			for i in matches:
				if self.idobjects[i] == idobject:
					foundmatch = i
			if foundmatch is not False:
				# Match found -- delete it
				del self.actions[foundmatch]
				del self.verbs[foundmatch]
				del self.idobjects[foundmatch]
			return True
		except:
			# No matches
			game.Log("Failed to remove action")
			return False
	def ResetAction(self, verb):
		if verb in ["drop", "look", "get", "smell", "listen", "touch", "open", "close"]:
			self.SetAction(verb, "{scripts." + verb.capitalize() + "(\""+self.name+"\")}")
		elif verb == "put":
			self.SetAction("put", "{scripts.Put(\""+name+"\", game.Settings().current['idobject'])}")
		else:
			return self.RemoveAction(verb)
	def Do(self, verb, idobject = None):
		if type(verbs.objects[verbs.directory.index(verb)]) is str:
			verb = verbs.objects[verbs.directory.index(verb)]
		if idobject is None and verbs.Get(verb).idclarify is not None:
			return verbs.Get(verb).ClarifyIndirect(self.name) # Clarify the verb if we don't have an indirect object
		try:
			if idobject is not None and scripts.PlayerHas("idobject"): # I don't remember what this was supposed to do.
				return verbs.Get(verb).DefaultResponse()
		except:
			pass
		try: # Find the action
			matches = Indices(self.verbs, verb)
			foundmatch = False
			foundnone = False
			using = ""
			take = ""
			for i in matches:
				if self.idobjects[i] == idobject:
					foundmatch = i
				if self.idobjects[i] is None:
					foundnone = i
			if foundmatch is not False:
				# Match found
				if idobject is not None:
					if scripts.PlayerHas(idobject, True):
						action = self.actions[foundmatch].replace("%idobject%", idobject)
					else:
						raise
				else:
					# Hmm, we don't have a match. Let's see if we have a match using the same verb and an item in the player's inventory
					for i in matches:
						if scripts.PlayerHas(self.idobjects[i]):
							# Ha, we do! Let's use it.
							idobject = self.idobjects[i]
							using = "(with " + Get(idobject).Grammar("the") + " " + Get(idobject).Description("short") + ")\n"
							action = self.actions[i].replace("%idobject%", idobject)
					if not using:
						action = self.actions[foundmatch]
			elif foundnone is not False:
				# No direct match, but we found a match without the indirect object. We'll push it to that.
				if idobject is not None:
					action = self.actions[foundnone].replace("%idobject%", idobject)
				else:
					action = self.actions[foundnone]
			else:
				raise
			take = ""
			if action and self.autoTake and self.Location() != "me" and self.canTake and not verb in ignoreautotake:
				take += "(first taking " + self.Grammar("the") + " " + self.Description("short") + ")\n" + scripts.Take(self.name) + "\n"
			if idobject:
				if action and Get(idobject).autoTake and Get(idobject).Location() is not "me" and Get(idobject).canTake and not verb in ignoreautotake:
					take += "(first taking " + Get(idobject).Grammar("the") + " " + Get(idobject).Description("short") + ")\n" + scripts.Take(Get(idobject).name) + "\n"
			return using + take + action
		except:
			# Opps, we don't seem to have that action set for this object
			return verbs.Get(verb).DefaultResponse()
			
def New(name, aliases = None, adjective = None):
	# print "Created object \""+name+"\""
	directory.append(name.lower())
	if adjective:
		adjectives.append(adjective.lower())
	else:
		adjectives.append(None)
	objects.append(InitObject(name, adjective))
	if aliases is not None:
		if type(aliases) is str:
			directory.append(aliases.lower())
			if adjective:
				adjectives.append(adjective.lower())
			else:
				adjectives.append(None)
			objects.append(name.lower())
		else:
			for i in aliases:
				directory.append(i.lower())
				if adjective:
					adjectives.append(adjective.lower())
				else:
					adjectives.append(None)
				objects.append(name.lower())
		# print "Alises for "+name+": \""+output+"\""
	# Default actions
	Get(name).SetAction("drop", "{scripts.Drop(\""+name+"\")}")
	Get(name).SetAction("look", "{scripts.Look(\""+name+"\")}")
	Get(name).SetAction("get", "{scripts.Take(\""+name+"\")}")
	Get(name).SetAction("smell", "{scripts.Smell(\""+name+"\")}")
	Get(name).SetAction("listen", "{scripts.Listen(\""+name+"\")}")
	Get(name).SetAction("touch", "{scripts.Touch(\""+name+"\")}")
	Get(name).SetAction("put", "{scripts.Put(\""+name+"\", game.Settings().current['idobject'])}")
	Get(name).SetAction("open", "{scripts.Open(\""+name+"\")}")
	Get(name).SetAction("close", "{scripts.Close(\""+name+"\")}")


def Get(word, adj = None):
	word = word.lower()
	try:
		try:
			matches = Indices(directory, word)
			nearmatches = []
			for i in matches:
				if type(objects[i]) is not str:
					return objects[i]
				else:
					nearmatches.append(Get(objects[i]))
			if adj: # Hmm, we don't have any direct hits. Let's check to see if there's an adjective.
				for i in nearmatches:
					if i.adjective is adj:
						return i
			return nearmatches[0] # There's no way of knowing what object this was supposed to be. I give up. Just take whatever.
		except:
			try: return objects[directory.index(word)]
			except: return None
	except:
		game.Log("Item '"+word+"' does not exist.")
		
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/54cf12c507cce7dc/f3c3fe42520e20f9#f3c3fe42520e20f9
def Indices(L,x):  return[i for i,y in enumerate(L) if x==y] 

def Disambig(objecttype):
	# Wow, this is an eyesore. This is invoked when the parser can't narrow down the object being referred to by the player to a single item.
	# Type can be "object" or "idobject"
	if objecttype == "object" or objecttype == "idobject":
		try:
			ambig = Indices(directory, game.Settings().current[objecttype])
			if len(ambig) > 1:
				# Hmm, we have conflicting indirect objects. Let's try to figure out which one's being referred to.
				possibilities = []
				for i in ambig: # Finds objects that are currently in the room
					if type(objects[i]) is str:
						if Get(objects[i]).Location() == Get("me").Location() or Get(objects[i]).Location() == "me": 
							possibilities.append({"id": i, "name": Get(objects[i]).name, "adjective": Get(objects[i]).Adjective()})
						elif Get(objects[i]).Location() in locations.Get(Get("me").Location()).contents:
							possibilities.append({"id": i, "name": Get(objects[i]).name, "adjective": Get(objects[i]).Adjective()})
					else:
						if objects[i].Location() == Get("me").Location() or objects[i].Location() == "me": # Rules out anything not in the room
							possibilities.append({"id": i, "name": objects[i].name, "adjective": objects[i].Adjective()})
						elif objects[i].Location() in locations.Get(Get("me").Location()).contents:
							possibilities.append({"id": i, "name": objects[i].name, "adjective": objects[i].Adjective()})
				if len(possibilities) == 0:
					return "You don't see that here." + daemonoutput
				# Okay, we have some possibilities. Let's see if any adjectives line up.
				for i in range(len(possibilities)):
					if str(game.Settings().current[objecttype+"adj"]) == possibilities[i]["adjective"]:
						game.Settings().current[objecttype] = possibilities[i]["name"]
						raise
				if len(possibilities) == 1:
					game.Settings().current[objecttype] = possibilities[0]["name"]
					raise
				else:
					captureprompt = "Which " + game.Settings().current[objecttype] + ": "
					if len(possibilities) == 2:
						captureprompt += possibilities[0]["adjective"] + " or " + possibilities[1]["adjective"] + "?"
					else:
						for i in range(len(possibilities)):
							if i < len(possibilities)-2:
								captureprompt += possibilities[i]["adjective"] + ", "
						captureprompt += possibilities[(len(possibilities)-2)]["adjective"] + " or " + possibilities[(len(possibilities)-1)]["adjective"] + "?"
					# We'll need to rebuild the input a bit to fit in the new adjective
					if objecttype == "object":
						captureprocess = game.Settings().current["verb"] + " %input% " + game.Settings().current["object"]
						if game.Settings().current["idobject"]:
							if game.Settings().current["idobjectadj"]:
								captureprocess += " " + game.Settings().current["idobjectadj"] + " " + game.Settings().current["idobject"]
							else:
								captureprocess += " " + game.Settings().current["idobject"]
						return scripts.Capture(captureprompt, captureprocess)
					if objecttype == "idobject":
						captureprocess = game.Settings().current["verb"]
						if game.Settings().current["objectadj"]:
							captureprocess += " " + game.Settings().current["objectadj"]
						captureprocess += " " + game.Settings().current["object"] + " to %input% " + game.Settings().current["idobject"]
						return scripts.Capture(captureprompt, captureprocess)
			else:
				# No more conflicts.
				return None
		except:
			return None
	else:
		game.Log("Incorrect object type: '" + type + "'")
		return None
