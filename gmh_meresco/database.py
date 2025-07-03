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

    def add_nbn_locations(self, identifier, locations, registrant_id, isLTP):
        with self.cursor() as cursor:
            for location in locations:
                cursor.execute(
                    "call addNbnLocation(%(identifier)s, %(location)s, %(registrant_id)s, %(isLTP)s)",
                    dict(
                        identifier=unfragment(identifier),
                        location=str(location),
                        registrant_id=registrant_id,
                        isLTP=isLTP,
                    ),
                )

    def delete_nbn_locations(self, identifier, registrant_id, isLTP):
        with self.cursor() as cursor:
            cursor.execute(
                "call deleteNbnLocationsByRegistrantId(%(identifier)s, %(registrant_id)s, %(isLTP)s)",
                dict(
                    identifier=unfragment(identifier),
                    registrant_id=registrant_id,
                    isLTP=isLTP,
                ),
            )

    def ensure_registrant(self, repoGroupId):
        results = self.select_query(
            ["registrant_id", "isLTP", "prefix"],
            from_stmt="registrant",
            where_stmt="registrant_groupid = %(groupid)s",
            values=dict(groupid=repoGroupId),
        )
        if len(results) > 0:
            r = results[0]
            return r["registrant_id"], bool(r["isLTP"]), r["prefix"]
        ltp = False
        prefix = "urn:nbn:nl:"
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
