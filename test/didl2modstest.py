# -*- coding: utf-8 -*-

from cq2utils import CQ2TestCase, CallTrace

from lxml.etree import parse, tostring, XML, fromstring, dump
from StringIO import StringIO
from narcis.didl2mods import Didl2Mods

KNAWL_NS = "http://www.knaw.nl/narcis/1.0/long/"
KNAWL = "{%s}" % KNAWL_NS
knawNamespaceMap = {None : KNAWL_NS} # the default namespace (no prefix)

class Didl2ModsTest(CQ2TestCase):
    def testDidlWithFullMods(self):
	component = Didl2Mods()
	observer = CallTrace('observer')
	component.addObserver(observer)
	
	didl_full = parse(StringIO(DIDL_FULL))
	component.add('identifier', 'partname', didl_full)

	self.assertEquals(1, len(observer.calledMethods))
	method0 = observer.calledMethods[0]
	self.assertEquals('add', method0.name)
	self.assertEquals(('identifier', 'partname'), method0.args[:2])
	mods = method0.args[2]
	self.assertEqualsWS(tostring(parse(StringIO(DIDL_FULL_MODS))), tostring(mods))

    def testDidlWithMiniMods(self):
	component = Didl2Mods()
	observer = CallTrace('observer')
	component.addObserver(observer)
	
	didl_mini = parse(StringIO(DIDL_MINI_MODS))
	component.add('identifier', 'partname', didl_mini)

	self.assertEquals(1, len(observer.calledMethods))
	method0 = observer.calledMethods[0]
	self.assertEquals('add', method0.name)
	self.assertEquals(('identifier', 'partname'), method0.args[:2])
	mods = method0.args[2]
	self.assertEqualsWS(tostring(parse(StringIO(MINI_MODS))), tostring(mods))

    def testSpelenMetLxml(self):
	lxmlNode = parse(StringIO('<aap xmlns="aap"><noot>mies</noot></aap>'))
	root = lxmlNode.getroot()
	newElement = root.makeelement('publisher')
	newElement.text = 'iets'
	root.append(newElement)
	
	self.assertEquals('<aap xmlns="aap"><noot>mies</noot><publisher>iets</publisher></aap>', tostring(lxmlNode))

    def testSpelenMetLxml2(self):
	lxmlNode = parse(StringIO('<aap xmlns="aap"><noot>mies</noot></aap>'))
	#knaw_lElement = etree.XML('<knaw_long xmlns="'+KNAWL_NS+'"></knaw_long>')
	#lxmlNode = XML('<aap xmlns="aap"><noot>mies</noot></aap>')
	#lxmlNode = fromstring('<aap xmlns="aap"><noot>mies</noot></aap>')
	root = lxmlNode.getroot()
	newElement = root.makeelement('publisher')
	newElement.text = 'iets'
	root.append(newElement)
	dump(newElement)
	self.assertEquals('<aap xmlns="aap"><noot>mies</noot><publisher>iets</publisher></aap>', tostring(lxmlNode))


DIDL_FULL_MODS = """<mods:mods xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:mods="http://www.loc.gov/mods/v3" version="3.0" xsi:schemaLocation="http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-0.xsd"><mods:originInfo><mods:dateIssued encoding="iso8601">1983</mods:dateIssued><mods:publisher>Foris Publications</mods:publisher><mods:place><mods:placeTerm type="text">Dordrecht</mods:placeTerm></mods:place></mods:originInfo><mods:titleInfo><mods:title>De syntaxis van het Nederlands</mods:title></mods:titleInfo><mods:name ID="n548-aut0" type="personal"><mods:namePart type="given">prof.dr. H.J.</mods:namePart><mods:namePart type="family">Bennis</mods:namePart><mods:namePart type="termsOfAddress">prof</mods:namePart><mods:role><mods:roleTerm type="code" authority="marcrelator">aut</mods:roleTerm></mods:role></mods:name><mods:name ID="n548-aut1" type="personal"><mods:namePart type="given">T.</mods:namePart><mods:namePart type="family">Hoekstra</mods:namePart><mods:namePart type="termsOfAddress"></mods:namePart><mods:role><mods:roleTerm type="code" authority="marcrelator">aut</mods:roleTerm></mods:role></mods:name><mods:extension><dai:daiList xmlns:dai="info:eu-repo/dai" xsi:schemaLocation="info:eu-repo/dai https://www.surfgroepen.nl/sites/oai/metadata/Shared%20Documents/dai-extension.xsd"><dai:identifier IDref="n548-aut0" authority="info:eu-repo/dai/nl">071792279</dai:identifier></dai:daiList></mods:extension><mods:typeOfResource>text</mods:typeOfResource><mods:genre>info:eu-repo/semantics/book</mods:genre></mods:mods>"""

