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

class Map(object):
"""A container of a map element"""
  # just few variables
  def __init__(self, subject):
    self.uri_value    = subject
    self.domain_value = None
    self.range_value  = None
    self.sparql_value = None
    self.sparql_negate = False
    self.assumption_value = None

  # setters/getters

  def _get_uri(self):
    return self.uri_value

  def _set_uri(self, value):
    self.uri_value = value

  def _get_domain(self):
    return self.domain_value

  def _set_domain(self, value):
    self.domain_value = value

  def _get_range(self):
    return self.range_value

  def _set_range(self, value):
    self.range_value = value

  def _get_sparql(self):
    return self.sparql_value

  def _set_sparql(self, value):
    self.sparql_value = value

  def _get_assumption(self):
    return self.assumption_value

  def _set_assumption(self, value):
     self.assumption_value = value

  uri    = property(_get_uri,    _set_uri)
  domain = property(_get_domain, _set_domain)
  range  = property(_get_range,  _set_range)
  sparql = property(_get_sparql, _set_sparql)
  assumption = property(_get_assumption, _set_assumption)

  def is_completed(self):
    if self.domain != None and self.range != None and self.sparql != None:
      return True

    return False

