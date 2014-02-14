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
		f_lpath = os.path.join(path,"flow.json")
		ret = {}
		try:
			f = json.load(open(f_lpath))
			
			for key in f.get('questions'):
				ret["%s.text" % key] = f.get('questions').get(key).get('text')
				if f.get('questions').get(key).get('options') is not None:
					for i, opt in enumerate(f.get('questions').get(key).get('options')):
						ret["%s.options.%s.text" % (key, i)] = f.get('questions').get(key).get('options')[i].get('text')

			print json.dumps(ret,indent = 3)
		except Exception, e:
			pass

