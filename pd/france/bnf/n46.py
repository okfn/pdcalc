import RDF

import json
import urllib2
import const

def evaluate_question(model, *args, **kwargs):
	q = """
	prefix dc: <http://purl.org/dc/terms/> 
	SELECT ?x
	WHERE {?a dc:creator ?x }
	"""

	que = RDF.Query(q, query_language="sparql")
	result = que.execute(model)
	columns = result.get_bindings_count()
	for row in result:
		author =  str(row['x'])
	


	#Query to get creator uri
	ids = json.load(open('france/bnf/morts.json', 'r'))

	author_id = author.split('#')[0].split('/')[5][2:-1]

	return author_id in ids


