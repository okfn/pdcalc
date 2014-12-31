
import rdflib
from rdflib import BNode, RDF

import json
import sys
from dateutil import parser 
from dateutil.relativedelta import relativedelta
import datetime
from datetime import timedelta

def evaluate_question(model, *args, **kwargs):
	
	#return True
	q = """
	prefix bio: <http://vocab.org/bio/0.1/> 
	SELECT  ?x 
	WHERE {
		?c bio:death ?x.
	}
	"""
	#print model
	result = model.query(q)
	
	try:
		c = kwargs.get("context").get("node").get("query").get("parameters").get("pdcalc:years")
	except:
		c = 70

	rc = kwargs.get("res_context", None)

	for row in result:
		date = str(row['x'])
	d = parser.parse(date)
	
	rc["fromdate"] = str(d+timedelta(days=c*365)+timedelta(days=1)).split(" ")[0]
	rc["fromyear"] = (d+timedelta(days=c*365)+timedelta(days=1)).year+1

	return d < datetime.datetime.now() - relativedelta(years=c)


