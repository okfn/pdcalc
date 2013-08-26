import RDF
import const
from maps import Map
from option import Option
from rdflib import Graph

import re

# A class for a mapping RDF document
class Mapping:
  def __init__(self, globalities):
    # We need just a list of 'mapping' objects - and a list of assumptions
    self.globalities = globalities
    self.maps = []
    self.assumptions = []
    self.model = RDF.Model()
    if self.model is None:
      raise Exception("new RDF.model failed")
    self.parser = RDF.Parser('raptor')
    if self.parser is None:
      raise Exception("Failed to create RDF.Parser raptor")

    self.query_re= r'%\((.*?)\)'

  def parse(self, filename):
    # load the file
    uri = RDF.Uri(string = "file:" + filename)

    # all the triples in the model
    for s in self.parser.parse_as_stream(uri, const.base_uri):
      self.model.add_statement(s)

    # Let's look for any mapping resource
    statement = RDF.Statement(None,
                              RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                              RDF.Uri("http://okfnpad.org/flow/0.1/Map"))
    for s in self.model.find_statements(statement):
      if s.subject.is_resource():
        self.add_map(self.model, s.subject)
    print "parsed", filename

  # This method populates a Map object
  def add_map(self, model, subject):
    m = Map(subject.uri)
    statement = RDF.Statement(subject,
                              RDF.Uri("http://www.w3.org/2000/01/rdf-schema#domain"),
                              None)
    for s in model.find_statements(statement):
      if s.object.is_resource():
        m.domain = str(s.object.uri)

    statement = RDF.Statement(subject,
                              RDF.Uri("http://www.w3.org/2000/01/rdf-schema#range"),
                              None)
    for s in model.find_statements(statement):
      if s.object.is_resource():
        m.range = str(s.object.uri)

    statement = RDF.Statement(subject,
                              RDF.Uri("http://okfnpad.org/flow/0.1/sparql"),
                              None)
    for s in model.find_statements(statement):
      if s.object.is_literal():
        m.sparql = s.object.literal_value['string']

    
    statement = RDF.Statement(subject,
                              RDF.Uri("http://okfnpad.org/flow/0.1/sparql-not"),
                              None)
    for s in model.find_statements(statement):
      if s.object.is_literal():
        m.sparql = s.object.literal_value['string']
	m.sparql_negate = 1


    statement = RDF.Statement(subject,
			      RDF.Uri("http://okfnpad.org/flow/0.1/assumption"),
			      None)
    for s in model.find_statements(statement):
      if s.object.is_literal():
	m.assumption = s.object.literal_value['string']

    # Add it in the list only if completed
    if m.is_completed():
      self.maps.append(m)

  # Some information
  def info(self):
    print "The map RDF document contains:", len(self.maps), "mapping objects"

  # This method chooses an answer
  def choose(self, model, node):
    uri = str(node.uri)

    # Creating a list of the mapping object related to this URI
    map_list = []
    for m in self.maps:
      if m.domain == uri:
        map_list.append(m)

    if len(map_list) == 0:
      raise Exception('Uri ' + uri + ' is not mapped.')

    # Let's choose an option:
    option = self.choose_node(model, map_list)
    if option == None:
      raise Exception('I cannot choose. Sorry.')

    # Validation:
    for o in node.options:
      if str(o.uri) == option:
        return o

    raise Exception('The mapping points to an non-option uri: ' + option + ' for uri: ' + uri)

  # The operation is simple:
  def choose_node(self, model, map_list):
		for m in map_list:
      # if the sparql query returns 'true', we have a result

			elements = re.findall(self.query_re, m.sparql)
			replacement_dict = {}
			prefixes = {}
			prefixes_string = ""
			for element in elements:
				replacement_dict[element] = self.globalities['sameAs'][element][0]
				prefixes[self.globalities['sameAs'][element][0].split(':')[0]] = self.globalities['namespaces'][self.globalities['sameAs'][element][0].split(':')[0]]
			for p,u in prefixes.iteritems():
				prefixes_string += "prefix %s: <%s>" % (p, u)
			sparql = str(prefixes_string + " " + m.sparql % replacement_dict)
			print "sparql query: "
			print sparql
			query = RDF.Query(sparql, query_language="sparql")
			#query = RDF.SPARQLQuery(str(m.sparql))
			result = query.execute(model)
			print "result: "
			print result
			mini = 0
			if result.is_boolean() == False:
				#raise Exception('The mapping must use only boolean Sparql queries.')
				for k in result:
					print result 
					mini = 1
					print k
			elif result.get_boolean() == True: mini = 1

			if(m.sparql_negate): 
				#print "NEGATING"
				if(mini): mini = 0
				else: mini = 1
			if mini == 1:
				if(m.assumption):
					self.assumptions.append(m.assumption)  
					print('ASSUMPTIONS so far: ' + "\n".join(self.assumptions))
					print("New assumption: " + m.assumption)
				return m.range

		return None
