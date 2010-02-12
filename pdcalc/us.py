from pdw.pd import CalculatorBase

class CalculatorUnitedStates(CalculatorBase):
    def __init__(self, when=None):
        CalculatorBase.__init__(self, when)

    def get_work_status(self, parcel):
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

