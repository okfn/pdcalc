
'''
to create a model to interact with the JSON
'''
import json
from pdw import pd

class WORKTYPES:
    LITERARY = "text"
    SOUND = "recording"
    PHOTO = "photograph"
    VIDEO = "video"
    DATABASE = "database"


class DomainObject(object):
    def json_output(self):
        print json.load(self.__dict__)
    pass

class Item(DomainObject):
    '''publications'''
    pass

class Work(DomainObject):
    def __init__(self,**kwargs):
        for k,v in kwargs.items():
            if k == 'date':
                self.date_ordered = float(int(v[:4]))
                self.items = []
                newitem = Item()
                newitem.date = v
                newitem.date_ordered = float(int(v[:4]))
                self.items.append(newitem)
            if k == 'persons':
                setattr(self,k,[])
                for person in v:
                    newperson = Person(**person)
                    self.persons.append(newperson)
            else:
                setattr(self,k,v)
    pass

class Person(DomainObject):
    def __init__(self,**kwargs):
        if kwargs['death_date'] == 'None' and kwargs['birth_date']>0:
            self.death_date = int(kwargs['birth_date'][:4])+100
        if 'death_date_ordered' not in kwargs and 'death_date' in kwargs:
            if kwargs['death_date'] == 'None':
                setattr(self,'death_date_ordered',float(self.death_date))
            else:
                setattr(self,'death_date_ordered',float(int(kwargs['death_date'][:4])))
        for k,v in kwargs.items():
            setattr(self,k,v)

    pass



class Manifestation(DomainObject):
    pass

import datetime

class Consultation(DomainObject):
    def __init__(self,**kwargs):
        now = datetime.datetime.now()
        self.when = now.strftime("%Y%m%d")
        self.work = kwargs['work']


        for k,v in kwargs.items():
            setattr(self,k,v)
    def calculate(self):
        object = json.JSONDecoder(self.json_data)
        print object.encoding
        status = pd.determine_status(object.encoding,'uk')
        return status


    def make_json(self,work):
        consult = []
        result = json.dump(work,consult)
        return result


