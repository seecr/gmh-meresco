# -*- coding: utf-8 -*-
# encoding: utf-8
## begin license ##
#
#    Meresco Examples is a project demonstrating some of the features of
#    various Meresco components.
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2009 Delft University of Technology http://www.tudelft.nl
#    Copyright (C) 2009 Tilburg University http://www.uvt.nl
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#
#    This file is part of Meresco Examples.
#
#    Meresco Examples is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Examples is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Examples; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from os import getuid
#WST
import sys
#
assert getuid() != 0, "Do not run tests as 'root'"
#WST:
sys.path.insert(0, "..")

import pdb
#
from os import system
from sys import exit, exc_info

from os.path import isdir, isfile

from unittest import main
from random import randint
from time import time
from glob import glob

from amara.binderytools import bind_file, bind_string

from weightless.io import Reactor
from weightless.core import compose
from cq2utils import CQ2TestCase, getRequest, postRequest, wheelOfTime

from meresco.core import be

from narcis.server import dna, config

#integrationTempdir = '/home/meresco/wilkos/meresco-integration-test'
integrationTempdir = '/data/meresco'

class IntegrationTest(CQ2TestCase):

    def _path(self, subdir):
        return join(self.tempdir, subdir)

    def testExplain(self):
        
        header, body = getRequest(reactor, port, '/sru', {})
        explainResponse = body.explainResponse
        self.assertEquals(config['host'], str(explainResponse.record.recordData.explain.serverInfo.host))
        portNumber = int(explainResponse.record.recordData.explain.serverInfo.port)
        self.assertTrue(50000 <= portNumber <= 60000, portNumber)
        
#     def testIndex(self):
#         self.assertSruQuery(2, 'unqualifiedterms="Seek You Too"')
#         self.assertSruQuery(2, 'title = program')
#         self.assertSruQuery(1, 'untokenized.oai_identifier exact "record:1"')
#         self.assertSruQuery(2, 'untokenized.dd_year exact "2008"')
#         self.assertSruQuery(1, 'untokenized.dais exact "info:eu-repo/dai/nl/29806278"')
        
#     def testDrilldown(self):
#         result = self.doDrilldown('collection exact "publication" OR collection exact "vpub"', 'dd_year')
#         navigator = result.extraResponseData.drilldown.term_drilldown.navigator
#         #print result.xml()
#         #print navigator.xml()
#         self.assertEquals(1, len(navigator), result.xml())
#         self.assertEquals('dd_year', str(navigator.name))
#         self.assertEquals(3, len(navigator.item))
#         #sorted by dd_numbers, not sorted by year...
# #         itemValues = [(item.count, str(item)) for item in navigator.item]
# #         self.assertEquals([(2, '2008'), (2, '1993'), (1, '2004')], itemValues)
#         itemValues = [(item.count) for item in navigator.item]
#         self.assertEquals([(2), (2), (1)], itemValues)
      
    def testRSS(self):
#         #, 'maximumRecords':'2'
        body = self._doQuery({'query':'luchtscheiding', 'querylabel':'MyLabel', 'preflang': 'en', 'sortKeys': 'untokenized.oai_identifier,,0'}, path="/rss")
        print '\nBODY:', body.xml()
        items = [(str(item.title), str(item.description), str(item.link)) for item in body.rss.channel.item]
        
        #print '\nBODY:', body.xml(),
        # for item in items:
#             print '\nITEM:', item
            
        self.assertEquals(2, len(items))
        #self.assertSruQuery(2, 'luchtscheiding')
        #print str(items)
        # self.assertEquals([('Condition assessment PVC', 'Projectomschrijving<br>Ontwikkeling van betrouwbare\n                        methoden, procedures en extrapolatiemodellen om de conditie en\n                        restlevensduur van in gebruik zijnde PVC-leidingen te\n                        bepalen.<br>Beoogde projectopbrengsten<br>-\n               ', 'http://www.narcis.nl/research/RecordID/OND1272024/Language/en'), ('Example Publication', 'This is an example RDF entity to illustrate the structure of an Enhanced Publication.', 'http://www.narcis.nl/vpub/RecordID/vpub%3Aurn%3Anbn%3Anl%3Aui%3A10-1234/xyz/Language/en'), ('Example Program 1', 'This is an example program about Search with Meresco', 'http://www.narcis.nl/publication/RecordID/record%3A1/Language/en'), ('Example Program 2', 'This is an example program about Programming with Meresco', 'http://www.narcis.nl/publication/RecordID/record%3A2/Language/en')], items)
         
      #Should be tested by reindex-client in tools dir??  
