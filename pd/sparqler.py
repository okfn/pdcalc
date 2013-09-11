import re

def render(query, globalities, localities):
	query_re= r'%\((.*?)\)'
	ret = ""
	if query is not None:
		replacement_dict = {}
		q = globalities['queries'][query["template"]]
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
			ret += "prefix %s: <%s> " % (prefix, globalities['namespaces'][prefix])
		ret += "ASK "
		ret += q['query'] % replacement_dict
	return ret