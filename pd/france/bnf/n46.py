import RDF

import json

def evaluate_question(model, *args, **kwargs):
	author = "http://data.bnf.fr/ark:/12148/cb13338797s#foaf:Person"
	#Query to get creator uri
	ids = json.load(open('france/bnf/morts.json', 'r'))

	author_id = author.split('#')[0].split('/')[5][2:-1]

	return author_id in ids


