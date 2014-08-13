#	Javascript
#
#	A simple Grendel JavaScript client

print "content-type: text/html\n\n"
print

import cgitb, cgi, sys
cgitb.enable()
# cgitb.enable(display=0, logdir="/tmp")

def Main():
	import os, grendel
	pathinfo = os.environ.get('PATH_INFO')
	form = cgi.FieldStorage()
	if "storyfile" in form:
		storyfile = form.getvalue("storyfile")
		grendel.game.softdata["storyfile"] = storyfile
		grendel.game.LoadGRN(grendel.game.softdata["storyfile"])
		grendel.StartGame()
		grendel.game.Settings().Session(BuildSession()) # Creates (or loads) a session ID
		print "\t<!--\n\t\t\tSession ID: " + grendel.game.Settings().Session() + "\n\t\t\tStory: " + storyfile + "\n\t\t-->\n"
		print "<html>\n<head>\n<style>span.medium { font-size: 14pt; font-weight: bold;} span.big {font-size: 18pt; font-weight: bold;} p.center { text-align: center; margin: 40px; } body { background: #000; color: #fff; font-family: Georgia; font-size: 10pt; margin: 100px 30px 30px 30px;}</style>\n<title>" + grendel.game.Settings().Name() + "</title></head>\n<body>\n\t<div style='max-width: 600px; margin: auto;'>\n"
		print """\t\t<script type="text/javascript" src="jquery.js"></script>\n
			<script type="text/javascript">
				window.onload = function() { document.submit.input.focus(); }
				function update() {
					$("#input").css("color", "#4aa");
					$("#marker").css("display", "none");
					document.submit.input.blur();
					window.scroll(0,100000000000);
					$.get("server.py/Submit?html=True&storyfile="+document.submit.storyfile.value+"&session="+document.submit.session.value+"&input="+document.submit.input.value, function(data) { 
						$("#output").append("<p style='color: #777;'> "+document.submit.input.value+"</p>");
						document.submit.input.value = "";
						$("#input").css("color", "#fff");
						$("#output").append(data);
						window.scroll(0,100000000000);
						$("#marker").css("display", "block");
						document.submit.input.focus();
					});
				}
			</script>"""
		print "\t\t<div id='output'>\n"
		ProcessOutput(grendel.game.Settings().Response())
		print "\t\t</div>\n"
		print "\t\t<p><form action='server.py/Submit' method='post' name='submit' onsubmit='update(); return false;' style='position: relative; top: -1px;'>\n\t\t\t<input type='hidden' name='session' value='"+grendel.game.Settings().Session()+"'/>\n\t\t\t<input type='hidden' name='storyfile' value='"+storyfile+"'/>\n\t\t\t"
		print "<div id=\"marker\" style='position: absolute; margin-left: -20px; color: #777;'>&gt;</div><input type='text' style='border: 0; font-family: inherit; font-size: inherit; background: #000; color: #fff; margin-left: -1px; width: 100%' name='input' id='input' autocomplete='off' />\n\t\t</form></p>\n"
		grendel.game.SaveSession()
	else:
		print "Error: No storyfile."

def BuildSession():
	import md5, time, base64, random
	m = md5.new()
	m.update(str(time.time())) # Timestamped!
	m.update(str(random.randint(0, 10000000))) # Randomed!
	return base64.encodestring(m.digest()).replace("==", "").replace("\n", "").replace("\\", "0").replace("/", "0").replace("+", "0")

def ProcessOutput(text):
	text = text.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;").replace("<center>", "<p class='center'>").replace("</center>", "</p>").replace("<br>", "<br/>").replace("<big>", "<span class='big'>").replace("</big>", "</span>").replace("<medium>", "<span class='medium'>").replace("</medium>", "</span>").split("\n")
	for i in text:
		if i is not "":
			print "\t\t\t<p>"+i+"</p>\n"

Main()