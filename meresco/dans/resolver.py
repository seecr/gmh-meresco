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

from meresco.core import Observable
from meresco.xml.namespaces import namespaces
from lxml import etree
from lxml.etree import parse, XMLSchema, XMLSchemaParseError, _ElementTree, tostring, fromstring


class Resolver(Observable):

    def __init__(self, ro=True, name=None, nsMap=None):
        Observable.__init__(self, name=name)
        self._nsMap = namespaces.copyUpdate(nsMap or {})
        self._isReadOnly = ro


    def add(self, identifier, partname, lxmlNode, **kwargs):

        # TODO: Check if we need to resolve urn:nbn avaialable from DIDL-objectFile's too.

        # - Meerdere lokaties per urn:nbn per repository: JA, OVERNEMEN (in praktijk is er maar 1 per repo, maar is nodig voor provenance): Er wordt geitereerd over locaties die NIET marked DELETED zijn. De meest recente wint.
        # - Deletes van urn:nbn en bijhorende lokatie (via SRU-delete): NEE = OVERNEMEN
        # - Bij een nieuwe upload van locaties-nbn pairs voor een merescoGroup ID, worden de Locaties die reeds in database staan, maar niet meer voorkomen in de nieuwe lijst, in de database deleted voor de betreffende repository

        f_normdoc = fromstring(lxmlNode.xpath("//document:document/document:part[@name='normdoc']/text()", namespaces=self._nsMap)[0]) #TODO: import 'normdoc" string.
        f_meta = fromstring(lxmlNode.xpath("//document:document/document:part[@name='meta']/text()", namespaces=self._nsMap)[0]) #TODO: import 'normdoc" string.

        nbnlocation = f_normdoc.xpath('//didl:DIDL/didl:Item/didl:Component/didl:Resource/@ref', namespaces=self._nsMap)
        urnnbn = f_normdoc.xpath('//didl:DIDL/didl:Item/didl:Descriptor/didl:Statement/dii:Identifier/text()', namespaces=self._nsMap)[0]
        repositorygroupid = f_meta.xpath('//meta:meta/meta:repository/meta:repositoryGroupId/text()', namespaces=self._nsMap)[0]
        
        yield self.do.addNbnToDB(identifier, locations=nbnlocation, urnnbn=urnnbn, rgid=repositorygroupid)
