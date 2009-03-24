"""Determine copyright status of works given relevant information such as
creator death date.

# TODO: internationalize this
# TODO: function to calculate PD date (i.e. date at which work goes PD)

Remarks
=======

Often cannot calculate PD with certainty (at least in an automated process). Different kinds of uncertainty:

  * Do not know persons associated with work (with certainty or at all)
  * Do not know their death dates (may or may not know birth dates)
  * Do not know when work was published
  * etc

And this is even assuming we have identified the work (and/or whether it is a
translation, critical edition etc etc).

This uncertainty must therefore be presented. Core features

  * PD/Copyright status
  * Level of uncertainty ...
  * Comments
  * Compressed comments/Standard flags

Suggestions for flags:
  * normalized title
  * notes
  * translation

def determine_status(work, jurisdiction, when):
    # now dispatch on jurisdiction (+ work type?)

class CopyrightStatus:
    # Flags etc

class CalculatorBase:
    def status(self, work):

class CalculatorUK(CalculatorBase):
    pass
"""
import datetime

class CopyrightStatus:
    UNKNOWN = 0
    OUT = 1
    IN = 2

today = datetime.date.today()
def out_of_authorial_copyright(death_date, when=today):
    '''
    TODO: support birth_date (for cases where death_date not known)

    '''
    life_plus_70 = datetime.date(death_date.year + 70, death_date.month,
            death_date.day) 
    if life_plus_70 <= when:
        return True
    else:
        return False

def out_of_recording_copyright(release_date):
    # Europe is 50 years for US and elsewhere this will be different
    today = datetime.date.today()
    release_plus_50 = datetime.date(release_date.year + 50, release_date.month,
            release_date.day) 
    return release_plus_50 <= today

def copyright_status(performance):
    if not performance.work:
        return CopyrightStatus.UNKNOWN
    if len(performance.work.creators) == 0: # something wrong ...
        return CopyrightStatus.UNKNOWN
    for creator in performance.work.creators:
        if creator.death_date:
            # TODO: deal with stuff like '?'
            if not out_of_authorial_copyright(creator.death_date):
                return CopyrightStatus.IN
        else:
            return CopyrightStatus.UNKNOWN
    if not out_of_recording_copyright(performance.performance_date):
        return CopyrightStatus.IN
    return CopyrightStatus.OUT


