import pdw.pd
from datetime import datetime

class TestCopyrightStatus:
    # more than 70 years ago
    date1 = datetime(1900, 1, 1)
    # more than 50 but less than 70
    date2 = datetime(1955, 1, 1)
    # less than 50
    date3 = datetime(2000, 1, 1)

    def setUp(self):
        class X:
            pass
        artist = X()
        artist.death_date = self.date1
        work = X()
        work.persons = [ artist ]
        item = X()
        item.work = work
        item.date = self.date2
        self.item = item

    def test_out_of_authorial_copyright(self):
        out = pdw.pd.out_of_authorial_copyright(self.date1)
        assert out == True
        out = pdw.pd.out_of_authorial_copyright(self.date2)
        assert out == False

    def test_out_of_recording_copyright(self):
        out = pdw.pd.out_of_recording_copyright(self.date2)
        assert out == True

    def test_copyright_status_1(self):
        out = pdw.pd.copyright_status(self.item)
        assert out == pdw.pd.CopyrightStatus.OUT

    def test_copyright_status_2(self):
        self.item.date = self.date3
        out = pdw.pd.copyright_status(self.item)
        assert out == pdw.pd.CopyrightStatus.IN
        
    def test_copyright_status_3(self):
        self.item.work.persons[0].death_date = self.date2
        out = pdw.pd.copyright_status(self.item)
        assert out == pdw.pd.CopyrightStatus.IN
        
    def test_copyright_status_4(self):
        self.item.work = None
        out = pdw.pd.copyright_status(self.item)
        assert out == pdw.pd.CopyrightStatus.UNKNOWN
        
    def test_copyright_status_5(self):
        self.item.work.persons[0].death_date = None
        out = pdw.pd.copyright_status(self.item)
        assert out == pdw.pd.CopyrightStatus.UNKNOWN
        

class TestPDStatus:
    calc = pdw.pd.PDCalculator()

    @classmethod
    def setup_class(self):
        class X:
            pass
        artist = X()
        artist.death_date = '1900'
        artist.name = 'Test'
        work = X()
        work.id = u'abc'
        work.persons = [ artist ]
        item = X()
        item.work = work
        item.date = '1955'
        self.work = work
        self.item = item

    def test_work_status(self):
        self.calc.work_status(self.work)
        assert self.calc.pdstatus == True, self.calc.pdstatus

    def test_person_status(self):
        self.calc.item_status(self.item)
        assert self.calc.pdstatus == True, self.calc.pdstatus

    # TODO: test using proper search
    # TODO: much more testing
