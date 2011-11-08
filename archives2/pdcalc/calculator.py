#!/usr/bin/env python


import logging
from datetime import datetime, timedelta

import time
import re

try:
    import json
except ImportError:
    import simplejson as json

logger = logging.getLogger('pdcalc.pd')
    

calculators = {}

def register_calculator(jurisdiction, calc):
    calculators[jurisdiction.lower()] = calc

def get_calculator(jurisdiction):
    cls = calculators.get(jurisdiction.lower())
    if cls is not None:
        return cls()
    else:
        return None


class Calculator:
    """ Generic Public Domain Calculator """
  
    def __init__(self, where):
        self.where = where
        
        if calculators.has_key(self.where):
            self.calc = calculators[self.where]()
        else:
            raise ValueError("No calculator for jurisdiction %s is known" % self.where)

    def list(self): 
        return calculators.keys()
        
    def get_status(self, work, when=None): # when=None means today's date
        return self.calc.get_status(work, when)
        



class CalculatorBase(object):
    
    def __init__(self):
	self.assumptions = [] # where all assumptions made by each Calculator will be collected

    def get_status(self, work, when=None):
        raise NotImplementedError("not implemented")
        
        
    
        
    
    
