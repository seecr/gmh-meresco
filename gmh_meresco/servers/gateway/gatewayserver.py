## begin license ##
#
# Gemeenschappelijke Metadata Harvester (GMH) data extractie en OAI service
#
# Copyright (C) 2015-2016 Drents Archief http://www.drentsarchief.nl
# Copyright (C) 2015-2016, 2025 Seecr (Seek You Too B.V.) https://seecr.nl
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

import pathlib
import json
from meresco.components import (
    XmlPrintLxml,
    RewritePartname,
    FilterMessages,
)
from meresco.components.log import ApacheLogWriter, LogCollector, HandleRequestLog
from meresco.components.http import (
    BasicHttpHandler,
    ObservableHttpServer,
    PathFilter,
    IpFilter,
    Deproxy,
)
from meresco.components.sru import SruRecordUpdate

from meresco.core import Observable
from meresco.core.processtools import setSignalHandlers, registerShutdownHandler

from meresco.oai import (
    OaiJazz,
    OaiPmh,
    SuspendRegister,
    OaiAddDeleteRecordWithPrefixesAndSetSpecs,
)
from meresco.oai.info import OaiInfo

from sys import stdout

from weightless.core import be, consume
from weightless.io import Reactor

from storage import StorageComponent
from storage.storageadapter import StorageAdapter

from gmh_meresco.dans.storagesplit import Md5HashDistributeStrategy
from gmh_meresco.dans.xmlvalidator import Validate
from gmh_meresco.dans.logger import Logger  # Normalisation Logger.
from gmh_meresco.dans.normalisedidl import NormaliseDIDL
from gmh_meresco.dans.normalisemods import NormaliseMODS
from gmh_meresco.dans.addparttodocument import AddMetadataDocumentPart

# from gmh_meresco.dans.metapartconverter import AddMetadataNamespace
# from gmh_meresco.dans.longconverter import NormaliseOaiRecord

from gmh_meresco.dans.utils import NAMESPACEMAP

NORMALISED_DOC_NAME = "normdoc"


def main(reactor, port, statePath, config, **ignored):
    apacheLogStream = stdout

    oaiSuspendRegister = SuspendRegister()
    oaiJazz = OaiJazz(
        statePath.joinpath("oai").as_posix(),
        alwaysDeleteInPrefixes=[NORMALISED_DOC_NAME],
    )
    oaiJazz.updateMetadataFormat(NORMALISED_DOC_NAME, "", NAMESPACEMAP.norm)
    oaiJazz.addObserver(oaiSuspendRegister)

    normLogger = Logger(statePath.joinpath("normlogger").as_posix())

    # strategie = HashDistributeStrategy() # filename (=partname) is also hashed: difficult to read by human eye...
    strategie = Md5HashDistributeStrategy()

    storeComponent = StorageComponent(
        statePath.joinpath("store").as_posix(),
        strategy=strategie,
        partsRemovedOnDelete=[NORMALISED_DOC_NAME],
    )

    oaixIpFilter = IpFilter(
        allowedIps=config.get("allowedIps", ["127.0.0.1"]),
        allowedIpRanges=config.get("allowedIpRanges", []),
    )
    deproxy_gateway = Deproxy(
        deproxyForIps=config.get("deproxyForIps", ["127.0.0.1"]),
        deproxyForIpRanges=config.get("deproxyForIpRanges", []),
    )

    return (
        Observable(),
        # (scheduledCommitPeriodicCall,),
        # (DebugPrompt(reactor=reactor, port=port+1, globals=locals()),),
        (
            ObservableHttpServer(reactor=reactor, port=port),
            (
                LogCollector(),
                (ApacheLogWriter(apacheLogStream),),
                (
                    deproxy_gateway,
                    (
                        HandleRequestLog(),
                        (
                            BasicHttpHandler(),
                            (
                                oaixIpFilter,
                                (
                                    PathFilter("/oaix", excluding=["/oaix/info"]),
                                    (
                                        OaiPmh(
                                            repositoryName="Gateway",
                                            adminEmail="harvester@dans.knaw.nl",
                                            supportXWait=True,
                                            batchSize=2000,  # Override default batch size of 200.
                                        ),
                                        (oaiJazz,),
                                        (oaiSuspendRegister,),
                                        (
                                            StorageAdapter(),
                                            (storeComponent,),
                                        ),
                                    ),
                                ),
                                (
                                    PathFilter("/oaix/info"),
                                    (
                                        OaiInfo(reactor=reactor, oaiPath="/oaix"),
                                        (oaiJazz,),
                                    ),
                                ),
                            ),
                            (
                                PathFilter("/update"),
                                (
                                    SruRecordUpdate(
                                        sendRecordData=False,
                                        logErrors=True,
                                    ),
                                    (
                                        FilterMessages(allowed=["delete"]),
                                        (storeComponent,),
                                        (oaiJazz,),
                                    ),
                                    (
                                        FilterMessages(allowed=["add"]),
                                        # (LogComponent("LXML:"),),
                                        (
                                            Validate(
                                                [
                                                    (
                                                        "OAI-PMH header",
                                                        "//oai:header",
                                                        "OAI-PMH-header.xsd",
                                                    ),
                                                    (
                                                        "DIDL container",
                                                        "//didl:DIDL",
                                                        "didl.xsd",
                                                    ),
                                                    (
                                                        "MODS metadata",
                                                        "//mods:mods",
                                                        "mods-3-6.xsd",
                                                    ),
                                                ]
                                            ),
                                            # (LogComponent("VALIDATED:"),),
                                            (
                                                AddMetadataDocumentPart(
                                                    partName="normdoc",
                                                    fromKwarg="lxmlNode",
                                                ),
                                                (
                                                    NormaliseDIDL(
                                                        nsMap=NAMESPACEMAP,
                                                        fromKwarg="lxmlNode",
                                                    ),  # Normalise DIDL in partname=normdoc metadata
                                                    (normLogger,),
                                                    (
                                                        NormaliseMODS(
                                                            nsMap=NAMESPACEMAP,
                                                            fromKwarg="lxmlNode",
                                                        ),  # Normalise MODS in partname=normdoc metadata
                                                        (normLogger,),
                                                        (
                                                            XmlPrintLxml(
                                                                fromKwarg="lxmlNode",
                                                                toKwarg="data",
                                                            ),
                                                            (
                                                                RewritePartname(
                                                                    NORMALISED_DOC_NAME
                                                                ),  # Rename converted part.
                                                                (
                                                                    storeComponent,
                                                                ),  # Store converted/renamed part.
                                                            ),
                                                        ),
                                                        (
                                                            OaiAddDeleteRecordWithPrefixesAndSetSpecs(
                                                                metadataPrefixes=[
                                                                    NORMALISED_DOC_NAME
                                                                ]
                                                            ),
                                                            (oaiJazz,),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


def startServer(port, stateDir, globalConfig, **kwargs):
    setSignalHandlers()
    print("Firing up Gateway Server.")
    statePath = pathlib.Path(stateDir).resolve()
    statePath.mkdir(parents=True, exist_ok=True)
    config = json.loads(globalConfig.read_text())

    reactor = Reactor()
    dna = main(reactor=reactor, port=port, statePath=statePath, config=config, **kwargs)
    server = be(dna)
    consume(server.once.observer_init())

    registerShutdownHandler(
        statePath=statePath, server=server, reactor=reactor, shutdownMustSucceed=False
    )

    print("Ready to rumble at %s" % port)
    print("Global Config:")
    print(json.dumps(config, indent=2))
    stdout.flush()
    reactor.loop()
