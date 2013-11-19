# -*- coding: utf-8 -*-

from seecr.test import SeecrTestCase, CallTrace
from lxml.etree import parse, tostring, XML, fromstring, dump, XMLSchema, parse as lxmlParse
from StringIO import StringIO
from meresco_server.normalize_nl_mods import Normalize_nl_MODS
from weightless.core import be, compose
from os.path import abspath, dirname, join
from difflib import unified_diff
from meresco.core import Observable



namespacesMap = {
    'dip'     : 'urn:mpeg:mpeg21:2005:01-DIP-NS',
    'dii'     : 'urn:mpeg:mpeg21:2002:01-DII-NS',
    'document': 'http://meresco.org/namespace/harvester/document',
    'oai'     : 'http://www.openarchives.org/OAI/2.0/',
    'meta'    : 'http://meresco.org/namespace/harvester/meta',
    'oai_dc'  : 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'dc'      : 'http://purl.org/dc/elements/1.1/',
    'mods'    : 'http://www.loc.gov/mods/v3',
    'didl'    : 'urn:mpeg:mpeg21:2002:02-DIDL-NS',
    'rdf'     : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'ucp'     : 'info:lc/xmlns/update-v1',
    'dcterms' : 'http://purl.org/dc/terms/',
    'xsi' : 'http://www.w3.org/2001/XMLSchema-instance'
}


class NormModsTest(SeecrTestCase):

    def setUp(self):
        SeecrTestCase.setUp(self)

        self.norm_mods = Normalize_nl_MODS(nsMap=namespacesMap)
        self.observer = CallTrace('observer')
        self.norm_mods.addObserver(self.observer)
        

    def testOne(self):
        self.observer.methods['add'] = lambda *args, **kwargs: (x for x in [])
        #self.observer.methods['logMsg'] = lambda *args, **kwargs: (x for x in [])
        
        list( compose(self.norm_mods.all_unknown('add', 'id', 'metadata', 'anotherone', lxmlNode=parse(open("data/didl_mods.xml")), identifier='oai:very:secret:09987' )))
        
        self.assertEquals(2, len(self.observer.calledMethods))
        for m in self.observer.calledMethods:
            print 'method name:',m.name, m.args, m.kwargs
        print "Converted:", tostring(self.observer.calledMethods[1].kwargs.get('lxmlNode'))
        self.assertEquals(2, len(self.observer.calledMethods[0].args))
        
        arguments = self.observer.calledMethods[1].args
        self.assertEquals("id", arguments[0])
        self.assertEquals("metadata", arguments[1])

"""
    def tearDown(self):
        SeecrTestCase.tearDown(self)        



    def testConvertBySchema(self):
        knawLongSchema = XMLSchema(lxmlParse(open(join(self.schemasPath, 'knaw_long.xsd'))))
        for ssformat in SurfShareFormat.SURFSHARE_FORMAT:
            inputRecord = lxmlParse(open("data/%s.xml" % ssformat))
            expectedResult = open("data/%s.knaw_long.xml" % ssformat).read()
            # Get xml-schema:            
            result = self.knawlong.convert(inputRecord)
            knawLongSchema.validate(lxmlParse(StringIO(tostring(result, pretty_print = True, encoding='utf-8'))))

            if knawLongSchema.error_log.last_error:
                for nr, line in enumerate(tostring(result, pretty_print = True, encoding='utf-8').split('\n')):
                    print nr+1, line
                self.fail(knawLongSchema.error_log.last_error)

            self.assertEqualsWithDiff(expectedResult, tostring(result, pretty_print = True, encoding='utf-8'))
            
    def testChain(self):
        for i in range(len(SurfShareFormat.SURFSHARE_FORMAT)):
            inputRecord = lxmlParse(open("data/%s.xml" % SurfShareFormat.SURFSHARE_FORMAT[i]))
            expectedResult = open("data/%s.knaw_long.xml" % SurfShareFormat.SURFSHARE_FORMAT[i]).read()
            # Send some method with inputdata:
            self.startHere.do.some_method('identifier', 'partname', inputRecord)
            # Assert number of methods being called:
            self.assertEquals(i+1, len(self.observer.calledMethods))
            # Assert footprint method called:
            method = self.observer.calledMethods[i]
            self.assertEquals('some_method', method.name)
            self.assertEquals(('identifier', 'partname'), method.args[:2])
            # Get conversion result send to observer by knawlong2short:
            knawlong2short_data_out = method.args[2]
            # Assert it is equal to expected result:
            self.assertEqualsWS(expectedResult, tostring(knawlong2short_data_out))
            
            
    def assertEqualsWithDiff(self, expected, result):
        diffs = list(unified_diff(
            [x.strip() for x in result.split('\n') if x.strip()],
            [x.strip() for x in expected.split('\n') if x.strip()],
            fromfile='result', tofile='expected', lineterm=''))
        self.assertFalse(diffs, '\n' + '\n'.join(diffs))
"""