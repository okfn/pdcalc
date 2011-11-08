'''Public Domain Calculators library.'''

from calculator import register_calculator, get_calculator, calculators

def get_pd_status(work, jurisdiction=None):
    if jurisdiction is not None:
        calculator = get_calculator(jurisdiction)
        status = calculator.get_status(work)
        out = {
            jurisdiction: {
                'pd': status,
                'assumptions': calculator.assumptions
                }
        }
        return out
    else:
        out = {}
        for jurisdiction in calculators:
            calculator = get_calculator(jurisdiction)
            status = calculator.get_status(work)
            out[jurisdiction] = {
                'pd': status,
                'assumptions': calculator.assumptions
                }
        return out

