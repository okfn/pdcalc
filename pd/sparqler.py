import re

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