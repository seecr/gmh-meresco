## begin license ##
#
# Gemeenschappelijke Metadata Harvester (GMH) data extractie en OAI service
#
# Copyright (C) 2025 Koninklijke Bibliotheek (KB) https://www.kb.nl
# Copyright (C) 2025 Seecr (Seek You Too B.V.) https://seecr.nl
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

import pathlib
from lxml.etree import parse
from io import StringIO

update_request_path = pathlib.Path(__file__).parent / "updateRequest"

from meresco.xml import xpathFirst


def xtest_normalise_mods():

    for filename in sorted(update_request_path.glob("*.updateRequest")):
        with filename.open() as fp:
            xml_record = parse(fp)
            document_data = xpathFirst(
                xml_record,
                "/ucp:updateRequest/srw:record/srw:recordData/document:document/document:part[@name='record']/text()",
            )
            if document_data is None:
                print(f"Skipping {filename}")
                continue
            document_xml = parse(StringIO(document_data))
            didl = xpathFirst(document_xml, "/oai:record/oai:metadata/*")
