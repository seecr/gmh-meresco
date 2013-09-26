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

sys.path.insert(0, '..')

import unittest

from StringIO import StringIO

from cq2utils import CQ2TestCase, CallTrace
from meresco.framework import be
from narcis.drilldown.srudrilldownadapter import SRUDrilldownAdapter, SRUTermDrilldown, SRUFieldDrilldown, DRILLDOWN_HEADER

from cqlparser.cqlcomposer import compose as cqlCompose

class SRUDrilldownAdapterTest(CQ2TestCase):

    def testOne(self):
        
        class MockedImpl:
            def extraResponseData(sself, webRequest, hits):
                yield "<tag>"
                yield "something</tag>"

        adapter = be(
            (SRUDrilldownAdapter(),
                (MockedImpl(), ),
                (MockedImpl(), )
            )
        )

        result = list(adapter.extraResponseData("ignored_webRequest", "ignored_hits"))
        self.assertEqualsWS([
            DRILLDOWN_HEADER,
            '<tag>', 'something</tag>',
            '<tag>', 'something</tag>',
            '</dd:drilldown>'], result)

class SRUTermDrilldownTest(CQ2TestCase):

    def testSRUTermDrilldown(self):
        arguments = {"x-term-drilldown": ["field0:1,field1:2,field2:3"]}
        
        adapter = SRUTermDrilldown()
        adapter.addObserver(self)
        hits = ['recordId:1', 'recordId:2']
        cqlAbstractSyntaxTree = 'cqlAbstractSyntaxTree'
        
        result = adapter.extraResponseData(arguments, cqlAbstractSyntaxTree)
        self.assertEqualsWS("""<dd:term-drilldown><dd:navigator name="field0">
    <dd:item count="14">value0_0</dd:item>
</dd:navigator>
<dd:navigator name="field1">
    <dd:item count="13">value1_0</dd:item>
    <dd:item count="11">value1_1</dd:item>
</dd:navigator>
<dd:navigator name="field2">
    <dd:item count="3">value2_0</dd:item>
    <dd:item count="2">value2_1</dd:item>
    <dd:item count="1">value2_2</dd:item>
</dd:navigator></dd:term-drilldown>""", "".join(result))
        self.assertEquals([('field0', 1, False), ('field1', 2, False), ('field2', 3, False)], list(self.processed_tuples))
        self.assertEquals('cqlAbstractSyntaxTree', self.processed_ast)

    def testSRUTermDrilldownNoMaximums(self):
        arguments = {"x-term-drilldown": ["field0,field1,field2"]}
        adapter = SRUTermDrilldown()
        adapter.addObserver(self)
        hits = CallTrace("Hits")
        list(adapter.extraResponseData(arguments, []))
        self.assertEquals([('field0', 10, False), ('field1', 10, False), ('field2', 10, False)], list(self.processed_tuples))

    def bitMatrixRow(self, ast):
        self.processed_ast = ast
        return 'row'

    def drilldown(self, row, tuples):
        self.processed_row = row
        self.processed_tuples = tuples
        return [
            ('field0', [('value0_0', 14)]),
            ('field1', [('value1_0', 13), ('value1_1', 11)]),
            ('field2', [('value2_0', 3), ('value2_1', 2), ('value2_2', 1)])]

class SRUFieldDrilldownTest(CQ2TestCase):

    def testSRUParamsAndXMLOutput(self):
        arguments = {"x-field-drilldown": ["term"], 'x-field-drilldown-fields': ['field0,field1'], 'query': ['original']}
        adapter = SRUFieldDrilldown()
        adapter.drilldown = self.drilldown

        self.drilldownCall = None
        result = adapter.extraResponseData(arguments, "ignored_hits")
        #print "".join(result)

        self.assertEqualsWS("""<dd:field-drilldown>
<dd:field name="field0">5</dd:field>
<dd:field name="field1">10</dd:field></dd:field-drilldown>""", "".join(result))

        self.assertEquals(('original', 'term', ['field0', 'field1']), self.drilldownCall)

    def drilldown(self, query, term, fields):
        self.drilldownCall = (query, term, fields)
        return [('field0', 5),('field1', 10)]

    def testDrilldown(self):
        adapter = SRUFieldDrilldown()
        observer = CallTrace("Observer")
        observer.returnValues["executeCQL"] = (16, range(16))
        adapter.addObserver(observer)
        result = list(adapter.drilldown('original', 'term', ['field0', 'field1']))

        self.assertEquals(2, len(observer.calledMethods))
        self.assertEquals("executeCQL(cqlAbstractSyntaxTree=<class CQL_QUERY>)", str(observer.calledMethods[0]))
        self.assertEquals("(original) and field0=term",  cqlCompose(observer.calledMethods[0].kwargs['cqlAbstractSyntaxTree']))
        self.assertEquals([("field0", 16), ("field1", 16)], result)
        
        
if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        os.system('find .. -name "*.pyc" | xargs rm -f')

