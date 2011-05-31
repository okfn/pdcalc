import pdcalc.uk as uk
import pdcalc.fr as fr
from pdcalc.work import Work
from pdcalc.calculator import * 
from pdcalc.bibliographica import *

from pprint import pprint

# Run this test: nosetests pdcalc/CalculatorFR.py
def test():
    calc = {}
    results = {} 
 
    for k in calculators.keys():
        calc[k] = Calculator(k)
   

 
    #for f in [ '%02d' % i for i in range(2)]:
    data = load_from_file("pdcalc/test/data/01.json")
    results["uk"] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    results["fr"] = [0, 0, 0, 0, 1, 1, 1, 0, 1, 0]

    n = 0;
    for i in data:
        test = Bibliographica(i)
        work = Work(test.data)

	#pprint(test.data)

        for k, v in calc.items():
            #print "%s in [%s] = %s\n" % (work.title, k, v.get_status(work))
	    #if v.get_status(work) != results[k][n]: raise ValueError("error")
            assert v.get_status(work) == results[k][n]
        n+=1

#test()

                
