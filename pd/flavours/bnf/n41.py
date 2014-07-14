
import RDF

import json

def evaluate_question(model, *args, **kwargs):
	q = """
	prefix foaf: <http://xmlns.com/foaf/0.1/> 
	prefix dc: <http://purl.org/dc/terms/> 
	prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
	SELECT ?bio
	WHERE { ?a dc:creator ?bio. ?a dc:title ?b } 
	"""

	que = RDF.Query(q, query_language="sparql")
	result = que.execute(model)
	columns = result.get_bindings_count()
	ct =0
	for row in result:
		ct += 1
	return ct > 1


