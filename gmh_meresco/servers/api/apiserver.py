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
from os.path import dirname, abspath
import pathlib
import markdown2

from weightless.core import be, consume
from weightless.io import Reactor


from meresco.core import Observable
from meresco.core.processtools import setSignalHandlers, registerShutdownHandler
from meresco.sequentialstore import MultiSequentialStorage, StorageComponentAdapter

from meresco.components import (
    PeriodicDownload,
    XmlPrintLxml,
    XmlXPath,
    FilterMessages,
    RewritePartname,
    XmlParseLxml,
    Schedule,
    RetrieveToGetDataAdapter,
)  # , Rss, RssItem
from meresco.components.http import (
    ObservableHttpServer,
    BasicHttpHandler,
    PathFilter,
    PathRename,
    Deproxy,
    IpFilter,
    FileServer,
)
from meresco.components.log import (
    LogCollector,
    ApacheLogWriter,
    HandleRequestLog,
    LogComponent,
)
from meresco.html import DynamicHtml

from meresco.oai import (
    OaiPmh,
    OaiDownloadProcessor,
    UpdateAdapterFromOaiDownloadProcessor,
    OaiJazz,
    OaiBranding,
    OaiProvenance,
)  # , OaiAddDeleteRecordWithPrefixesAndSetSpecs
from meresco.oai.info import OaiInfo


from storage import StorageComponent

from meresco.xml import namespaces


from gmh_meresco.dans.nldidlcombined import NlDidlCombined
from gmh_meresco.dans.writedeleted import ResurrectTombstone, WriteTombstone
from gmh_meresco.servers.gateway.gatewayserver import NORMALISED_DOC_NAME
from gmh_meresco.servers.information import server_information
from gmh_meresco.dans.loggerrss import LoggerRSS
from gmh_meresco.dans.logger import Logger  # Normalisation Logger.
from gmh_meresco.seecr.oai import OaiAddRecord

from .docdata import DocData

import pathlib
import json

NL_DIDL_NORMALISED_PREFIX = "nl_didl_norm"
NL_DIDL_COMBINED_PREFIX = "nl_didl_combined"

NAMESPACEMAP = namespaces.copyUpdate(
    {
        "dip": "urn:mpeg:mpeg21:2005:01-DIP-NS",
        "gal": "info:eu-repo/grantAgreement",
        "hbo": "info:eu-repo/xmlns/hboMODSextension",
        "wmp": "http://www.surfgroepen.nl/werkgroepmetadataplus",
        "gmhnorm": "http://gh.kb-dans.nl/normalised/v0.9/",
        "gmhcombined": "http://gh.kb-dans.nl/combined/v0.9/",
        "meta": "http://meresco.org/namespace/harvester/meta",
        "oai": "http://www.openarchives.org/OAI/2.0/",
    }
)

my_path = pathlib.Path(__file__).resolve().parent
dynamicPath = my_path / "dynamic"
staticPath = my_path / "static"
docPath = pathlib.Path("/usr/share/doc/gmh-meresco")
docPath = my_path.parent.parent.parent / "doc"  # DO_NOT_DISTRIBUTE
# staticHtmlPath = join(myPath, 'controlpanel', 'html', 'static')


