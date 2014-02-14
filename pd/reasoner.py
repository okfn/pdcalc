import RDF
import sys
import const
from mapping import Mapping
from flow import Flow
from node import Node
from xml.etree import ElementTree as ET
import json
import sys

detail_level =  {
  "low":1,
  "medium":2,
  "high":3
}

import collections

def update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

class Reasoner(object):

  # The variables:
  def __init__(self, flow_filename, local_map, flavor_map=None, global_map=None, detail="low", output="cli", language="en"):
    self.parser = RDF.Parser('raptor')
    if self.parser is None:
      raise Exception("Failed to create RDF.Parser raptor")

    const.base_uri = RDF.Uri("baku")

    self.globalities = json.load(open(global_map, 'r'))
    self.localities = json.load(open(local_map, 'r'))
    self.flavor = json.load(open(flavor_map, 'r'))
    self.language= json.load(open(language, 'r'))

    if flavor_map is not None:
      sys.path.append("/".join(flavor_map.split('/')[:-1]))
    sys.path.append("/".join(local_map.split('/')[:-1]))

    self.localities = update(self.localities, self.flavor)

    self.mapping = Mapping(self.globalities, self.localities, self.language)
    self.flow = Flow(self.globalities, self.localities, self.language)

    self.detail = detail_level[detail]
    self.output = output

    self.model = RDF.Model()
    if self.model is None:
      raise Exception("new RDF.model failed")

    self.parse_flow(flow_filename)



  def parse_flow(self, filename):
    self.flow_filename = filename
    #print "setting the local flow", self.flow_filename
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
      #if s.object.is_resource():
     #   print "yay",s.object.uri
        #self.model.load(s.object.uri)
    #print self.model
       # pass

    try:
      a = __import__("prerun")
      a.pre_run(self.model)
    except Exception, e:
      pass
    
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
    try:
      self.out = []
      while not resolved and isinstance(n, Node):
        # maybe this is a question:
        if n.is_question():
          # Let's think about this question:
          if self.detail >= 2:
            if self.output == "cli": 
              self.out.append('>> Question %s: %s'% (n.uri, n.text.encode('utf8')))
            elif self.output == "json":
              self.out.append({"question":n.text.encode('utf8'), "id":n.uri, "type":"question"})
          
          option = self.flow.choose(self.model, n, detail=self.detail, mode=self.output, out=self.out)
          
          # The option chosen is:
          if self.detail >= 2: 
            if self.output == "cli":
              self.out.append('>> Answer: %s' % option.text.encode('utf8'))
            elif self.output == "json":
              self.out.append({"answer":option.text.encode('utf8'), "type":"answer"})
          
          n = self.flow.node(option.node)

        # maybe this is already the answer:
        else:
          if self.detail >= 1:
            if self.output == "cli":
              self.out.append('>> Response: %s - %s' % (n.is_public, n.text.encode('utf8')))
            elif self.output == "json":
              self.out.append({"response":n.text.encode('utf8'), "result":n.is_public, "type":"response"})
          
          resolved = True
    except Exception, e:
      pass

    if self.output == "cli":
      if self.out[-1].startswith(">> Response") == False:
        self.out.append(">> Response: unknown - Not enough ifnormation to evaluate")
    elif self.output == "json":
      if self.out[-1]['type'] != "response":
        self.out.append({"response":"Not enough data to evaluate", "result":"unknown", "type":"response"})

      
    if self.output == "json":
      self.out = json.dumps(self.out)
    elif self.output == "cli":
      self.out = "\n".join(self.out)

  def query(self, q):
    que = RDF.Query(q, query_language="sparql")
    result = que.execute(self.model)
    self.out = str(result)

  def get_result(self):
    return self.out
