from option import Option

# A container for a node with its properties
class Node:
  def __init__(self, subject, is_question):
    self.question = is_question
    self.uri_value = subject
    self.text_value = None
    self.options_list = []

  def is_question(self):
    return self.question

  def _get_text(self):
    return self.text_value

  def _set_text(self, value):
    self.text_value = value

  def _get_uri(self):
    return self.uri_value

  def _get_options(self):
    return self.options_list

  options = property(_get_options)
  uri = property(_get_uri)
  text = property(_get_text, _set_text)

  def add_options(self, option):
    if isinstance(option, Option):
      self.options_list.append(option)
