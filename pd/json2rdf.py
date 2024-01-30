# MIT License
#
# Copyright (c) 2008-2024 Rufus Pollock, Open Knowledge Foundation and
# contributors
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

  
from xml.etree import ElementTree as ET

def convert(record):
    '''Takes a BibJSON record as input, and converts it into the minimal set of RDF elements needed by the current pdcalc reasoner
    {http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF
    ..{http://purl.org/ontology/bibo/}Document
    ....{http://purl.org/dc/terms/}issued 
    ....{http://purl.org/dc/terms/}subject
    ......{http://www.w3.org/2004/02/skos/core#}Concept>
    ........{http://www.w3.org/2004/02/skos/core#}inScheme {http://www.w3.org/1999/02/22-rdf-syntax-ns#}:resource
    ........{http://www.w3.org/2004/02/skos/core#}notation
    ....{http://iflastandards.info/ns/isbd/elements/}:hasPlaceOfPublicationProductionDistribution
    ......{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description
    ........{http://www.w3.org/2000/01/rdf-schema#}:label
    ..{http://xmlns.com/foaf/0.1/}Agent
    ....{http://purl.org/vocab/bio/0.1/}event
    ......{http://purl.org/vocab/bio/0.1/}Birth
    ........{http://purl.org/vocab/bio/0.1/}date
    ....{http://purl.org/vocab/bio/0.1/}event
    ......{http://purl.org/vocab/bio/0.1/}Death
    ........{http://purl.org/vocab/bio/0.1/}date
    ....{http://xmlns.com/foaf/0.1/}name
    '''
    e_RDF = ET.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF')
    e_Document = ET.SubElement(e_RDF, '{http://purl.org/ontology/bibo/}Document')
    if 'issued' in record:
        ET.SubElement(e_Document, '{http://purl.org/dc/terms/}issued').text = record['issued']
    for coverage in record.get('coverage', []):
        e_1 = ET.SubElement(e_Document, '{http://iflastandards.info/ns/isbd/elements/}:hasPlaceOfPublicationProductionDistribution')
        e_2 = ET.SubElement(e_1, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
        e_3 = ET.SubElement(e_2, '{http://www.w3.org/2000/01/rdf-schema#}:label')
        e_3.text=coverage.get('about', u'')
    for subject in record.get('subject', []):
        if subject.get('type') == 'http://dewey.info/scheme/e18':
            e_subject = ET.SubElement(e_Document, '{http://purl.org/dc/terms/}subject')
            e_Concept = ET.SubElement(e_subject, '{http://www.w3.org/2004/02/skos/core#}Concept')
            e_inScheme = ET.SubElement(e_Concept, '{http://www.w3.org/2004/02/skos/core#}inScheme')
            e_inScheme.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', 'http://dewey.info/scheme/e22' )
            ET.SubElement(e_Concept, '{http://www.w3.org/2004/02/skos/core#}notation').text = subject.get('about', u'')
    for author in record.get('author', []):
        e_agent = ET.SubElement(e_RDF, '{http://xmlns.com/foaf/0.1/}Agent')
        ET.SubElement(e_agent, '{http://xmlns.com/foaf/0.1/}name').text = author.get('name')
        if 'birth' in author:
            e_1 = ET.SubElement(e_agent, '{http://purl.org/vocab/bio/0.1/}event')
            e_2 = ET.SubElement(e_1, '{http://purl.org/vocab/bio/0.1/}Birth')
            ET.SubElement(e_2, '{http://purl.org/vocab/bio/0.1/}date').text = '%s-01-01T00:00:00Z' % author.get('birth')
        if 'death' in author:
            e_1 = ET.SubElement(e_agent, '{http://purl.org/vocab/bio/0.1/}event')
            e_2 = ET.SubElement(e_1, '{http://purl.org/vocab/bio/0.1/}Death')
            ET.SubElement(e_2, '{http://purl.org/vocab/bio/0.1/}date').text = '%s-01-01T00:00:00Z' % author.get('death')
    return ET.tostring(e_RDF)

if __name__ == '__main__':
    import sys, json
    for x in json.loads(sys.stdin.read()):
        if type(x) is dict:
            print ET.tostring(convert(x))
