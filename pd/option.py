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

import re
import sparqler
# A container for an option and its properties
class Option(object):
  def __init__(self, obj, parent, mapping={}, text=""):
    self.parent = parent

    self.val = obj.get('value')
    self.text_value = text
    self.node_value = obj.get('node')

    self.is_boolean = self.parent.is_binary()

    if "query" in obj:
      self.s_query = obj['query']
    elif mapping != {}:
      self.s_query = mapping
    else:
      self.s_query = None

  def get_value(self):
    if self.is_boolean:
      return True if self.text_value == "Yes" else False
    else:
      return self.text_value

  def render_query(self, globalities, localities):
    if self.s_query is None:
      return None
    return sparqler.render(self.s_query, globalities, localities)



  def _get_text(self):
    return self.text_value

  def _set_text(self, value):
    self.text_value = value

  def _get_node(self):
    return self.node_value

  def _set_node(self, value):
    self.node_value = value

  def _get_uri(self):
    return self.uri_value

  def _set_query(self, value):
    self.s_query = value

  def _get_query(self):
    return self.s_query
    
  def _get_value(self):
    return self.val

  uri = property(_get_uri)
  text = property(_get_text, _set_text)
  node = property(_get_node, _set_node)
  query = property(_get_query, _set_query)

  value = property(_get_value)
