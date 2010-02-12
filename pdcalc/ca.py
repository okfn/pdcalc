from pdw.pd import *
            
class CalculatorCanada(CalculatorBase):
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

