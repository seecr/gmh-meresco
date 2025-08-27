#!/usr/bin/env python3
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

import argparse
import pathlib
from meresco.components import lxmltostring
from lxml.etree import XMLParser, parse


def _parse(file):
    with file.open() as fp:
        parser = XMLParser(remove_blank_text=True)
        return parse(fp, parser)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--inplace",
        help="Pretty print in place",
        default=False,
        action="store_true",
    )
    parser.add_argument("files", type=pathlib.Path, nargs="*")
    args = parser.parse_args()

    for file in args.files:
        if not file.is_file():
            print(f"No file {file!r}")
            continue
        x = _parse(file)
        pretty = lxmltostring(x, pretty_print=True)
        if not args.inplace:
            print(pretty)
        t = file.with_name("~" + file.name + ".tmp")
        t.write_text(pretty)
        t.rename(file)
