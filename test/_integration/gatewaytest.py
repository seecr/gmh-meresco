## begin license ##
#
# Gemeenschappelijke Metadata Harvester (GMH) data extractie en OAI service
#
# Copyright (C) 2016, 2025 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2025 Koninklijke Bibliotheek (KB) https://www.kb.nl
#
# This file is part of "GMH-Meresco"
#
# "GMH-Meresco" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "GMH-Meresco" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "GMH-Meresco"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from seecr.test import IntegrationTestCase
from seecr.test.utils import getRequest
from meresco.xml import xpath
from lxml import etree
from meresco.servers.gateway.gatewayserver import NORMALISED_DOC_NAME


class GatewayTest(IntegrationTestCase):

    def testOai(self):
        header, body = getRequest(
            self.gatewayPort,
            "/oaix",
            arguments=dict(verb="ListRecords", metadataPrefix=NORMALISED_DOC_NAME),
        )
        self.assertEqual(
            {
                "StatusCode": "200",
                "Headers": {"Content-Type": "text/xml; charset=utf-8"},
            },
            header,
        )
        print("OAIX body:", etree.tostring(body))
        records = xpath(body, b"//oai:record")
        self.assertEqual(18, len(records))

        deletes = xpath(body, '//oai:record[oai:header/@status = "deleted"]')
        self.assertEqual(2, len(deletes))

    def testOaiIdentify(self):
        header, body = getRequest(
            self.gatewayPort, "/oaix", arguments=dict(verb="Identify")
        )
        # print("Identify body:", etree.tostring(body))
        self.assertEqual(
            {
                "StatusCode": "200",
                "Headers": {"Content-Type": "text/xml; charset=utf-8"},
            },
            header,
        )
        adminEmail = xpath(body, "//oai:Identify/oai:adminEmail/text()")
        self.assertEqual("harvester@dans.knaw.nl", adminEmail[0])

    def testOaixInfo(self):
        header, body = getRequest(self.gatewayPort, "/oaix/info/index")
        self.assertEqual(
            {
                "StatusCode": "200",
                "Headers": {"Content-Type": "text/html; charset=utf-8"},
            },
            header,
        )
        # print "testOaixInfo:", etree.tostring(body)
        self.assertTrue(b"normdoc" in etree.tostring(body))
