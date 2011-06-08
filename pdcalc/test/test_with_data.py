import pdcalc
import pdcalc.uk as uk
import pdcalc.fr as fr
from pdcalc.work import Work
from pdcalc.calculator import * 
from pdcalc.bibliographica import *

from pprint import pprint

def test():
    calc = {}
    results = {} 
 
    for k in calculators.keys():
        calc[k] = Calculator(k)
   
    data = load_from_file("pdcalc/test/data/01.json")
    results["uk"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    results["fr"] = [0, 0, 0, 0, 1, 1, 1, 0, 1, 0]

    for n,i in enumerate(data):
        test = Bibliographica(i)
        work = Work(test.data)

        for k, v in calc.items():
            assert v.get_status(work) == results[k][n]
            assert pdcalc.get_pd_status(work, k)[k]['pd'] == results[k][n]
            assert pdcalc.get_pd_status(work)[k]['pd'] == results[k][n]
                
