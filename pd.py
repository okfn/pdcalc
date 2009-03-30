"""Determine copyright status of works given relevant information such as
creator death date.

# TODO: internationalize this
# TODO: function to calculate PD date (i.e. date at which work goes PD)

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
    def status(self, work):

class CalculatorUK(CalculatorBase):
    pass
"""
import logging
import datetime

logger = logging.getLogger('pdw.pd')

class CopyrightStatus:
    UNKNOWN = 0
    OUT = 1
    IN = 2

today = datetime.date.today()
def out_of_authorial_copyright(death_date, when=today):
    '''
    TODO: support birth_date (for cases where death_date not known)

    '''
    life_plus_70 = datetime.date(death_date.year + 70, death_date.month,
            death_date.day) 
    if life_plus_70 <= when:
        return True
    else:
        return False

def out_of_recording_copyright(release_date):
    # Europe is 50 years for US and elsewhere this will be different
    today = datetime.date.today()
    release_plus_50 = datetime.date(release_date.year + 50, release_date.month,
            release_date.day) 
    return release_plus_50 <= today

def copyright_status(performance):
    if not performance.work:
        return CopyrightStatus.UNKNOWN
    if len(performance.work.persons) == 0: # something wrong ...
        return CopyrightStatus.UNKNOWN
    for creator in performance.work.persons:
        if creator.death_date:
            # TODO: deal with stuff like '?'
            if not out_of_authorial_copyright(creator.death_date):
                return CopyrightStatus.IN
        else:
            return CopyrightStatus.UNKNOWN
    if not out_of_recording_copyright(performance.date):
        return CopyrightStatus.IN
    return CopyrightStatus.OUT


from pdw.search import Titlizer
class PDCalculator(object):
    '''A Public Domain Calculator.

    Stateful: store pdstatus and info in variables of that name. Should call
    reset before running with different data.
    '''
    def __init__(self, now=datetime.date.today().year, jurisdiction='uk'):
        self.now = now
        self.jurisdiction = jurisdiction
        if self.jurisdiction != 'uk':
            logger.warn('Only the UK jurisdiction is currently supported')
        self.reset()

    def reset(self):
        self.info = { 'title': '',
                'errors': '',
                'warnings': [],
                'authority': [] }
        self.pdstatus = False

    def work_status(self, work):
        self.info['authority'].append(work.id)
        for p in work.persons:
            self.info['authority'].append([p.name, p.death_date])
            if not p.death_date or p.death_date > '1933':
                self.pdstatus = False
        self.pdstatus = True

    def item_status(self, item):
        '''Calculate PD for an item.

        1. match by work title and author simultaneously
        2. If that fails search by author(s) and 
        '''
        self.info['warnings'].append('S1')
        work = self.find_work(item)
        if work:
            self.work_status(work)
            return
        if not item.persons:
            self.info['errors'] = 'ERROR: no authors for %s' % normtitle
            return
        self.info['warnings'].append('S2')
        # try by (first) author alone
        first_author_name = clean_name(item.persons[0].name)
        self.status_by_name(first_author_name)

    def find_work(self, item, search_if_not_there=True):
        if item.work:
            return item.work
        elif not search_if_not_there:
            return None

        # TODO: put this under test
        return search.get_work_for_item(item)

    def person_status(self, person):
        # NB: None < '1933'
        if p.death_date is None:
            score = -0.5
        elif p.death_date < '1933':
            score = 1
        else:
            score = -3
        return score

    def status_by_name(self, names):
        '''Compute based on a list of author names alone.''' 
        persons = model.Person.query.filter(
                model.Person.name.ilike(first_author_name + '%')
                ).limit(10).all()
        if not persons:
            self.info['warnings'].append('No person found with name: %s' % first_author_name)
            return
        # TODO: rather than require all to be PD pick those with most
        # works
        # self.info['warnings'].append('Found %s matching author name' % len(persons))
        score = 0
        for p in persons:
            self.info['authority'].append([p.name, p.death_date])
            # NB: None < '1933'
            score += self.person_status(p)
        if score > 0:
            self.pdstatus = True
            return
        else:
            return

