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

from meresco.dans.storagesplit import Md5HashDistributeStrategy, md5Split, md5Join


def test_split():
    for split_function in [Md5HashDistributeStrategy.split, md5Split]:
        result = split_function(("identifier", "partname"))
        assert result == ["identifier", "partname"]
        result = split_function(("identifier:subpart", "partname"))
        assert result == ["identifier", "81", "ed", "subpart", "partname"]

        result = split_function((b"identifier:subpart", "partname"))
        assert result == ["identifier", "81", "ed", "subpart", "partname"]
        result = split_function(("identifier:subpart", b"partname"))
        assert result == ["identifier", "81", "ed", "subpart", "partname"]
        result = split_function((b"identifier:subpart", b"partname"))
        assert result == ["identifier", "81", "ed", "subpart", "partname"]

        assert split_function(("tue:oai:library.tue.nl:692605", "metadata")) == [
            "tue",
            "ff",
            "fa",
            "oai:library.tue.nl:692605",
            "metadata",
        ]


def test_join():
    for join_function in [Md5HashDistributeStrategy.join, md5Join]:
        assert join_function(
            ["tue", "ff", "fa", "oai:library.tue.nl:692605", "metadata"]
        ) == ("tue:oai:library.tue.nl:692605", "metadata")
