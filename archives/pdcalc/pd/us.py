from pdcalc.pd import CalculatorBase

class CalculatorUnitedStates(CalculatorBase):
    def __init__(self, when=None):
        CalculatorBase.__init__(self,when)

    def get_work_status(self, work):
        super(CalculatorUnitedStates, self).get_work_status(work)
        if self.when == None:
            self.calc_result.log.append('No date was given. Calculating public domain for today')

        # Call this when we know when pd expires
        def pd_expires(expiry_date):
            if expiry_date > self._now:
                self.calc_result.pd_prob = 0.0
            else:
                self.calc_result.pd_prob = 1.0
            return self.calc_result        
        
        self.calc_result.log.append("We're assuming it was published.")
        self.calc_result.log.append("We're assuming it was published in the US.")
        self.calc_result.log.append("We're assuming it was published with a valid copyright notice.")

        # Different rules depending on when it was published
        pubyear = self.work.date_ordered
        if pubyear < 1923:
            # PUBLICATION + 28+28 years
            self.calc_result.log.append('Published before 1923 (actually %s)' % pubyear)
            expiry = float(int(pubyear + 28 + 28))
            self.calc_result.log.append('PD expires at "publication + 28 + 28" (%s + 28 + 28 = %s)' % (pubyear, expiry))
            return pd_expires(expiry)
        elif pubyear < 1964:
            # PUBLICATION + 95 years
            self.calc_result.log.append('Published between 1923 and 1964 (actually %s)' % pubyear)
            self.calc_result.log.append('Assuming its copyright was renewed')
            expiry = float(int(pubyear + 95))
            self.calc_result.log.append('PD expires at "publication + 95" (%s + 95 = %s)' % (pubyear, expiry))
            return pd_expires(expiry)
        elif pubyear < 1978:
            # PUBLICATION + 95 years
            self.calc_result.log.append('Published between 1964 and 1978 (actually %s)' % pubyear)
            expiry = float(int(pubyear + 95))
            self.calc_result.log.append('PD expires at "publication + 95" (%s + 95 = %s)' % (pubyear, expiry))
            return pd_expires(expiry)
            pdyear = pubyear + 95

        # DEATH + 70 years
        self.calc_result.log.append('Published after 1978 (actually %s)' % pubyear)
        self.calc_result.log.append('Assuming it was not published by a corporation or under a pseudonym.')
        self.calc_death_dates()
        expiry = float(int(self.calc_result.most_recent_death_date + 70))
        self.calc_result.log.append('PD expires at "death + 70" (%s + 70 = %s)' % (self.calc_result.most_recent_death_date, expiry))
        return pd_expires(expiry)

