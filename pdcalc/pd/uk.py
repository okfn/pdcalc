from pdcalc.pd import CalculatorBase

class CalculatorUk(CalculatorBase):
    def __init__(self, when=None):
        CalculatorBase.__init__(self,when)

    def get_work_status(self, work):
        super(CalculatorUk, self).get_work_status(work)
        if self.when == None:
            self.calc_result.log.append('No date was given. Calculating public domain for today')

        # Call this when we know when pd expires
        def pd_expires(expiry_date):
            if expiry_date > self._now:
                self.calc_result.pd_prob = 0.0
            else:
                self.calc_result.pd_prob = 1.0
            self.calc_result.uncertainty = 0.0
            self.calc_result.date_pd = expiry_date
            self.calc_result.calc_finished = True
            return self.calc_result
        def dont_know():
            self.calc_result.uncertainty = 1.0
            self.calc_result.pd_prob = 0.0
            self.calc_result.calc_finished = True
            return self.calc_result
        
        # Is it a sound recording?
        if work.type == 'recording':
            # YES
            self.calc_result.log.append('Sound recording')
            # PUB + 1st Jan + 50
            pub_date = work.date_ordered
            self.calc_result.log.append('Assuming the date given for the work is the date of first publication: %s' % pub_date)
            if not pub_date:
                # TODO
                return dont_know()
            expiry = float(int(pub_date + 1 + 50))
            self.calc_result.log.append('PD expires at "first publication + 1st Jan + 50" (%s + 50 = %s)' % (pub_date, expiry))
            return pd_expires(expiry)
        elif not work.type:
            # assume no
            self.calc_result.log.append('No "type" stored - assuming literary work')
        else:
            # no
            self.calc_result.log.append('Literary / musical work (not sound recording) (%s)' % work.type)
        # NO

        # Is it anonymous?
        self.calc_anon()
        if self.calc_result.is_anon:
            # YES
            self.calc_result.log.append('Anonymous work - %s' % self.get_author_list(self.calc_result))
            pub_date = work.date_ordered
            if not pub_date:
                # TODO
                return dont_know()
            
            # PUB + 1st Jan + 70 years
            expiry = float(int(pub_date + 1 + 70))
            self.calc_result.log.append('PD expires at "first publication + 1st Jan + 70" (%s + 70 = %s)' % (pub_date, expiry))
            return pd_expires(expiry)
        # NO
        # DEATH + 1st Jan + 70 years
        self.calc_death_dates()
        if not self.calc_result.most_recent_death_date:
            # TODO
            return dont_know()
        expiry = float(int(self.calc_result.most_recent_death_date + 1 + 70))
        self.calc_result.log.append('PD expires at "death + 1st Jan + 70" (%s + 70 = %s)' % (self.calc_result.most_recent_death_date, expiry))
        return pd_expires(expiry)

