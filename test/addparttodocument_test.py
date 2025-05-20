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
from lxml.etree import parse, tostring
from io import BytesIO

update_request_path = pathlib.Path(__file__).parent / "updateRequest"
testdata_path = pathlib.Path(__file__).parent / "testdata"

from meresco.xml import xpathFirst, xpath
from meresco.dans.addparttodocument import AddMetadataDocumentPart

from seecr.test import CallTrace
from meresco.core import Observable, be
from weightless.core import compose


#
# Dit component voegt de geescapede DIDL container toe als part van document.
# Dit gebeurd IN-PLACE(!!!!!!!). De test toont aan dat de add call naar beneden
# een document:part[name="normdoc"]. Het resultaat wordt in de testdata directory
# gelegd voor andere test als input.
#
def test_add_metadata_document_part():

    observer = CallTrace(emptyGeneratorMethods=["add"])
    dna = be(
        (
            Observable(),
            (
                AddMetadataDocumentPart(partName="normdoc", fromKwarg="lxmlNode"),
                (observer,),
            ),
        )
    )

    for filename in sorted(update_request_path.glob("*.updateRequest")):
        with filename.open() as fp:
            lxmlNode = parse(fp)
            update_request = xpathFirst(lxmlNode, '/*[local-name()="updateRequest"]')

            record_identifier = xpathFirst(
                update_request, "ucp:recordIdentifier/text()"
            )

            action = xpathFirst(update_request, "ucp:action/text()")
            if action.partition("info:srw/action/1/")[-1] in ["create", "replace"]:
                document_data = xpathFirst(
                    update_request, "srw:record/srw:recordData/*"
                )
                if document_data is not None:
                    document_xml = parse(BytesIO(tostring(document_data)))

                    assert xpath(document_xml, "//document:part/@name") == [
                        "record",
                        "meta",
                    ]
                    try:
                        list(
                            compose(
                                dna.all.add(
                                    record_identifier,
                                    partname="document",
                                    lxmlNode=document_xml,
                                )
                            )
                        )
                    except:
                        print("ERROR with", record_identifier)
                    assert xpath(document_xml, "//document:part/@name") == [
                        "record",
                        "meta",
                        "normdoc",
                    ]

                    formatted = tostring(document_xml, pretty_print=True).decode(
                        encoding="utf-8"
                    )
                    target_filename = (
                        testdata_path / filename.with_suffix(".normdoc").name
                    )

                    if (
                        not target_filename.exists()
                        or target_filename.read_text() != formatted
                    ):
                        target_filename.write_text(formatted)
                        print(f"Wrote {target_filename}")
