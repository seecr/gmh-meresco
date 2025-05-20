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
