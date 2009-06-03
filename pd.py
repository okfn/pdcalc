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

class CalculatorUk(CalculatorBase):
    def __init__(self, when=None):
        CalculatorBase.__init__(self, when)

    def get_work_status(self, parcel):
        assert type(parcel) == CalcParcel
        work = parcel.work

        # Call this when we know when pd expires
        def pd_expires(expiry_date, parcel):
            if expiry_date > self._now:
                parcel.pd_prob = 0.0
            else:
                parcel.pd_prob = 1.0
            parcel.uncertainty = 0.0
            parcel.date_pd = expiry_date
            parcel.calc_finished = True
            return parcel        
        
        # Is it a sound recording?
        if work.type == 'recording':
            # YES
            parcel.log.append('Sound recording')
            # PUB + 1st Jan + 50
            pub_date = work.date_ordered
            parcel.log.append('Assuming the date given for the work is the date of first publication: %s' % pub_date)
            expiry = float(int(pub_date + 1 + 50))
            parcel.log.append('PD expires at "first publication + 1st Jan + 50" (%s + 50 = %s)' % (pub_date, expiry))
            return pd_expires(expiry, parcel)
        elif not work.type:
            # assume no
            parcel.log.append('No "type" stored - assuming literary work')
        else:
            # no
            parcel.log.append('Literary / musical work (not sound recording) (%s)' % work.type)
        # NO

        # Is it anonymous?
        self.calc_anon(parcel)
        if parcel.is_anon:
            # YES
            parcel.log.append('Anonymous work - %s' % self.get_author_list(parcel))
            pub_date = work.date_ordered
            
            # PUB + 1st Jan + 70 years
            expiry = float(int(pub_date + 1 + 70))
            parcel.log.append('PD expires at "first publication + 1st Jan + 70" (%s + 70 = %s)' % (pub_date, expiry))
            return pd_expires(expiry, parcel)
        # NO
        # DEATH + 1st Jan + 70 years
        self.calc_death_dates(parcel)
        expiry = float(int(parcel.most_recent_death_date + 1 + 70))
        parcel.log.append('PD expires at "death + 1st Jan + 70" (%s + 70 = %s)' % (parcel.most_recent_death_date, expiry))
        return pd_expires(expiry, parcel)

class CalculatorUnitedStates(CalculatorBase):
    def __init__(self, when=None):
        CalculatorBase.__init__(self, when)

    def get_work_status(self, parcel):
        assert type(parcel) == CalcParcel
        
        work = parcel.work
        
        # Call this when we know when pd expires
        def pd_expires(expiry_date, parcel):
            if expiry_date > self._now:
                parcel.pd_prob = 0.0
            else:
                parcel.pd_prob = 1.0
            return parcel        
        
        parcel.log.append("We're assuming it was published.")
        parcel.log.append("We're assuming it was published in the US.")
        parcel.log.append("We're assuming it was published with a valid copyright notice.")

        # Different rules depending on when it was published
        pubyear = work.date_ordered
        if pubyear < 1923:
            # PUBLICATION + 28+28 years
            parcel.log.append('Published before 1923 (actually %s)' % pubyear)
            expiry = float(int(pubyear + 28 + 28))
            parcel.log.append('PD expires at "publication + 28 + 28" (%s + 28 + 28 = %s)' % (pubyear, expiry))
            return pd_expires(expiry, parcel)
        elif pubyear < 1964:
            # PUBLICATION + 95 years
            parcel.log.append('Published between 1923 and 1964 (actually %s)' % pubyear)
            parcel.log.append('Assuming its copyright was renewed')
            expiry = float(int(pubyear + 95))
            parcel.log.append('PD expires at "publication + 95" (%s + 95 = %s)' % (pubyear, expiry))
            return pd_expires(expiry, parcel)
        elif pubyear < 1978:
            # PUBLICATION + 95 years
            parcel.log.append('Published between 1964 and 1978 (actually %s)' % pubyear)
            expiry = float(int(pubyear + 95))
            parcel.log.append('PD expires at "publication + 95" (%s + 95 = %s)' % (pubyear, expiry))
            return pd_expires(expiry, parcel)
            pdyear = pubyear + 95

        # DEATH + 70 years
        parcel.log.append('Published after 1978 (actually %s)' % pubyear)
        parcel.log.append('Assuming it was not published by a corporation or under a pseudonym.')
        self.calc_death_dates(parcel)
        expiry = float(int(parcel.most_recent_death_date + 70))
        parcel.log.append('PD expires at "death + 70" (%s + 70 = %s)' % (parcel.most_recent_death_date, expiry))
        return pd_expires(expiry, parcel)
        

            
class CalculatorCanada(CalculatorBase):
    def __init__(self, when=None):
        CalculatorBase.__init__(self, when)

    def get_work_status(self, parcel):
        assert type(parcel) == CalcParcel
        
        work = parcel.work
        
        # Call this when we know when pd expires
        def pd_expires(expiry_date, parcel):
            if expiry_date > self._now:
                parcel.pd_prob = 0.0
            else:
                parcel.pd_prob = 1.0
            return parcel        
        
        # Is it a photograph?
        if work.type == 'photograph':
            assert NotImplementedError
        # NO
        if not work.type:
            parcel.log.append('Work type not given - assuming it is not a photograph')
        parcel.log.append('Work is not a photograph')

        # Is it crown author?
        # NO
        parcel.log.append('Assuming not a crown author')

        # Is it an anonymous author?
        self.calc_anon(parcel)
        if parcel.is_anon:
            # YES
            assert NotImplementedError
        parcel.log.append('Author known')
        # NO

        # Are any authors living?
        self.calc_death_dates(parcel)
        if parcel.an_author_lives:
            # YES
            parcel.log.append('Author alive %s' % repr(parcel.death_dates))
            parcel.pd_prob = 0.0
            parcel.uncertainty = 0.0
            return parcel
        # NO
        parcel.log.append('Author dead %s' % (repr(parcel.death_dates)))

        # Is it a published work?
        if not work.items:
            parcel.log.append('No item attached to work. Assuming this is a published work though.')
        # YES
        parcel.log.append('Published work')

        # Any authors living on date of publication?
        if parcel.most_recent_death_date > work.date_ordered:
            # YES
            parcel.log.append('Author living on date of publication (%s)' % work.date_ordered)
            # DEATH + 50
            parcel.log.append('PD expires at "death + 50" (%s + 50 = %s)' % (parcel.most_recent_death_date, parcel.most_recent_death_date + 50))
            return pd_expires(parcel.most_recent_death_date + 50, parcel)
        #NO
        parcel.log.append('Author dead on date of publication (%s)' % work.date_ordered)

        # Published before Jan 1, 1999?
        if work.date_ordered < float_date(1999, 1, 1):
            # YES
            parcel.log.append('Published before Jan 1, 1999 (%s)' % work.date_ordered)

            # PUBLICATION + 50
            parcel.log.append('PD expires at "publication + 50" (%s + 50 = %s)' % (work.date_ordered, work.date_ordered + 50))
            return pd_expires(work.date_ordered + 50, parcel)
        # NO
        parcel.log.append('Published after Jan 1, 1999 (%s)' % work.date_ordered)
        # DEATH + 50
        parcel.log.append('PD expires at "death + 50" (%s + 50 = %s)' % (parcel.most_recent_death_date, parcel.most_recent_death_date + 50))
        return pd_expires(parcel.most_recent_death_date + 50, parcel)


