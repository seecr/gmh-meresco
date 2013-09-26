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

from narcis.knawlongserver import dna, config
import urllib


integrationTempdir = '/home/meresco/wilkos/meresco-wst-test'
reactor = Reactor()

class IntegrationTest(CQ2TestCase):

    def testIndex(self):
        self.assertSruQuery(1, 'untokenized.dais exact "info:eu-repo/dai/nl/327773901"')
        #self.assertSruQuery(3, 'unqualifiedterms="nod"')
        #self.assertSruQuery(4, 'unqualifiedterms="knaw_mir"')
        #self.assertSruQuery(1, 'sort.persistentidentifier exact "URN:NBN:NL:UI:17-565"')
        #self.assertSruQuery(1, 'dais="info:eu-repo/dai/nl/666"')
        #self.assertSruQuery(1, 'dais="info:eu-repo/dai/be/15081968"')
        #self.assertSruQuery(1, 'unqualifiedterms=info:eu-repo/dai/be/15081968')
        #self.assertSruQuery(1, 'untokenized.dais exact "info:eu-repo/dai/be/15081968"')
        #self.assertSruQuery(1, 'dare-identifier exact oaidepotknawnl564')
        #self.assertSruQuery(1, 'dare-identifier="oaidepotknawnl564"')

    def testDrilldown(self):
        #result = self.doDrilldown('title="Galaxy"', 'dd_year')
        result = self.doDrilldown('collection="nodorganisaties"', 'dd_institute')
        #result = self.doDrilldown('unqualifiedterms="boellaard"', 'dd_cat')
        #result = self.doDrilldown('unqualifiedterms="warmtewisselaars"', 'dd_cat')
        navigator = result.extraResponseData.drilldown.term_drilldown.navigator
        print '\n\nsru_response:\n', result.xml(), '\n'
        #self.assertEquals(1, len(navigator), result.xml())
        self.assertEquals('dd_institute', str(navigator.name))
        #self.assertEquals(2, len(navigator.item)) # select distinct drillD. fieldname
        #itemValues = [(item.count, str(item)) for item in navigator.item]
        ##self.assertEquals([(4, '2004'), (4, '2005'), (2, 'doctoralthesis')], itemValues)
        #self.assertEquals([(4, '2004'), (4, '2005')], itemValues)

    def testRSS(self):
        body = self._doQuery({'query':'Appositie', 'x-rss-profile':'narcis', 'querylabel':'MyLabel' , 'preflang': 'en'}, path="/rss") 
        items = [(str(item.title), str(item.description), str(item.link)) for item in body.rss.channel.item]
        #print 'BODY:', body.xml()
        #for item in items:
        #    print 'ITEM:', item
        #self.assertEquals(4, len(body.rss.channel.item))
        ##self.assertEquals([('Example Program 1', 'This is an example program about Search with Meresco', 'operation=searchRetrieve&version=1.1&query=dc.identifier%3Dhttp%3A//meresco.com%3Frecord%3D1'), ('Example Program 2', 'This is an example program about Programming with Meresco', 'operation=searchRetrieve&version=1.1&query=dc.identifier%3Dhttp%3A//meresco.com%3Frecord%3D2')], items)

    #def testOaiIdentify(self):
        #header, body = getRequest(reactor, port, '/oai', {'verb': 'Identify'})
        #self.assertEquals('HTTP/1.0 200 Ok\r\nContent-Type: text/xml; charset=utf-8', header)
        #self.assertEquals('NARCIS Repository', body.OAI_PMH.Identify.repositoryName)
        #self.assertEquals('narcis@bureau.knaw.nl', body.OAI_PMH.Identify.adminEmail)

#TODO: OAIJAZZ juist implementeren.
    #def testOaiListRecords(self):
        #header, body = getRequest(reactor, port, '/oai', {'verb': 'ListRecords', 'metadataPrefix': 'dans_pi'})
        #self.assertEquals('HTTP/1.0 200 Ok\r\nContent-Type: text/xml; charset=utf-8', header)
        #self.assertEquals(8, len(body.OAI_PMH.ListRecords.record))

    #def testDeleteRecord(self):
        #self.assertSruQuery(0, 'oaiidentifier="oai:depot.knaw.nl:551"')
        #header, body = getRequest(reactor, port, '/oai', {'verb': 'ListRecords', 'metadataPrefix': '??'})
        #print 'ListRecords: ' , body.xml()
        #self.assertEquals('deleted', body.OAI_PMH.ListRecords.record[2].header.status)
        
    #def testMd5SummedStorage(self):
        #self.assertTrue(isfile(join(integrationTempdir, 'storage', 'PRS', 'b0', '47', 'PRS1242583', 'knaw_short')))


    def doDrilldown(self, query, drilldownField):
        message = self._doQuery({'query':query, 'x-term-drilldown': drilldownField})
        result = message.searchRetrieveResponse
        return result

    def assertSruQuery(self, numberOfRecords, query):
        message = self._doQuery({'query':query})
        #print '\n\nsru_response:\n', message.xml(), '\n'
        result = message.searchRetrieveResponse
        self.assertEquals(numberOfRecords, int(str(result.numberOfRecords)))
        return result

    #Default wordt 'oai_dc' als recordSchema gebruikt bij het zoeken.
    #Als een record niet het gevraagde recordSchema heeft, dan kan het wel gevonden worden, maar krijgen we een "srw/diagnostics" om onze oren:
    #<uri>info://srw/diagnostics/1/1</uri>
    #<details>General System Error</details>
    #<message>Name '(u'knaw_mir:oai:depot.knaw.nl:759', 'oai_dc')' does not exist.</message>
    def _doQuery(self, arguments, path="/sru"):
        queryArguments = {'version': '1.1', 'operation': 'searchRetrieve'} 
	#, 'recordSchema': 'knaw_short', 'x-recordSchema': 'header', 'sortKeys': 'sort.dateissued,,0'}
        queryArguments.update(arguments)
        header, body = getRequest(reactor, port, path, queryArguments)
        return body

def createDatabase(port):
    recordPacking = 'xml'
    start = time()
    print "Creating database in", integrationTempdir
    sourceFiles = glob('harvester_output/*.updateRequest')
    for updateRequestFile in sorted(sourceFiles):
        print 'Sending:', updateRequestFile  
        
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
