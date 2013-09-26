# -*- coding: utf-8 -*-
#WST
import sys
#
sys.path.insert(0, "..")

from cq2utils import CQ2TestCase, CallTrace
from lxml.etree import parse, tostring, XML, fromstring, dump, XMLSchema, parse as lxmlParse
from StringIO import StringIO
from narcis.harvestdate import AddHarvestDateToMetaPart
from os.path import abspath, dirname, join
from difflib import unified_diff
from meresco.core import Observable
import time
from unittest import main


metaNS = {'meta' : 'http://meresco.org/namespace/harvester/meta'}

class AddHarvestdateTest(CQ2TestCase):

    def setUp(self):        
        CQ2TestCase.setUp(self)
        self.startHere = Observable()
        self.harvestdate = AddHarvestDateToMetaPart(verbose=True)
        self.observer = CallTrace()
        self.startHere.addObserver(self.harvestdate)
        self.harvestdate.addObserver(self.observer)

    def tearDown(self):
        CQ2TestCase.tearDown(self)
            
    def testAddHarvestDate(self):
        inputRecord = lxmlParse(open("data/anymetapart.xml"))
        # Send some method with inputdata:
        self.startHere.do.some_method('identifier', 'metapart', inputRecord)
        # Assert number of methods being called:
        self.assertEquals(1, len(self.observer.calledMethods))
        # Assert footprint method called:
        method = self.observer.calledMethods[0]
        self.assertEquals('some_method', method.name)
        self.assertEquals(('identifier', 'metapart'), method.args[:2])
        # Get conversion result send to observer by knawlong2short:
        result = method.args[2]
        #Zoek harvestDate:
        harvest_date = result.xpath('/meta:meta/meta:record/meta:harvestdate/text()', namespaces=metaNS)
        hdstring = 'to be replaced'
        print tostring(result)
        if len(harvest_date) > 0: hdstring = harvest_date[0]
        self.assertTrue( len(harvest_date)==1 and hdstring.startswith( time.strftime("%Y-%m-%dT%H:", time.gmtime()) ))        
        
    def testHasHarvestDate(self):
        inputRecord = lxmlParse(open("data/anymetapart_harvestdate.xml"))
        # Send some method with inputdata:
        self.startHere.do.some_method('identifier', 'metapart', inputRecord)
        # Assert footprint method called:
        method = self.observer.calledMethods[0]
        self.assertEquals('some_method', method.name)
        self.assertEquals(('identifier', 'metapart'), method.args[:2])
        # Get conversion result send to observer by knawlong2short:
        result = method.args[2]        
        #Zoek harvestDate:
        harvest_date = result.xpath('/meta:meta/meta:record/meta:harvestdate/text()', namespaces=metaNS)
        self.assertTrue(len(harvest_date)==1)
        
if __name__ == '__main__':
    main()