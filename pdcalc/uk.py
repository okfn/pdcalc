from pdw.pd import CalculatorBase

class CalculatorUk(CalculatorBase):
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
            parcel.uncertainty = 0.0
            parcel.date_pd = expiry_date
            parcel.calc_finished = True
            return parcel
        def dont_know():
            parcel.uncertainty = 1.0
            parcel.pd_prob = 0.0
            parcel.calc_finished = True
            return parcel
        
        # Is it a sound recording?
        if work.type == 'recording':
            # YES
            parcel.log.append('Sound recording')
            # PUB + 1st Jan + 50
            pub_date = work.date_ordered
            parcel.log.append('Assuming the date given for the work is the date of first publication: %s' % pub_date)
            if not pub_date:
                # TODO
                return dont_know()
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
            if not pub_date:
                # TODO
                return dont_know()
            
            # PUB + 1st Jan + 70 years
            expiry = float(int(pub_date + 1 + 70))
            parcel.log.append('PD expires at "first publication + 1st Jan + 70" (%s + 70 = %s)' % (pub_date, expiry))
            return pd_expires(expiry, parcel)
        # NO
        # DEATH + 1st Jan + 70 years
        self.calc_death_dates(parcel)
        if not parcel.most_recent_death_date:
            # TODO
            return dont_know()
        expiry = float(int(parcel.most_recent_death_date + 1 + 70))
        parcel.log.append('PD expires at "death + 1st Jan + 70" (%s + 70 = %s)' % (parcel.most_recent_death_date, expiry))
        return pd_expires(expiry, parcel)

