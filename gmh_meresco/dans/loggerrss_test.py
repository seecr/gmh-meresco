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

from weightless.core import be, asString
from meresco.core import Observable
from .loggerrss import LoggerRSS
from meresco.components.http import utils as httputils
from lxml.etree import XML


def test_bad_request():

    # observer = CallTrace(emptyGeneratorMethods=["add"])
    dna = be(
        (
            Observable(),
            (
                LoggerRSS(
                    title="GMH DANS-KB Normalisationlog Syndication",
                    description="Harvester normalisation log for: ",
                    link="http://rss.gharvester.dans.knaw.nl/rss",
                    maximumRecords=30,
                ),
            ),
        )
    )

    response = asString(dna.all.handleRequest(RequestURI="/rss"))
    assert response.startswith(httputils.okRss)
    rss = response.partition(httputils.CRLF * 2)[-1]
    header = '<?xml version="1.0" encoding="UTF-8"?>'
    assert rss.startswith(header)
    rss = XML(rss[len(header) :])
    assert rss.xpath("/rss/channel/title/text()") == [
        "ERROR GMH DANS-KB Normalisationlog Syndication"
    ]
