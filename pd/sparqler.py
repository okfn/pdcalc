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

import re
import sys

def render(query, globalities, localities):
	"""transforms json to sparql"""
	query_re= r'%\((.*?)\)'
	ret = ""
	if query is not None:
		if "template" in query:
			replacement_dict = {}
			if "queries" in localities:
				q = localities['queries'][query["template"]] if query["template"] in localities['queries'] else globalities['queries'][query["template"]]
			else:
				q = globalities['queries'][query["template"]]
			mode = q.get('mode', "ASK")
			elements = re.findall(query_re, q['query'])
			for element in elements:
				if "parameters" in query and element in query['parameters']:
					replacement_dict[element] = query['parameters'][element]
				elif element in localities['sameAs']:
					replacement_dict[element] = localities['sameAs'][element][0]
					q['prefixes'].append(globalities['sameAs'][element][0].split(':')[0])
				elif element in globalities['sameAs']:
					replacement_dict[element] = globalities['sameAs'][element][0]
					q['prefixes'].append(globalities['sameAs'][element][0].split(':')[0])

			#print "Assumptions:",query.get('assumptions')
			for prefix in set(q['prefixes']):
				ret += "prefix %s: <%s> " % (prefix, globalities['namespaces'][prefix] if prefix in globalities['namespaces'] else localities['namespaces'][prefix])
			ret += mode + " "
			ret += q['query'] % replacement_dict
		else:
			ret = query['query'];
	return ret
