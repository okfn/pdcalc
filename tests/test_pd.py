import pdw.pd as pd
from datetime import datetime

class TestPdStatusCanada:
    jurisdiction = 'ca'

    def setUp(self):
        class X:
            pass

        artist = X()
        artist.name = 'Bloggs, Joe'
        artist.death_date_ordered = 1900.0
        artist.birth_date_ordered = None

        work = X()
        work.title = 'Song for the Common Man'
        work.persons = [ artist ]
        work.date_ordered = 1945.0
        work.type = 'composition'

        item = X()
        item.title = 'Songs CD'
        item.date_ordered = 1955.0
        item.works = [work]

        work.items = [item]

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

class TestPdStatusUk:
    jurisdiction = 'uk'

    @classmethod
    def setUp(self):
        class X:
            pass

        composer = X()
        composer.name = 'Schumann, Robert'
        composer.birth_date_ordered = 1830.0
        composer.death_date_ordered = 1900.0

        singer = X()
        singer.name = 'Terfel, Bryn'
        singer.birth_date_ordered = 1974
        singer.death_date_ordered = None

        composition_work = X()
        composition_work.title = 'I love flowers'
        composition_work.persons = [ composer ]
        composition_work.date_ordered = 1945.0
        composition_work.type = 'composition'

        recording_work = X()
        recording_work.title = 'Bryn Terfel sings "I love flowers"'
        recording_work.persons = [ composer, singer ]
        recording_work.date_ordered = 1945.0
        recording_work.type = 'recording'

        cd_item = X()
        cd_item.title = 'Songs CD'
        cd_item.date_ordered = 1985.0
        cd_item.works = [composition_work, recording_work]

        score_item = X()
        score_item.title = 'Song score'
        score_item.date_ordered = 1955.0
        score_item.works = [composition_work]

        composition_work.items = [cd_item, score_item]

        self.composer = composer
        self.composition_work = composition_work
        self.recording_work = recording_work
        self.cd_item = cd_item
        self.score_item = score_item


    def _log_has(self, str, log):
        for log_line in log:
            if str in log_line:
                return True
        return False
        
    def test_work_status_1(self):
        self.composer.death_date_ordered = 1900.0

        pdstatus = pd.determine_status(self.composition_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('death + 1st Jan + 70', pdstatus.log)
        assert pdstatus.pd_prob == 1.0

    def test_work_status_2(self):
        self.composer.death_date_ordered = 1950.0

        pdstatus = pd.determine_status(self.composition_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('death + 1st Jan + 70', pdstatus.log)
        assert pdstatus.pd_prob == 0.0

    def test_work_status_3(self):
        print "NAME", self.composition_work.persons[0].name
        self.composition_work.persons[0].name = 'anonymous'
        self.composition_work.date_ordered = 1930.0

        pdstatus = pd.determine_status(self.composition_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('first publication + 1st Jan + 70', pdstatus.log)
        assert pdstatus.pd_prob == 1.0

    def test_work_status_4(self):
        self.recording_work.date_ordered = 1845.0

        pdstatus = pd.determine_status(self.recording_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('first publication + 1st Jan + 50', pdstatus.log)
        assert pdstatus.pd_prob == 1.0

    def test_work_status_5(self):
        self.recording_work.date_ordered = 1985.0

        pdstatus = pd.determine_status(self.recording_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('first publication + 1st Jan + 50', pdstatus.log)
        assert pdstatus.pd_prob == 0.0

    def test_work_status_6(self):
        self.composer.birth_date_ordered = 1820.0
        self.composer.death_date_ordered = None

        pdstatus = pd.determine_status(self.composition_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('assuming died 100 years after birth', pdstatus.log)
        assert self._log_has('death + 1st Jan + 70', pdstatus.log)
        assert pdstatus.pd_prob == 1.0

    def test_work_status_7(self):
        self.composer.birth_date_ordered = 1920.0
        self.composer.death_date_ordered = None

        pdstatus = pd.determine_status(self.composition_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('assuming died 100 years after birth', pdstatus.log)
        assert self._log_has('death + 1st Jan + 70', pdstatus.log)
        assert pdstatus.pd_prob == 0.0

class TestPdStatusUnitedStates:
    jurisdiction = 'us'

    @classmethod
    def setUp(self):
        class X:
            pass

        composer = X()
        composer.name = 'Schumann, Robert'
        composer.birth_date_ordered = 1830.0
        composer.death_date_ordered = 1900.0

        singer = X()
        singer.name = 'Terfel, Bryn'
        singer.birth_date_ordered = 1974
        singer.death_date_ordered = None

        composition_work = X()
        composition_work.title = 'I love flowers'
        composition_work.persons = [ composer ]
        composition_work.date_ordered = 1945.0
        composition_work.type = 'composition'

        recording_work = X()
        recording_work.title = 'Bryn Terfel sings "I love flowers"'
        recording_work.persons = [ composer, singer ]
        recording_work.date_ordered = 1945.0
        recording_work.type = 'recording'

        cd_item = X()
        cd_item.title = 'Songs CD'
        cd_item.date_ordered = 1985.0
        cd_item.works = [composition_work, recording_work]

        score_item = X()
        score_item.title = 'Song score'
        score_item.date_ordered = 1955.0
        score_item.works = [composition_work]

        composition_work.items = [cd_item, score_item]

        self.composer = composer
        self.composition_work = composition_work
        self.recording_work = recording_work
        self.cd_item = cd_item
        self.score_item = score_item


    def _log_has(self, str, log):
        for log_line in log:
            if str in log_line:
                return True
        return False
        
    def test_work_status_1(self):
        self.composition_work.date_ordered = 1920.0

        pdstatus = pd.determine_status(self.composition_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('publication + 28 + 28', pdstatus.log)
        assert pdstatus.pd_prob == 1.0

    def test_work_status_2(self):
        self.composition_work.date_ordered = 1950.0

        pdstatus = pd.determine_status(self.composition_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('publication + 95', pdstatus.log)
        assert self._log_has('Assuming its copyright was renewed', pdstatus.log)
        assert pdstatus.pd_prob == 0.0

    def test_work_status_3(self):
        self.composition_work.date_ordered = 1970.0

        pdstatus = pd.determine_status(self.composition_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('publication + 95', pdstatus.log)
        assert not self._log_has('Assuming its copyright was renewed', pdstatus.log)
        assert pdstatus.pd_prob == 0.0

    def test_work_status_4(self):
        self.composition_work.date_ordered = 1980.0
        self.composer.death_date_ordered = 1900

        pdstatus = pd.determine_status(self.composition_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('death + 70', pdstatus.log)
        assert pdstatus.pd_prob == 1.0

    def test_work_status_5(self):
        self.composition_work.date_ordered = 1980.0
        self.composer.death_date_ordered = 1990

        pdstatus = pd.determine_status(self.composition_work, self.jurisdiction)
        print pdstatus
        assert self._log_has('death + 70', pdstatus.log)
        assert pdstatus.pd_prob == 0.0



