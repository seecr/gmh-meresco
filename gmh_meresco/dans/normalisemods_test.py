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

import pytest
from lxml.etree import parse
from meresco.xml import xpathFirst, namespaces
from meresco.xml.utils import createElement, createSubElement
from meresco.components import lxmltostring
from seecr.test import CallTrace
from weightless.core import Observable, be, compose

from gmh_meresco import testdata_path
from gmh_meresco.dans.normalisemods import NormaliseMODS
from gmh_meresco.dans.utils import NAMESPACEMAP


@pytest.mark.parametrize("filename", testdata_path.glob("*.normdoc"))
def test_normalise_mods(filename):

    observer = CallTrace(emptyGeneratorMethods=["add"])
    dna = be(
        (
            Observable(),
            (
                NormaliseMODS(nsMap=NAMESPACEMAP, fromKwarg="lxmlNode"),
                (observer,),
            ),
        )
    )

    with filename.open() as fp:
        lxmlNode = parse(fp)
        record_identifier = filename.stem

        before = xpathFirst(lxmlNode, "//document:part[@name='normdoc']/text()")
        list(
            compose(
                dna.all.add(
                    record_identifier,
                    partname="document",
                    lxmlNode=lxmlNode,
                )
            )
        )
        after = xpathFirst(lxmlNode, "//document:part[@name='normdoc']/text()")
        print(after)


def test_convertFullMods2GHMods():
    n = NormaliseMODS(nsMap=NAMESPACEMAP, fromKwarg="lxmlNode")


@pytest.mark.parametrize("filename", testdata_path.glob("*.getrecord.xml"))
def test_normalise_real_life_data(filename):
    normalise = NormaliseMODS(nsMap=NAMESPACEMAP, fromKwarg="lxmlNode")
    with filename.open() as fp:
        lxmlNode = parse(fp)
        oai_metadata = xpathFirst(lxmlNode, "//oai:metadata")
        doc = createElement("document:document", nsmap=namespaces.select("document"))
        createSubElement(
            doc,
            "document:part",
            attrib={"name": "normdoc"},
            text=lxmltostring(oai_metadata),
        )
        normalise._convertArgs(identifier=filename.name, lxmlNode=doc.getroottree())
