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

import configparser


from meresco.xml import namespaces

NAMESPACEMAP = namespaces.copyUpdate(
    {
        "dip": "urn:mpeg:mpeg21:2005:01-DIP-NS",
        "gal": "info:eu-repo/grantAgreement",
        "hbo": "info:eu-repo/xmlns/hboMODSextension",
        "wmp": "http://www.surfgroepen.nl/werkgroepmetadataplus",
        "norm": "http://dans.knaw.nl/narcis/normalized",
        "gmhnorm": "http://gh.kb-dans.nl/normalised/v0.9/",
        "gmhcombined": "http://gh.kb-dans.nl/combined/v0.9/",
        "meta": "http://meresco.org/namespace/harvester/meta",
        "oai": "http://www.openarchives.org/OAI/2.0/",
    }
)


def read_db_config(
    conffile_path, section="client"
):  # TODO: Even importeren ergens anders vandaan. Dubbele code...
    """Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = configparser.ConfigParser()
    parser.read(conffile_path)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception("{0} not found in the {1} file".format(section, conffile_path))
    print(
        "DB-configfile read from: {0}".format(
            conffile_path,
        )
    )
    return db
