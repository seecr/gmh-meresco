## begin license ##
#
# Gemeenschappelijke Metadata Harvester (GMH) data extractie en OAI service
#
# Copyright (C) 2012-2016, 2025 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2025 Koninklijke Bibliotheek (KB) https://www.kb.nl
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

from os import getuid
import sys

assert getuid() != 0, "Do not run tests as 'root'"


from seecrdeps import includeParentAndDeps

includeParentAndDeps(__file__, scanForDeps=True)

from seecr.test.testrunner import TestRunner
from _integration import GmhTestIntegrationState

if __name__ == "__main__":  # TODO: arg[0] fastMode uitlezen.
    runner = TestRunner()
    # Setting fastmode to True, will SKIP the upload part, and reuse existing database/store for the integration tests.
    runner.fastMode = False
    print("FASTMODE:", runner.fastMode)

    GmhTestIntegrationState(
        "brigmh",
        "/home/seecr/.seecr/.gmhtestdb.conf",
        tests=[
            "_integration.gatewaytest.GatewayTest",
            "_integration.apitest.ApiTest",
            "_integration.resolvertest.ResolverTest",
        ],
        fastMode=runner.fastMode,
    ).addToTestRunner(runner)
    runner.run()
