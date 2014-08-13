#	Init
#
#	This crunches the user's input into something parsable, then generates a response.

import verbs, locations, items, scripts, game, dialogue

def Item(item): return items.Get(item)
def Location(location): return locations.Get(location)
def Verb(verb): return verbs.Get(verb)
def Game(): return game.Settings()

directobjectlist = ["through", "into", "in", "out", "on", "off", "with", "to", "for", "from", "at", "around"]
verbignorelist = ["restoreas", "saveas", "restore", "save"]
directionlist = ["north", "n", "south", "s", "east", "e", "west", "w", "up", "u", "down", "d", "in", "out", "left", "right", "forward", "forwards", "back", "backwards"]

def StartGame():
	global story
	import dialogue
	dialogue.Init() # Loads the dialogue module -- needs game.softdata to be complete first, so this is called by the client
	exec Game().storyscripts in globals()
	story = StoryScripts()
	if not game.Settings().Started():
		intro = Game().Intro() + "\n<center><b><big>" + Game().Name() + "</big></b>"
		if Game().Author() != "Unknown": intro += "<br/>By " + Game().Author()
		intro += "</center>\n" + scripts.Go(Game().StartRoom()) + "\n(For instructions on how to play, type 'help' and hit enter)"
		Game().Started(True)
		Game().Response(intro)
		if Game().Response().find("{") is not -1:
			try:
				Game().Response(SplitCommand(Game().Response()))
			except:
				game.Log("Error with splitting a command.")

def SplitCommand(command):
	# Takes a command contained in curly braces and processes it, replacing the curly-braced code with the returned result.
	silent = False
	split1 = command.partition("{")
	split2 = split1[2].partition("}")
	command = split2[0]
	if command[0] == "~":
		silent = True
		command = command[1:]
	try:
		exec "response = (" + command + ")"
	except:
		response = "(Oops, it seems we had an error. You probably shouldn't try doing that again.)"
		game.Log("Broken command: (" + command + ")")
	if response is not None and not silent:
		combine = str(split1[0]) + str(response) + str(split2[2])
	else:
		combine = str(split1[0]) + str(split2[2])
	if combine.find("{") is -1:
		return combine
	else:
		return SplitCommand(combine)

def CleanOutput(output):
	return output.replace("\t", "").replace("\n\n", "\n").replace("\n ", "\n")
		
def Parse(command):
	# Is there code contained in the string? If so, execute it. If not, just dump the string back to the terminal.
	command = ProcessInput(command)
	if command.find("{") is -1: # No code. We're all done here.
		output = CleanOutput(command)
	else: # Oops, still some inline code to crunch.
		output = SplitCommand(command)
	output = output.strip()
	return Game().Response(output)

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

def RequiresIDO(verb, words = ""):
	# Certain verbs in certain situations require an indirect object. This helps determine those situations.
	if (verb == "throw" or verb == "push") and (FindIndex(directobjectlist, words)):
		return 1
	elif verb == "put":
		return 1
	else:
		return None