DIDL_FULL = """<didl:DIDL xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dip="urn:mpeg:mpeg21:2005:01-DIP-NS" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:didl="urn:mpeg:mpeg21:2002:02-DIDL-NS" xsi:schemaLocation="
		urn:mpeg:mpeg21:2002:02-DIDL-NS http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/did/didl.xsd 
		urn:mpeg:mpeg21:2002:01-DII-NS http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/dii/dii.xsd
		urn:mpeg:mpeg21:2005:01-DIP-NS http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/dip/dip.xsd
	" xmlns:dii="urn:mpeg:mpeg21:2002:01-DII-NS"><didl:Item><didl:Descriptor><didl:Statement mimeType="application/xml"><dii:Identifier>URN:NBN:NL:UI:17-548</dii:Identifier></didl:Statement></didl:Descriptor><didl:Descriptor><didl:Statement mimeType="text/xml"><dcterms:modified>2009-02-13T16:15:43Z</dcterms:modified></didl:Statement></didl:Descriptor><didl:Component><didl:Resource ref="http://depot.knaw.nl/548/" mimeType="text/html"></didl:Resource></didl:Component><didl:Item><didl:Descriptor><didl:Statement mimeType="application/xml"><dip:ObjectType>info:eu-repo/semantics/humanStartPage</dip:ObjectType></didl:Statement></didl:Descriptor><didl:Component><didl:Resource ref="http://depot.knaw.nl/548/" mimeType="text/html"></didl:Resource></didl:Component></didl:Item><didl:Item><didl:Descriptor><didl:Statement mimeType="application/xml"><dip:ObjectType>info:eu-repo/semantics/descriptiveMetadata</dip:ObjectType></didl:Statement></didl:Descriptor><didl:Component><didl:Resource mimeType="application/xml">%s</didl:Resource></didl:Component></didl:Item><didl:Item><didl:Descriptor><didl:Statement mimeType="application/xml"><dip:ObjectType>info:eu-repo/semantics/objectFile</dip:ObjectType></didl:Statement></didl:Descriptor><didl:Descriptor><didl:Statement mimeType="text/xml"><dcterms:modified>2009-02-13T15:52:02Z</dcterms:modified></didl:Statement></didl:Descriptor><didl:Component><didl:Resource ref="http://depot.knaw.nl/548/1/14788_292_bennis.pdf" mimeType="application/pdf"></didl:Resource></didl:Component></didl:Item></didl:Item></didl:DIDL>""" % DIDL_FULL_MODS

