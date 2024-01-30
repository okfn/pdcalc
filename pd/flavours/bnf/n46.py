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

def evaluate_question(model, *args, **kwargs):
	q = """
	prefix dc: <http://purl.org/dc/terms/> 
	SELECT ?x
	WHERE {?a dc:creator ?x }
	"""

	result = model.query(q)
	for row in result:
		author =  str(row['x'])
	


	#Query to get creator uri
	ids = json.load(open('flavours/bnf/morts.json', 'r'))

	author_id = author.split('#')[0].split('/')[5][2:-1]

	return author_id in ids


