#!/usr/bin/python

from reasoner import Reasoner
import argparse


# int main(...) { ...
if __name__ == '__main__':
    if (len(sys.argv) != 4):
      print 'Usage: ', sys.argv[0], ' <map.rdf> <flow.rdf> <input.rdf>'
      sys.exit(1)

    a = Reasoner(sys.argv[1], sys.argv[2])
    a.parse_input(sys.argv[3])
    a.info()
    a.run()
