import RDF

import const
from node import Node
from option import Option
import json
import re

# The flow class contains a flow RDF document
class Flow(object):
  # list of variables
  def __init__(self, globalities = {}, localities = {}):
    self.parser = RDF.Parser('raptor')
    if self.parser is None:
      raise Exception("Failed to create RDF.Parser raptor")

    self.localities = localities    
    self.globalities = globalities
    self.questions = {}
    self.answers = {}
    self.root = None

  # A getter for the root node
  def root_node(self):
    if self.root in self.questions:
      return self.questions[self.root]
    return None

  # a getter for a node based on its URI
  def node(self, node_uri):
    uri = str(node_uri)
    if uri in self.questions:
      return self.questions[uri]
    elif uri in self.answers:
      return self.answers[uri]
    else:
      raise Exception('Node ' + uri + ' is not part of the flow.')

  # Parser of a file:
  def parse(self, filename):
    # memory model
    self.model = json.load(open(filename, "ro"))

    self.get_root(self.model)
    self.get_nodes(self.model)
    #print "parsed", filename

  # store the root node into the object
  def get_root(self, model):
    self.root = model["root"]

  # Store all the nodes into this object
  def get_nodes(self, model):
    self.questions = {key: self.get_node(key, value) for key, value in model["questions"].items()}

  def get_node(self, key, node_model):
    node = Node(key, node_model['type'] == "question")
    
    if "query" in node_model:
      node.query = node_model['query']
    if "is_public" in node_model:
      node.is_public = node_model.get('is_public')
    node.text = node_model['text']
    if "options" in node_model:
      for o in node_model['options']:
        self.get_options(node, o)

    return node

  def get_options(self, node, option):
    node.add_options(Option(option, node))
    pass

  def get_alt_options(self, node, model, subject):
    statement = RDF.Statement(subject,
                              None,
                              None)
    for s in model.find_statements(statement):
      if str(s.predicate.uri).startswith('http://www.w3.org/1999/02/22-rdf-syntax-ns#_'):
        statement2 = RDF.Statement(s.object,
                                   RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                                   RDF.Uri("http://okfnpad.org/flow/0.1/Option"))
        for ss in model.find_statements(statement2):
          node.add_options(self.get_option(model, ss.subject))

  def get_option(self, model, subject):
    option = Option(subject.uri)

    statement = RDF.Statement(subject,
                              RDF.Uri("http://okfnpad.org/flow/0.1/node"),
                              None)

    uri = None
    for s in model.find_statements(statement):
      if s.object.is_resource():
        uri = s.object.uri

    option.node = uri

    statement = RDF.Statement(subject,
                              RDF.Uri("http://okfnpad.org/flow/0.1/text"),
                              None)

    for s in model.find_statements(statement):
      if s.object.is_literal():
        option.text = s.object.literal_value['string']

    statement = RDF.Statement(subject,
                              RDF.Uri("http://okfnpad.org/flow/0.1/query"),
                              None)

    for s in model.find_statements(statement):
      if s.object.is_literal():
        option.query = s.object.literal_value['string']

    return option

  # Some information
  def info(self):
    #print "The flow RDF document contains:", len(self.questions), "questions and", len(self.answers), "answers."
    pass

  def choose(self, model, node, detail=1, mode="cli",  out=None):
    if node.is_binary():
      try:
        a = __import__(node.uri)
        result = a.evaluate_question(model)
        return node.get_option_for(result)
      except:
        sparql = node.render_query(self.globalities, self.localities)
        if detail >=3:
          if mode=="cli":
            out.append(">  Query: %s" % sparql)
          else:
            out.append({"query":sparql, "type":"query"})
          
        query = RDF.Query(sparql, query_language="sparql")
        result = query.execute(model).get_boolean()
        return node.get_option_for(result)
    else:
      for option in node.options:
        if detail >=3:
          if mode=="cli":
            out.append( ">  Evaluating option: %s" % option.text)
          else:
            out.append({"evaluation":option.text, "type":"evaluation"})
        sparql = option.render_query(self.globalities, self.localities)
        
        if sparql is not None:
          if detail >=3:
            if mode=="cli":
              out.append(">  Query: %s" % sparql)
            else:
              out.append({"query":sparql, "type":"query"})
          query = RDF.Query(sparql, query_language="sparql")
          result = query.execute(model).get_boolean()
        else:
          result = False
        if result:
          break
      if result is not None:
        return option
      else:
        return None
