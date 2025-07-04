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

from mysql.connector.pooling import MySQLConnectionPool
import mysql.connector
import time

from contextlib import contextmanager


def unfragment(identifier):
    return identifier.split("#", 1)[0]


class Database:
    def __init__(self, host, user, password, database, port=3306):
        self._pool = MySQLConnectionPool(
            pool_reset_session=True,
            pool_size=5,
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
        )

    @contextmanager
    def cursor(self, commit=True):
        with self._pool.get_connection() as conn:
            with conn.cursor() as _cursor:
                yield _cursor
            if commit is True:
                conn.commit()

    def execute_statements(self, stmts):
        with self.cursor(commit=False) as cursor:
            for stmt in stmts:
                cursor.execute(stmt)

    def select_query(
        self,
        fields,
        from_stmt,
        where_stmt,
        values,
        order_by_stmt="",
        target_fields=None,
        conv=None,
    ):
        if callable(conv):
            result_fields = [conv(f) for f in fields]
        else:
            result_fields = target_fields or fields

        if len(result_fields) != len(fields):
            raise RuntimeError("result_fields and fields need to be same length")

        results = []
        select_stmt = ", ".join(fields)

        query = f"SELECT {select_stmt} FROM {from_stmt} WHERE {where_stmt}"
        if order_by_stmt != "":
            query = f"{query} ORDER BY {order_by_stmt}"

        with self.cursor(commit=False) as cursor:
            cursor.execute(query, values)
            for hit in cursor:
                results.append(dict(zip(result_fields, hit)))
        return results

    def select_query_one(self, *args, **kwargs):
        results = self.select_query(*args, **kwargs)
        if len(results) == 0:
            return {}
        if len(results) > 1:
            raise ValueError(
                f"Unexpected more results, total ({len(results)}), for select_query(*{args!r}, **{kwargs!r})"
            )
        return results[0]

    def get_locations(self, identifier, include_ltp):
        return self.select_query(
            ["L.location_url", "IL.isFailover"],
            from_stmt="identifier I JOIN identifier_location IL ON I.identifier_id = IL.identifier_id JOIN location L ON L.location_id = IL.location_id",
            where_stmt=(
                "I.identifier_value=%(identifier)s"
                + ("" if include_ltp else " AND IL.isFailover=0")
            ),
            order_by_stmt="IL.isFailover, IL.last_modified ASC",
            values=dict(identifier=unfragment(identifier)),
            target_fields=["uri", "ltp"],
        )

    def update_nbn_locations(self, repoGroupId, identifier, locations):

        registrant_id, isLTP, prefix = self.ensure_registrant(repoGroupId)
        t0 = time.time()
        self.delete_nbn_locations(
            identifier=identifier, registrant_id=registrant_id, isLTP=isLTP
        )
        t1 = time.time()
        self.add_nbn_locations(
            identifier=identifier,
            locations=locations,
            registrant_id=registrant_id,
            isLTP=isLTP,
        )
        t2 = time.time()

        print("addNbnLocations", identifier, [str(l) for l in locations])
        print(f"Total: {t2-t0:.2f}, Delete {t1-t0:.2f}, Add {t2-t1:.2f}")

    def add_nbn_locations(self, identifier, locations, registrant_id, isLTP):
        loc_identifierid = self.select_query_one(
            ["identifier_id"],
            from_stmt="identifier",
            where_stmt="identifier_value = %s",
            values=(identifier,),
        ).get("identifier_id")
        loc_locationids = []
        for location in locations:
            loc_locationids.append(
                (
                    self.select_query_one(
                        ["location_id"],
                        from_stmt="location",
                        where_stmt="location_url = %s",
                        values=(str(location),),
                    ).get("location_id"),
                    str(location),
                )
            )
        with self.cursor() as cursor:
            if loc_identifierid is None:
                cursor.execute(
                    "INSERT INTO identifier (identifier_value) VALUES (%s)",
                    [identifier],
                )
                loc_identifierid = cursor.lastrowid
            cursor.execute(
                (
                    "INSERT IGNORE INTO identifier_registrant (identifier_id, registrant_id) "
                    "VALUES (%(loc_identifierid)s, %(registrant_id)s)"
                ),
                dict(loc_identifierid=loc_identifierid, registrant_id=registrant_id),
            )

            for loc_locationid, location in loc_locationids:
                if loc_locationid is None:
                    cursor.execute(
                        "INSERT INTO location (location_url) VALUES (%s)", [location]
                    )
                    loc_locationid = cursor.lastrowid
                cursor.execute(
                    (
                        "INSERT IGNORE INTO location_registrant (location_id, registrant_id) "
                        "VALUES (%(loc_locationid)s, %(registrant_id)s)"
                    ),
                    dict(loc_locationid=loc_locationid, registrant_id=registrant_id),
                )
                # try:
                cursor.execute(
                    (
                        "INSERT INTO identifier_location (location_id, identifier_id, last_modified, isFailover) "
                        "VALUES (%(location)s, %(identifier)s, NOW(4), %(failover)s) "
                        "ON DUPLICATE KEY "
                        "UPDATE location_id=%(location)s, identifier_id=%(identifier)s, last_modified=NOW(4)"
                    )
                    + (", isFailover=%(failover)s" if isLTP else ""),
                    dict(
                        location=loc_locationid,
                        identifier=loc_identifierid,
                        failover=isLTP,
                    ),
                )
                # except mysql.connector.IntegrityError as err:
                #     cursor.execute(
                #         "UPDATE identifier_location SET last_modified=NOW(4) "
                #         + ("isFailover=%(failover)s " if isLTP else "")
                #         + "WHERE location_id=%(location)s AND identifier_id=%(identifier)s",
                #         dict(
                #             location=loc_locationid,
                #             identifier=loc_identifierid,
                #             failover=isLTP,
                #         ),
                #     )

        # return self._stored_procedure_add_nbn_locations(
        #     identifier, locations, registrant_id, isLTP
        # )

    def delete_nbn_locations(self, identifier, registrant_id, isLTP):
        identifier_id = self.select_query_one(
            ["identifier_id"],
            from_stmt="identifier",
            where_stmt="identifier_value = %s",
            values=(identifier,),
        ).get("identifier_id")
        if identifier_id is None:
            return
        with self.cursor() as cursor:
            cursor.execute(
                (
                    "DELETE identifier_location "
                    "FROM identifier_location "
                    "INNER JOIN location_registrant ON identifier_location.location_id = location_registrant.location_id "
                    "WHERE location_registrant.registrant_id = %(registrant_id)s "
                    "AND identifier_location.identifier_id = %(identifier_id)s "
                    "AND identifier_location.isFailover = %(ltp)s"
                ),
                dict(
                    registrant_id=registrant_id,
                    ltp=isLTP,
                    identifier_id=identifier_id,
                ),
            )

    def ensure_registrant(self, repoGroupId, ltp=False, prefix="urn:nbn:nl:"):
        results = self.select_query(
            ["registrant_id", "isLTP", "prefix"],
            from_stmt="registrant",
            where_stmt="registrant_groupid = %(groupid)s",
            values=dict(groupid=repoGroupId),
        )
        if len(results) > 0:
            r = results[0]
            return r["registrant_id"], bool(r["isLTP"]), r["prefix"]
        with self.cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO registrant "
                    "(registrant_groupid, isLTP, prefix) "
                    "VALUES (%(groupid)s, %(ltp)s, %(prefix)s)"
                ),
                dict(groupid=repoGroupId, ltp=ltp, prefix=prefix),
            )
        new_reg_id = cursor.lastrowid
        return new_reg_id, ltp, prefix