#     def testReindexAll(self):
#         print '\nStarting reindex'
#         #First call: creates batchfiles and processes them all...
#         header, body = getRequest(reactor, port, '/reindex', {'session':['narcisindex'], 'batchsize': ['2'], 'processbatch' : ['all']}, parse=False) #parse=False: returns string
#         self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: plain/text', header)        
#         print body
#         batches_created =  int(body.count('#'))
#         self.assertEquals(6, batches_created)
#     
#         remaining_batches =  int(body[len(body)-1])
#         print 'Remainder:', remaining_batches
#         ##Process all batches one by one:
#         while remaining_batches > 0:
#             header, body = getRequest(reactor, port, '/reindex', {'session':['narcisindex'], 'processbatch' : ['single']}, parse=False)            
#             remaining_batches =  int(body[len(body)-1])
#             self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: plain/text', header)
#             print "remaining_batches:", remaining_batches
#         self.assertEquals(0, remaining_batches)
        
#     def testOaiListMetadataFormats(self):
#         header, body = getRequest(reactor, port, '/oai', {'verb': 'ListMetadataFormats'})
#         #print 'ListMetadataFormats:', body.xml()
#         self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
#         self.assertEquals(1, len(body.OAI_PMH.ListMetadataFormats.metadataFormat[0].metadataPrefix))
#         self.assertEquals('oai_dc', body.OAI_PMH.ListMetadataFormats.metadataFormat[0].metadataPrefix) 
#         
#     def testOaiIdentify(self):
#         header, body = getRequest(reactor, port, '/oai', {'verb': 'Identify'})
#         #print body.xml()
#         self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
#         self.assertEquals('NARCIS Repository', body.OAI_PMH.Identify.repositoryName)
#         self.assertEquals('narcis@dans.knaw.nl', body.OAI_PMH.Identify.adminEmail)

#     def testOaiSetListRecords(self):
#         header, body = getRequest(reactor, port, '/oai', {'verb': 'ListRecords', 'metadataPrefix': 'oai_dc', 'set': 'dataset'})
#         #print body.xml()
#         self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
#         self.assertEquals(1, len(body.OAI_PMH.ListRecords.record))
#         
#         header, body = getRequest(reactor, port, '/oai', {'verb': 'ListRecords', 'metadataPrefix': 'oai_dc', 'set': 'publication'})
#         #print body.xml()
#         self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
#         self.assertEquals(7, len(body.OAI_PMH.ListRecords.record))
# 
#         header, body = getRequest(reactor, port, '/oai', {'verb': 'ListRecords', 'metadataPrefix': 'oai_dc', 'set': 'oa_publication'})
#         #print body.xml()
#         self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
#         self.assertEquals(5, len(body.OAI_PMH.ListRecords.record))
# 
# 
#     def testOaiGetRecord(self):
#         #header, body = getRequest(reactor, port, '/oai', {'verb': 'GetRecord', 'metadataPrefix': 'knaw_long', 'identifier': 'knaw_mir:oai:depot.knaw.nl:557'}) 
#         header, body = getRequest(reactor, port, '/oai', {'verb': 'GetRecord', 'metadataPrefix': 'oai_dc', 'identifier': 'dans:oai:easy.dans.knaw.nl:twips.dans.knaw.nl-833486382286886219-1174311206456'})
#         #print body.xml()
#         self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
#         self.assertEquals(1, len(body.OAI_PMH.GetRecord.record))
# 
#     def testDeleteRecord(self):
#         # Record #3 should not exist...
#         self.assertSruQuery(0, 'untokenized.oai_identifier exact "record:3"')
#         # #2 should...
#         self.assertSruQuery(1, 'untokenized.oai_identifier exact "record:2"')
#         
#         header, body = getRequest(reactor, port, '/oai', {'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc'})
#         #print body.xml()
#         self.assertEquals(8, len(body.OAI_PMH.ListIdentifiers.header))
# 
#         header, body = getRequest(reactor, port, '/oai', {'verb': 'GetRecord', 'identifier': 'meresco:record:3', 'metadataPrefix': 'oai_dc'})
#         #print body.xml()        
#         self.assertEquals('deleted', body.OAI_PMH.GetRecord.record[0].header.status)
    
