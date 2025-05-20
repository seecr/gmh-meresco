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
import time


class WriteTombstone(Observable):

    def __init__(self, name=None):
        Observable.__init__(self, name=name)

    def delete(self, identifier):
        tombstone = "%s %s" % (
            identifier,
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        yield self.all.add(identifier=identifier, partname="tombstone", data=tombstone)


class ResurrectTombstone(Observable):

    def __init__(self, name=None):
        Observable.__init__(self, name=name)

    def add(self, identifier, partname, **kwargs):
        yield self.do.deletePart(identifier=identifier, partname="tombstone")
        # return
        # yield


# For now we can only add current datetime to tombstone, because 'datestamp' of deletion is only available from OAI-pmh delete,
# but NOT from the SRU updaterequest. Thats a pitty. Now we can only say when the record was deleted from OUR system,
# not when it was deleted from the REMOTE system.

# OAI-pmh:
# <record status="deleted">
#   <header>
#     <identifier>meresco:record:3</identifier>
#     <datestamp>1999-12-21</datestamp>
#   </header>
# </record>

# SRU:
# <updateRequest>
#     <srw:version xmlns:srw="http://www.loc.gov/zing/srw/">1.0</srw:version>
#     <ucp:action xmlns:ucp="info:lc/xmlns/update-v1">info:srw/action/1/delete</ucp:action>
#     <ucp:recordIdentifier xmlns:ucp="info:lc/xmlns/update-v1">meresco:record:3</ucp:recordIdentifier>
# </updateRequest>
