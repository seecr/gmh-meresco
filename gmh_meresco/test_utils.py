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

import mysql.connector
from gmh_meresco.dans.utils import read_db_config
from gmh_meresco.database import Database
import pathlib

default_conf = pathlib.Path("/home/seecr/.seecr/.gmhtestdb.conf")


class TestDbConf:
    __test__ = False

    def __init__(self, conf_file=default_conf):
        self._conf_file = default_conf
        truncate_test_db(self._conf_file)
        self.db = Database(**read_db_config(self._conf_file))

    def write_conf(self, aPath):
        aPath.write_text(self._conf_file.read_text())


def truncate_test_db(dbconfig):
    try:
        cnx = mysql.connector.connect(**read_db_config(dbconfig))
        cursor = cnx.cursor()

        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        # cursor.execute(("TRUNCATE TABLE gmhtest.credentials")
        # cursor.execute(query)
        cursor.execute("TRUNCATE TABLE gmhtest.identifier_location")
        cursor.execute("TRUNCATE TABLE gmhtest.location_registrant")
        cursor.execute("TRUNCATE TABLE gmhtest.identifier_registrant")
        cursor.execute("TRUNCATE TABLE gmhtest.identifier")
        cursor.execute("TRUNCATE TABLE gmhtest.location")
        cursor.execute("TRUNCATE TABLE gmhtest.registrant")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        cursor.close()
        cnx.commit()
        cnx.close()

    except mysql.connector.Error as err:
        print("Error with SQLstore: {}".format(err))
