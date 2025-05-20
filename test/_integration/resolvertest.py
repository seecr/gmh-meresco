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
from lxml import etree


class ResolverTest(IntegrationTestCase):

    def testOaiIdentify(self):
        header, body = getRequest(
            self.resolverPort,
            "/",
            arguments=dict(
                identifier="urn:nbn:nl:ui:39-ae86436a9031f6f287b2fdc6f54e3fe6"
            ),
        )
        self.assertEqual(
            {
                "StatusCode": "200",
                "Headers": {"Content-Type": "text/plain; charset=utf-8"},
            },
            header,
        )
        self.assertEqual(
            "<html><body><p>Resolver Server</p></body></html>", etree.tostring(body)
        )
