import pdw.pd as pd
from datetime import datetime

class TestPDStatusCanada:
    def __init__(self):
        self.jurisdiction = 'canada'

    @classmethod
    def setup_class(self):
        class X:
            pass

        artist = X()
        artist.name = 'Bloggs, Joe'
        artist.death_date_ordered = 1900.0

        work = X()
        work.title = 'Song for the Common Man'
        work.persons = [ artist ]
        work.date_ordered = 1945.0
        work.type = 'composition'

        item = X()
        item.title = 'Songs CD'
        item.date_ordered = 1955.0
        item.work = work

        work.item = item

        self.artist = artist
        self.work = work
        self.item = item

    def _log_has(self, str, log):
        for log_line in log:
            if str in log_line:
                return True
        return False
        
    def test_work_status_1(self):
        self.artist.death_date_ordered = 1900.0
        self.work.date_ordered = 1945.0

        pdstatus = pd.determine_status(self.work, self.jurisdiction)
        print pdstatus.log
        assert self._log_has('publication + 50', pdstatus.log)
        assert pdstatus.pd_prob == 1.0

    def test_work_status_2(self):
        self.artist.death_date_ordered = 1930.0
        self.work.date_ordered = 1965.0

        pdstatus = pd.determine_status(self.work, self.jurisdiction)
        print pdstatus.log
        assert self._log_has('publication + 50', pdstatus.log)
        assert pdstatus.pd_prob == 0.0

    def test_work_status_3(self):
        self.artist.death_date_ordered = 1960.0
        self.work.date_ordered = 1945.0

        pdstatus = pd.determine_status(self.work, self.jurisdiction)
        print pdstatus.log
        assert self._log_has('death + 50', pdstatus.log)
        assert pdstatus.pd_prob == 0.0

    def test_work_status_4(self):
        self.artist.death_date_ordered = 1860.0
        self.work.date_ordered = 1845.0

        pdstatus = pd.determine_status(self.work, self.jurisdiction)
        print pdstatus.log
        assert self._log_has('death + 50', pdstatus.log)
        assert pdstatus.pd_prob == 1.0

    def test_work_status_5(self):
        self.artist.death_date_ordered = None
        self.work.date_ordered = 1945.0

        pdstatus = pd.determine_status(self.work, self.jurisdiction)
        print pdstatus.log
        assert self._log_has('Author alive', pdstatus.log)
        assert pdstatus.pd_prob == 0.0

