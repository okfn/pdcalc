import RDF

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
	SELECT ?date
	WHERE { ?a dc:creator ?bio. ?bio bio:Death ?date } 
	"""

	que = RDF.Query(q, query_language="sparql")
	result = que.execute(model)
	columns = result.get_bindings_count()
	ct = "" 
	for row in result:
		ct = str(row['date'])

	year = int(ct.split('-')[0])
	return ( year + 100) <= date.today().year

