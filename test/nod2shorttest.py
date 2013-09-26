# -*- coding: utf-8 -*-

from cq2utils import CQ2TestCase, CallTrace
from lxml.etree import parse, tostring, XML, fromstring, dump, XMLSchema, parse as lxmlParse
from StringIO import StringIO
from narcis.nod2short import NOD2short
from os.path import abspath, dirname, join
from difflib import unified_diff
from meresco.core import Observable
from lxml import etree


class NOD2ShortTest(CQ2TestCase):

    def setUp(self):
        CQ2TestCase.setUp(self)
        self.schemasPath = join(dirname(abspath(__file__)), 'schemas')
        self.startHere = Observable()
        self.nod2short = NOD2short()
        self.observer = CallTrace()
        self.startHere.addObserver(self.nod2short)
        self.nod2short.addObserver(self.observer)

    def tearDown(self):
        CQ2TestCase.tearDown(self)

    def testConvertBySchema(self):
        knawshortschema = XMLSchema(lxmlParse(open(join(self.schemasPath, 'knaw_short.xsd'))))
        for nod in NOD2short.NODnamespaceMap.keys():
            
            inputRecord = lxmlParse(open("data/%s.xml" % nod))
            expectedResult = open("data/%s.knaw_short.xml" % nod).read()
            ## Get xml-schema:
            
            result = self.nod2short.convert(inputRecord)
            knawshortschema.validate(lxmlParse(StringIO(tostring(result, pretty_print = True, encoding='utf-8'))))

            if knawshortschema.error_log.last_error:
                for nr, line in enumerate(tostring(result, pretty_print = True, encoding='utf-8').split('\n')):
                    print nr+1, line
                self.fail(knawshortschema.error_log.last_error)
            self.assertEqualsWithDiff(expectedResult, tostring(result)) #tostring(result, pretty_print = True, encoding='utf-8')


    def testMethodChain(self):
        nod = NOD2short.NODnamespaceMap.keys()
        for i in range(len(nod)):            
            inputRecord = lxmlParse(open("data/%s.xml" % nod[i]))
            expectedResult = open("data/%s.knaw_short.xml" % nod[i]).read()
            # Send some method with inputdata:
            self.startHere.do.some_method('identifier', 'partname', inputRecord)
            # Assert number of methods being called:
            self.assertEquals(i+1, len(self.observer.calledMethods))
            # Assert footprint method called:
            method = self.observer.calledMethods[i]
            self.assertEquals('some_method', method.name)
            self.assertEquals(('identifier', 'partname'), method.args[:2])
            # Get conversion result send to observer by NOD2short:
            nod2short_data_out = method.args[2]
            # Assert it is equal to expected result:
            #print 'expected', expectedResult, '\n'
            #print 'result',tostring(nod2short_data_out)
            self.assertEqualsWithDiff(expectedResult, tostring(nod2short_data_out))


    def assertEqualsWithDiff(self, expected, result):
        diffs = list(unified_diff(
            [x.strip() for x in result.split('\n') if x.strip()],
            [x.strip() for x in expected.split('\n') if x.strip()],
            fromfile='result', tofile='expected', lineterm=''))
        self.assertFalse(diffs, '\n' + '\n'.join(diffs))
