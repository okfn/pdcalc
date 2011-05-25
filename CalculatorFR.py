#!/usr/bin/env python

from Calculator import *

from datetime import datetime


try:
    import json
except ImportError:
    import simplejson as json


    
class CalculatorFR(CalculatorBase):

    def __init__(self):
	super(CalculatorFR, self).__init__()



    def get_status(self, work, when=None): # when=None means today's date
        

	if not when: when = datetime.now()
            
	""" If the Work is an unoriginal database? """
        if work.is_db():
		self.assumptions.append("Assuming that the author of the work is also the right holder.")
			
		""" was the DB created by an individual or organisation resident or registrated in an EEA state? """ # no need to distinguish between corporate or individual because the consequences are the same
		if not work.eea():	return False
		
		else:
			""" was the DB made available to the public after its completion or last substantial change? """
			if work.changed: 
				return work.last_changed() < 15
			else:
				self.assumptions.append("Assuming that the DB was made available to the public after its completion or last substantial change.")
					
				""" was the DB made available to the public in the last 15 years? """
				return work.publication_years() < 15
							

	elif work.is_artistic():
           
 
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


register_calculator("fr", CalculatorFR)
        

if __name__ == "__main__":
    register_calculator("uk", CalculatorFR)
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
    calcUK = CalculatorFR()
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


    
    
    
