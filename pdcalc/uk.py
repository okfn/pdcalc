#!/usr/bin/env python

from calculator import *


import logging
from datetime import datetime, timedelta

import time
import re

try:
    import json
except ImportError:
    import simplejson as json


from work import Work


    
class CalculatorUK(CalculatorBase):

    def __init__(self):
	super(CalculatorUK, self).__init__()
        #register_calculator("uk", CalculatorUK)

    def get_status(self, work, when=None):
        

	if not when: when = datetime.now()
            
        if work.is_artistic():
           
 
            if any(x.type == "person" for x in work.authors):

                if work.eea():
                    if work.oldest_author():
                        return work.oldest_author().death_years(when) > 70
                    else:
                        self.assumptions.append("Didn't get date of death or birth; assuming death after 100 years fro, creation/publication.")
                        return work.creation_years(when) > 70

                t = work.treaty()
                if t: 
                    if work.oldest_author():

                        return work.oldest_author().death_years(when) > t
                
                    else:
                        self.assumptions.append("Didn't get date of death or birth; assuming death after 100 years fro, creation/publication.")
                        return work.creation_years(when) > 70

                else:
                    print "Work is not eligible for protection in because it has not been created in a EEA or Treaty country"
                    return True 
            
            if any(x.type == "anonymous" or x.type == "organization" for x in work.authors):
                
                return work.publication_years(when) > 70
                
            if any(x.type == "computer" for x in work.authors):
                
                return work.publication_years(when) > 50
                
            if any(x.type == "government" for x in work.authors):
                
                if work.published: return work.creation_years(when) > 125

                else: return (work.creation_years(when) > 125 or work.publication_years(when) > 50)
                    
        elif work.type in ["recording", "broadcast", "performance"] or (work.type == "film" and work.original == False):
            
            return work.publication_years(when) > 50
            
        elif work.type == "database" and work.original == False:
            
            return work.last_changed() > 15
            
        elif work.type == "typographic":
            
            return work.publication_years(when) > 25
            
        else:
            raise ValueError("cannot get status")


register_calculator("uk", CalculatorUK)
        
# Run this test: nosetests pdcalc/CalculatorFR.py
def test():

    calc = Calculator("uk")

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
    assert not calc.get_status(mywork)


    data = {
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

    mywork = Work(data)
    assert calc.get_status(mywork)


    
    
    
