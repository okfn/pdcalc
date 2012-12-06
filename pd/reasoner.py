#!/usr/bin/python

import RDF
import sys
import const
from mapping import Mapping
from flow import Flow
from node import Node
from xml.etree import ElementTree as ET

# The reasoner :)
class Reasoner:

  # The variables:
  def __init__(self):
    self.mapping = Mapping()
    self.flow = Flow()
    self.model = RDF.Model()
    const.base_uri = RDF.Uri("baku")

    if self.model is None:
      raise Exception("new RDF.model failed")

  def parse_map(self, filename):
    self.mapping.parse(filename)

  def parse_flow(self, filename):
    self.flow.parse(filename)

  # Let's store all the RDF triples into the internal model
  def parse_input(self, filename):

    # parse the file
    parser = RDF.Parser('raptor')
    if parser is None:
      raise Exception("Failed to create RDF.Parser raptor")

    uri = RDF.Uri(string = "file:" + filename)

    # all the triples in the model
    for s in parser.parse_as_stream(uri, const.base_uri):
      self.model.add_statement(s)

  def parse_json_input(self, filename):
    import json2rdf, json
    data = json.loads(open(filename).read())
    if type(data) is list:
        data = data[0]
    if not type(data) is dict:
        raise Exception('The JSON data is not a dict')
    rdf_string = json2rdf.convert(data)

    # parse the string
    parser = RDF.Parser('raptor')
    if parser is None:
      raise Exception("Failed to create RDF.Parser raptor")

    uri = RDF.Uri(string = "file:" + filename)

    # all the triples in the model
    for s in parser.parse_string_as_stream(rdf_string, const.base_uri):
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

      # The option choosed is:
      print 'Answer:', option.text.encode('utf8'), "\n"
      n = self.flow.node(option.node)

# int main(...) { ...
if __name__ == '__main__':
    if (len(sys.argv) != 4):
      print 'Usage: ', sys.argv[0], ' <map.rdf> <flow.rdf> <input.rdf>'
      sys.exit(1)

    a = Reasoner()
    a.parse_map(sys.argv[1])
    a.parse_flow(sys.argv[2])
    if sys.argv[3].endswith('.json'):
      a.parse_json_input(sys.argv[3])
    else:
      a.parse_input(sys.argv[3])
    a.info()
    a.run()
