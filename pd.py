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
    def get_work_status(self, work):

class CalculatorUK(CalculatorBase):
    pass
"""
import logging
import datetime
import swiss

logger = logging.getLogger('pdw.pd')

def float_date(year, month=0, day=0):
    return swiss.date.FlexiDate(year, month, day).as_float()

class PdStatus:
    def __init__(self):
        self.pd_prob = 0.0 # P(is PD)
        self.uncertainty = 0.0
        self.log = [] # strings

def determine_status(work, jurisdiction):
    # now dispatch on jurisdiction (+ work type?)
    if jurisdiction == 'canada':
        pd_calculator = CalculatorCanada
    else:
        logger.error('Jurisdiction "%s" not currently supported.' % jurisdiction)
        assert 0
        
    return pd_calculator(when=now).get_work_status(work)


class CalculatorBase(object):
    def get_work_status(self, work):
        raise NotImplementedError()

class CalculatorUK(CalculatorBase):
    def get_work_status(self, work):
        raise NotImplementedError()

class CalculatorCanada(CalculatorBase):
    """A Public Domain Calculator
    when=None means today's date
    """
    def __init__(self, when=None):
        if when:
            self._now = when
        else:
            self._now = float_date(datetime.date.today().year)
        self._jurisdiction = 'canada'

    def get_work_status(self, work):
        pdstatus = PdStatus()

        # Call this when we know when pd expires
        def pd_expires(expiry_date, pdstatus):
            if expiry_date > self._now:
                pdstatus.pd_prob = 0.0
            else:
                pdstatus.pd_prob = 1.0
            return pdstatus        
        
        # Is it a photograph?
        if work.type == 'photograph':
            assert NotImplementedError
        # NO
        if not work.type:
            pdstatus.log.append('Work type not given - assuming it is not a photograph')
        pdstatus.log.append('Work is not a photograph')

        # Is it crown author?
        # NO
        pdstatus.log.append('Assuming not a crown author')

        # Is it an anonymous author?
        is_anon = False
        for person in work.persons:
            if 'anon' in person.name.lower():
                is_anon = True
        if work.persons == []:
            pdstatus.log.append('No authors given: assuming anonymous')
            is_anon = True
        if is_anon:
            assert NotImplementedError
        pdstatus.log.append('Author known')
        # NO

        # Are any authors living?
        death_dates = [] # list of: (name, float date)
        names = []
        most_recent_death_date = 0.0
        for person in work.persons:
            death_date = person.death_date_ordered
            death_dates.append((person.name, death_date))
            if death_date and death_date > most_recent_death_date:
                most_recent_death_date = death_date
        an_author_lives = False
        for name, death_date in death_dates:
            if not death_date:
                # alive: big assumption!
                pdstatus.log.append('Author "%s" death date not given - assuming alive' % name)
                an_author_lives = True
        if an_author_lives:
            # YES
            pdstatus.log.append('Author alive %s' % repr(death_dates))
            pdstatus.pd_prob = 0.0
            pdstatus.uncertainty = 0.0
            return pdstatus
        # NO
        pdstatus.log.append('Author dead %s' % (repr(death_dates)))

        # Is it a published work?
        if not work.item:
            pdstatus.log.append('No item attached to work. Assuming this is a published work though.')
        # YES
        pdstatus.log.append('Published work')

        # Any authors living on date of publication?
        if most_recent_death_date > work.date_ordered:
            # YES
            pdstatus.log.append('Author living on date of publication (%s)' % work.date_ordered)
            # DEATH + 50
            pdstatus.log.append('PD expires at "death + 50" (%s + 50 = %s)' % (most_recent_death_date, most_recent_death_date + 50))
            return pd_expires(most_recent_death_date + 50, pdstatus)
        #NO
        pdstatus.log.append('Author dead on date of publication (%s)' % work.date_ordered)

        # Published before Jan 1, 1999?
        if work.date_ordered < float_date(1999, 1, 1):
            # YES
            pdstatus.log.append('Published before Jan 1, 1999 (%s)' % work.date_ordered)

            # PUBLICATION + 50
            pdstatus.log.append('PD expires at "publication + 50" (%s + 50 = %s)' % (work.date_ordered, work.date_ordered + 50))
            return pd_expires(work.date_ordered + 50, pdstatus)
        # NO
        pdstatus.log.append('Published after Jan 1, 1999 (%s)' % work.date_ordered)
        # DEATH + 50
        pdstatus.log.append('PD expires at "death + 50" (%s + 50 = %s)' % (most_recent_death_date, most_recent_death_date + 50))
        return pd_expires(most_recent_death_date + 50, pdstatus)


    

