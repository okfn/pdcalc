
import rdflib

import json

def evaluate_question(model, *args, **kwargs):
	q = """
	prefix foaf: <http://xmlns.com/foaf/0.1/> 
	prefix dc: <http://purl.org/dc/terms/> 
	prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
	SELECT ?bio
	WHERE { ?a dc:creator ?bio. ?a dc:title ?b } 
	"""

	result = model.query(q)
	ct =0
	for row in result:
		ct += 1
	return ct > 1


