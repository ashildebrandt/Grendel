#	Scripts
#
#	This defines a lot of the default scripts needed by most games, such as movement, examination, and item interaction.
#	It also has some scripts for basic logical queries for inline code.

import verbs, items, locations, game

def Item(item): return items.Get(item)
def Location(location): return locations.Get(location)
def Verb(verb): return verbs.Get(verb)
def Game(): return game.Settings()

def SaveGame():
	if game.Settings().Current("object"):
		return SaveGameProcess()
	else:
		return Capture("What would you like to name your saved game (this will overwrite any saved game with the same name)?", "saveas %input%")
	
def RestoreGame():
	if game.Settings().Current("object"):
		return RestoreGameProcess()
	else:
		return Capture("What is the name of the saved game you would like to restore?", "restoreas %input%")

def SaveGameProcess():
	try:
		game.Save(game.Settings().Current("object"))
		return "Saved \"" + game.Settings().Current("object") + "\"."
	except:
		return "Failed to save \"" + game.Settings().Current("object") + "\". You might not have permission to create that file on this computer."
	
def RestoreGameProcess():
	try:
		game.Load(game.Settings().Current("object"))
		return "Restored \"" + game.Settings().Current("object") + "\".\n" + Look()
	except:
		return "Failed to restore \"" + game.Settings().Current("object") + "\". Perhaps the file does not exist?"

def FindIndex(search, words):
	# Checks to see if an array of words exists inside another array.
	for i in search:
		try:
			index = words.index(i)+1
		except:
			None
	try:
		return index
	except:
		return None		
	
def PlayerHas(item, extended = False): # Returns true if the player has the item in their inventory
	try: 
		if items.Get(item).Location() == "me":
			return True
		if extended is True:
			# We're allowed to look around the player to see if he can grab it.
			if items.Get(item).Location() == items.Get("me").Location():
				return True
			elif items.Get(items.Get(item).Location()).isContainer and items.Get(items.Get(item).Location()).isOpen:
				return True
			elif items.Get(items.Get(item).Location()).isSurface:
				return True
			else:
				return False
		else:
			raise
	except:
		return False

def EmptyInventory():
	for i in items.Get("me").contents:
		if i is not "all":
			items.Get(i).Location("null")

def ShowInventory():
	try:
		itemlist = []
		for i in items.Get("me").contents:
			if items.Get(i).name != "all":
				# if items.Get(i).Adjective() is not None:
					# itemlist.append(items.Get(i).Grammar("a") + " " + items.Get(i).Adjective() + " " + items.Get(i).description["short"])
				# else:
				itemlist.append(items.Get(i).Grammar("a") + " " + items.Get(i).description["short"])
		output = "You are carrying"
		for i in itemlist:
			output += " "+i+","
		if output == "You are carrying":
			output = "You are not carrying anything."
		else:
			output += "."
		if len(itemlist) > 2:
			output = (output[::-1].replace(",", "", 1).replace(",", "dna ,", 1))[::-1] # Ha, I'm brilliant.
		elif len(itemlist) == 2:
			output = (output[::-1].replace(",", "", 1).replace(",", "dna ", 1))[::-1]
		else:
			output = (output[::-1].replace(",", "", 1))[::-1]
		return output
	except:
		return "You aren't carrying anything."

