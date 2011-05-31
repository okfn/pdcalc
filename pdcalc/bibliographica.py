#!/usr/bin/env python
# -*- coding: utf-8 -*-


from work import Work
from calculator import Calculator
import uk
import fr

import urllib2
import json
import sys

import time
from datetime import datetime
from pprint import pprint

import os.path

import re

bibo_to_pdc = {
    "literary": ["Book", "Document", "ComputerFileFormats"],
    "artistic": [],
    "dramatic": [],
    "composition": [],
    "recording": [],
    "photograph": [],
    "video": [],
    "database": [],
    "law": [],
    "performance": [],
    "database": [],
    "broadcast": [],
    "film": [],
    "typographic": []
}

foaf_to_pdc = {
    "person": ["Agent"],
    "organization": [],
    "government": [],
    "anonymous": [],
    "computer": []
}



def url_to_id(url):
    return url.replace("http://bibliographica.org/entry/", "")

def load(what):
    if(os.path.isfile("data/%s.json" % what)):
	return load_from_file(what)
    else:
	return load_from_web(what)

def load_from_web(what):
    base_url = "http://bibliographica.org/search.json?q=%s"
    target_url = base_url % what
    data = urllib2.urlopen(target_url).read()
    
    # save web-data to file: data/%s.json
    myfile = open("data/%s.json" % what, 'w')
    myfile.write(data)
    myfile.close()

    data = json.loads(data)
    data = data["response"]["docs"]

    for i in range(len(data)):
	d = urllib2.urlopen(data[i]["uri"].replace("<", "").replace(">", "") + ".json").read();
        data[i]["work"] = json.loads(d)
	# save web-data to file: data/%s.json
	myfile = open("data/%s.json" % url_to_id(data[i]["uri"]), 'w')
	myfile.write(d)
	myfile.close()	

	print "saving... %s.json" % url_to_id(data[i]["uri"])
    return data

def load_from_file(what):
    data = open(what, 'r').read()
    data = json.loads(data)
    data = data["response"]["docs"]   
 
    for i in range(len(data)):
	try:
            data[i]["file"] = url_to_id(data[i]["uri"])
            data[i]["work"] = json.loads(open("data/%s.json" % data[i]["file"], 'r').read())
	except:
            print "cannot load %s" % data[i]["file"]
    return data

class Bibliographica:
    def __init__(self, raw_data):
        self.raw_data = raw_data
       
 
	self.data = {}
        self.data["title"] = raw_data["title"]
	if type(self.raw_data["work"]["type"]) is not list:
		self.raw_data["work"]["type"] = [ self.raw_data["work"]["type"]]
        self.data["type"] = self.get_type(bibo_to_pdc, self.raw_data["work"]["type"][-1])
        self.data["date"] = self.get_date()
        self.data["creation_date"] = self.data["date"]

        self.data["authors"] = self.get_authors() 
        if not self.data["authors"]: self.data["authors"] = self.get_publishers()
        
    def get_publishers(self):
        authors = []
        if not "publishers" in self.raw_data["work"].keys(): return 0

        if type(self.raw_data["work"]["publishers"]) is not list:
             self.raw_data["work"]["publishers"] = [self.raw_data["work"]["publishers"]]
        
        for publisher in self.raw_data["work"]["publishers"]:
            p = {
                    "name": publisher["name"],
                    "type": "organization",
                    "country": "uk", # VERY BAD
                }
            authors.append(p)
        return authors

    def get_authors(self):
        authors = []
        if not "creators" in self.raw_data["work"].keys(): return 0

        if type(self.raw_data["work"]["creators"]) is not list:
            self.raw_data["work"]["creators"] = [self.raw_data["work"]["creators"]]

        for author in self.raw_data["work"]["creators"]:
           a =  {
                    "name": author["name"],
                    "type": self.get_type(foaf_to_pdc, author["type"]),
                    "country": "uk", # VERY BAD
                }
           self.put_author_dates(author, a)
           authors.append(a)
        return authors


    def put_author_dates(self, author, a):
        date_list = ["birth", "death"]
        if "events" in author:
            if type(author["events"]) is not list:
                author["events"] = [ author["events"] ]
            for e in author["events"]:
                key = e["type"].split('/')[-1][:-1].lower()
                a["%s_date" % key] = e["date"].split('T')[0].replace('-', '')

        else:
            return

    def get_date(self):
        #return datetime.fromtimestamp(time.mktime(time.strptime(self.raw_data["work"]["issued"].split('T')[0], "%Y-%m-%d")))
        if "issued" in self.raw_data["work"]:
		return self.raw_data["work"]["issued"].split('T')[0].replace('-', '')
	elif "descriptions" in self.raw_data["work"]:
		for v in self.raw_data["work"]["descriptions"]: 
			z = re.findall(r'[0-9]+', v)
			if len(z) >= 1:	
				return z[0]

    def get_type(self, base, data):
        return [k for k, v in base.iteritems() if data.split('/')[-1][:-1] in v][0]
            

if __name__ == "__main__":

    args = '+'.join(sys.argv[1:])  
    data = load(args)

    for i in data:
    	test = Bibliographica(i)
    	work = Work(test.data)
		

	calcUK = Calculator("uk")	
	calcFR = Calculator("fr")

    	print "UK STATUS: %s" % calcUK.get_status(work)
	print "FR STATUS: %s" % calcFR.get_status(work)


