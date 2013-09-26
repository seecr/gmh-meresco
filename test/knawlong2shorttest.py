# -*- coding: utf-8 -*-

from cq2utils import CQ2TestCase, CallTrace
from lxml.etree import parse, tostring, XML, fromstring, dump, XMLSchema, parse as lxmlParse
from StringIO import StringIO
from narcis.knawlong2short import KNAWLong2Short
from narcis.knawlong import KNAWLong
from os.path import abspath, dirname, join
from difflib import unified_diff
from meresco.core import Observable
from narcis.surfshareformat import SurfShareFormat


class KNAWLong2ShortTest(CQ2TestCase):

    def setUp(self):
        CQ2TestCase.setUp(self)
        self.schemasPath = join(dirname(abspath(__file__)), 'schemas')
        self.startHere = Observable()
        self.knawlong = KNAWLong()
        self.knawlong2short = KNAWLong2Short()
        self.observer = CallTrace()
        self.startHere.addObserver(self.knawlong)
        self.knawlong.addObserver(self.knawlong2short)
        self.knawlong2short.addObserver(self.observer)

    def tearDown(self):
        CQ2TestCase.tearDown(self)


    def testConvertBySchema(self):
        for ssformat in SurfShareFormat.SURFSHARE_FORMAT:
            if ssformat != SurfShareFormat.SURFSHARE_FORMAT[5]:
                inputRecord = lxmlParse(open("data/%s.knaw_long.xml" % ssformat))
                expectedResult = open("data/%s.knaw_short.xml" % ssformat).read()
                # Get xml-schema:
                knawshortschema = XMLSchema(lxmlParse(open(join(self.schemasPath, 'knaw_short.xsd'))))
                result = self.knawlong2short.convert(inputRecord)
                #print 'Converted:', tostring(result, pretty_print = True, encoding='utf-8')
                knawshortschema.validate(result)
                
                if knawshortschema.error_log.last_error:
                    for nr, line in enumerate(tostring(result, pretty_print = True, encoding='utf-8').split('\n')):
                        print nr+1, line
                    self.fail(knawshortschema.error_log.last_error)
                    
                self.assertEqualsWS(expectedResult, tostring(result))

    def testMethodChain(self):
        for i in range(len(SurfShareFormat.SURFSHARE_FORMAT)):
            if i != 5:
                inputRecord = lxmlParse(open("data/%s.xml" % SurfShareFormat.SURFSHARE_FORMAT[i]))
                expectedResult = open("data/%s.knaw_short.xml" % SurfShareFormat.SURFSHARE_FORMAT[i]).read()
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