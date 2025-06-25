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

import pathlib


class DocData:
    def __init__(self, doc_paths):
        self._paths = [pathlib.Path(p).resolve() for p in doc_paths]

    def get_document(self, name):
        print(f"get_document({name!r})")
        for p in self._paths:
            f = p.joinpath(name).resolve()
            print(f"Path {f!r}")
            if p.parts != f.parts[: len(p.parts)] or not f.is_file():
                continue
            return f.read_text()
