# A container for an option and its properties
class Option:
  def __init__(self, subject):
    self.uri_value = subject
    self.text_value = None

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

  uri = property(_get_uri)
  text = property(_get_text, _set_text)
  node = property(_get_node, _set_node)
