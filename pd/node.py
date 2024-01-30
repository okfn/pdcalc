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

from option import Option
import sys
import sparqler
# A container for a node with its properties
class Node(object):
  def __init__(self, subject, is_question, query = None):
    self.question = is_question
    self.uri_value = subject
    self.text_value = None
    self.options_list = []
    self.query_value = query
    self._public = None

  def is_binary(self):
    return len(self.options) == 2 and self.query_value is not None

  def is_question(self):
    return self.question
    #return len(self._get_options())>0

  def _get_text(self):
    return self.text_value

  def _set_text(self, value):
    self.text_value = value

  def _get_query(self):
    return self.query_value

  def _set_query(self, value):
    self.query_value = value

  def _get_uri(self):
    return self.uri_value

  def _get_options(self):
    return self.options_list
 
  def _get_is_public(self):
    if self._public is None:
      return "unknown"
    return self._public

  def _set_is_public(self, value):
    self._public = value

  options = property(_get_options)
  uri = property(_get_uri)
  text = property(_get_text, _set_text)
  query = property(_get_query, _set_query)
  is_public = property(_get_is_public, _set_is_public)

  def add_options(self, option):
    if isinstance(option, Option):
      self.options_list.append(option)

  def render_query(self, globalities, localities):
    q = sparqler.render(self.query, globalities, localities)
    return q

  def get_option_for(self, value):
    if self.is_binary():
      if bool(self.options_list[0].value) == bool(value):
        return self.options_list[0]
      else:
        return self.options_list[1]
    else:
      pass
