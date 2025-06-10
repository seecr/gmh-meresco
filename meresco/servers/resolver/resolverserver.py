# -*- coding: utf-8 -*-
## begin license ##
#
# Gemeenschappelijke Metadata Harvester (GMH) data extractie en OAI service
#
# Copyright (C) 2012-2016, 2025 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2015 Data Archiving and Networked Services (DANS) http://dans.knaw.nl
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

import sys
from sys import stdout
from os.path import join, dirname, abspath

from weightless.core import be, consume
from weightless.io import Reactor

import json

from meresco.core import Observable
from meresco.core.alltodo import AllToDo
from meresco.core.processtools import setSignalHandlers, registerShutdownHandler

from meresco.components import (
    RenameFieldForExact,
    PeriodicDownload,
    XmlPrintLxml,
    XmlXPath,
    FilterMessages,
    RewritePartname,
    XmlParseLxml,
    CqlMultiSearchClauseConversion,
    PeriodicCall,
    Schedule,
    XsltCrosswalk,
    RetrieveToGetDataAdapter,
)  # , Rss, RssItem
from meresco.components.http import (
    ObservableHttpServer,
    BasicHttpHandler,
    PathFilter,
    Deproxy,
    StringServer,
    FileServer,
)
from meresco.components.log import (
    LogCollector,
    ApacheLogWriter,
    HandleRequestLog,
    LogCollectorScope,
    QueryLogWriter,
    DirectoryLog,
    LogFileServer,
    LogComponent,
)

from meresco.oai import (
    OaiPmh,
    OaiDownloadProcessor,
    UpdateAdapterFromOaiDownloadProcessor,
    OaiJazz,
    OaiBranding,
    OaiProvenance,
    OaiAddDeleteRecordWithPrefixesAndSetSpecs,
)


from seecr.utils import DebugPrompt

from meresco.dans.resolver import Resolver
from meresco.dans.resolverstoragecomponent import ResolverStorageComponent
from meresco.servers.gateway.gatewayserver import NORMALISED_DOC_NAME

from meresco.components.http.utils import (
    ContentTypePlainText,
    okPlainText,
    ContentTypeJson,
)

# from meresco.dans.loggerrss import LoggerRSS
# from meresco.dans.logger import Logger # Normalisation Logger.

# NL_DIDL_NORMALISED_PREFIX = 'nl_didl_norm'
# NL_DIDL_COMBINED_PREFIX = 'nl_didl_combined'

from meresco.dans.utils import NAMESPACEMAP


def createDownloadHelix(reactor, periodicDownload, oaiDownload, dbStorageComponent):
    return (
        periodicDownload,  # Scheduled connection to a remote (response / request)...
        (
            XmlParseLxml(
                fromKwarg="data",
                toKwarg="lxmlNode",
                parseOptions=dict(huge_tree=True, remove_blank_text=True),
            ),  # Convert from plain text to lxml-object.
            (
                oaiDownload,  # Implementation/Protocol of a PeriodicDownload...
                (
                    UpdateAdapterFromOaiDownloadProcessor(),  # Maakt van een SRU update/delete bericht (lxmlNode) een relevante message: 'delete' of 'add' message.
                    # (FilterMessages(['delete']), # Filtert delete messages
                    #     # (LogComponent("Delete msg:"),),
                    #     # Write a 'deleted' part to the storage, that holds the (Record)uploadId.
                    #     # (WriteTombstone(),
                    #     #     (storageComponent,),
                    #     # )
                    # ),
                    (
                        FilterMessages(allowed=["add"]),
                        # (LogComponent("AddToNBNRES"),),
                        (
                            Resolver(ro=False, nsMap=NAMESPACEMAP),
                            (dbStorageComponent,),
                        ),
                        # (XmlXPath(['//document:document/document:part[@name="normdoc"]/text()'], fromKwarg='lxmlNode', toKwarg='data', namespaces=NAMESPACEMAP),
                        #     (XmlParseLxml(fromKwarg='data', toKwarg='lxmlNode'),
                        #         (LogComponent("NORMDOC"),),   #TODO: get urn:nbn and location from document.
                        #         # (RewritePartname(NL_DIDL_NORMALISED_PREFIX), # Hernoemt partname van 'record' naar "metadata".
                        #         #     (XmlPrintLxml(fromKwarg="lxmlNode", toKwarg="data", pretty_print=True),
                        #         #         (storageComponent,) # Schrijft oai:metadata (=origineel) naar storage.
                        #         #     )
                        #         # )
                        #     )
                        # )
                    ),
                ),
            ),
        ),
    )


def main(
    reactor, port, state_path, gatewayPort, dbConfig, quickCommit=False, **ignored
):

    # TODO: Implement logging.
    # normLogger = Logger(state_path.joinpath('..', 'gateway', 'normlogger').as_posix())

    dbStorageComponent = ResolverStorageComponent(dbConfig)
    verbose = True

    periodicGateWayDownload = PeriodicDownload(
        reactor,
        host="localhost",
        port=gatewayPort,
        schedule=Schedule(
            period=0.1 if quickCommit else 10
        ),  # WST: Interval in seconds before sending a new request to the GATEWAY in case of an error while processing batch records.(default=1). IntegrationTests need <=1 second! Otherwise tests will fail!
        name="resolver",
        autoStart=True,
    )

    oaiDownload = OaiDownloadProcessor(
        path="/oaix",
        metadataPrefix=NORMALISED_DOC_NAME,
        workingDirectory=state_path.joinpath("harvesterstate", "gateway").as_posix(),
        userAgentAddition="ResolverServer",
        xWait=True,
        name="resolver",
        autoCommit=False,
    )

    return (
        Observable(),
        createDownloadHelix(
            reactor, periodicGateWayDownload, oaiDownload, dbStorageComponent
        ),
        (
            ObservableHttpServer(reactor, port, compressResponse=True),
            (
                BasicHttpHandler(),
                (
                    PathFilter("/"),
                    (StringServer("Resolver Server", ContentTypePlainText),),
                ),
            ),
        ),
    )


def startServer(
    port, stateDir, gatewayPort, dbConfig, globalConfig, quickCommit=False, **kwargs
):
    setSignalHandlers()
    print("Firing up resolver Server.")
    state_path = stateDir.resolve()
    state_path.mkdir(parents=True, exist_ok=True)
    config = json.loads(globalConfig.read_text())

    reactor = Reactor()
    dna = main(
        reactor=reactor,
        port=port,
        state_path=state_path,
        gatewayPort=gatewayPort,
        dbConfig=dbConfig,
        config=config,
        quickCommit=quickCommit,
        **kwargs
    )

    server = be(dna)
    consume(server.once.observer_init())

    registerShutdownHandler(
        statePath=state_path.as_posix(),
        server=server,
        reactor=reactor,
        shutdownMustSucceed=False,
    )

    print("Ready to rumble at %s" % port)
    print("Global Config:")
    print(json.dumps(config, indent=2))
    sys.stdout.flush()
    reactor.loop()
