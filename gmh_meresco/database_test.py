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
import random
from gmh_meresco.test_utils import TestDbConf

# Idee: Database gaat alles overnemen van de huidige ResolveStorageComponent

from gmh_meresco.dans.resolverstoragecomponent import ResolverStorageComponent


@pytest.fixture(scope="session")
def db_conf(tmp_path_factory):
    conf = TestDbConf()
    conf_file = tmp_path_factory.mktemp("conf") / "db.conf"
    conf.write_conf(conf_file)
    conf.file = conf_file

    def get_registrant_id(groupid):
        result = conf.db.select_query(
            fields=["registrant_id"],
            from_stmt="registrant",
            where_stmt="registrant_groupid=%(groupid)s",
            values=dict(groupid=groupid),
        )
        assert len(result) == 1
        return result[0]["registrant_id"]

    conf.get_registrant_id = get_registrant_id
    yield conf


def tmp_urnnbn():
    a = random.randint(1, 99)
    b = random.randint(1, 999)
    return f"urn:nbn:nl:XX:{a:02d}-{b:03d}"


def test_add_urnbn(db_conf):
    rsc = ResolverStorageComponent(db_conf.file.as_posix())
    rsc.addNbnToDB(
        identifier="ignored",
        locations=["http://publications.beeldengeluid.nl/pub/125"],
        urnnbn="urn:nbn:nl:in:10-125",
        rgid="repogroup",
    )
    assert db_conf.db.get_locations("urn:nbn:nl:in:10-125", include_ltp=True) == [
        {"uri": "http://publications.beeldengeluid.nl/pub/125", "ltp": 0}
    ]


def test_multiple_locations(db_conf):
    urnnbn = tmp_urnnbn()
    rsc = ResolverStorageComponent(db_conf.file.as_posix())
    rsc.addNbnToDB(
        identifier="ignored",
        locations=["https://example.org/1", "https://example.org/2"],
        urnnbn=urnnbn,
        rgid="repogroup",
    )
    assert db_conf.db.get_locations(urnnbn, include_ltp=True) == [
        {"uri": "https://example.org/1", "ltp": 0},
        {"uri": "https://example.org/2", "ltp": 0},
    ]


def test_urns_with_samelocation(db_conf):
    urnnbn1 = tmp_urnnbn()
    urnnbn2 = tmp_urnnbn()
    assert urnnbn1 != urnnbn2
    rsc = ResolverStorageComponent(db_conf.file.as_posix())
    for urn in [urnnbn1, urnnbn2]:
        rsc.addNbnToDB(
            identifier="ignored",
            locations=["https://example.org/1"],
            urnnbn=urn,
            rgid="repogroup",
        )
    assert db_conf.db.get_locations(urnnbn1, include_ltp=True) == [
        {"uri": "https://example.org/1", "ltp": 0},
    ]
    assert db_conf.db.get_locations(urnnbn2, include_ltp=True) == [
        {"uri": "https://example.org/1", "ltp": 0},
    ]
    rsc.addNbnToDB(
        identifier="ignored",
        locations=["https://example.org/2"],
        urnnbn=urnnbn2,
        rgid="repogroup",
    )
    assert db_conf.db.get_locations(urnnbn1, include_ltp=True) == [
        {"uri": "https://example.org/1", "ltp": 0},
    ]
    assert db_conf.db.get_locations(urnnbn2, include_ltp=True) == [
        {"uri": "https://example.org/2", "ltp": 0},
    ]


def test_registrant_only_added_once(db_conf):
    rsc = ResolverStorageComponent(db_conf.file.as_posix())
    rsc.addNbnToDB(
        identifier="ignored",
        locations=["https://example.org/1"],
        urnnbn=tmp_urnnbn(),
        rgid="tmp_rg01",
    )
    reg_db_id = db_conf.get_registrant_id("tmp_rg01")

    for i in range(4):
        rsc.addNbnToDB(
            identifier="ignored",
            locations=["https://example.org/1"],
            urnnbn=tmp_urnnbn(),
            rgid="tmp_rg01",
        )
    assert db_conf.get_registrant_id("tmp_rg01") == reg_db_id


def test_ensure_registrant(db_conf):
    rsc = ResolverStorageComponent(db_conf.file.as_posix())
    reg_id, ltp, prefix = db_conf.db.ensure_registrant("group0")
    assert ltp is False
    assert prefix == "urn:nbn:nl:"
    reg_id_again, ltp, prefix = db_conf.db.ensure_registrant("group0")
    assert reg_id_again == reg_id
    with db_conf.db.cursor() as cursor:
        cursor.execute(
            (
                "INSERT INTO registrant "
                "(registrant_groupid, isLTP, prefix) "
                "VALUES (%(groupid)s, %(ltp)s, %(prefix)s)"
            ),
            dict(groupid="group8", ltp=True, prefix="urn:nbn:nl:XX"),
        )
        new_reg_id = cursor.lastrowid
    reg_id, ltp, prefix = db_conf.db.ensure_registrant("group8")
    assert new_reg_id == reg_id
    assert ltp is True
    assert prefix == "urn:nbn:nl:XX"


# ids_uri = [
#     (
#         "urn:nbn:nl:in:10-125",
#         ["http://publications.beeldengeluid.nl/pub/125"],
#     ),
#     (
#         "urn:nbn:nl:in:10-136",
#         ["http://publications.beeldengeluid.nl/pub/136"],
#     ),
#     (
#         "urn:nbn:nl:in:10-155",
#         ["http://publications.beeldengeluid.nl/pub/155"],
#     ),
#     (
#         "urn:nbn:nl:in:10-157",
#         ["http://publications.beeldengeluid.nl/pub/157#fragment"],
#     ),
#     (
#         "urn:nbn:nl:ui:10-1874-1170",
#         ["http://dspace.library.uu.nl/bitstream/1874/1170/1/Glandorf2001.pdf"],
#     ),
#     (
#         "urn:nbn:nl:ui:11-dbi/509105ab6e3b0",
#         ["http://irs.ub.rug.nl/dbi/509105ab6e3b0"],
#     ),
#     (
#         "urn:nbn:nl:ui:13-9qz-2ce",
#         [
#             "https://easy.dans.knaw.nl/dms?command=AIP_info&aipId=twips.dans.knaw.nl-833486382286886219-1174311206456&windowStyle=default&windowContext=default"
#         ],
#     ),
#     (
#         "urn:nbn:nl:ui:24-uuid:86513f19-0e70-4927-bc43-462e154d72dd",
#         ["http://irs.ub.rug.nl/dbi/509105ab6e3b0"],
#     ),
#     (
#         "urn:nbn:nl:ui:26-1887/12275",
#         ["http://hdl.handle.net/1887/12275"],
#     ),
#     (
#         "urn:nbn:nl:ui:28-5548",
#         ["http://purl.utwente.nl/publications/5548"],
#     ),
#     (
#         "urn:nbn:nl:ui:32-377300",
#         ["http://library.wur.nl/WebQuery/wurpubs/377300"],
#     ),
#     (
#         "urn:nbn:nl:ui:39-45cce635b62db054591d4e3e35996f47",
#         ["https://www.differ.nl/node/162"],
#     ),
#     (
#         "urn:nbn:nl:ui:39-4720abcd4605174ae41bdd50ac65b952",
#         ["https://www.differ.nl/node/232"],
#     ),
