# -*- coding: utf-8 -*-

from cq2utils import CQ2TestCase, CallTrace
from lxml.etree import parse, tostring, XML, fromstring, dump, XMLSchema, parse as lxmlParse
from StringIO import StringIO
from narcis.knawlong2short import KNAWLong2Short
from narcis.knawlong import KNAWLong
from os.path import abspath, dirname, join
from difflib import unified_diff
from meresco.framework import Observable


class DeleteTest(CQ2TestCase):
	
	def setUp(self):
		CQ2TestCase.setUp(self)
		self.knawlong2short = KNAWLong2Short()

	def tearDown(self):
		CQ2TestCase.tearDown(self)


	def testConvertBySchema(self):
		inputRecord = lxmlParse(StringIO("""<knaw_long xmlns="http://www.knaw.nl/narcis/1.0/long/"><humanStartPage>http://purl.org/utwente/60819</humanStartPage><persistentIdentifier>URN:NBN:NL:UI:28-60819</persistentIdentifier><modificationDate>2009-04-02T10:09:37Z</modificationDate><objectFiles><objectFile><mimeType>application/pdf</mimeType><url>http://doc.utwente.nl/60819/1/1713-1.pdf</url></objectFile></objectFiles><accessRights>closedAccess</accessRights><metadata><titleInfo><title>Self adapting control charts</title></titleInfo><titleInfo xml:lang="en"><title>Self adapting control charts</title></titleInfo><name><type>personal</type><name>Albers</name><given>Willem</given><mcRoleTerm>aut</mcRoleTerm></name><name><type>personal</type><name>Kallenberg</name><given>Wilbert C.M.</given><mcRoleTerm>aut</mcRoleTerm></name><genre>report</genre><publisher>University of Twente, Faculty of Electrical Engineering, Mathematics and Computer Science</publisher><abstract/><dateIssued><dateIssued>2004</dateIssued><unParsed>2004</unParsed></dateIssued><placeTerm>Enschede</placeTerm><typeOfResource>text</typeOfResource></metadata></knaw_long>"""))
		
		result = self.knawlong2short.convert(inputRecord)
		print 'Result:', result