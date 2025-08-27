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
        self.assertEqual(b"Resolver Server", body)

    def testIdentifiersInDB(self):
        ids_uri = [
            (
                "urn:nbn:nl:in:10-125",
                ["http://publications.beeldengeluid.nl/pub/125"],
            ),
            (
                "urn:nbn:nl:in:10-136",
                ["http://publications.beeldengeluid.nl/pub/136"],
            ),
            (
                "urn:nbn:nl:in:10-155",
                ["http://publications.beeldengeluid.nl/pub/155"],
            ),
            (
                "urn:nbn:nl:in:10-157",
                ["http://publications.beeldengeluid.nl/pub/157#fragment"],
            ),
            (
                "urn:nbn:nl:ui:10-1874-1170",
                ["http://dspace.library.uu.nl/handle/1874/1170"],
            ),
            (
                "urn:nbn:nl:ui:11-dbi/509105ab6e3b0",
                ["http://irs.ub.rug.nl/dbi/509105ab6e3b0"],
            ),
            (
                "urn:nbn:nl:ui:13-9qz-2ce",
                [
                    "https://easy.dans.knaw.nl/dms?command=AIP_info&aipId=twips.dans.knaw.nl-833486382286886219-1174311206456&windowStyle=default&windowContext=default"
                ],
            ),
            (
                "urn:nbn:nl:ui:24-uuid:86513f19-0e70-4927-bc43-462e154d72dd",
                ["http://irs.ub.rug.nl/dbi/509105ab6e3b0"],
            ),
            (
                "urn:nbn:nl:ui:26-1887/12275",
                ["http://hdl.handle.net/1887/12275"],
            ),
            (
                "urn:nbn:nl:ui:28-5548",
                ["http://purl.utwente.nl/publications/5548"],
            ),
            (
                "urn:nbn:nl:ui:32-377300",
                ["http://library.wur.nl/WebQuery/wurpubs/377300"],
            ),
            (
                "urn:nbn:nl:ui:39-45cce635b62db054591d4e3e35996f47",
                ["https://www.differ.nl/node/162"],
            ),
            (
                "urn:nbn:nl:ui:39-4720abcd4605174ae41bdd50ac65b952",
                ["https://www.differ.nl/node/232"],
            ),
            (
                "urn:nbn:nl:ui:39-4cdece612010e2332d3d304cbbddfdb1",
                ["https://www.differ.nl/node/160"],
            ),
            (
                "urn:nbn:nl:ui:39-79442a501b171a2d1437557022989bf8",
                ["https://www.differ.nl/node/161"],
            ),
            (
                "urn:nbn:nl:ui:39-ae86436a9031f6f287b2fdc6f54e3fe6",
                ["https://www.differ.nl/node/163"],
            ),
        ]

        for identifier, expected in ids_uri:
            self.assertEqual(
                [{"uri": uri, "ltp": 0} for uri in expected],
                self.db.get_locations(identifier, include_ltp=True),
            )
