import items, verbs, locations

def OutputFullGameText():
	output = ""
	for i in items.objects:
		if type(i) is not str:
			output += "Item: " + i.name + "\n"
			output += "\tDescriptions\n"
			for j in i.description:
				if i.description[j]:
					if i.description[j][0] == "{" and i.description[j][len(i.description[j])-1] == "}":
						pass
					else:
						output += "\t\t" + j + "\n\t\t\t" + str(i.description[j]).replace("\n", "") +"\n"
			output += "\tActions\n"
			for j in i.verbs:
				if i.actions[i.verbs.index(j)]:
					if i.actions[i.verbs.index(j)][0] == "{" and i.actions[i.verbs.index(j)][len(i.actions[i.verbs.index(j)])-1] == "}":
						pass
					else:
						output += "\t\t" + j + "\n\t\t\t" + str(i.actions[i.verbs.index(j)]).replace("\n", "") +"\n"
	for i in locations.objects:
		if type(i) is not str:
			output += "Location: " + i.name + "\n"
			output += "\tDescriptions\n"
			for j in i.description:
				if i.description[j]:
					output += "\t\t" + j + "\n\t\t\t" + str(i.description[j]).replace("\n", "") +"\n"
	f= open('script.txt', 'w')
	f.write(output)
	f.close()