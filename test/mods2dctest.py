# -*- coding: utf-8 -*-
from cq2utils import CQ2TestCase
from meresco.components.xml_generic import schemasPath
from meresco.components import Crosswalk
from lxml.etree import tostring, XMLParser, XMLSchema, parse as lxmlParse
from StringIO import StringIO
from os.path import join
from narcis.mods2dc import Mods2Dc
from difflib import unified_diff

oaiDcSchema = XMLSchema(lxmlParse(open(join(schemasPath, 'oai_dc.xsd'))))

def prettyPrint(node):
    return tostring(node, pretty_print = True, encoding='utf-8').replace('><','>\n<')
    #TJ: added the replace hack because lxml doesn't do the job.'

class Mods2DcTest(CQ2TestCase):
    def testFindAndBind(self):
        x = lxmlParse(StringIO("""<tag><sub>&amp;Eacute;</sub></tag>"""))
        result = Mods2Dc()._findAndBind(x, '<newtag>%s</newtag>', '/tag/sub/text()')
        self.assertEquals('<newtag>&amp;Eacute;</newtag>', result)

    def testElsevierFiles(self):
        # http://loc.gov/standards/mods/mods-dcsimple.html
        self.assertMods2DC("somerecord")

    def assertMods2DC(self, id):
        crosswalk = Mods2Dc()
        inputRecord = lxmlParse(open("data/%s.mods.xml" % id))
        expectedResult = open("data/%s.dc.xml" % id).read()
        result = crosswalk.convert(inputRecord)

        oaiDcSchema.validate(lxmlParse(StringIO(prettyPrint(result))))

        if oaiDcSchema.error_log.last_error:
            for nr, line in enumerate(prettyPrint(result).split('\n')):
                print nr+1, line
            self.fail(oaiDcSchema.error_log.last_error)

        self.assertEqualsWithDiff(expectedResult, prettyPrint(result))

    def assertEqualsWithDiff(self, expected, result):
        diffs = list(unified_diff(
            [x.strip() for x in result.split('\n') if x.strip()],
            [x.strip() for x in expected.split('\n') if x.strip()],
            fromfile='result', tofile='expected', lineterm=''))
        self.assertFalse(diffs, '\n' + '\n'.join(diffs))
