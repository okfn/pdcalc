#!/usr/bin/python

import argparse

# int main(...) { ...
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Public Domain Calculator')
  parser.add_argument('-c', '--country', dest='country',  help='country for which to test', required=True)
  parser.add_argument('-i', '--instance', dest='instance',  help='instance to test', required=True)
  parser.add_argument('-g', '--global', dest='global',  help='global mapping', default="global.rdf")
  parser.add_argument('-l', '--list', dest="list", help="True if list", action='store_true', default=False)
  parser.add_argument('-m', '--mode', dest='mode',  help='instance definition mode', choices=['file', 'url'], default="file")
  parser.add_argument('-f', '--format', dest='format',  help='format of the instances', choices=['rdf', 'json'], default="rdf")
  args = parser.parse_args()

  from reasoner import Reasoner
  a = Reasoner(args.country+"/map.rdf", args.country+"/flow.rdf")
  a.parse_input(args.instance)
  a.info()
  a.run()
