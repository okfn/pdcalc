pdcalc
======

Public Domain Calculator - determine what is public domain and what's not.

All the code is released under <a href="http://opensource.org/licenses/MIT" target"_BLANK">The MIT License (MIT)<a>.

CLI Usage
---------

`pdcalc.py [-h] -c COUNTRY -i INSTANCE [-g GLOBAL] [-l] [-m {file,url}] [-f {rdf,json}]`

    -c COUNTRY, --country COUNTRY

country for which to test

    -i INSTANCE, --instance INSTANCE 

instance to test

    -g GLOBAL, --global GLOBAL
    
global mapping - Usable to test if a given global mapping works.

    -l, --list

True if the file contains a list of other files or ulrs

    -m {file,url}, --mode {file,url}

instance definition mode - Valid values are "file" or "url"

    -f {rdf,json}, --format {rdf,json}

format of the instances - Valid values are "rdf" or "json".
    
    -V 

lists the valid country/flavor combinations
