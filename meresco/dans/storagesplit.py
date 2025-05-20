# -*- coding: utf-8 -*-
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

from hashlib import md5


class Md5HashDistributeStrategy(object):

    @classmethod
    def split(self, identifier_partname):
        (identifier, partName) = identifier_partname
        if isinstance(identifier, bytes):
            identifier = identifier.decode(encoding="utf-8")
        if isinstance(partName, bytes):
            partName = partName.decode(encoding="utf-8")

        result = [identifier]
        if ":" in identifier:
            first, second = identifier.split(":", 1)
            md5string = md5(identifier.encode(encoding="utf-8")).hexdigest()
            result = [first, md5string[0:2], md5string[2:4], second]
        if partName is not None:
            return result + [partName]
        return result

    @classmethod
    def join(self, parts):
        if parts and len(parts) == 5:
            return ("%s:%s" % (parts[0], parts[3]), parts[-1])
        raise MD5JoinError("md5Join Error. Need 5 parts" + str(parts))


def md5Split(xxx_todo_changeme1):
    return Md5HashDistributeStrategy.split(xxx_todo_changeme1)


def md5Join(parts):
    return Md5HashDistributeStrategy.join(parts)


class MD5JoinError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
