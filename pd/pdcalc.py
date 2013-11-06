#!/usr/bin/python

import argparse
import tempfile
import requests
import os
from os import path


# int main(...) { ...
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Public Domain Calculator')
  parser.add_argument('-c', '--country', dest='country',  help='country for which to test', required=True)
  parser.add_argument('-i', '--instance', dest='instance',  help='instance to test', required=True)
  parser.add_argument('-l', '--flavor', dest='flavor',  help='specific flavor', default="")
  parser.add_argument('-g', '--global', dest='globalmap',  help='global mapping', default="global.json")
  parser.add_argument('-m', '--mode', dest='mode',  help='instance definition mode', choices=['file', 'url'], default="file")
  parser.add_argument('-f', '--format', dest='format',  help='format of the instances', choices=['rdf', 'json'], default="rdf")
  args = parser.parse_args()

  if args.instance.startswith("http"):
    args.mode = "url"

  if args.mode == "url":
    f = tempfile.NamedTemporaryFile("w", delete=False)
    data = requests.get(args.instance)
    print data.encoding
    print data.text

    f.write(data.text.encode('ascii', 'ignore'))
    f.close()
    args.instance = f.name

  files = [ os.path.join(args.country,"flow.json"), os.path.join(args.country,args.flavor, "local.json"), args.globalmap, args.instance]
  print files
  files = map(path.isfile, files)
  print files
  if all(files):
    from reasoner import Reasoner
    a = Reasoner(os.path.join(args.country,"flow.json"), local_map = os.path.join(args.country,args.flavor, "local.json"), global_map = args.globalmap)
    a.parse_input(args.instance)
    a.info()
    a.run()

  if args.mode == "url":
    os.remove(args.instance)
