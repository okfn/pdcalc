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

OLDEST_PERSON = 100

logger = logging.getLogger('pdw.pd')

def float_date(year, month=0, day=0):
    return swiss.date.FlexiDate(year, month, day).as_float()

def determine_status(work, jurisdiction):
    # now dispatch on jurisdiction (+ work type?)
    # note two letter country codes based on ISO 3166
    if jurisdiction == 'us':
        pd_calculator = CalculatorUnitedStates
    elif jurisdiction == 'ca':
        pd_calculator = CalculatorCanada
    elif jurisdiction in ('uk', 'gb') :
        pd_calculator = CalculatorUk
    else:
        logger.error('Jurisdiction "%s" not currently supported.' % jurisdiction)
        assert 0

    parcel = CalcParcel(work, jurisdiction)

    return pd_calculator().get_work_status(parcel)


class CalcParcel(object):
    '''
    A CalcParcel object is passed into the calculator
    with the calculation request and stores calculation
    results, to be returned to the caller.
    '''
    def __init__(self, work, jurisdiction, when=None):
        # about the calc request
        self.work = work
        self.jurisdiction = jurisdiction
        if when:
            self.when = when
        else:
            self.when = float_date(datetime.date.today().year)

        # results
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
        raise NotImplementedError()

    def get_author_list(self, parcel):
        if self.author_list == None:
            self.author_list = []
            for person in parcel.work.persons:
                self.author_list.append(person.name)
        return self.author_list

    def calc_anon(self, parcel):
        parcel.is_anon = False
        for person in parcel.work.persons:
            if person.name.lower() in ('anon', 'anon.', 'anonymous') :
                parcel.is_anon = True

    def calc_death_dates(self, parcel):
        death_dates = [] # list of: (name, float date)
        names = []
        most_recent_death_date = 0.0
        for person in parcel.work.persons:
            death_date = person.death_date_ordered
            # if we have no deathdate but do have a birthdate, assume
            # death OLDEST_PERSON years after birth
            if not death_date and person.birth_date_ordered:
                death_date = person.birth_date_ordered + OLDEST_PERSON
                parcel.log.append('Author "%s" death date not given - assuming died %s years after birth (%s + %s = %s)' % (person.name, OLDEST_PERSON, person.birth_date_ordered, OLDEST_PERSON, death_date))
            death_dates.append((person.name, death_date))
            if death_date and death_date > most_recent_death_date:
                most_recent_death_date = death_date
        an_author_lives = False
        for name, death_date in death_dates:
            if not death_date:
                # no birthday
                # alive: big assumption!
                parcel.log.append('Author "%s" death date not given - assuming alive (!)' % name)
                an_author_lives = True

        parcel.death_dates = death_dates
        parcel.most_recent_death_date = most_recent_death_date
        parcel.an_author_lives = an_author_lives

from uk import *
from us import *
from ca import *
from fast import *

