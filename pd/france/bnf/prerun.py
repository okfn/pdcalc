import RDF

import json
import urllib2
import const
import tempfile
import cacher 

def pre_run(model, *args, **kwargs):
	q = """
	prefix dc: <http://purl.org/dc/terms/> 
	SELECT ?x
	WHERE {?a dc:creator ?x. }
	"""

	que = RDF.Query(q, query_language="sparql")
	result = que.execute(model)
	columns = result.get_bindings_count()
	author = ""
	for row in result:
		author =  str(row['x'])

	parser = RDF.Parser('raptor')	
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
		to_parse = RDF.Uri(string = "file:" + auth_url)

		op = parser.parse_as_stream
		for s in op(to_parse, const.base_uri):
			model.add_statement(s)