DIDL_MINI_MODS = """<didl:DIDL DIDLDocumentId="oai:openaccess.leidenuniv.nl1887/512" xmlns:didl="urn:mpeg:mpeg21:2002:02-DIDL-NS" xmlns:dii="urn:mpeg:mpeg21:2002:01-DII-NS" xmlns:dip="urn:mpeg:mpeg21:2005:01-DIP-NS" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:mpeg:mpeg21:2002:02-DIDL-NS http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/did/didl.xsd urn:mpeg:mpeg21:2002:01-DII-NS http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/dii/dii.xsd urn:mpeg:mpeg21:2002:01-DIP-NS http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/dip/dip.xsd">
  <didl:Item>
    <didl:Descriptor>
      <didl:Statement mimeType="application/xml">

         <dii:Identifier>URN:NBN:NL:UI:26-1887/512</dii:Identifier>
      </didl:Statement>
    </didl:Descriptor>
    <didl:Descriptor>
      <didl:Statement mimeType="application/xml">
        <dcterms:modified>2006-11-07T13:22:26Z</dcterms:modified>
      </didl:Statement>
    </didl:Descriptor>

    <didl:Component>
	<!-- Actual resource of Item: Location of the DIDL document -->
	<didl:Resource mimeType="application/xml" ref="http://hdl.handle.net/1887/512"/>
    </didl:Component>
    <didl:Item>
      <didl:Descriptor>
        <didl:Statement mimeType="application/xml">
          <dip:ObjectType>info:eu-repo/semantics/descriptiveMetadata</dip:ObjectType>

        </didl:Statement>
      </didl:Descriptor>
      <didl:Component>
        <didl:Resource mimeType="application/xml">
          
<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">

  <dc:title>Late-type Giants in the Inner Galaxy</dc:title>
  <dc:creator>Messineo, Maria</dc:creator>

  <dc:publisher>Leiden University, Faculty of Mathematics &amp; Natural Sciences, Observatory</dc:publisher>
  <dc:date>2004-06-30</dc:date>
  <dc:type>Doctoral thesis</dc:type>
  <dc:format>application/pdf</dc:format>
  <dc:format>application/pdf</dc:format>

  <dc:identifier>http://hdl.handle.net/1887/512</dc:identifier>
  <dc:language>en</dc:language>

</oai_dc:dc>
          
        </didl:Resource>
      </didl:Component>
    </didl:Item>
    <!-- Introducing the area for MODS metadata  -->
    <didl:Item>
      <didl:Descriptor>

      <!-- ObjectType of Item -->
        <didl:Statement mimeType="application/xml">
          <dip:ObjectType>info:eu-repo/semantics/descriptiveMetadata</dip:ObjectType>
        </didl:Statement>
      </didl:Descriptor>
      <didl:Component>
        <didl:Resource mimeType="application/xml">
          <mods version="3.2" xmlns="http://www.loc.gov/mods/v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-2.xsd">

            <titleInfo xml:lang="en">
              <title>Late-type Giants in the Inner Galaxy</title> 
            </titleInfo> 
             
            <name type="personal"  ID="ref512MessineoMaria">
              <namePart type="family">Messineo</namePart>
              <namePart type="given">Maria</namePart>
              <role>
                <roleTerm authority="marcrelator" type="code">aut</roleTerm>

              </role>
            </name>
            
            <extension>
              <daiList xmlns:dai="info:eu-repo/dai" xsi:schemaLocation="info:eu-repo/dai http://www.surfgroepen.nl/sites/oai/metadata/Shared%20Documents/dai-extension.xsd">
               
              
                <identifier IDref="ref512MessineoMaria" authority="info:eu-repo/dai/nl">265573947</identifier>
              
              
              </daiList>
            </extension>
          </mods>

        </didl:Resource>
      </didl:Component>
    </didl:Item>
    
    <didl:Item>
      <didl:Descriptor>
        <didl:Statement mimeType="application/xml">
          <dip:ObjectType>info:eu-repo/semantics/objectFile</dip:ObjectType>
        </didl:Statement>

      </didl:Descriptor>
      <didl:Component>
        <didl:Resource ref="https://openaccess.leidenuniv.nl/dspace/bitstream/1887/512/27/cover2.pdf" mimeType="application/pdf"></didl:Resource>
      </didl:Component>
    </didl:Item>
    
    <didl:Item>
      <didl:Descriptor>
        <didl:Statement mimeType="application/xml">

          <dip:ObjectType>info:eu-repo/semantics/objectFile</dip:ObjectType>
        </didl:Statement>
      </didl:Descriptor>
      <didl:Component>
        <didl:Resource ref="https://openaccess.leidenuniv.nl/dspace/bitstream/1887/512/25/01.pdf" mimeType="application/pdf"></didl:Resource>
      </didl:Component>
    </didl:Item>
    
    
    <didl:Item>
      <didl:Descriptor>
        <didl:Statement mimeType="application/xml">
          <dip:ObjectType>info:eu-repo/semantics/humanStartPage</dip:ObjectType>
        </didl:Statement>
      </didl:Descriptor>
      <didl:Component>

        <didl:Resource mimeType="text/html" ref="http://hdl.handle.net/1887/512"></didl:Resource>
      </didl:Component>
    </didl:Item>
  </didl:Item>
</didl:DIDL>"""

MINI_MODS="""<mods version="3.2" xmlns="http://www.loc.gov/mods/v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-2.xsd">

            <titleInfo xml:lang="en">
              <title>Late-type Giants in the Inner Galaxy</title> 
            </titleInfo> 
             
            <name type="personal"  ID="ref512MessineoMaria">
              <namePart type="family">Messineo</namePart>
              <namePart type="given">Maria</namePart>
              <role>
                <roleTerm authority="marcrelator" type="code">aut</roleTerm>

              </role>
            </name>
            
            <extension>
              <daiList xmlns:dai="info:eu-repo/dai" xsi:schemaLocation="info:eu-repo/dai http://www.surfgroepen.nl/sites/oai/metadata/Shared%20Documents/dai-extension.xsd">
               
              
                <identifier IDref="ref512MessineoMaria" authority="info:eu-repo/dai/nl">265573947</identifier>
              
              
              </daiList>
            </extension>
            <originInfo>
		<publisher>Leiden University, Faculty of Mathematics &amp; Natural Sciences, Observatory</publisher>
	    </originInfo>
          </mods>"""