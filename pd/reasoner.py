

import RDF
import sys
import const
from mapping import Mapping
from flow import Flow
from node import Node
from xml.etree import ElementTree as ET


class Reasoner:

  # The variables:
  def __init__(self, mapping_filename, flow_filename):
    const.base_uri = RDF.Uri("baku")

    self.mapping_filename = mapping_filename
    self.flow_filename = flow_filename

    self.model = RDF.Model()

    self.mapping = Mapping()
    self.flow = Flow()

    if self.model is None:
      raise Exception("new RDF.model failed")

    self.parse_map(self.mapping_filename)
    self.parse_flow(self.flow_filename)

  def parse_map(self, filename):
    self.mapping.parse(filename)

  def parse_flow(self, filename):
    self.flow.parse(filename)

  # Let's store all the RDF triples into the internal model
  def parse_input(self, filename):
    if filename.endswith('.json'):
      import json2rdf, json
      data = json.loads(open(filename).read())
      if type(data) is list:
          data = data[0]
      if not type(data) is dict:
          raise Exception('The JSON data is not a dict')
      to_parse = json2rdf.convert(data)
      op = parser.parse_string_as_stream
    else:
      to_parse = RDF.Uri(string = "file:" + filename)
      op = parser.parse_as_stream
    # parse the file
    parser = RDF.Parser('raptor')
    if parser is None:
      raise Exception("Failed to create RDF.Parser raptor")

    # all the triples in the model
    for s in op(to_parse, const.base_uri):
      self.model.add_statement(s)
    
  # Debug info
  def info(self):
    self.mapping.info()
    self.flow.info();

  # the main operation of the reasoner
  def run(self):

    # Let's start from the root node
    n = self.flow.root_node()

    # Until we have a node...
    while isinstance(n, Node):

      # maybe this is already the answer:
      if n.is_question() == False:
        print 'The solution is:',n.text.encode('utf8')
        break

      # Let's think about this question:
      print 'Question:', n.text.encode('utf8')
      option = self.mapping.choose(self.model, n)

      # The option chosen is:
      print 'Answer:', option.text.encode('utf8'), "\n"
      n = self.flow.node(option.node)
