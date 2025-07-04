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
from seecr.test import CallTrace
from weightless.core import Observable, be, compose

normdoc_path = pathlib.Path(__file__).parent / "testdata"

from meresco.xml import xpathFirst

from gmh_meresco.dans.normalisemods import NormaliseMODS
from gmh_meresco.dans.utils import NAMESPACEMAP

import pytest
from meresco.components.xml_generic.validate import ValidateException


def test_normalise_mods():

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

    for filename in sorted(normdoc_path.glob("*.normdoc")):
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
