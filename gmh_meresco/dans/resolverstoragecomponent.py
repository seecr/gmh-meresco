# -*- coding: utf-8 -*-
## begin license ##
#
# Gemeenschappelijke Metadata Harvester (GMH) data extractie en OAI service
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2012, 2016-2018, 2025 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2012 Stichting Bibliotheek.nl (BNL) http://stichting.bibliotheek.nl
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

import mysql.connector
import mysql.connector.pooling
import time
from re import compile

from gmh_common.utils import read_db_config
from gmh_common.database import Database

urnnbnRegex = compile("^[uU][rR][nN]:[nN][bB][nN]:[nN][lL](:([a-zA-Z]{2}))?:\\d{2}-.+")


class ResolverStorageComponent(object):
    def __init__(self, dbconfig, name=None):
        self._db = Database(**read_db_config(conffile_path=dbconfig))
        self._name = name

    def observable_name(self):
        return self._name

    def addNbnToDB(self, identifier, locations, urnnbn, rgid):
        """Add a prioritized list of locations for a pid and repository to storage.

        The locations-list is added in reversed order.
        Therefore the highest priority-location will be inserted last and will resolve first.

        :param identifier: Meresco uploadid of this record. NOT IN USE, but good Meresco design practise. (Meresco => repoId:OAI-PMH-identifier)
        :param locations: prioritized list of locations
        :param urnnbn: urn:nbn persistent identifier
        :param rgid: meresco repository group identifier
        :return: void
        """
        rgid = rgid.lower()
        urnnbn = urnnbn.lower()

        # Get rid of the fragment part:
        if urnnbn is not None and "#" in urnnbn:
            urnnbn = urnnbn.split("#", 1)[0]

        if not urnnbnRegex.match(
            urnnbn
        ):  # DIDL normalisation rejects records with invalid urn:nbn identifiers. So this check is overhead, for this situation.
            return

        try:
            self._db.update_nbn_locations(
                repoGroupId=rgid, identifier=urnnbn, locations=locations
            )
        except mysql.connector.Error as e:
            print("Error from SQL-db: {}".format(e))
            raise
        return