def Go(direction = None):
	output = ""
	if direction is None and game.Settings().Current("object"):
		direction = game.Settings().Current("object")
		if direction == "enter":
			direction = "i"
		if direction == "exit":
			direction = "o"
		if direction in ["forward", "forwards"]:
			direction = "f"
		if direction in ["back", "backwards"]:
			direction = "b"
		direction = direction[0]
	elif direction is None and game.Settings().Current("verb") == "climb":
		direction = "u"
	elif direction is None:
		direction = "f"
	if direction in ["n", "s", "e", "w", "u", "d", "i", "o", "l", "r", "f", "b"]:
		if direction == "f":
			if game.Settings().Facing() in ["n", "u", "d"]:
				output += "\n(north)"
			elif game.Settings().Facing() == "s":
				output += "\n(south)"
			elif game.Settings().Facing() == "e":
				output += "\n(east)"
			elif game.Settings().Facing() == "w":
				output += "\n(west)"
			direction = game.Settings().Facing()
		if direction == "b":
			if game.Settings().Facing() == "n":
				direction = "s"
				output += "\n(south)"
			elif game.Settings().Facing() == "s":
				direction = "n"
				output += "\n(north)"
			elif game.Settings().Facing() == "e":
				direction = "w"
				output += "\n(west)"
			elif game.Settings().Facing() == "w":
				direction = "e"
				output += "\n(east)"
			elif game.Settings().Facing() == "u":
				direction = "d"
				output += "\n(down)"
			elif game.Settings().Facing() == "d":
				direction = "u"
				output += "\n(up)"
			elif game.Settings().Facing() == "i":
				direction = "o"
				output += "\n(outt)"
			elif game.Settings().Facing() == "o":
				direction = "i"
				output += "\n(in)"
			else:
				direction = "s"
				output += "\n(south)"
		if direction == "l":
			if game.Settings().Facing() == "n":
				direction = "w"
				output += "\n(west)"
			elif game.Settings().Facing() == "s":
				direction = "e"
				output += "\n(east)"
			elif game.Settings().Facing() == "e":
				direction = "n"
				output += "\n(north)"
			elif game.Settings().Facing() == "w":
				direction = "s"
				output += "\n(south)"
			else:
				direction = "w"
				output += "\n(west)"
		if direction == "r":
			if game.Settings().Facing() == "n":
				direction = "e"
				output += "\n(east)"
			elif game.Settings().Facing() == "s":
				direction = "w"
				output += "\n(west)"
			elif game.Settings().Facing() == "e":
				direction = "s"
				output += "\n(south)"
			elif game.Settings().Facing() == "w":
				direction = "n"
				output += "\n(north)"
			else:
				direction = "e"
				output += "\n(east)"
		currentlocation = items.Get("me").Location()
		try: # Check to see if everything is blocked
			return locations.Get(currentlocation).blockedconnections["a"]
		except: # So far so good
			try: # Check to see if that direction is blocked
				return locations.Get(currentlocation).blockedconnections[direction]
			except: # Coast is clear!
				try:
					if locations.Get(currentlocation).Description("exit") is not None:
						output += "\n" + locations.Get(currentlocation).Description("exit")
					items.Get("me").Location(locations.Get(currentlocation).connections[direction])
					for i in locations.Get(currentlocation).contents:
						if items.Get(i).followPlayer is True:
							items.Get(i).Location(items.Get("me").Location())
							if items.Get(i).Description("follow") is not None:
								output += "\n" + items.Get(i).Description("follow")
					output += "\n" + Look()
					if locations.Get(items.Get("me").Location()).Description("firstenter") is not None:
						output += "\n" + locations.Get(items.Get("me").Location()).Description("firstenter")
						locations.Get(items.Get("me").Location()).Description("firstenter", "")
					if locations.Get(items.Get("me").Location()).Description("enter") is not None:
						output += "\n" + locations.Get(items.Get("me").Location()).Description("enter")
					game.Settings().Facing(direction)
					return output
				except:
					# raise
					return "You can't go in that direction."
	else:
		try:
			currentlocation = items.Get("me").Location()
			items.Get("me").Location(locations.Get(direction).name)
			if currentlocation:
				if locations.Get(currentlocation).Description("exit") is not None:
					output += locations.Get(currentlocation).Description("exit") + "\n"
				for i in locations.Get(currentlocation).contents:
					if items.Get(i).followPlayer is True:
						items.Get(i).Location(items.Get("me").Location())
						if items.Get(i).Description("follow") is not None:
							output += "\n" + items.Get(i).Description("follow")
			output += "\n" + Look()
			if locations.Get(items.Get("me").Location()).Description("firstenter") is not None:
				output += locations.Get(items.Get("me").Location()).Description("firstenter") + "\n"
				locations.Get(items.Get("me").Location()).Description("firstenter", "")
			if locations.Get(items.Get("me").Location()).Description("enter") is not None:
				output += locations.Get(items.Get("me").Location()).Description("enter") + "\n"
			game.Settings().Facing("n")
			return output
		except:
			return "You can't go in that direction."