#     def testJson(self):
#         sru = self._doQuery({'recordSchema': 'ore_json', 'maximumRecords': '10', 'recordPacking': 'string', 'query':'untokenized.collection exact "vpub"'})         
#         self.assertEquals('{"http://myrepository.org/resource/metadatarecord":{"http://purl.org/dc/elements/1.1/publisher":[{"type":"literal","value":""}],"http://purl.org/dc/terms/modified":[{"type":"literal","value":""}],"http://www.w3.org/1999/02/22-rdf-syntax-ns#type":[{"type":"uri","value":"http://purl.org/info:eu-repo/semantics/DescriptiveMetadata"}],"http://purl.org/dc/elements/1.1/creator":[{"type":"literal","value":""}],"http://purl.org/dc/elements/1.1/description":[{"type":"literal","value":""}],"http://purl.org/dc/elements/1.1/title":[{"type":"literal","value":""}],"http://purl.org/dc/elements/1.1/format":[{"type":"literal","value":"application/xml"}]},"_:id0":{"http://www.w3.org/1999/02/22-rdf-syntax-ns#type":[{"type":"uri","value":"http://purl.org/info:eu-repo/dai"},{"type":"uri","value":"http://xmlns.com/foaf/0.1/OnlineAccount"}],"http://xmlns.com/foaf/0.1/accountName":[{"type":"literal","value":"info:eu-repo/dai/nl/123456789-D"}]},"http://myrepository.org/resource/dataobject":{"http://purl.org/dc/elements/1.1/publisher":[{"type":"literal","value":""}],"http://purl.org/dc/terms/modified":[{"type":"literal","value":"2011-01-01"}],"http://www.w3.org/1999/02/22-rdf-syntax-ns#type":[{"type":"uri","value":"http://purl.org/info:eu-repo/semantics/Datafile"}],"http://purl.org/dc/elements/1.1/creator":[{"type":"literal","value":""}],"http://purl.org/dc/elements/1.1/description":[{"type":"literal","value":"A fictitious dataset in a CSV format."}],"http://purl.org/dc/elements/1.1/title":[{"type":"literal","value":"Dataset XYZ"}],"http://purl.org/dc/elements/1.1/format":[{"type":"literal","value":"text/csv"}],"http://www.openarchives.org/ore/terms/similarTo":[{"type":"uri","value":"http://hdl.handle.net/123456789/1234"}]},"http://myrepository.org/resource/enhancedpublication":{"http://purl.org/dc/elements/1.1/publisher":[{"type":"literal","value":"A simple research institute"}],"http://purl.org/dc/terms/modified":[{"type":"literal","value":"2011-01-11"}],"http://www.w3.org/1999/02/22-rdf-syntax-ns#type":[{"type":"uri","value":"http://purl.org/info:eu-repo/semantics/EnhancedPublication"},{"type":"uri","value":"http://www.openarchives.org/ore/terms/Aggregation"}],"http://purl.org/dc/terms/issued":[{"type":"literal","value":"1993-08-15"}],"http://purl.org/dc/elements/1.1/title":[{"type":"literal","value":"Example Publication"}],"http://purl.org/dc/elements/1.1/description":[{"type":"literal","value":"This is an example RDF entity to illustrate the structure of an Enhanced Publication."}],"http://www.openarchives.org/ore/terms/similarTo":[{"type":"uri","value":"urn:nbn:nl:ui:99-123456789"}],"http://www.openarchives.org/ore/terms/aggregates":[{"type":"uri","value":"http://myrepository.org/resource/dataobject"},{"type":"uri","value":"http://myrepository.org/resource/eprint"},{"type":"uri","value":"http://myrepository.org/resource/metadatarecord"}],"http://www.openarchives.org/ore/terms/isDescribedBy":[{"type":"uri","value":"http://myrepository.org/resource/resourcemap"}],"http://purl.org/dc/terms/creator":[{"type":"literal","value":"SURFfoundation"}]},"http://myrepository.org/resource/person":{"http://xmlns.com/foaf/0.1/givenName":[{"type":"literal","value":"Klaas"}],"http://xmlns.com/foaf/0.1/account":[{"type":"bnode","value":"_:id0"}],"http://www.w3.org/1999/02/22-rdf-syntax-ns#type":[{"type":"uri","value":"http://xmlns.com/foaf/0.1/Person"}],"http://xmlns.com/foaf/0.1/familyName":[{"type":"literal","value":"de Vries"}]},"http://myrepository.org/resource/resourcemap":{"http://www.openarchives.org/ore/terms/describes":[{"type":"uri","value":"http://myrepository.org/resource/enhancedpublication"}],"http://purl.org/dc/terms/creator":[{"type":"literal","value":"SURFfoundation"}]},"http://myrepository.org/resource/eprint":{"http://purl.org/dc/elements/1.1/publisher":[{"type":"literal","value":""}],"http://purl.org/dc/terms/modified":[{"type":"literal","value":"2011-01-02"}],"http://www.w3.org/1999/02/22-rdf-syntax-ns#type":[{"type":"uri","value":"http://purl.org/info:eu-repo/semantics/Article"}],"http://purl.org/dc/elements/1.1/creator":[{"type":"literal","value":""}],"http://purl.org/dc/elements/1.1/description":[{"type":"literal","value":"Some example text that describes the resource."}],"http://purl.org/dc/elements/1.1/title":[{"type":"literal","value":"A digital textual publication"}],"http://purl.org/dc/elements/1.1/format":[{"type":"literal","value":"application/pdf"}],"http://www.openarchives.org/ore/terms/similarTo":[{"type":"uri","value":"doi:11.1213/DUMMY.2011.123456789"}]}}', str(sru.searchRetrieveResponse.records.record[0].recordData))
#         self.assertEquals(1, int(sru.searchRetrieveResponse.numberOfRecords))
#         self.assertEquals(1, len(sru.searchRetrieveResponse.records.record))

