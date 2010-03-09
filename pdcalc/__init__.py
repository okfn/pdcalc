"""Determine copyright status of works given relevant information such as
creator death date.

Remarks
=======

Often cannot calculate PD with certainty (at least in an automated process). Different kinds of uncertainty:

  * Do not know persons associated with work (with certainty or at all)
  * Do not know their death dates (may or may not know birth dates)
  * Do not know when work was published
  * etc

And this is even assuming we have identified the work (and/or whether it is a
translation, critical edition etc etc).

This uncertainty must therefore be presented. Core features

  * PD/Copyright status
  * Level of uncertainty ...
  * Comments
  * Compressed comments/Standard flags

Suggestions for flags:
  * normalized title
  * notes
  * translation

def determine_status(work, jurisdiction, when):
    # now dispatch on jurisdiction (+ work type?)

class CopyrightStatus:
    # Flags etc

class CalculatorBase:
    def get_work_status(self, work):

class CalculatorUK(CalculatorBase):
    pass
"""
import logging
import datetime

import swiss
try:
    import json
except ImportError:
    import simplejson as json

#from sqlalchemy import orm
import pdw


logger = logging.getLogger('pdw.pd')


OLDEST_PERSON = 100

now = datetime.datetime.now()
def float_date(year, month=0, day=0):
    return swiss.date.FlexiDate(year, month, day).as_float()

def determine_status(work, jurisdiction):
    # now dispatch on jurisdiction (+ work type?)
    # note two letter country codes based on ISO 3166
    # 
    if jurisdiction == 'us':
        pd_calculator = CalculatorUnitedStates
    elif jurisdiction == 'ca':
        pd_calculator = CalculatorCanada
    elif jurisdiction in ('uk', 'gb') :
        pd_calculator = CalculatorUk
    else:
        logger.error('Jurisdiction "%s" not currently supported. Try us,ca,uk' % jurisdiction)
        assert 0
    return pd_calculator().get_work_status(work)

def determine_status_from_raw(json_data):
    '''
    To create a Work object and analize its pd status from a 
    python or json dict
    '''

    params = json.loads(json_data)
    jur = params['jurisdiction'] 

    work =  pdw.model.Work.from_dict(params['work'])

    calculation = determine_status(work, jur)
    result = json.dumps({'pd_probability': calculation.pd_prob,
                        'confidence': 1-calculation.uncertainty,
                        'log': calculation.log,
                        'input': params},indent=2)
    return result


class CalcResult(object):
    '''A CalcResult object is returned by the calculator
    '''
    def __init__(self):
        self.calc_finished = False
        self.date_pd = None
        self.pd_prob = 0.0 # P(is PD)
        self.uncertainty = 0.0
        self.log = [] # strings

    def __str__(self):
        return "date_pd=%s pd_prob=%s log=%s" % (self.date_pd, self.pd_prob, self.log)

class CalculatorBase(object):
    """A Public Domain Calculator
    when=None means today's date
    """
    def __init__(self, when):
        self.author_list = None
        if when:
          self._now = when
        else:
            self._now = float_date(datetime.date.today().year)
    
    def get_work_status(self, work):
        self.calc_result = CalcResult()
        self.work = work

    def get_author_list(self, parcel):
        if self.author_list == None:
            self.author_list = []
            for person in self.work.persons:
                self.author_list.append(person.name)
        return self.author_list

    def calc_anon(self):
        self.calc_result.is_anon = False
        for person in self.work.persons:
            if person.name.lower() in ('anon', 'anon.', 'anonymous') :
                self.calc_result.is_anon = True

    def calc_death_dates(self):
        death_dates = [] # list of: (name, float date)
        names = []
        most_recent_death_date = 0.0
        for person in self.work.persons:
            death_date = person.death_date_ordered
            # if we have no deathdate but do have a birthdate, assume
            # death OLDEST_PERSON years after birth
            if not death_date and person.birth_date_ordered:
                death_date = person.birth_date_ordered + OLDEST_PERSON
                self.calc_result.log.append('Author "%s" death date not given - assuming died %s years after birth (%s + %s = %s)' % (person.name, OLDEST_PERSON, person.birth_date_ordered, OLDEST_PERSON, death_date))
            death_dates.append((person.name, death_date))
            if death_date and death_date > most_recent_death_date:
                most_recent_death_date = death_date
        an_author_lives = False
        for name, death_date in death_dates:
            if not death_date:
                # no birthday
                # alive: big assumption!
                self.calc_result.log.append('Author "%s" death date not given - assuming alive (!)' % name)
                an_author_lives = True

        self.calc_result.death_dates = death_dates
        self.calc_result.most_recent_death_date = most_recent_death_date
        self.calc_result.an_author_lives = an_author_lives

from uk import *
from us import *
from ca import *
from fast import *

