#!/usr/bin/env python
# -*- coding: utf-8 -*-

import CalculatorBase as pd
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json


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


class TestApiJSON:
    @classmethod
    def setup_class(self):
        self.json_data2 = json.dumps({  
                    "jurisdiction":"uk",
                    "work": 
                            {
                                "title":"Collected Papers on the Public Domain (ed)", 
                                "type": "text",
                                "date" : "18230101",
                                "creation_date" : "18220101",
                                "persons" : 
                                    [
                                            {"name" : "Sturgeon, Theodore", 
                                            "type" : "person",
                                            "birth_date" :"18090101",
                                            "death_date" : "18390205",
                                            "country": "ca"
                                            }
                                    ]
                            }
                    })
        self.json_data1 = json.dumps({  "when": "20110101",
                    "jurisdiction":"ca",
                    "work": 
                            {
                                "title":"Collected Papers on the Public Domain (ed)", 
                                "type": "photograph",
                                "date" : "20030101",
                                "creation_date" : "20030101",
                                "persons" : 
                                    [
                                            {"name" : "Boyle, James", 
                                            "type" : "person",
                                            "birth_date" :"19590101",
                                            "death_date" : "19890205",
                                            "country": "uk"
                                            }
                                    ]
                            }
                    })
        assert json

    def creating_by_hand(self):
        newperson = pd.Person(name='Borges, Jorge Luis',
                               death_date='1986',
                               type='person')
        newwork = pd.Work(title='El Aleph',
                           date='1949',
                           creation_date='1919',
                           type='text')
        newwork.persons = [ newperson]
        self.person = newperson
        self.work = newwork
        calc = pd.determine_status(newwork,'ca')
        return calc
        assert 'confidence' in calc.log

    def test_uk(self):
        '''
        test the calculator api for the UK
        '''
        parsed = json.loads(self.json_data2)
        workdata = parsed['work']
        jurisdiction = parsed['jurisdiction']
        newwork = pd.Work.from_dict(workdata)
        calc = pd.determine_status(newwork,jurisdiction)

        print parsed  
        return calc
        assert calc.log>0

    def test_pd_inthepast(self):
        '''test calculator with date different than today'''
        parsed = json.loads(self.json_data2)
        workdata = parsed['work']
        jurisdiction = parsed['jurisdiction']
        newwork = pd.Work.from_dict(workdata)
        when = '1840' #one year after death of author...
        calc = pd.determine_status(newwork,jurisdiction,when)

        assert calc.pd_prob == 0.0

    def test_pd_from_json_in_api(self):
        '''test import from raw json'''
        calc = pd.determine_status_from_raw(self.json_data1)

        assert 'pd_probability' in calc



