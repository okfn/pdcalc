#!/usr/bin/python

import argparse
import tempfile
import requests
import os
import sys
from os import path

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Public Domain Calculator')
  parser.add_argument('-c', '--country', dest='country',  help='country for which to test', required=True)
  parser.add_argument('-i', '--instance', dest='instance',  help='instance to test', required=True)
  parser.add_argument('-l', '--flavor', dest='flavor',  help='specific flavor', default="")
  parser.add_argument('-g', '--global', dest='globalmap',  help='global mapping', default="global.json")
  parser.add_argument('-m', '--mode', dest='mode',  help='instance definition mode', choices=['file', 'url'], default="file")
  parser.add_argument('-f', '--format', dest='format',  help='format of the instances', choices=['rdf', 'json'], default="rdf")
  parser.add_argument('-d', '--detail', dest='detail',  help='detail levels', choices=['low', 'medium', 'high'], default="low")
  parser.add_argument('-o', '--output', dest='output',  help='output format', choices=["cli", "json"], default="cli")
  parser.add_argument('-q', '--query', dest="query", help="one-shot query", default=None)

  args = parser.parse_args()

  if args.instance.startswith("http"):
    args.mode = "url"

  if args.mode == "url":
    f = tempfile.NamedTemporaryFile("w", delete=False)
    data = requests.get(args.instance)
    #print data.encoding
    #print data.text
    if data.status_code != 200:
      raise Exception("Wrong Status ==> Network Error.")
    f.write(data.text.encode('ascii', 'ignore'))
    f.close()
    args.instance = f.name

  files = [ os.path.join(args.country,"flow.json"), os.path.join(args.country,args.flavor, "local.json"), os.path.join(args.country, "local.json"), args.globalmap, args.instance]
  #print files
  files = map(path.isfile, files)
  #print files
  if all(files):
    from reasoner import Reasoner
    a = Reasoner(os.path.join(args.country,"flow.json"), local_map = os.path.join(args.country, "local.json"), flavor_map = os.path.join(args.country,args.flavor, "local.json"), global_map = args.globalmap, detail=args.detail, output=args.output)
    a.parse_input(args.instance)
    a.info()
    if args.query is None:
      a.run()
    else:
      a.query(args.query)
    print a.get_result()

  if args.mode == "url":
    os.remove(args.instance)

  sys.exit()
