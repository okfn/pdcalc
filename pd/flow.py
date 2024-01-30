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
import sys
import const
from node import Node
from option import Option
import json
import re
import traceback

# The flow class contains a flow RDF document
class Flow(object):
  # list of variables
  def __init__(self, globalities = {}, localities = {}, mapping={},  language="en"):
    self.language = language
    self.localities = localities    
    self.globalities = globalities
    self.mapping = mapping
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
      print >>sys.stderr, "q", uri
      print >>sys.stderr, self.questions[uri]
      return self.questions[uri]
    elif uri in self.answers:
      print >>sys.stderr, "e", uri
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
    elif key in self.mapping:
      if "query" in self.mapping[key]:
        node.query = self.mapping[key]["query"]
    if "is_public" in node_model:
      node.is_public = node_model.get('is_public')
    node.text = self.language[key+".text"]
    if "options" in node_model:
      if len(node_model.get("options", [])) == 2: #binary
        for i, o in enumerate(node_model['options']):
          self.get_options(node, o, text=self.language[key+".options."+str(i)+".text"])	
      else:
        for i, o in enumerate(node_model['options']):
          if key in self.mapping:
            self.get_options(node, o, mapping=self.mapping[key][i]["query"], text=self.language[key+".options."+str(i)+".text"])
          else:
            self.get_options(node, o, text=self.language[key+".options."+str(i)+".text"])
    return node

  def get_options(self, node, option, mapping={}, text=""):
      node.add_options(Option(option, node, mapping, text))
    
  # Some information
  def info(self):
    #print "The flow RDF document contains:", len(self.questions), "questions and", len(self.answers), "answers."
    pass

  def choose(self, model, node, detail=1, mode="cli",  out=None, res_context=None):
    if node.is_binary():
      try:
        a = __import__(node.uri)
        result = a.evaluate_question(model, context = {"g":self.globalities, "l":self.localities, "node":node}, res_context = res_context)
        return node.get_option_for(result)
      except ImportError, e:
        sparql = node.render_query(self.globalities, self.localities)
        if detail >=3:
          if mode=="cli":
            out.append(">  Query: %s" % sparql)
          else:
            out.append({"query":sparql, "type":"query"})
          
        result = model.query(sparql)
        
        return node.get_option_for(result)
      except Exception, e:
        print >> sys.stderr, e
        traceback.print_exc(file=sys.stderr)
    else:
      try:
        a = __import__(node.uri)
        result = a.evaluate_question(model, context = {"g":self.globalities, "l":self.localities, "node":node}, res_context = res_context)
        
        return node.get_option_for(result)
      except ImportError, e:
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
            result = model.query(sparql)
          else:
            result = False
          if result:
            break
      except Exception, e:
        print >> sys.stderr, e
        traceback.print_exc(file=sys.stderr)
      if result is not None:
        return option
      else:
        return None
