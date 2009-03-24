import pdw.copyright
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
        stub_artist = X()
        stub_artist.death_date = self.date1
        stub_work = X()
        stub_work.creators = [ stub_artist ]
        stub_perf = X()
        stub_perf.work = stub_work
        stub_perf.performance_date = self.date2
        self.perf = stub_perf

    def test_out_of_authorial_copyright(self):
        out = pdw.copyright.out_of_authorial_copyright(self.date1)
        assert out == True
        out = pdw.copyright.out_of_authorial_copyright(self.date2)
        assert out == False

    def test_out_of_recording_copyright(self):
        out = pdw.copyright.out_of_recording_copyright(self.date2)
        assert out == True

    def test_copyright_status_1(self):
        out = pdw.copyright.copyright_status(self.perf)
        assert out == pdw.copyright.CopyrightStatus.OUT

    def test_copyright_status_2(self):
        self.perf.performance_date = self.date3
        out = pdw.copyright.copyright_status(self.perf)
        assert out == pdw.copyright.CopyrightStatus.IN
        
    def test_copyright_status_3(self):
        self.perf.work.creators[0].death_date = self.date2
        out = pdw.copyright.copyright_status(self.perf)
        assert out == pdw.copyright.CopyrightStatus.IN
        
    def test_copyright_status_4(self):
        self.perf.work = None
        out = pdw.copyright.copyright_status(self.perf)
        assert out == pdw.copyright.CopyrightStatus.UNKNOWN
        
    def test_copyright_status_5(self):
        self.perf.work.creators[0].death_date = None
        out = pdw.copyright.copyright_status(self.perf)
        assert out == pdw.copyright.CopyrightStatus.UNKNOWN
        
