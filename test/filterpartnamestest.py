# -*- coding: utf-8 -*-
from seecr.test import SeecrTestCase, CallTrace

from lxml.etree import parse, tostring, XML, fromstring
from StringIO import StringIO
from meresco_server.filterpartnames import FilterPartNames
from meresco.core import Observable
from unittest import TestCase
from weightless.core import compose

class FilterPartNamesTest(SeecrTestCase):

    def testMetadataNamePart(self):
        
        filterpn = FilterPartNames(allowed=['metadata'])
        observer = CallTrace('observer')
        didlNode = parse(StringIO(DIDL_FULL))
        observer.methods['some_method'] = lambda **kwargs: (f for f in ['data'])
        filterpn.addObserver(observer)

        self.assertEquals(['data'], list(compose(filterpn.do.some_method(identifier='identifier', partname='metadata'))))
        
        
        for m in observer.calledMethods:
            print 'Called methods:', m.name
        else:
            print 'No methods called!'
            
        self.assertEquals(1, len(observer.calledMethods))


#        filter = FilterPartByName(included=['thisone'])
#        observer = CallTrace('observer')
#        observer.methods['yieldRecord'] = lambda **kwargs: (f for f in ['data'])
#        filter.addObserver(observer)
#
#        self.assertEquals(['data'], list(compose(filter.yieldRecord(identifier='identifier', partname='thisone'))))
#        self.assertEquals([], list(compose(filter.yieldRecord(identifier='identifier', partname='no'))))



    def testMetadataNamePart2(self):
        startHere = Observable()
        filterpn = FilterPartNames(allowed=['metadata'])
        observer = CallTrace('observer')
        startHere.addObserver(filterpn)
        filterpn.addObserver(observer)
        didlNode = parse(StringIO(DIDL_FULL))
        startHere.all.unknown('identifier', 'metadata', didlNode)
        
        for m in observer.calledMethods:
            print 'Called methods:', m.name
        else:
            print 'No methods called!'
        
        self.assertEquals(1, len(observer.calledMethods))

    def testOtherNamePart(self):
        startHere = Observable()
        filterpn = FilterPartNames(allowed=['metadata'])
        observer = CallTrace()
        startHere.addObserver(filterpn)
        filterpn.addObserver(observer)
        didlNode = parse(StringIO(DIDL_FULL))
        startHere.all.unknown('identifier', 'metadata', didlNode)
        self.assertEquals(1, len(observer.calledMethods))

    def testOtherNamePartKwargs(self):
        startHere = Observable()
        filterpn = FilterPartNames(allowed=['some_partname'])
        observer = CallTrace()
        startHere.addObserver(filterpn)
        filterpn.addObserver(observer)
        didlNode = parse(StringIO(DIDL_FULL))
        startHere.do.some_method(identifier='some_identifier', partname='some_partname', lxmlNode=didlNode)
        self.assertEquals(1, len(observer.calledMethods))

    def testOtherNamePartKwargs2(self):
        startHere = Observable()
        filterpn = FilterPartNames(disallowed=['some_partname'])
        observer = CallTrace()
        startHere.addObserver(filterpn)
        filterpn.addObserver(observer)
        didlNode = parse(StringIO(DIDL_FULL))
        startHere.do.some_method(identifier='some_identifier', partname='my_partname', lxmlNode=didlNode)
        self.assertEquals(1, len(observer.calledMethods))


FULL_MODS = """<mods:mods xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:mods="http://www.loc.gov/mods/v3" version="3.0" xsi:schemaLocation="http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-0.xsd"><mods:originInfo><mods:dateIssued encoding="iso8601">1983</mods:dateIssued><mods:publisher>Foris Publications</mods:publisher><mods:place><mods:placeTerm type="text">Dordrecht</mods:placeTerm></mods:place></mods:originInfo><mods:titleInfo><mods:title>De syntaxis van het Nederlands</mods:title></mods:titleInfo><mods:name ID="n548-aut0" type="personal"><mods:namePart type="given">prof.dr. H.J.</mods:namePart><mods:namePart type="family">Bennis</mods:namePart><mods:namePart type="termsOfAddress">prof</mods:namePart><mods:role><mods:roleTerm type="code" authority="marcrelator">aut</mods:roleTerm></mods:role></mods:name><mods:name ID="n548-aut1" type="personal"><mods:namePart type="given">T.</mods:namePart><mods:namePart type="family">Hoekstra</mods:namePart><mods:namePart type="termsOfAddress"></mods:namePart><mods:role><mods:roleTerm type="code" authority="marcrelator">aut</mods:roleTerm></mods:role></mods:name><mods:extension><dai:daiList xmlns:dai="info:eu-repo/dai" xsi:schemaLocation="info:eu-repo/dai https://www.surfgroepen.nl/sites/oai/metadata/Shared%20Documents/dai-extension.xsd"><dai:identifier IDref="n548-aut0" authority="info:eu-repo/dai/nl">071792279</dai:identifier></dai:daiList></mods:extension><mods:typeOfResource>text</mods:typeOfResource><mods:genre>info:eu-repo/semantics/book</mods:genre></mods:mods>"""

DIDL_FULL = """<didl:DIDL xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dip="urn:mpeg:mpeg21:2005:01-DIP-NS" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:didl="urn:mpeg:mpeg21:2002:02-DIDL-NS" xsi:schemaLocation="
		urn:mpeg:mpeg21:2002:02-DIDL-NS http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/did/didl.xsd 
		urn:mpeg:mpeg21:2002:01-DII-NS http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/dii/dii.xsd
		urn:mpeg:mpeg21:2005:01-DIP-NS http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/dip/dip.xsd
	" xmlns:dii="urn:mpeg:mpeg21:2002:01-DII-NS"><didl:Item><didl:Descriptor><didl:Statement mimeType="application/xml"><dii:Identifier>URN:NBN:NL:UI:17-548</dii:Identifier></didl:Statement></didl:Descriptor><didl:Descriptor><didl:Statement mimeType="text/xml"><dcterms:modified>2009-02-13T16:15:43Z</dcterms:modified></didl:Statement></didl:Descriptor><didl:Component><didl:Resource ref="http://depot.knaw.nl/548/" mimeType="text/html"></didl:Resource></didl:Component><didl:Item><didl:Descriptor><didl:Statement mimeType="application/xml"><dip:ObjectType>info:eu-repo/semantics/humanStartPage</dip:ObjectType></didl:Statement></didl:Descriptor><didl:Component><didl:Resource ref="http://depot.knaw.nl/548/" mimeType="text/html"></didl:Resource></didl:Component></didl:Item><didl:Item><didl:Descriptor><didl:Statement mimeType="application/xml"><dip:ObjectType>info:eu-repo/semantics/descriptiveMetadata</dip:ObjectType></didl:Statement></didl:Descriptor><didl:Component><didl:Resource mimeType="application/xml">%s</didl:Resource></didl:Component></didl:Item><didl:Item><didl:Descriptor><didl:Statement mimeType="application/xml"><dip:ObjectType>info:eu-repo/semantics/objectFile</dip:ObjectType></didl:Statement></didl:Descriptor><didl:Descriptor><didl:Statement mimeType="text/xml"><dcterms:modified>2009-02-13T15:52:02Z</dcterms:modified></didl:Statement></didl:Descriptor><didl:Component><didl:Resource ref="http://depot.knaw.nl/548/1/14788_292_bennis.pdf" mimeType="application/pdf"></didl:Resource></didl:Component></didl:Item></didl:Item></didl:DIDL>""" % FULL_MODS