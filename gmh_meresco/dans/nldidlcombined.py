# -*- coding: utf-8 -*-
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

from lxml.etree import parse, _ElementTree, tostring
from lxml import etree
from meresco.core import Observable
from copy import deepcopy
from io import StringIO
from weightless.core import Transparent, be, compose
from gmh_meresco.dans.uiaconverter import UiaConverter

# lxml staat het gebruik van colonisednames niet meer toe: gebruik kwarg: prefix="[ns_alias]"
# This component handles ADD messages only.
# It will try to convert the data from the 'metadata' part into GH combined format.
# If it fails in doing so, it will block (NOT pass) the ADD message.
# Returns: xml-string.

GH_COMBINED_NS = "http://gh.kb-dans.nl/combined/v0.9/"
GH_COMBINED = "{%s}" % GH_COMBINED_NS
NSMAP = {None: GH_COMBINED_NS}  # Default namespace (no prefix)


class NlDidlCombined(UiaConverter):

    def __init__(self, fromKwarg, nsMap={}, toKwarg=None, name=None):
        UiaConverter.__init__(self, name=name, fromKwarg=fromKwarg, toKwarg=toKwarg)
        self._nsMap = nsMap
        self._bln_success = False

    def _convert(self, lxmlNode):
        # Get partName from disk to combine:
        storage_part = self._getPart(self._uploadid, "nl_didl_norm")
        original_part = lxmlNode.getroot().xpath("//didl:DIDL", namespaces=self._nsMap)

        # Create wrapper:
        root = etree.Element(GH_COMBINED + "nl_didl_combined", nsmap=NSMAP)
        e_original = etree.SubElement(root, GH_COMBINED + "nl_didl")
        e_normalized = etree.SubElement(root, GH_COMBINED + "nl_didl_norm")

        nl_didl_norm = storage_part.xpath("//didl:DIDL", namespaces=self._nsMap)
        # print(etree.tostring(didl_xml[0], pretty_print=True))
        if nl_didl_norm:
            e_normalized.append(nl_didl_norm[0])
        e_original.append(original_part[0])

        return root

    def _getPart(self, recordId, partname):
        if self.call.isAvailable(recordId, partname) == (True, True):
            # print 'Getting', partname, ' part for', self._uploadid
            stream = self.call.getStream(recordId, partname)
            return parse(stream)  # stream.read()
        return None

    def __str__(self):
        return "NL_DIDL_combined"
