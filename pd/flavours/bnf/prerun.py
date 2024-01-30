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

import json
import urllib2
import const
import tempfile
import cacher 

import sys

import re

def pre_run(model, *args, **kwargs):
	q = """
	prefix dcterms: <http://purl.org/dc/terms/> 
	SELECT ?a ?x
	WHERE {?a dcterms:creator ?x. }
	"""

	result = model.query(q)
	author = ""

	rc = kwargs.get("res_context", None)

	for row in result:
		author =  str(row['x'])

	auth_url =  author.split('#')[0]
	if auth_url != "":
		var = urllib2.urlopen(auth_url)

		auth_url = var.geturl()

		auth_url = auth_url +"rdf.xml"
		f = tempfile.NamedTemporaryFile("w", delete=False)
		data = cacher.get(auth_url)
		f.write(data)
		auth_url = f.name
		f.close()

		model.parse(auth_url)

	

	bnf_code = row["a"].split("#")[0].split("/")[-1]
	bnf_code = bnf_code[2:]
	#bnf_code = re.findall(r'\d+', bnf_code)[0]

	
	rc["bnf_code"] = bnf_code

	q2 = """
	prefix foaf: <http://xmlns.com/foaf/0.1/> 
	SELECT ?x
	WHERE {?a foaf:familyName ?x. }
	"""

	result = model.query(q2)
	for row in result:
		rc["author"] = row["x"]
