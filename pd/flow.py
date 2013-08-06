import RDF
import const
from node import Node
from option import Option

# The flow class contains a flow RDF document
class Flow:

  # list of variables
  def __init__(self):
    self.questions = {}
    self.answers = {}
    self.root = None
    self.parser = RDF.Parser('raptor')
    if self.parser is None:
      raise Exception("Failed to create RDF.Parser raptor")

  # A getter for the root node
  def root_node(self):
    if self.root in self.questions:
      return self.questions[self.root]
    return None

  # a getter for a node based on its URI
  def node(self, node):
    uri = str(node)
    if uri in self.questions:
      return self.questions[uri]
    elif uri in self.answers:
      return self.answers[uri]
    else:
      raise Exception('Uri ' + uri + ' is not part of the RDF document.')

  # Parser of a file:
  def parse(self, filename):
    # memory model
    model = RDF.Model()
    if model is None:
      raise Exception("new RDF.model failed")

    # parse the file
    uri = RDF.Uri(string = "file:" + filename)

    # all the triples in the model
    for s in self.parser.parse_as_stream(uri, const.base_uri):
      model.add_statement(s)

    self.get_root(model)
    self.get_nodes(model)

  # store the root node into the object
  def get_root(self, model):
    statement = RDF.Statement(None,
                              RDF.Uri("http://okfnpad.org/flow/0.1/root"),
                              None)
    for s in model.find_statements(statement):
      if s.object.is_resource():
        self.root = str(s.object.uri)

  # Store all the nodes into this object
  def get_nodes(self, model):
    statement = RDF.Statement(None,
                              RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                              None)

    for s in model.find_statements(statement):
      if s.subject.is_resource() and s.object.is_resource():
        if s.object.uri == RDF.Uri('http://okfnpad.org/flow/0.1/Answer'):
          self.answers[str(s.subject.uri)] = self.get_node(model, s.subject, False)
        elif s.object.uri == RDF.Uri('http://okfnpad.org/flow/0.1/Question'):
          self.questions[str(s.subject.uri)] = self.get_node(model, s.subject, True)

  def get_node(self, model, subject, is_question):
    node = Node(subject.uri, is_question)

    statement = RDF.Statement(subject,
                              RDF.Uri("http://okfnpad.org/flow/0.1/text"),
                              None)

    for s in model.find_statements(statement):
      if s.object.is_literal():
        node.text = s.object.literal_value['string']

    statement = RDF.Statement(subject,
                              RDF.Uri("http://okfnpad.org/flow/0.1/option"),
                              None)

    for s in model.find_statements(statement):
      self.get_options(node, model, s.object)

    return node

  def get_options(self, node, model, option):
    statement = RDF.Statement(option,
                              RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                              None)

    for s in model.find_statements(statement):
      if s.object.is_resource() and s.object.uri == RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#Alt"):
        self.get_alt_options(node, model, s.subject)
      elif s.object.is_resource() and s.object.uri == RDF.Uri("http://okfnpad.org/flow/0.1/Option"):
        node.add_options(self.get_option(model, s.subject))

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

    return option

  # Some information
  def info(self):
    print "The flow RDF document contains:", len(self.questions), "questions and", len(self.answers), "answers."
