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

try:
    import json
except ImportError:
    import simplejson as json

#from sqlalchemy import orm
import pdcalc


logger = logging.getLogger('pdcalc.pd')


OLDEST_PERSON = 100

now = datetime.datetime.now()

def float_date(year, month=1, day=1):
    '''to convert a date in a float type'''
    if year is not None:
        return float(int(year))
    else:
        return None

def determine_status(work, jurisdiction, when=None):
    # now dispatch on jurisdiction (+ work type?)
    # note two letter country codes based on ISO 3166
    # need to add 'when' parameter here and deeper 
    if jurisdiction == 'us':
        pd_calculator = CalculatorUnitedStates
    elif jurisdiction == 'ca':
        pd_calculator = CalculatorCanada
    elif jurisdiction in ('uk', 'gb') :
        pd_calculator = CalculatorUk
    else:
        logger.error('Jurisdiction "%s" not currently supported. Try us,ca,uk' % jurisdiction)
        raise NotImplementedError, "Jurisdiction not currently supported. Try us,ca,uk"
    return pd_calculator(when).get_work_status(work)

def determine_status_from_raw(json_data):
    '''
    To create a Work object and analize its pd status from a 
    python or json dict
    @param  params: json formatted string
    @type   params: string
    '''
    params = json.loads(json_data)
    if 'jur' in params:
        jur = params['jurisdiction'] 
    else:
        jur = 'uk'

    work = Work.from_dict(params['work'])
    if 'when' in params:
        when = float_date(params['when'][:4])
    else:
        when = None

    calculation = determine_status(work, jur, when)
    result = { 'input': params, 'result': calculation.to_dict() }
    return json.dumps(result,indent=2)


class WORK_TYPES:
    text = u'text'
    composition = u'composition'
    recording = u'recording'
    photograph = u'photograph'
    video = u'video'
    database = u'database'

class ENTITY_TYPES:
    person = u'person'
    organization = u'organization'
    unknown = u'unknown'

class DomainObject(object):
    def __init__(self):
        self._data = {}

    @classmethod
    def from_dict(cls, dict_):
        out = cls()
        out._data.update(dict(dict_))
        return out


class Work(DomainObject):
    def __init__(self):
        self._data = {
            'type': WORK_TYPES.text,
            'items': [],
            'persons': []
            }

    @property
    def persons(self):
        return [Person.from_dict(x) for x in self._data['persons']]

    @property
    def items(self):
        return self._data['items']

    @property
    def date_ordered(self):
        return float_date(self._data.get('date', None))

    @property
    def type(self):
        return self._data['type']

class Person(DomainObject):
    def __init__(self):
        self._data = {
            'death_date': None,
            'birth_date': None
            }

    @property
    def name(self):
        return self._data['name']

    @property
    def death_date_ordered(self):
        return float_date(self._data.get('death_date', None))

    @property
    def birth_date_ordered(self):
        return float_date(self._data.get('birth_date', None))


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

    def to_dict(self):
        '''Creates a dict result to give back as json in the api
        '''
        out_dict = { 'pd_uncertainty': self.uncertainty,
                    'pd_probability': self.pd_prob,
                    'death_dates': self.death_dates,
                    'log': self.log,
                    'when': self.when,
                   }
        return out_dict

class CalculatorBase(object):
    """A Public Domain Calculator
    when=None means today's date
    """
    def __init__(self,when=None):
        self.author_list = None
        self.death_dates = []
        self.names = []
        self.when = when
    
    def get_work_status(self, work):
        self.calc_result = CalcResult()
        self.work = work
        if self.when:
            self._now = float_date(self.when)
        else:
            self._now = float(int((datetime.datetime.now().year)))

    def get_author_list(self, parcel):
        if self.author_list == None:
            self.author_list = []
            for person in self.work.persons:
                self.author_list.append(person.name)
        return self.author_list

    def calc_anon(self):
        self.calc_result.is_anon = False
        for person in self.work.persons:
            if person.name and person.name.lower() in ('anon', 'anon.', 'anonymous') :
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
        self.calc_result.when = self._now

from uk import *
from us import *
from ca import *