def createDownloadHelix(
    reactor, periodicDownload, oaiDownload, storageComponent, oaiJazz
):
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
                    (
                        FilterMessages(["delete"]),  # Filtert delete messages
                        # (LogComponent("Delete Update"),),
                        (storageComponent,),  # Delete from storage
                        (oaiJazz,),  # Delete from OAI-pmh repo
                        # Write a 'deleted' part to the storage, that holds the (Record)uploadId.
                        (
                            WriteTombstone(),
                            (storageComponent,),
                        ),
                    ),
                    (
                        FilterMessages(allowed=["add"]),
                        # (LogComponent("ADD"),),
                        (
                            XmlXPath(
                                [
                                    '//document:document/document:part[@name="normdoc"]/text()'
                                ],
                                fromKwarg="lxmlNode",
                                toKwarg="data",
                                namespaces=NAMESPACEMAP,
                            ),
                            # (LogComponent("NORMDOC"),),
                            (
                                XmlParseLxml(fromKwarg="data", toKwarg="lxmlNode"),
                                (
                                    RewritePartname(
                                        NL_DIDL_NORMALISED_PREFIX
                                    ),  # Hernoemt partname van 'record' naar "metadata".
                                    (
                                        XmlPrintLxml(
                                            fromKwarg="lxmlNode",
                                            toKwarg="data",
                                            pretty_print=True,
                                        ),
                                        (
                                            storageComponent,
                                        ),  # Schrijft oai:metadata (=origineel) naar storage.
                                    ),
                                ),
                            ),
                        ),
                        (
                            XmlXPath(
                                [
                                    '//document:document/document:part[@name="record"]/text()'
                                ],
                                fromKwarg="lxmlNode",
                                toKwarg="data",
                                namespaces=NAMESPACEMAP,
                            ),
                            (
                                XmlParseLxml(fromKwarg="data", toKwarg="lxmlNode"),
                                # TODO: Check indien conversies misgaan, dat ook de meta en header part niet naar storage gaan: geen enkel part als het even kan...
                                # Schrijf 'header' partname naar storage:
                                (
                                    XmlXPath(
                                        ["/oai:record/oai:header"],
                                        fromKwarg="lxmlNode",
                                        namespaces=NAMESPACEMAP,
                                    ),
                                    (
                                        RewritePartname("header"),
                                        (
                                            XmlPrintLxml(
                                                fromKwarg="lxmlNode",
                                                toKwarg="data",
                                                pretty_print=True,
                                            ),
                                            (
                                                storageComponent,
                                            ),  # Schrijft OAI-header naar storage.
                                        ),
                                    ),
                                ),
                                # Schrijf 'metadata' partname naar storage:
                                # Op gharvester21 gaat dit niet goed: Daar is het root element <metadata> in het 'metadata' part, in plaats van <DIDL>.
                                # Liever hier een child::node(), echter gaat deze syntax mis i.c.m. XmlXPath component??
                                (
                                    XmlXPath(
                                        ["/oai:record/oai:metadata/didl:DIDL"],
                                        fromKwarg="lxmlNode",
                                        namespaces=NAMESPACEMAP,
                                    ),
                                    # (LogComponent("METADATA_PART"),),
                                    (
                                        RewritePartname("metadata"),
                                        (
                                            XmlPrintLxml(
                                                fromKwarg="lxmlNode",
                                                toKwarg="data",
                                                pretty_print=True,
                                            ),
                                            (
                                                storageComponent,
                                            ),  # Schrijft metadata naar storage.
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        (
                            XmlXPath(
                                [
                                    '//document:document/document:part[@name="record"]/text()'
                                ],
                                fromKwarg="lxmlNode",
                                toKwarg="data",
                                namespaces=NAMESPACEMAP,
                            ),
                            (
                                XmlParseLxml(fromKwarg="data", toKwarg="lxmlNode"),
                                (
                                    NlDidlCombined(
                                        nsMap=NAMESPACEMAP, fromKwarg="lxmlNode"
                                    ),
                                    # Create combined format from stored metadataPart and normalized part.
                                    (
                                        XmlPrintLxml(
                                            fromKwarg="lxmlNode", toKwarg="data"
                                        ),  # Convert it to plaintext
                                        (
                                            RewritePartname(
                                                NL_DIDL_COMBINED_PREFIX
                                            ),  # Rename combined partName
                                            (
                                                storageComponent,
                                            ),  # Write combined partName to storage
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        (
                            XmlXPath(
                                [
                                    '//document:document/document:part[@name="meta"]/text()'
                                ],
                                fromKwarg="lxmlNode",
                                toKwarg="data",
                                namespaces=NAMESPACEMAP,
                            ),
                            (
                                RewritePartname("meta"),
                                (
                                    storageComponent,
                                ),  # Schrijft harvester 'meta' data naar storage.
                            ),
                        ),
                        (
                            OaiAddRecord(
                                metadataPrefixes=[
                                    (
                                        "metadata",
                                        "http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/did/didmodel.xsd",
                                        "urn:mpeg:mpeg21:2002:02-DIDL-NS",
                                    ),
                                    (
                                        NL_DIDL_NORMALISED_PREFIX,
                                        "",
                                        NAMESPACEMAP.gmhnorm,
                                    ),
                                    (
                                        NL_DIDL_COMBINED_PREFIX,
                                        "",
                                        NAMESPACEMAP.gmhcombined,
                                    ),
                                ]
                            ),  # [(partname, schema, namespace)]
                            # (LogComponent("OaiAddRecord:"),),
                            (storageComponent,),
                            (
                                oaiJazz,
                            ),  # Assert partNames header and meta are available from storage!
                        ),
                        (
                            ResurrectTombstone(),
                            (storageComponent,),
                        ),
                    ),
                    # (FilterMessages(allowed=['add']),
                    #     # (LogComponent("UnDelete"),),
                    #     (ResurrectTombstone(),
                    #         (storageComponent,),
                    #     )
                    # )
                ),
            ),
        ),
    )


def main(reactor, port, statePath, gatewayPort, config, quickCommit=False, **ignored):
    apacheLogStream = stdout

    storage = be(
        (
            StorageComponentAdapter(),
            # (LogComponent("STORAGE"),),
            (MultiSequentialStorage(statePath.joinpath("store").as_posix()),),
        )
    )

    server_info = server_information(config)
    additionalGlobals = {
        "markdown2": markdown2,
        "server_info": server_info,
    }

    oaiJazz = OaiJazz(statePath.joinpath("oai").as_posix())
    oaiJazz.updateMetadataFormat(
        "metadata", "http://didl.loc.nl/didl.xsd", NAMESPACEMAP.didl
    )
    oaiJazz.updateMetadataFormat(NL_DIDL_COMBINED_PREFIX, "", NAMESPACEMAP.gmhcombined)
    oaiJazz.updateMetadataFormat(NL_DIDL_NORMALISED_PREFIX, "", NAMESPACEMAP.gmhnorm)

    normLogger = Logger(statePath.joinpath("..", "gateway", "normlogger").as_posix())

    periodicGateWayDownload = PeriodicDownload(
        reactor,
        host="localhost",
        port=gatewayPort,
        schedule=Schedule(
            period=0.1 if quickCommit else 10
        ),  # WST: Interval in seconds before sending a new request to the GATEWAY in case of an error while processing batch records.(default=1). IntegrationTests need <=1 second! Otherwise tests will fail!
        name="api",
        autoStart=True,
    )

    oaiDownload = OaiDownloadProcessor(
        path="/oaix",
        metadataPrefix=NORMALISED_DOC_NAME,
        workingDirectory=statePath.joinpath("harvesterstate", "gateway").as_posix(),
        userAgentAddition="ApiServer",
        xWait=True,
        name="api",
        autoCommit=False,
    )
    deproxy = Deproxy(
        deproxyForIps=config.get("deproxyForIps", ["127.0.0.1"]),
        deproxyForIpRanges=config.get("deproxyForIpRanges", []),
    )
    oaiInfoIpFilter = IpFilter(
        allowedIps=config.get("allowedIps", ["127.0.0.1"]),
        allowedIpRanges=config.get("allowedIpRanges", []),
    )

    return (
        Observable(),
        createDownloadHelix(
            reactor, periodicGateWayDownload, oaiDownload, storage, oaiJazz
        ),
        (
            ObservableHttpServer(reactor, port, compressResponse=True),
            (
                LogCollector(),
                (ApacheLogWriter(apacheLogStream),),
                (
                    deproxy,
                    (
                        HandleRequestLog(),
                        (
                            BasicHttpHandler(),
                            (
                                PathFilter("/oai", excluding=["/oai/info"]),
                                (
                                    OaiPmh(
                                        repositoryName="Gemeenschappelijke Metadata Harvester KB",
                                        adminEmail=server_info.oai_admin_email,
                                        externalUrl=server_info.oai_base_url,
                                        batchSize=200,
                                        supportXWait=False,
                                        # preciseDatestamp=False,
                                        # deleteInSets=False
                                    ),
                                    (oaiJazz,),
                                    (
                                        RetrieveToGetDataAdapter(),
                                        (storage,),
                                    ),
                                    (
                                        OaiBranding(
                                            url="https://www.kb.nl",
                                            link=server_info.harvester_base_url,
                                            title="Gemeenschappelijke Metadata Harvester (GMH) van de KB",
                                        ),
                                    ),
                                    (
                                        OaiProvenance(
                                            nsMap=NAMESPACEMAP,
                                            baseURL=(
                                                "meta",
                                                "//meta:repository/meta:baseurl/text()",
                                            ),
                                            harvestDate=(
                                                "meta",
                                                "//meta:harvestdate/text()",
                                            ),
                                            metadataNamespace=(
                                                "meta",
                                                "//meta:metadataPrefix/text()",
                                            ),  # TODO: Kan hardcoded in harvester mapper gezet eventueel: <metadataNamespace>urn:mpeg:mpeg21:2002:01-DII-NS</metadataNamespace>?? (storage,) #metadataNamespace=('meta', '//meta:record/meta:metadataNamespace/text()'),
                                            identifier=(
                                                "header",
                                                "//oai:identifier/text()",
                                            ),
                                            datestamp=(
                                                "header",
                                                "//oai:datestamp/text()",
                                            ),
                                        ),
                                        (
                                            RetrieveToGetDataAdapter(),
                                            (storage,),
                                        ),
                                    ),
                                ),
                            ),
                            (
                                PathFilter("/oai/info"),
                                (
                                    oaiInfoIpFilter,
                                    (
                                        OaiInfo(reactor=reactor, oaiPath="/oai"),
                                        (oaiJazz,),
                                    ),
                                ),
                            ),
                            (
                                PathFilter("/rss"),
                                (
                                    LoggerRSS(
                                        title="GMH KB Normalisationlog Syndication",
                                        description="Harvester normalisation log for: ",
                                        link=f"{server_info.harvester_base_url}/rss",
                                        maximumRecords=30,
                                    ),
                                    (
                                        normLogger,
                                        (
                                            StorageComponentAdapter(),
                                            (storage,),
                                        ),
                                    ),
                                ),
                            ),
                            (
                                PathFilter("/static/"),
                                (
                                    PathRename(
                                        lambda path: path.replace("/static/", "/", 1)
                                    ),
                                    (FileServer(staticPath.as_posix()),),
                                ),
                            ),
                            (
                                PathFilter("/doc"),
                                (
                                    PathRename(lambda path: path[len("/doc") :] or "/"),
                                    (
                                        DynamicHtml(
                                            [dynamicPath.as_posix()],
                                            reactor=reactor,
                                            indexPage="/doc/index",
                                            additionalGlobals=additionalGlobals,
                                        ),
                                        (DocData([docPath]),),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


def startServer(port, stateDir, gatewayPort, globalConfig, quickCommit=False, **kwargs):
    setSignalHandlers()
    print("Firing up API Server.")
    statePath = pathlib.Path(stateDir).resolve()
    statePath.mkdir(parents=True, exist_ok=True)
    config = json.loads(globalConfig.read_text())

    reactor = Reactor()
    dna = main(
        reactor=reactor,
        port=port,
        statePath=statePath,
        gatewayPort=gatewayPort,
        quickCommit=quickCommit,
        config=config,
        **kwargs,
    )

    server = be(dna)
    consume(server.once.observer_init())

    registerShutdownHandler(
        statePath=statePath, server=server, reactor=reactor, shutdownMustSucceed=False
    )

    print("Ready to rumble at %s" % port)
    print("Global Config:")
    print(json.dumps(config, indent=2))
    sys.stdout.flush()
    reactor.loop()
