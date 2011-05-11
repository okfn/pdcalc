from pdcalc.pd import *
            
class CalculatorCanada(CalculatorBase):

    def __init__(self,when=None):
        CalculatorBase.__init__(self, when)


    def get_work_status(self, work):
        super(CalculatorCanada, self).get_work_status(work)
        if self.when == None:
            self.calc_result.log.append('No date was given. Calculating public domain for today')
        
        # Call this when we know when pd expires
        def pd_expires(expiry_date):
            if expiry_date > self._now:
                self.calc_result.pd_prob = 0.0
            else:
                self.calc_result.pd_prob = 1.0
            return self.calc_result
        
        # Is it a photograph?
        if work.type == 'photograph':
            assert NotImplementedError
        else:
            self.calc_result.log.append('Work is not a photograph')
        # NO
        if not work.type:
            self.calc_result.log.append('Work type not given - assuming it is not a photograph')
        self.calc_result.log.append('Assuming not a crown author')


        # Is it crown author?
        # NO

        # Is it an anonymous author?
        self.calc_anon()
        if self.calc_result.is_anon:
            # YES
            assert NotImplementedError
        self.calc_result.log.append('Author known')
        # NO

        # Are any authors living?
        self.calc_death_dates()
        if self.calc_result.an_author_lives:
            # YES
            self.calc_result.log.append('Author alive %s' % repr(self.calc_result.death_dates))
            self.calc_result.pd_prob = 0.0
            self.calc_result.uncertainty = 0.0
            return self.calc_result
        # NO
        self.calc_result.log.append('Author dead %s' % (repr(self.calc_result.death_dates)))

        # Is it a published work?
        if not work.items:
            self.calc_result.log.append('No item attached to work. Assuming this is a published work though.')
        # YES
        self.calc_result.log.append('Published work')

        # Any authors living on date of publication?
        if self.calc_result.most_recent_death_date > work.date_ordered:
            # YES
            self.calc_result.log.append('Author living on date of publication (%s)' % work.date_ordered)
            # DEATH + 50
            self.calc_result.log.append('PD expires at "death + 50" (%s + 50 = %s)' % (self.calc_result.most_recent_death_date, self.calc_result.most_recent_death_date + 50))
            return pd_expires(self.calc_result.most_recent_death_date + 50)
        #NO
        self.calc_result.log.append('Author dead on date of publication (%s)' % work.date_ordered)

        # Published before Jan 1, 1999?
        if work.date_ordered < float_date(1999, 1, 1):
            # YES
            self.calc_result.log.append('Published before Jan 1, 1999 (%s)' % work.date_ordered)

            # PUBLICATION + 50
            self.calc_result.log.append('PD expires at "publication + 50" (%s + 50 = %s)' % (work.date_ordered, work.date_ordered + 50))
            return pd_expires(work.date_ordered + 50)
        # NO
        self.calc_result.log.append('Published after Jan 1, 1999 (%s)' % work.date_ordered)
        # DEATH + 50
        self.calc_result.log.append('PD expires at "death + 50" (%s + 50 = %s)' % (self.calc_result.most_recent_death_date, self.calc_result.most_recent_death_date + 50))
        return pd_expires(self.calc_result.most_recent_death_date + 50)

