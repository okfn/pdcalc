import rdflib

import json
import urllib2
import const
from datetime import date

def evaluate_question(model, *args, **kwargs):

	q = """
	prefix foaf: <http://xmlns.com/foaf/0.1/> 
	prefix dc: <http://purl.org/dc/terms/> 
	prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
	prefix bio: <http://vocab.org/bio/0.1/>
	prefix foaf: <http://xmlns.com/foaf/0.1/>
	SELECT ?date
	WHERE { ?a dc:creator ?bio. 
			?bio a foaf:Person.
			?bio bio:death ?date } 
	"""

	result = model.query(q)

	rc = kwargs.get("res_context", None)

	ct = "" 
	for row in result:
		ct = str(row['date'])

	year = int(ct.split('-')[0])

	rc["fromyear"] = year+95+1

	return ( year + 95) <= date.today().year 

