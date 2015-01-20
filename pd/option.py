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