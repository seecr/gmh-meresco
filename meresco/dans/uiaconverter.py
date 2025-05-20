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

from meresco.components import Converter


class UiaConverter(Converter):
    """ "Upload Identifier Aware Converter" (UiaConverter) overrides meresco.components.Converter#_convertArgs().
    The uploadid (kwargs['identifier'] from the calling message should now be available in the #_convert() method as self._uploadid). """

    def __init__(self, fromKwarg, toKwarg=None, name=None):
        Converter.__init__(self, name=name, fromKwarg=fromKwarg, toKwarg=toKwarg)
        self._uploadid = None

    def _convertArgs(self, *args, **kwargs):
        """ Overrides meresco.components.Converter#_convertArgs() to be able to extract the meresco uploadid. """
        try:
            oldvalue = kwargs[self._fromKwarg]
            self._uploadid = kwargs['identifier']
        except KeyError:
            pass
        else:
            del kwargs[self._fromKwarg]
            kwargs[self._toKwarg] = self._convert(oldvalue)
        return args, kwargs