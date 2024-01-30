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


