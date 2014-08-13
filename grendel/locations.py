import items, verbs, scripts, game

def Item(item): return items.Get(item)
def Verb(verb): return verbs.Get(verb)
def Game(): return game.Settings()

objects = []
directory = []

class InitLocation(object):
	def __init__(self, sDesc, lDesc = None):
		self.name = sDesc # Should never change after creation
		self.description = {"short": sDesc, "long": lDesc, "smell": None, "sound": None, "enter": None, "exit": None, "firstenter": None}
		self.connections = {}
		self.blockedconnections = {}
		self.contents = []
		self.lit = True
		self.flags = {}
	def Flag(self, id, value = None):
		if value is not None:
			self.flags.update({id: value})
		else:
			try:
				return self.flags[id]
			except:
				return None
	def Decoration(self, name, longdesc, aliases = None, adjective = None):
		if aliases:
			if type(aliases) is str:
				aliases = [name, aliases]
			else:
				aliases.append(name)
		else:
			aliases = name
		name = self.name+"_"+name
		items.New(name, aliases, adjective)
		items.Get(name).Location(self.name)
		items.Get(name).isSilent = True
		items.Get(name).Description("long", longdesc)
	def Description(self, type, description = None):
		if description is not None:
			self.description[type] = description
		else:
			return self.description[type]
	def BlockConnection(self, direction, message):
		self.blockedconnections[direction[0]] = message
	def UnblockConnection(self, direction):
		try:
			del self.blockedconnections[direction[0]]
		except:
			pass
	def SetConnection(self, direction, connection):
		self.connections[direction[0]] = connection
	def RemoveConnection(self, direction):
		try:
			del self.connections[direction]
		except:
			pass
	def Describe(self):
		output = "<br/><medium>" + str(self.description["short"]) + "</medium>\n\n"
		if self.description["long"]:
			output += self.description["long"]
		if game.Settings().showexits is True:
			output += "Exits are"
			list = ""
			for i in self.connections.keys():
				list += " " + i + ","
			output += scripts.Listify(list)
			output += "."
		if len(self.contents) > 1:
			initialoutput = []
			noinitialoutput = []
			for i in self.contents:
				if items.Get(i).description["initial"] is not None and items.Get(i).isSilent is False:
					initialoutput.append(items.Get(i).Description("initial"))
				elif items.Get(i).name != "me" and items.Get(i).isSilent is False:
					noinitialoutput.append(items.Get(i).name)
			if initialoutput:
				for i in initialoutput:
					if i != "me":
						output += "\n" + i
			if noinitialoutput:
				output += "\n\nHere, you find "
				itemlist = ""
				for i in noinitialoutput:
					itemlist += " " + items.Get(i).Grammar("a") + " "
					# if items.Get(i).Adjective() is not None:
						# itemlist += items.Get(i).Adjective() + " "
					itemlist += items.Get(i).Description("short") + ", "
				output += scripts.Listify(itemlist)
#					output += "\n\t"+items.Get(i).Grammar("a").capitalize()+ " "+i
		output += "\n\n"
		return output

def New(name, aliases = None):
	# print "Created location \""+name+"\""
	directory.append(name.lower())
	objects.append(InitLocation(name))
	if aliases is not None:
		output = ""
		for i in aliases:
			output += i+" "
			directory.append(i.lower())
			objects.append(name.lower())
		# print "Alises for "+name+": \""+output+"\""

def Get(word):
	word = word.lower()
	# Usage: location locations location location locationdirectory locations location. Seriously, I need to think of more distinguishing variable names.
	try:
		if type(objects[directory.index(word)]) is str:
			return objects(objects[directory.index(word)]) # Wow, that's a painful-looking line of code
		else:
			try: return objects[directory.index(word)]
			except: return None
	except:
		try: return objects[directory.index(word)]
		except: return None

