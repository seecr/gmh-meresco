# -*- coding: utf-8 -*-

from cq2utils import CQ2TestCase, CallTrace

from narcis.crosswalk import Crosswalk
#from meresco.components import Crosswalk
from meresco.framework import Observable
from StringIO import StringIO
from lxml.etree import parse, tostring

from os.path import abspath, dirname, join

myRulesDir = join(dirname(abspath(__file__)), 'rules')

class Dc2KnawShortTest(CQ2TestCase):
    def testOne(self):
	startHere = Observable()
        crosswalk = Crosswalk(rulesDir=myRulesDir)
        observer = CallTrace()
	startHere.addObserver(crosswalk)
        crosswalk.addObserver(observer)
	dcNode = parse(StringIO(DC))

	startHere.do.someMessage(dcNode)

	self.assertEquals(1, len(observer.calledMethods))
	resultNode = observer.calledMethods[0].args[0]
	print tostring(resultNode)


DC = """<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">

  <dc:title>Late-type Giants in the Inner Galaxy</dc:title>
  <dc:creator>Messineo, Maria</dc:creator>

  <dc:publisher>Leiden University, Faculty of Mathematics &amp; Natural Sciences, Observatory</dc:publisher>
  <dc:date>2004-06-30</dc:date>
  <dc:type>Doctoral thesis</dc:type>
  <dc:format>application/pdf</dc:format>
</oai_dc:dc>"""