def Drop(item):
	try:
		if item == "all":
			itemlist = []
			for i in items.Get("me").contents:
				if items.Get(i).canDrop is True and i is not "all":
					if items.Get(i).Adjective() is not None:
						itemlist.append(items.Get(i).Adjective().capitalize() + " " + items.Get(i).description["short"] + ": " + items.Get(i).Do("drop"))
					else:
						itemlist.append(items.Get(i).description["short"].capitalize() + ": " + items.Get(i).Do("drop"))
			if len(itemlist) > 0:
				output = ""
				for i in itemlist:
					output += i + "\n"
				return output
			else:
				return "You can't drop anything."
		elif items.Get(item).Location() == "me":
			items.Get(item).Location(items.Get("me").Location())
			return "Dropped."
		else:
			return "You aren't holding it."
	except:
		return "You can't drop that."

def Put(item, where = None):
	try:
		if items.Get("me").Location() != items.Get(where).Location():
			return "You don't see that here."
		if items.Get(where).Location() == items.Get(item).Location():
			return "It's already there."
		if items.Get(where).isSurface or (items.Get(where).isContainer and items.Get(where).isOpen):
			items.Get(item).Location(items.Get(where).name)
			return "Done."
		elif items.Get(where).isContainer and (items.Get(where).isOpen is not True):
			return "It's closed."
		else: 
			raise
	except:
		return "You can't put that there."

def Look(what = None, justcontents = False):
	import re
	output = ""
	if what is None:
		return locations.Get(items.Get("me").Location()).Describe()
	else:
		if not justcontents:
			if items.Get(what).description["long"] is None:
				output = "There doesn't seem to be anything interesting about " + items.Get(what).Grammar("it") + "."
			else:
				output = items.Get(what).description["long"]
		if items.Get(what).contents and items.Get(what).isContainer and (items.Get(what).isOpen is not True):
			output += " It's closed."
		elif items.Get(what).contents and items.Get(what).isContainer and items.Get(what).isOpen and items.Get(what).announceContents and what != "me":
			contents = ""
			initial = ""
			for i in items.Get(what).contents:
				if i is not "all" and not items.Get(i).Description("initial") and not items.Get(i).isSilent:
					contents += " " + items.Get(i).Grammar("a") + " " + items.Get(i).Description("short") + ", "
				if items.Get(i).Description("initial"):
					initial += "\n" + items.Get(i).Description("initial")
			if contents:
				output += " It contains" + Listify(contents) + "."
			if initial:
				output += initial
		if items.Get(what).contents and items.Get(what).isSurface and items.Get(what).announceContents:
			contents = ""
			initial = ""
			for i in items.Get(what).contents:
				if not items.Get(i).Description("initial") and not items.Get(i).isSilent:
					contents += " " + items.Get(i).Grammar("a") + " "
					if items.Get(i).Adjective() is not None:
						contents += items.Get(i).Adjective() + " "
					contents += items.Get(i).Description("short") + ", "
				if items.Get(i).Description("initial"):
					initial += "\n" + items.Get(i).Description("initial")
			if contents:
				output += " Here, you find" + Listify(contents) + "."
			if initial:
				output += initial
		p = re.compile(" a ")
		for i in p.finditer(output):
			if output[i.end()] in ["a", "e", "i", "o", "u"]:
				return output[:(i.start()+1)] + "an " + output[i.end():]
		return output.replace(" .", ".")

def Listify(list):
	# Properly format the list into a sentence
	if list.count(",") > 2:
		output = (list[::-1].replace(",", "", 1).replace(",", "dna ,", 1))[::-1] # Ha, I'm brilliant.
	elif list.count(",") == 2:
		output = (list[::-1].replace(",", "", 1).replace(",", "dna ", 1))[::-1]
	elif list:
		output = list.replace(",", ".", 1)
	return output.strip()

