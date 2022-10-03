# -*- coding: utf-8 -*-
## begin license ##
#
# "Storage" stores data in a reliable, extendable filebased storage
# with great performance.
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2012, 2016-2018 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012 Stichting Bibliotheek.nl (BNL) http://stichting.bibliotheek.nl
#
# This file is part of "Storage"
#
# "Storage" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Storage" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Storage"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import mysql.connector
import mysql.connector.pooling
import ConfigParser
from os.path import abspath, dirname, join, realpath
from re import compile


urnnbnRegex = compile('^[uU][rR][nN]:[nN][bB][nN]:[nN][lL](:([a-zA-Z]{2}))?:\\d{2}-.+')

class ResolverStorageComponent(object):
    def __init__(self, dbconfig, name=None): # https://pynative.com/python-mysql-tutorial/
        self._dbconfig = self.read_db_config(conffile_path=dbconfig)
        self._name = name
        self._cnxpool = self._create_cnxpool(pool_name="resolver_pool", pool_size=4)
        

    def observable_name(self):
        return self._name

    def addNbnToDB(self, identifier, locations, urnnbn, rgid):
        """ Add a prioritized list of locations for a pid and repository to storage.
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

        if not urnnbnRegex.match(urnnbn): # DIDL normalisation rejects records with invalid urn:nbn identifiers. So this check is overhead, for this situation.
            return
        #TODO: Check if NBN needs to be "unfragmented"...
        #TODO: Move all into one transaction.
        try:
            registrant_id, isLPT, prefix = self._selectOrInsertRegistrantId_pl(rgid)
            # Check if correct prefix:
            if not urnnbn.startswith(prefix):
                print "{nbn} does not match prefix '{prefix}'. Registration skipped.".format(nbn=urnnbn, prefix=prefix)
                return
            self._deleteNbnLocationsByRegId_pl(registrant_id, urnnbn)
            self._insertNbnLocations(registrant_id, urnnbn, locations)

        except mysql.connector.Error as e:
            print("Error from SQL-db: ", e)
        return


    def _insertNbnLocations(self, registrant_id, urnnbn, locations):
        """
         Upserts all locations for this identifier and registrantId
        """
        try:
            conn = self._cnxpool.get_connection()
            cursor = conn.cursor()
            for location in locations:
                cursor.callproc('insertNbnLocation', (str(urnnbn), str(location), int(registrant_id)))
                conn.commit()
            self.close(conn, cursor)
        except mysql.connector.Error as err:
            print "Error while execute'ing storedprocedure insertNbnLocation: {}".format(err)


    def _deleteNbnLocationsByRegId_pl(self, registrant_id, identifier):
        """
        Removes all id/loc & loc/reg pairs for this registrant_id and nbn-identifier.
        This prevents deleting locations for this NBN that where registered by OTHER registrants (NBN-own repo perhaps).
        It takes LTP into account.
        """
        try:
            conn = self._cnxpool.get_connection()
            cursor = conn.cursor()
            cursor.callproc('deleteNbnLocationsByRegistrant', (str(identifier), int(registrant_id)))
            conn.commit()
            self.close(conn, cursor)
        except mysql.connector.Error as err:
            print "Error while execute'ing storedprocedure deleteNbnLocationsByRegistrant: {}".format(err)


    def _selectOrInsertRegistrantId_pl(self, rgid):
        isLTP = False
        prefix = "urn:nbn:nl"
        try:
            conn = self._cnxpool.get_connection()
            # print conn.get_server_info()
            cursor = conn.cursor()
            sql = "SELECT * FROM registrant WHERE registrant_groupid = '%s'" % rgid
            cursor.execute(sql)
            res = cursor.fetchall()
            if len(res) > 0 :
                registrant_id = res[0][0]
                isLTP = bool(res[0][3])
                prefix = res[0][4]
            else:  # registrant_id not available from DB. Insert it and return the new id.
                sql = "INSERT INTO registrant (registrant_groupid) VALUES ('%s')" % rgid
                cursor.execute(sql)
                registrant_id = cursor.lastrowid
                conn.commit()
            self.close(conn, cursor)
            return registrant_id, isLTP, prefix
        except mysql.connector.Error as err:
            print "Error while execute'ing SQL-query: {}".format(err)


    def read_db_config(self, conffile_path, section='mysql'): #TODO: Even importeren ergens anders vandaan. Dubbele code...
        """ Read database configuration file and return a dictionary object
        :param filename: name of the configuration file
        :param section: section of database configuration
        :return: a dictionary of database parameters
        """
        # create parser and read ini configuration file
        parser = ConfigParser.ConfigParser()
        parser.read(conffile_path)

        # get section, default to mysql
        db = {}
        if parser.has_section(section):
            items = parser.items(section)
            for item in items:
                db[item[0]] = item[1]
        else:
            raise Exception('{0} not found in the {1} file'.format(section, conffile_path))
        print "DB-configfile read from: {0}".format(conffile_path, )
        return db

    def _create_cnxpool(self, pool_name="mypool", pool_size=5):
        """
        Create a connection pool, after created, the request of connecting
        MySQL could get a connection from this pool instead of request to
        create a connection.
        :param pool_name: the name of pool, default is "mypool"
        :param pool_size: the size of pool, default is 3
        :return: connection pool
        """
        try:
            pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                pool_reset_session=True,
                **self._dbconfig)
            print "Created ConnectionPool: Name=", pool.pool_name, ", Poolsize=", pool.pool_size
            return pool
        except mysql.connector.Error as err:
            print "Error while creating MySQL Connection pool : {}".format(err)

        # To close ALL connections in the pool: https://github.com/mysql/mysql-connector-python/blob/master/lib/mysql/connector/pooling.py#L335
        # pool._remove_connections()

    def close(self, conn, cursor):
        """
        A method used to close connection of mysql.
        :param conn:
        :param cursor:
        :return:
        """
        cursor.close()
        conn.close()

