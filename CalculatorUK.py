#!/usr/bin/env python

import CalculatorBase


import logging
from datetime import datetime, timedelta

import time
import re

try:
    import json
except ImportError:
    import simplejson as json


logger = logging.getLogger('pdcalc.pd')

assumptions = []

EU_COUNTRIES = [ "se", "fi", "dk",  "ee", "lt", "lv", "pl", "de", "nl", "be", "fr", "lu", "es", "pt", "it", "gr", "sl", "au", "hu", "ro", "bg", "sk", "cz", "mt", "cy", "ie", "uk" ]
EEA_COUNTRIES = list(EU_COUNTRIES) + ["is", "no"]



TREATY_COUNTRIES = { "us": 70, "ca": 70 } # to be completed




WORK_TYPES = [
    "literary",
    "artistic",
    "dramatic",
    "composition",
    "recording",
    "photograph",
    "video",
    "database",
    "law",
    "performance",
    "database",
    "broadcast",
    "film"
    "typographic"
]

ENTITY_TYPES = [
    "person",
    "organization",
    "government",
    "anonymous",
    "computer",
]




def getstruct(blob):
    if type(blob) == str:
        struct = json.loads(blob)
    elif type(blob) == dict:
        struct = blob
    else:
        raise TypeError("Can only load strings or dictionaries.")
        
    return struct


class LegalEntity:
    def __init__(self, blob=None):
        self.name = None
        self.death_date = None
        self.birth_date = None
        self.country = None
        self.type = None
        
        if blob:
            self.load(blob)
        
    def load(self, blob):
        person = getstruct(blob)
        self.name = person.get("name", None)
        bd = person.get("birth_date", None)
        if bd:
            try:    self.birth_date = datetime(int(bd[:4]), int(bd[4:6]), int(bd[6:8]))
            except: raise ValueError("'birth_date' is malformed. Correct format is 'YYYYMMDD'")
        dd = person.get("death_date", None)
        if dd:
            try:    self.death_date = datetime(int(dd[:4]), int(dd[4:6]), int(dd[6:8]))
            except: raise ValueError("'death_date' is malformed. Correct format is 'YYYYMMDD'")

        else:
            if self.birth_date:
                self.death_date = self.birth_date + timedelta(days=36525)    # 100 years
                assumptions.append("Didn't get date of death; assuming death after 100 years.")

        self.country = person.get("country", None)
        try:    self.type = person.get("type")
        except: raise ValueError("'type' is a mandatory field for legal entities/persons")
            
    def is_eu(self):
        return self.country in EU_COUNTRIES
    
    def is_eea(self):
        #print EEA_COUNTRIES
        return self.country in EEA_COUNTRIES
        
    def is_treaty(self):
        return TREATY_COUNTRIES.get(self.country, False)


    def death_years(self, when):
        return (when - self.death_date).days / 365.25
        
    
        
                    

class Work:
    def __init__(self, blob=None):
        self.type = None
        self.items = []
        self.authors = []
        self.publishers = []
        self.date = None
        self.creationdate = None
        self.title = None
        self.original = None
        self.country = None
        self.published = True
        self.original = True
        self.changed = False;
        
        if blob:
            self.load(blob)
        
    def load(self, blob):
        thing = getstruct(blob)
            
        self.title = thing.get("title", None)
        self.original = thing.get("original", True);
        self.authors = [LegalEntity(x) for x in thing.get("authors", [])]
        self.publishers = [LegalEntity(x) for x in thing.get("publishers", [])]


        self.creationdate = thing.get("creation_date", None)
        if self.creationdate:
            d = self.creationdate
            d = re.sub(r"\D+(\d\d\d\d)(\D+)?",r"\1", d); 
            if len(d) == 4: d += "0101"
            try: self.creationdate = datetime(int(d[:4]), int(d[4:6]), int(d[6:8]))
            except: print "invalid format for creation_date: %s" % self.creationdate

        try: self.date = thing.get("date")
        except: raise ValueError("'date' is a mandatory field for works.")

        try:    self.type = thing.get("type")
        except: raise ValueError("'type' is a mandatory field for works.")
    

    def str_to_datetime(self, date):
        return datetime.fromtimestamp(time.mktime(time.strptime(date, "%Y%m%d")))

    
    def is_artistic(self):
        if self.type in ["literary", "dramatic", "artistic"]: return True
        elif self.type == "photograph" and self.original: return True
        else: return False
    
    def eea(self):
        # is the author a citizen of the EEA?
        for person in self.authors:
            if person.type == "person" and person.is_eea(): return True
        # has the work been published in the EEA?
        return self.country in EEA_COUNTRIES
        
    def treaty(self):
        # is the author a citizen of a Treaty country?
        a = []
        for person in self.authors:
            if person.type == "person": 
                a.append(person.is_treaty())
        if a: return max(a)
        else: return 0
        
        
    def oldest_author(self):
        oldest = 0
        for a in self.authors: 
            if a.death_date and a.death_date.year > oldest:
                oldest = a

        return oldest
        
        
    def publication_years(self, when):
        return (when - self.str_to_datetime(self.date)).days / 365.25
        
    def creation_years(self, when):
        return (when - self.creationdate).days / 365.25
        
    def last_changed(self, when):
        date = self.changed or self.date;
        return (when - date).days / 365.25
        
        
    
