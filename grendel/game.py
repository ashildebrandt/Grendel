#	Game
#
#	This is a class that handles generic, common game information, such as points, move counts, and daemons.

import items, locations, verbs, scripts, os, time

softdata = {
	"gamepath": os.getcwd(),
	"storyfile": None,
	"storypath": "/stories",
	"savepath": os.getcwd() + "/saves"
}

class InitGame(object):
	def __init__(self):
		self.debug = False
		self.daemons = {}
		self.journal = []
		self.tracker = []
		self.moves = 0
		self.points = 0
		self.maxpoints = 0
		self.name = "Untitled"
		self.author = "Unknown"
		self.version = "0"
		self.capturemode = False
		self.showexits = False
		self.room = "startroom"
		self.response = ""
		self.session = "local"
		self.lastcommand = ""
		self.flags = []
		self.storyfile = ""
		self.started = False
		self.current = {"verb": None, "object": None, "idobject": None, "objectadj": None, "idobjectadj": None, "input": None}
		self.salience = ""
		self.facing = "n"
		self.storyscripts = None
	def Track(self, input = None):
		if input:
			self.tracker.append({'time': time.time(), 'location':items.Get("me").Location(), 'output': self.Response(), 'input': input})
			self.current["input"] = input
			return True
		else:
			return False
	def Journal(self, entry = None):
		if entry:
			self.journal.append(entry)
			return "You make a note about this in your journal."
		else:
			return self.journal
	def ClearJournal(self):
		self.journal = []
	def Facing(self, direction = None):
		if direction is not None:
			self.facing = direction
		else:
			return self.facing
	def Salience(self, item = None):
		if item is not None:
			self.salience = item
		else:
			return self.salience
	def ResetObjects():
		current = {"verb": None, "object": None, "idobject": None, "objectadj": None, "idobjectadj": None}
	def Session(self, session = None):
		if session is not None:
			self.session = session
			return LoadSession()
		else:
			return self.session
	def Response(self, response = None):
		if response is not None:
			self.response = response
			return self.response
		else:
			return self.response.replace("  ", " ")
	def Current(self, type = None):
		try:
			return self.current[type]
		except:
			Log("Trying to check an invalid type: " + type)
			return None
	def LastCommand(self, lastcommand = None):
		if lastcommand is not None:
			self.lastcommand = lastcommand
		else:
			return self.lastcommand
	def Started(self, started = None):
		if started is not None:
			self.started = started
		else:
			return self.started
	def Name(self, name = None):
		if name is not None:
			self.name = name
		else:
			return self.name
	def Author(self, author = None):
		if author is not None:
			self.author = author
		else:
			return self.author
	def Version(self, version = None):
		if version is not None:
			self.version = version
		else:
			return self.version
	def MaxPoints(self, maxpoints = None):
		if maxpoints is not None:
			self.maxpoints = maxpoints
		else:
			return self.maxpoints
	def Moves(self):
		return self.moves
	def AddMove(self):
		self.moves += 1
	def Points(self):
		return self.points
	def AddPoints(self, count):
		self.points += count
	def RemovePoints(self, count):
		self.points -= count
	def StartRoom(self, room = None):
		if room is not None:
			self.room = room
		else:
			return self.room
	def Intro(self, intro = None):
		if intro  is not None:
			self.intro = intro
		else:
			return self.intro

game = InitGame()

def Settings():
	return game
	
def SaveSession():
	global game
	import cPickle, gzip, os
	pickles = {'game': game, 'items_objects': items.objects, 'items_directory': items.directory, 'locations_objects': locations.objects, 'locations_directory': locations.directory, 'verbs_objects': verbs.objects, 'verbs_directory': verbs.directory}
	if Settings().Session() != "local":
		jar = gzip.open(softdata["savepath"]+"/"+softdata["storyfile"]+"."+Settings().Session()+".session", 'wb')
		cPickle.dump(pickles, jar, 2)
		jar.close()
		# For dumping the log -- no longer needed 
		# f = open(softdata["savepath"]+"/"+softdata["storyfile"]+"."+Settings().Session()+".txt", 'a')
		# f.write("> " + game.LastCommand() + "\n\n" + "---\n\n" + game.Response() + "\n\n" + "---\n\n")
		# f.close()

def LoadSession():
	global game
	import gzip, os, cPickle
	try:
		jar = gzip.open(softdata["savepath"]+"/"+softdata["storyfile"]+"."+Settings().Session()+".session", 'r')
		loaded = cPickle.load(jar)
		jar.close()
		game = loaded["game"]
		items.objects = loaded["items_objects"]
		items.directory = loaded["items_directory"]
		verbs.objects = loaded["verbs_objects"]
		verbs.directory = loaded["verbs_directory"]
		locations.objects = loaded["locations_objects"]
		locations.directory = loaded["locations_directory"]
		return True
	except:
		return False
	
def LoadGRN(storyfile):
	global game
	import gzip, os, cPickle
	jar = gzip.open(softdata["gamepath"]+softdata["storypath"]+"/"+storyfile+".grn", 'r')
	loaded = cPickle.load(jar)
	jar.close()
	
	# ... and now, load them back in
	game = loaded["game"]
	items.objects = loaded["items_objects"]
	items.directory = loaded["items_directory"]
	verbs.objects = loaded["verbs_objects"]
	verbs.directory = loaded["verbs_directory"]
	locations.objects = loaded["locations_objects"]
	locations.directory = loaded["locations_directory"]
	game.storyscripts = loaded["storyscripts"]
	
class InitDaemon:
	def __init__(self, delay, script, repeat):
		self.id = id
		self.delay = int(delay)
		self.countdown = int(delay)
		self.script = script
		self.repeat = repeat

def NewDaemon(id, delay, script, repeat = 0):
	daemon = InitDaemon(delay, script, repeat)
	Settings().daemons.update({id: daemon})

def KillDaemon(id):
	del Settings().daemons[id]
	
log = []

def Log(message = None):
	if message is not None:
		import sys
		log.append("*** " + sys._getframe(1).f_code.co_name + " > " + message)
	else:
		return log
		
def ClearLog():
	global log
	log = []