def Smell(what = None):
	if what is None:
		if locations.Get(items.Get("me").Location()).description["smell"] is not None:
			return locations.Get(items.Get("me").Location()).description["smell"]
		else:
			return "You don't smell anything unusual."
	else:
		try:
			if items.Get(what).Location() == items.Get("me").Location() or items.Get(what).Location() == "me":
				if items.Get(what).description["smell"] is None:
					return "You don't smell anything unusual."
				else:
					return items.Get(what).description["smell"]
		except:
			return "You don't smell anything unusual."

def Listen(what = None):
	if what is None:
		if locations.Get(items.Get("me").Location()).description["sound"] is not None:
			return locations.Get(items.Get("me").Location()).description["sound"]
		else:
			return "You don't hear anything unusual."
	else:
		try:
			if items.Get(what).Location() == items.Get("me").Location() or items.Get(what).Location() == "me":
				if items.Get(what).description["sound"] is None:
					return "It's quiet."
				else:
					return items.Get(what).description["sound"]
		except:
			return "You don't hear anything unusual."

def Touch(what = None):
	if what is None:
		if locations.Get(items.Get("me").Location()).description["touch"] is not None:
			return locations.Get(items.Get("me").Location()).description["touch"]
		else:
			return "You don't feel anything unusual."
	else:
		try:
			if items.Get(what).Location() == items.Get("me").Location() or items.Get(what).Location() == "me":
				if items.Get(what).description["touch"] is None:
					return "You don't feel anything unusual."
				else:
					return items.Get(what).description["touch"]
		except:
			return "You don't feel anything unusual."

def Open(item, force = False):
	if items.Get(item).isContainer and (items.Get(item).canOpen or force is True):
		if items.Get(item).isOpen:
			return "It's already open."
		else:
			items.Get(item).isOpen = True
			return "It opens.\n"+Look(item, True)
	else:
		return "You can't open that."

def Close(item, force = False):
	if items.Get(item).isContainer and (items.Get(item).canClose or force is True):
		if items.Get(item).isOpen is False:
			return "It's already closed."
		else:
			items.Get(item).isOpen = False
			return "It closes.\n"
	else:
		return "You can't close that."

def Take(item):
	if item == "all":
		itemlist = []
		taken = 0
		output = ""
		for i in locations.Get(items.Get("me").Location()).contents:
			if items.Get(i).canTake is True and i != "me":
				if items.Get(i).Adjective() is not None:
					itemlist.append(items.Get(i).Adjective().capitalize() + " " + items.Get(i).description["short"] + ": " + items.Get(i).Do("get"))
				else:
					itemlist.append(items.Get(i).description["short"].capitalize() + ": " + items.Get(i).Do("get"))
		if len(itemlist) > 0:
			for i in itemlist:
				output += i + "\n"
			return output
		else:
			return "There's nothing here to take."
	elif game.Settings().Current("object") in ["up", "u", "down", "d", "in", "out"]:
		Go(game.Settings().Current("object"));
	elif items.Get(item).Location() == "me":
		return "You're already carrying it."
	elif items.Get(item).canTake is True and PlayerHas(item, True):
		items.Get(item).Location("me")
		items.Get(item).Description("initial", None)
		return "Taken."
	else:
		# Okay, the item isn't in the room, it isn't "all", and we're not already carrying it. Let's check the other objects in the room to see if they have the object.
		return "You can't take that."

def Stats():
	print "Player location: " + items.Get("me").Location()
	print "Moves taken: " + str(game.Settings().Moves())
	print "Points: " + str(game.Settings().Points()) + " points (out of a possible " + str(game.Settings().MaxPoints()) + ")"
	print "Last command: " + str(Game().lastcommand)
	if game.Settings().Current("object"):
		try:
			print
			print "Location of '" + game.Settings().Current("object") + "':",
			if items.Get(game.Settings().Current("object")).Location():
				print items.Get(game.Settings().Current("object")).Location()
			else:
				print "The null world"
		except:
			print
			print "Item '" + game.Settings().Current("object") + "' does not exist."
	else:
		print
		print "Active daemons:"
		for i in game.Settings().daemons:
			print "\t" + i + " (" + str(game.Settings().daemons[i].countdown) + ")"

def Capture(prompt, script):
	game.Settings().capturemode = True
	game.Settings().captureprocess = script
	return prompt