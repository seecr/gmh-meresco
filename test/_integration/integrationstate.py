# -*- coding: utf-8 -*-
## begin license ##
#
# Gemeenschappelijke Metadata Harvester (GMH) data extractie en OAI service
#
# Copyright (C) 2012-2016, 2025 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2012-2014 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
# Copyright (C) 2015-2016 Drents Archief http://www.drentsarchief.nl
# Copyright (C) 2015, 2025 Koninklijke Bibliotheek (KB) https://www.kb.nl
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

from os.path import join, abspath, dirname, realpath
from time import sleep, time
from traceback import print_exc

from seecr.test.integrationtestcase import IntegrationState
from seecr.test.portnumbergenerator import PortNumberGenerator
from seecr.test.utils import postRequest, sleepWheel

from glob import glob

import mysql.connector
import configparser
import pathlib
import json

from gmh_meresco.dans.utils import read_db_config
from gmh_meresco.test_utils import TestDbConf

mydir = dirname(abspath(__file__))
projectDir = dirname(dirname(mydir))


class GmhTestIntegrationState(IntegrationState):
    def __init__(self, stateName, tests=None, fastMode=False):
        IntegrationState.__init__(self, stateName, tests=tests, fastMode=fastMode)
        self.testdataDir = join(dirname(mydir), "updateRequest")
        self.gatewayPort = PortNumberGenerator.nextPort()
        self.apiPort = PortNumberGenerator.nextPort()
        self.resolverPort = PortNumberGenerator.nextPort()

    def binDir(self):
        return join(projectDir, "bin")

    def setUp(self):
        db_conf = TestDbConf()
        self.db = db_conf.db
        db_conf.write_conf(pathlib.Path(self.integrationTempdir) / ".db.conf")
        global_config = pathlib.Path(self.integrationTempdir) / "global-config.json"
        global_config.write_text(
            json.dumps(
                {
                    "info": dict(
                        oai_admin_email="admin@example.org",
                        oai_base_url="https://oai.example.org",
                        harvester_base_url="https://harvester.example.org",
                    )
                }
            )
        )
        self.startGatewayServer()
        self.startApiServer()
        self.startResolverServer()
        self.waitForServicesStarted()
        self._createDatabase()
        sleep(0.2)

    def startGatewayServer(self):
        executable = self.binPath("start-gateway")
        self._startServer(
            serviceName="gateway",
            debugInfo=True,
            executable=executable,
            serviceReadyUrl="http://localhost:%s/info/version" % self.gatewayPort,
            cwd=dirname(abspath(executable)),
            port=self.gatewayPort,
            stateDir=join(self.integrationTempdir, "gateway"),
            globalConfig=join(self.integrationTempdir, "global-config.json"),
            waitForStart=False,
        )

    def startApiServer(self):
        executable = self.binPath("start-api")
        self._startServer(
            serviceName="api",
            debugInfo=True,
            executable=executable,
            serviceReadyUrl="http://localhost:%s/info/version" % self.apiPort,
            cwd=dirname(abspath(executable)),
            port=self.apiPort,
            gatewayPort=self.gatewayPort,
            stateDir=join(self.integrationTempdir, "api"),
            globalConfig=join(self.integrationTempdir, "global-config.json"),
            waitForStart=False,
            flagOptions=["quickCommit"],
        )

    def startResolverServer(self):
        executable = self.binPath("start-resolver")
        self._startServer(
            serviceName="resolver",
            debugInfo=True,
            executable=executable,
            serviceReadyUrl="http://localhost:%s/" % self.resolverPort,
            cwd=dirname(abspath(executable)),
            port=self.resolverPort,
            gatewayPort=self.gatewayPort,
            stateDir=join(self.integrationTempdir, "resolver"),
            dbConfig=join(self.integrationTempdir, ".db.conf"),
            globalConfig=join(self.integrationTempdir, "global-config.json"),
            waitForStart=False,
            flagOptions=["quickCommit"],
        )

    def _createDatabase(self):
        if self.fastMode:
            print("Reusing database in", self.integrationTempdir)
            return
        start = time()
        print("Creating database in", self.integrationTempdir)
        try:
            for f in sorted(glob(self.testdataDir + "/*.updateRequest")):
                print("Uploading file:", f)
                postRequest(
                    self.gatewayPort,
                    "/update",
                    data=open(join(self.testdataDir, f)).read(),
                    parse=False,
                )
                sleepWheel(0.3)
            # sleepWheel(1)
            print("Finished creating database in %s seconds" % (time() - start))
            # print "Pauzing for a while..."
            # sleepWheel(600)
        except Exception:
            print("Error received while creating database for", self.stateName)
            print_exc()
            sleep(1)
            exit(1)

    def tearDown(self):
        super(
            GmhTestIntegrationState, self
        ).tearDown()  # Call super, otherwise the services will NOT be killed and continue to run!