#     def testSparql(self):
#      #sparql = """PREFIX dcterms: <http://purl.org/dc/terms/>
#         sparql = """PREFIX dcterms: <http://purl.org/dc/elements/1.1/> 
# SELECT ?name ?ore
# WHERE {
# ?ore dcterms:title ?name ;
#     a <http://www.openarchives.org/ore/terms/Aggregation>
# }"""
#         header, body = getRequest(reactor, port, '/sparql', {'query': sparql}, parse=False)
#         print 'sparql query:', body

#     def testSparql2(self):
#         sparql = """PREFIX dcterms: <http://purl.org/dc/terms/>
# SELECT  ?y
# WHERE {
# 
# ?y a <http://www.openarchives.org/ore/terms/Aggregation>
# }"""
#         header, body = getRequest(reactor, port, '/sparql', {'query': sparql}, parse=False)
#         print 'alles:',body
        
    def doDrilldown(self, query, drilldownField):
        message = self._doQuery({'query':query, 'x-term-drilldown': drilldownField, 'maximumRecords': '0'})
        result = message.searchRetrieveResponse
        return result

    def assertSruQuery(self, numberOfRecords, query):
        message = self._doQuery({'query':query})
        result = message.searchRetrieveResponse
        self.assertEquals(numberOfRecords, int(str(result.numberOfRecords)))
        return result

    def _doQuery(self, arguments, path="/sru"):
        queryArguments = {'version': '1.1', 'operation': 'searchRetrieve'}
        queryArguments.update(arguments)
        header, body = getRequest(reactor, port, path, queryArguments)
        print 'header, body: ', header, body
        return body


if __name__ == '__main__':
    from sys import argv
    # if not '--fast' in argv:
#         system('rm -rf ' + integrationTempdir)
#         system('mkdir --parents '+ integrationTempdir)

    port = randint(50000, 60000)
    reactor = Reactor()
    server = be(dna(reactor, config['host'], portNumber=port, databasePath=integrationTempdir, batchedSize=1))
    server.once.observer_init()
    
    if isdir(integrationTempdir):
        #argv.remove('--fast')
        print "Using database in", integrationTempdir
    else:
        print 'No database found, exitting...'
        exit(123)
    #wheelOfTime(reactor, 6)
    main()
