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

from .docdata import DocData


def test_get_document(tmp_path):
    dd = DocData([tmp_path / "one", tmp_path / "two"])
    assert dd.get_document(name="some.txt") == None
    tmp_path.joinpath("one").mkdir()
    tmp_path.joinpath("two").mkdir()
    tmp_path.joinpath("two/sub").mkdir()
    tmp_path.joinpath("one/some.txt").write_text("Some text")
    tmp_path.joinpath("two/other.txt").write_text("Other text")
    tmp_path.joinpath("one/first.txt").write_text("First")
    tmp_path.joinpath("two/first.txt").write_text("Second")
    tmp_path.joinpath("two/sub/some.txt").write_text("Some sub text")
    assert dd.get_document(name="some.txt") == "Some text"
    assert dd.get_document(name="other.txt") == "Other text"
    assert dd.get_document(name="first.txt") == "First"
    assert dd.get_document(name="sub/some.txt") == "Some sub text"