calculators = {}


def register_calculator(jurisdiction, calc):
    calculators[jurisdiction.lower()] = calc


class Calculator:
    """A Public Domain Calculator
        when=None means today's date
    """
    def __init__(self, where):
        self.author_list = None
        self.death_dates = []
        self.names = []
        self.when = when
        self.where = where
        
        if calculators.has_key(self.where):
            self.calc = calculators[self.where]()
        else:
            raise ValueError("No calculator for jurisdiction %s is known" % self.where)
        
    def get_status(self, work, when=None):
        calc.get_status(work, when)
        

class CalculatorBase:
    
    def __init__(self):
       pass

    def get_status(self, work, when=None):
        raise NotImplementedError("not implemented")
        
        
    
        
    
    
class CalculatorUK(CalculatorBase):

    def __init__(self):
        register_calculator("uk", CalculatorUK)

    def get_status(self, work, when=None):
        if not when: when = datetime.now()
            
        if work.is_artistic():
            
            if any(x.type == "person" for x in work.authors):
                if work.eea():
                    if work.oldest_author():
                        return work.oldest_author().death_years(when) > 70
                    else:
                        assumptions.append("Didn't get date of death or birth; assuming death after 100 years fro, creation/publication.")
                        return work.creation_years(when) > 70

                t = work.treaty()
                if t: 
                    if work.oldest_author():

                        return work.oldest_author().death_years(when) > t
                
                    else:
                        assumptions.append("Didn't get date of death or birth; assuming death after 100 years fro, creation/publication.")
                        return work.creation_years(when) > 70

                else:
                    print "Work is not eligible for protection in because it has not been created in a EEA or Treaty country"
                    return True 
            
            if any(x.type == "anonymous" or x.type == "organization" for x in work.authors):
                
                return work.publication_years > 70
                
            if any(x.type == "computer" for x in work.authors):
                
                return work.publication_years > 50
                
            if any(x.type == "government" for x in work.authors):
                
                if work.published: return work.creation_years > 125
                else: return (work.creation_years.year > 125 or work.publication_years.year > 50)
                    
        elif work.type in ["recording", "broadcast", "performance"] or (work.type == "film" and work.original == False):
            
            return work.publication_years(when) > 50
            
        elif work.type == "database" and work.original == False:
            
            return work.last_changed() > 15
            
        elif work.type == "typographic":
            
            return work.publication_years() > 25
            
        else:
            raise ValueError("cannot get status")


        

if __name__ == "__main__":
    register_calculator("uk", CalculatorUK)
    data = json.dumps({ 
                            "title":"Collected Papers on the Public Domain (ed)", 
                            "type": "photograph",
                        "date" : "20030101",
                        "creation_date" : "20030101",
                        "authors" : 
                                        [
                                                {"name" : "Boyle, James", 
                                                "type" : "person",
                                                "birth_date" :"19590101",
                                                "death_date" : "19890205",
                                                "country": "uk"
                                                },
                                                {"name" : "Schumann, Robert",
                                                "type" : "person",
                                                "birth_date" :"18590101",
                                                "death_date" : "19990205",
                                                "country": "uk"
                                                }
                                        ]
                        })
    
    mywork = Work(data)
    calcUK = CalculatorUK()
    print calcUK.get_status(mywork)



    data2 = {
            "title": "I love flowers",
            "type": "recording",
            "date": "19450101",
            "creation_date": "19450101",
                        "authors" :
                                        [
                                                {"name" : "Schumann, Robert",
                                                "type" : "person",
                                                "birth_date" :"18590101",
                                                "death_date" : "18990205",
                                                "country": "uk"
                                                }
                                         ]
                         }

            
    mywork2 = Work(data2)
    print calcUK.get_status(mywork2)


    
    
    
