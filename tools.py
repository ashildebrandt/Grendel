import sys, grendel

def ExtractLogs():
	print "Dumping logs to 'log.xlsx'."
	print

	excel = True
	
	if excel is True:
		from win32com.client import Dispatch
		print "Opening Excel..."
		xlApp = Dispatch("Excel.Application")
		xlApp.Visible = 0
		try:
			import os, gzip, cPickle
			for savefile in os.listdir("saves"):
				xlApp.Workbooks.Add()
				if savefile.endswith("session"):
					jar = gzip.open(os.getcwd()+"/saves/"+savefile, 'r')
					loaded = cPickle.load(jar)
					jar.close()
					game = loaded["game"]
					timestamp = round(game.tracker[0]["time"])
					try:
						print "Dumping data... ("+savefile+")"
						xlApp.ActiveSheet.Cells(1,1).Value = "Time (sec)"
						xlApp.ActiveSheet.Cells(1,2).Value = "Location"
						xlApp.ActiveSheet.Cells(1,3).Value = "Output"
						xlApp.ActiveSheet.Cells(1,4).Value = "Input"
						row = 2
						for i in game.tracker:
							xlApp.ActiveSheet.Cells(row,1).Value = round(i["time"] - timestamp)
							xlApp.ActiveSheet.Cells(row,2).Value = i["location"]
							xlApp.ActiveSheet.Cells(row,3).Value = i["output"]
							xlApp.ActiveSheet.Cells(row,4).Value = i["input"]
							row += 1
					except:
						print "Couldn't dump the data into the spreadsheet."
						raise
					try:
						filename = os.getcwd()+"/logs/"+savefile
						filename = filename.replace("session", "xlsx")
						if os.path.exists(filename):
							print "Deleting the old log..."
							os.remove(filename)
						print "Saving workbook..."
						xlApp.ActiveWorkbook.SaveAs(filename)
						xlApp.ActiveWorkbook.Close(SaveChanges=0)
					except:
						print "Excel can't save for some reason. That's a problem."
						raise
			try:
				print "Closing Excel..."
				xlApp.ActiveWorkbook.Close(SaveChanges=0) # see note 1
				xlApp.Quit()
				xlApp.Visible = 0 # see note 2
				del xlApp
			except:
				print "Hmm, looks like Excel is still open. You might want to take a look at that."
				raise
		except:
			try:
				print "Closing Excel..."
				xlApp.Quit()
				# xlApp.Visible = 0
				del xlApp
			except:
				pass
			print
			raise
	if excel is False:
		try:
			import os, gzip, cPickle
			for savefile in os.listdir("saves"):
				if savefile.endswith("session"):
					jar = gzip.open(os.getcwd()+"/saves/"+savefile, 'r')
					loaded = cPickle.load(jar)
					jar.close()
					game = loaded["game"]
					timestamp = round(game.tracker[0]["time"])
					try:
						print "Dumping data... ("+savefile+")"
						lines = []
						lines.append("\"Time (sec)\"\t\"Location\"\t\"Output\"\t\"Input\"\n")
						for i in game.tracker:
							lines.append(str(round(i["time"] - timestamp)) + "\t" + i["location"].replace("\n", "").replace("\t", "").strip() + "\", \"" + i["output"].replace('"', '""').replace("\n", "").replace("\t", "").strip() + "\", \"" + i["input"].replace('"', '""').replace("\n", "").replace("\t", "").strip() + "\"\n")
					except:
						print "Couldn't dump the data into the spreadsheet."
						raise
					try:
						filename = os.getcwd()+"/logs/"+savefile
						filename = filename.replace("session", "txt")
						if os.path.exists(filename):
							print "Deleting the old log..."
							os.remove(filename)
						print "Saving CSV..."
						file = open(filename, "w")
						file.write(''.join(lines))
						file.close()
					except:
						print "The program can't save for some reason. That's a problem."
						raise
		except:
			print
			raise
	print
	print "Everything looks good. Take care!"

print
print "Grendel tools"
print

try:
	storyfile = sys.argv[1]
	if "/logs" in sys.argv:
		ExtractLogs()
	else:
		raise
except:
	print "To convert session logs to an Excel workbook:\n\tpython tools.py /logs [story]"
	print
	if "/debug" in sys.argv:
		raise
	else:
		sys.exit()