def ProcessInput(input):
	# Takes the user's input, chews it up, and tries to execute it as intelligently as possible.
	output = ""
	input = input.lower()
	Game().Track(input)
	for i in ["the", "a", "an"]:
		input = input.replace(" "+i+" ", " ")
	for i in ["?", ".", ",", "!", "\"", "\'"]: # Currently disallows multiple commands
		input = input.replace(i, " ")
	if Game().capturemode is False:
		words = input.split()
		try: Game().current["verb"] = words[0]
		except: Game().current["verb"] = None
		if (RequiresIDO(Game().current["verb"], words) or FindIndex(directobjectlist, words)) and len(words) > 3: # Do we need an indirect object?
			# This isn't a particularly intelligent way of finding the indirect object, but it seems to work fairly well.
			index = FindIndex(directobjectlist, words)
			if(index > 2): # Makes sure that the trigger word isn't directly after the verb
				# Yay, we found one of the trigger words!
				try:
					Game().current["idobject"] = words[len(words)-1]
					Game().current["idobjectadj"] = words[len(words)-2]
					Game().current["object"] = words[index-2]
					Game().current["objectadj"] = words[index-3]
				except:
					Game().current["idobject"] = None
					Game().current["object"] = words[len(words)-1]
					Game().current["objectadj"] = words[len(words)-2]
					game.Log("Missing an indirect object")
			else:
				Game().current["idobject"] = None
				Game().current["object"] = words[len(words)-1]
				Game().current["objectadj"] = words[len(words)-2] # Just guessing -- if this isn't it, we'll try harder later..
				game.Log("Missing an indirect object")
		else:
			# We don't need an indirect object, let's just try to grab the object from the end of the command.
			if len(words) > 1:
				Game().current["object"] = words[len(words)-1]
				Game().current["objectadj"] = words[len(words)-2] # Just guessing -- if this isn't it, we'll try harder later..
			else:
				Game().current["object"] = None
			Game().current["idobject"] = None
		if Game().current["object"] in ["it", "them", "him", "her"]:
			Game().current["object"] = Game().Salience()
			output += "(" + (Item(Game().Current("object")).Grammar("the") + " " + Item(Game().Current("object")).Description("short") + ")").strip() + "\n"
		else:
			if items.Disambig("object") is not None:
				return items.Disambig("object")
			if items.Disambig("idobject") is not None:
				return items.Disambig("idobject")
			try: 
				Game().current["object"] = Item(Game().Current("object")).name # Quick alternate name disambiguation, should make things easier further in
				Game().Salience(Game().Current("object"))
			except: pass
			try: 
				Game().current["idobject"] = Item(Game().current["idobject"]).name # Quick alternate name disambiguation, should make things easier further in
			except: pass
		try:
			if (Game().Current("verb") in verbignorelist) or ("sys_" in Game().Current("verb")):
				return Verb(Game().Current("verb")).DefaultResponse() # We're working with files, so let's not bother with all this game logic
			else:
				Game().LastCommand(input);
				# Now we have a verb, noun, and possibly an indirect object. Here, we can finally process it.
				if Verb(Game().Current("verb")) and Item(Game().current["object"]):
					# We have both a verb and an object! Let's check to see if the object is in the player's location.
					if Item(Game().current["object"]).Location() == Item("me").Location() or Item(Game().current["object"]).Location() == "me":
						# Awesome, it is! Let's try to push the verb to the object.
						output += Item(Game().current["object"]).Do(Verb(Game().current["verb"]).name, Game().current["idobject"])
					else:
						# Well, the object exists, but it's not here. Let's check to see if it's contained somewhere in the room
						if scripts.PlayerHas(Game().current["object"], True):
							output += Item(Game().current["object"]).Do(Verb(Game().current["verb"]).name, Game().current["idobject"])
						elif Item(Game().current["object"]).Location() in locations.Get(Item("me").Location()).contents:
							output += "You can't reach "
							output += Item(Game().current["object"]).Grammar("the") + " " + Item(Game().current["object"]).Description("short") + "."
						else:
							output += "You don't see "
							output += Item(Game().current["object"]).Grammar("a") + " "
							output += Item(Game().current["object"]).Description("short")+" here."
				else:
					# Either the verb or the object doesn't exist. Let's just fall back on the verb. Have I ever mentioned that I love the command "raise"? It's so simple.
					raise
		except:
			try:
				if Verb(Game().Current("verb")) and Game().Current("object"):
					if Game().Current("object") in directionlist:
						# It's okay, ma'am. We know this object.
						output += Verb(Game().Current("verb")).DefaultResponse()
					else:
						# There's an object, but it doesn't exist.
						return "I'm not sure what you mean by '" + Game().Current("object") + "'."
				elif Verb(Game().current["verb"]):
					# Hmm, we only seem to have a verb. We'll help if we can.
					if Verb(Game().current["verb"]).Clarify() is not None:
						return Verb(Game().current["verb"]).Clarify()
					else:
						output += Verb(Game().current["verb"]).DefaultResponse()
				else:
					raise
			except:
				# I have no idea whatsoever.
				if Game().Current("verb"):
					return "I don't understand the word '" + Game().current["verb"] + "'."
				else:
					# There's nothing here...
					return "Excuse me?"
		if output: # We go a little easier on the player by not adding a turn (and thus processing daemons) if we couldn't understand them
			Game().AddMove()
			daemonoutput = ""
			for i in Game().daemons.keys():
				Game().daemons[i].countdown -= 1
				if Game().daemons[i].countdown == 0 or Game().daemons[i].countdown == -1: # The -1 is for Daemons set to execute immediately
					daemonoutput += "\n" + Game().daemons[i].script
					if Game().daemons[i].repeat == 0:
						del Game().daemons[i]
					else:
						Game().daemons[i].repeat -= 1
						Game().daemons[i].countdown = Game().daemons[i].delay+1
			return output + daemonoutput
		else:
			return "I don't understand."
	else:
		Game().capturemode = False
		return Parse(Game().captureprocess.replace("%input%", input))