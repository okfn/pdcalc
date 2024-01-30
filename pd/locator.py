# MIT License
#
# Copyright (c) 2008-2024 Rufus Pollock, Open Knowledge Foundation and
# contributors
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
	print path
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
			try:
				os.mkdir(os.path.join(path, "i18n"))
			except:
				pass
			with open(os.path.join(path, "i18n", "en.json"), "wb") as en_lang:
				json.dump(ret, en_lang)
		except Exception, e:
			pass

