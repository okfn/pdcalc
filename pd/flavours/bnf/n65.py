
import rdflib
from rdflib import BNode, RDF,URIRef



import json
import sys
from dateutil import parser 
from dateutil.relativedelta import relativedelta
import datetime
from datetime import timedelta

def evaluate_question(model, *args, **kwargs):
	
	#return True
	q = """
	prefix dc: <http://purl.org/dc/terms/> 
	SELECT ?date
	WHERE { ?a dc:date ?date.} 
	"""
	#print model
	result = models.query(q)

	try:
		c = kwargs.get("context").get("node").get("query").get("parameters").get("pdcalc:years")
	except:
		c = 70

	rc = kwargs.get("res_context", None)

	for row in result:
		date = str(row['x'])
	d = parser.parse(date)
	
	
	rc["fromdate"] = str(d+timedelta(years=c)+timedelta(days=1))
	rc["fromyear"] = (d+timedelta(years=c)+timedelta(days=1)).year+1
	
	return d < datetime.datetime.now() - relativedelta(years=c)


