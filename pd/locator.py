import os 
import json

def get_keys(dm, path = ""):
	ret = []
	if typeof(dm) == dict:
		print "dict"
		for k in d.iterkeys():
			ret.append(get_keys(dm[k], path+"."+k))
		return ret
	elif typeof(dm) == str:
		print "str"
		return path
	else:
		print str(typeof(dm))


for path in os.listdir('.'):
	if "." in path or "-" in path:
		pass
	else:
		os.chdir(path)
		f_lpath = os.path.join("/Users/admin/Documents/prjs/pdcalc/pd", path, "flow.json")
		
		try:
			f = json.load(open(f_lpath))
			k = get_keys(f)
			print k
		except:
			pass
		os.chdir('..')

