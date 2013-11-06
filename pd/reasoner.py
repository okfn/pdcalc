import RDF
import sys
import const
from mapping import Mapping
from flow import Flow
from node import Node
from xml.etree import ElementTree as ET
import json

class Reasoner(object):

  # The variables:
  def __init__(self, flow_filename, local_map, global_map=None):
    self.parser = RDF.Parser('raptor')
    if self.parser is None:
      raise Exception("Failed to create RDF.Parser raptor")

    const.base_uri = RDF.Uri("baku")

    self.globalities = json.load(open(global_map, 'r'))
    self.localities = json.load(open(local_map, 'r'))

    self.mapping = Mapping(self.globalities, self.localities)
    self.flow = Flow(self.globalities, self.localities)

    self.model = RDF.Model()
    if self.model is None:
      raise Exception("new RDF.model failed")

#    self.parse_map(mapping_filename)
    self.parse_flow(flow_filename)

#  def parse_map(self, filename):
#    self.mapping_filename = filename
#    print "setting the local mapping", self.mapping_filename
#    self.mapping.parse(self.mapping_filename)

  def parse_flow(self, filename):
    self.flow_filename = filename
    print "setting the local flow", self.flow_filename
    self.flow.parse(self.flow_filename)

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
      op = self.parser.parse_string_as_stream
    else:
      to_parse = RDF.Uri(string = "file:" + filename)
      op = self.parser.parse_as_stream

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

    resolved = False
    # while we have a node...
    while not resolved and isinstance(n, Node):

      # maybe this is a question:
      if n.is_question():
        # Let's think about this question:
        print '\n>> Question %s:'% n.uri, n.text.encode('utf8')
        option = self.flow.choose(self.model, n)
        
        # The option chosen is:
        print '\n>> Answer:', option.text.encode('utf8'), "\n"
        n = self.flow.node(option.node)

      # maybe this is already the answer:
      else:
        print '\n>> Response:', n.text.encode('utf8')
        resolved = True
