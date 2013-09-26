#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
# encoding: utf-8
## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
import os, sys
os.system('find .. -name "*.pyc" | xargs rm -f')

from glob import glob
for path in glob('../deps.d/*'):
    sys.path.insert(0, path)

sys.path.insert(0, "..")

from os import system
from sys import exit, exc_info

from os.path import isdir, isfile, join

from unittest import main
from random import randint
from time import time
from glob import glob

from amara.binderytools import bind_file, bind_string

from weightless import Reactor
from cq2utils import CQ2TestCase, getRequest, postRequest, wheelOfTime

from meresco.framework import be

from narcis.nodserver import dna, config

integrationTempdir = '/tmp/meresco-integration-test-steiny_nod'
reactor = Reactor()

class IntegrationTest(CQ2TestCase):

    def testExplain(self):
        header, body = getRequest(reactor, port, '/sru', {})
        explainResponse = body.explainResponse
        #print 'ExplainResponseBody:\n\n', body.xml()
        self.assertEquals(config['host'], str(explainResponse.record.recordData.explain.serverInfo.host))
        portNumber = int(explainResponse.record.recordData.explain.serverInfo.port)
        self.assertTrue(50000 < portNumber < 60000, portNumber)

    def testIndex(self):
        self.assertSruQuery(5, 'dc=http')
	#self.assertSruQuery(1, 'mods=koekiemonster')
        #self.assertSruQuery(1, 'dc.publisher = foris')
        #self.assertSruQuery(1, 'dc.title = dialectsyntaxis')
        #self.assertSruQuery(1, 'dc.identifier="http://depot.knaw.nl/3758/"')
	#self.assertSruQuery(0, 'dc.creator= haegeman')


    def testOaiIdentify(self):
        header, body = getRequest(reactor, port, '/oai', {'verb': 'Identify'})
        self.assertEquals('HTTP/1.0 200 Ok\r\nContent-Type: text/xml; charset=utf-8', header)
        self.assertEquals('NARCIS Repository', body.OAI_PMH.Identify.repositoryName)
        self.assertEquals('narcis@bureau.knaw.nl', body.OAI_PMH.Identify.adminEmail)

    def testOaiListRecords(self):
        header, body = getRequest(reactor, port, '/oai', {'verb': 'ListRecords', 'metadataPrefix': 'nod_prs'})
	#print body.xml()
        self.assertEquals('HTTP/1.0 200 Ok\r\nContent-Type: text/xml; charset=utf-8', header)
        self.assertEquals(5, len(body.OAI_PMH.ListRecords.record))

    def testOaiListRecordsSteiny(self):
        header, body = getRequest(reactor, port, '/oai', {'verb': 'ListRecords', 'metadataPrefix': 'nod_prs'})
	#print body.xml()
        self.assertEquals('HTTP/1.0 200 Ok\r\nContent-Type: text/xml; charset=utf-8', header)
        #self.assertEquals(4, len(body.OAI_PMH.ListRecords.record))

    #def testDeleteRecord(self):
        #self.assertSruQuery(0, 'dc.identifier="test1:oai:depot.knaw.nl:675"')
        #header, body = getRequest(reactor, port, '/oai', {'verb': 'ListRecords', 'metadataPrefix': 'oai_dc'})
        ##print 'ListRecords: ' , body.xml()
        #self.assertEquals('deleted', body.OAI_PMH.ListRecords.record[2].header.status)
        

    #def doDrilldown(self, query, drilldownField):
        #message = self._doQuery({'query':query, 'x-term-drilldown': drilldownField})
        #result = message.searchRetrieveResponse
        #return result


    def assertSruQuery(self, numberOfRecords, query):
        message = self._doQuery({'query':query})
        print '\n\nsru_response:\n', message.xml(), '\n'
        result = message.searchRetrieveResponse
        self.assertEquals(numberOfRecords, int(str(result.numberOfRecords)))
        return result

    #Default wordt 'oai_dc' als recordSchema gebruikt bij het zoeken.
    #Als een record niet het gevraagde recordSchema heeft, dan kan het wel gevonden worden, maar krijgen we een "srw/diagnostics" om onze oren:
    #<uri>info://srw/diagnostics/1/1</uri>
    #<details>General System Error</details>
    #<message>Name '(u'knaw_mir:oai:depot.knaw.nl:759', 'oai_dc')' does not exist.</message>
    def _doQuery(self, arguments, path="/sru"):
        queryArguments = {'version': '1.1', 'operation': 'searchRetrieve', 'maximumRecords': '20', 'recordSchema': 'nod_prs' , 'x-recordSchema': 'meta, header'}
	#, 'recordSchema': 'oai_dc', 'x-recordSchema': 'knaw_oi_short','sortKeys': 'generic4,,1,0,highValue'}
        queryArguments.update(arguments)
        header, body = getRequest(reactor, port, path, queryArguments)
        return body

def createDatabase(port):
    recordPacking = 'xml'
    start = time()
    print "Creating database in", integrationTempdir
    sourceFiles = glob('harvester_test_nod_records/*.updateRequest')
    for updateRequestFile in sorted(sourceFiles):
        print 'Sending:', updateRequestFile  
#        print 'File: ', open(updateRequestFile).read()
        
        header, body = postRequest(reactor, port, '/update', open(updateRequestFile).read())
        
        if '200 Ok' not in header:
            print 'No 200 Ok response, but:'
            print header
            exit(123)
        if "srw:diagnostics" in body.xml():
            print body.xml()
            exit(1234)
    print "Finished creating database in %s seconds" % (time() - start)
    print "Giving the server index some time for a auto refresh"
    wheelOfTime(reactor, 2)

    print "Finished creating database"

if __name__ == '__main__':
    from sys import argv
    if not '--fast' in argv:
        system('rm -rf ' + integrationTempdir)
        system('mkdir --parents '+ integrationTempdir)

    port = randint(50000,60000)
    server = be(dna(reactor, config['host'], portNumber=port, databasePath=integrationTempdir))
    server.once.observer_init()

    if '--fast' in argv and isdir(integrationTempdir):
        argv.remove('--fast')
        print "Reusing database in", integrationTempdir
    else:
        createDatabase(port)
    main()
