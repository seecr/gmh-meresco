# -*- coding: utf-8 -*-
from lxml.etree import parse, _ElementTree, tostring, XMLSchema, parse as lxmlParse
from lxml import etree
from xml.sax.saxutils import escape as escapeXml
from meresco.core import Observable
from copy import deepcopy
from StringIO import StringIO
from meresco.components.xml_generic.validate import ValidateException
from re import compile
from dateutil.parser import parse as parseDate

#Schema validatie:
from os.path import abspath, dirname, join

# This component handles ADD messages only.
# It will try to convert the supplied data (KNAWLong) from the 'metadata' part into KNAWshort. All other parts and data formats are ignored (blocked).
# If it fails in doing so, it will block (NOT pass) the ADD message.
# Returns: xml-string!

## Default xml-encoding:
XML_ENCODING = 'utf-8'

DIDL_XSD = etree.XMLSchema(etree.parse(join((join(dirname(abspath(__file__)), 'xsd')), 'didl.xsd') ))
MODS_XSD = etree.XMLSchema(etree.parse(join((join(dirname(abspath(__file__)), 'xsd')), 'mods.xsd') ))


## Translation maps (key needs to be found somewhere in textvalues to be mapped):
pubVersions = {
    'publishedversion':'info:eu-repo/semantics/publishedVersion',
    'authorversion'  :'info:eu-repo/semantics/authorVersion',
}

accessRights = {
    'openaccess':'http://purl.org/eprint/accessRights/OpenAccess',
    'restrictedaccess'  :'http://purl.org/eprint/accessRights/RestrictedAccess',
    'closedaccess': 'http://purl.org/eprint/accessRights/ClosedAccess',
}

##Default DIDL Descriptor template: 
descr_templ = """<didl:Descriptor>
                    <didl:Statement mimeType="application/xml">
                        %s
                    </didl:Statement>
                </didl:Descriptor>"""  

##MODS root elements allwed by GH normalized:
allowed_mods_rootelem = ["abstract", "classification", "extension", "genre", "identifier", "language", "location", "name", "originInfo", "part", "physicalDescription", "relatedItem", "subject", "titleInfo", "typeOfResource"]


class NL_DIDL_normalized(Observable):

    def __init__(self, nsMap={}):
        Observable.__init__(self)
        self._nsMap=nsMap
        #self._nsOAI = {'dc': nsMap.get('dc'), None : nsMap.get('oai_dc')}
        self._bln_success = False
        
    def _detectAndConvert(self, anObject):
        if type(anObject) == _ElementTree:
            return self.convert(anObject)
        return anObject

    def convert(self, lxmlNode):
        self._bln_success = False
        
        #Throw ValidationException if invald DIDL:
        self._isValidDIDLschema(lxmlNode)
        
        #Throw ValidationException if invald MODS:
        self._isValidMODSschema(lxmlNode)
        
        result_tree = self._normalizeDIDLRecord(lxmlNode)
        if result_tree != None:
            self._bln_success = True
            
        return result_tree

    def all_unknown(self, method, *args, **kwargs):
        self._identifier = kwargs.get('identifier')
        newArgs = [self._detectAndConvert(arg) for arg in args]     
        newKwargs = dict((key, self._detectAndConvert(value)) for key, value in kwargs.items())
        if self._bln_success:
            return self.all.unknown(method, *newArgs, **newKwargs)


    def _isValidDIDLschema(self, lxmlNode):
        didl_xml = lxmlNode.xpath('//didl:DIDL', namespaces=self._nsMap)
        if didl_xml:
            if not DIDL_XSD.validate(didl_xml[0]):
#            if DIDL_XSD.error_log.last_error:
                #print "DIDL NOT VALID:", DIDL_XSD.error_log
                raise ValidateException("DIDL container is not valid: " + str( DIDL_XSD.error_log.last_error))            
            #else:
                #print "VALID DIDL"
        else:        
            raise ValidateException("Mandatory DIDL container not found!")     

    def _isValidMODSschema(self, lxmlNode):
        didl_xml = lxmlNode.xpath('//mods:mods', namespaces=self._nsMap)
        if didl_xml:
            if not MODS_XSD.validate(didl_xml[0]):
#            MODS_XSD.validate(didl_xml[0])
#            if MODS_XSD.error_log.last_error:
                raise ValidateException("MODS metadata is not valid: " + str(MODS_XSD.error_log.last_error))                   
            #else:
                #self.do.logMsg(self._identifier, "Found valid MODS metadata: Ga vooral zo door...")
        else:
            raise ValidateException("Mandatory MODS metadata not found!")     
           
    def _normalizeDIDLRecord(self, lxmlNode):
        #print 'Starting record normalization...'
        str_didl = ''
        
        # Call our functions:
        getDIDLfunctions = [ self._getDIDLrootElement, self._getDIDLtopItem, self._getMODSmetadata, self._getDIDLObjectfiles, self._getDIDLHumanStartPage ]     
        for DIDLfunction in getDIDLfunctions:
            str_didl += DIDLfunction(lxmlNode)
        
        #Close DIDL:
        str_didl += "</didl:Item></didl:DIDL>"
        #print str_didl
                
        #define our parser:
        parser = etree.XMLParser(remove_blank_text=True, ns_clean=True)
        
        try:
            e_didl = parse(StringIO(str_didl), parser)
            #print etree.tostring(e_didl, encoding=XML_ENCODING)
            return e_didl
        except:
            print 'Error while parsing: ', str_didl
            raise        
        
        
    def _getDIDLrootElement(self, lxmlNode):
        #Check if DIDLDocumentId is available, if so, if it is valid: not in use elsewhere in the document.
        didlDocumentId = lxmlNode.xpath('//didl:DIDL/@DIDLDocumentId', namespaces=self._nsMap)
        strDocId = ''
        
        if didlDocumentId:
            #check if it is valid: not in use elsewhere in the document (as an identifier):            
            diiIdentifiers = lxmlNode.xpath('//dii:Identifier/text()', namespaces=self._nsMap)
            blnIDexists = False
            for idee in diiIdentifiers: #lower-case() xpath 2.0 function not available???
                #print idee
                if idee.lower() == didlDocumentId[0].lower():
                    blnIDexists = True
                    break
            if not blnIDexists:
                strDocId = ' DIDLDocumentId="%s"' % (escapeXml(didlDocumentId[0]))

        return """<didl:DIDL%s 
    xmlns:didl="urn:mpeg:mpeg21:2002:02-DIDL-NS" 
    xmlns:dii="urn:mpeg:mpeg21:2002:01-DII-NS" 
    xmlns:dc="http://purl.org/dc/elements/1.1/" 
    xmlns:dcterms="http://purl.org/dc/terms/" 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"     
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="urn:mpeg:mpeg21:2002:02-DIDL-NS 
    http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/did/didl.xsd
    urn:mpeg:mpeg21:2002:01-DII-NS 
    http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/dii/dii.xsd">""" % (strDocId)


    def _getDIDLtopItem(self, lxmlNode):
        # Wrappers:
        pid, modified, mimetype, pidlocation = '', '', "application/xml", ''
        
#1:     Get persistentIdentifier:
        pidlist = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Descriptor/didl:Statement/dii:Identifier/text()', namespaces=self._nsMap)
        if pidlist:
            pid = pidlist[0].strip().lower()
            self._checkURNFormat(pid)                
        else:
            raise ValidateException("Mandatory persistent identifier (urn:nbn) not found in top level Item.")

#2:     Get toplevel modificationDate: self._validateISO8601()
        tl_modified = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Descriptor/didl:Statement/dcterms:modified/text()', namespaces=self._nsMap)
        #check op geldig/aanwezig-heid tlModified, anders exception:
        if tl_modified and not self._validateISO8601(tl_modified[0]):
            raise ValidateException("Mandatory date modified in toplevelItem not a valid ISO8601 date: " + tl_modified[0])
        elif not tl_modified:
            raise ValidateException("Mandatory date modified in toplevelItem missing")            

        #get all modified dates (min 1: the tl modified):
        all_modified = lxmlNode.xpath('//didl:Item/didl:Descriptor/didl:Statement/dcterms:modified/text()', namespaces=self._nsMap)
        
        #Get most recent date from all items:
        if all_modified:
            datedict = {}
            for date in all_modified:
                if self._validateISO8601(date.strip()):
                    datedict[parseDate(date.strip())] = date.strip()
            #Get first sorted key:
            for key in reversed(sorted(datedict.iterkeys())):
                modified = datedict[key]
                break            
            #print 'Most recent date:', modified

#3:     Get PidResourceMimetype
        mimetypelist = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Component/didl:Resource/@mimeType', namespaces=self._nsMap)
        if mimetypelist: #TODO controle op geldige mimetype?
            mimetype = mimetypelist[0].strip().lower()
        else:
            mimetype = "application/xml" #overrides the default init value...

#4:     Get PidResourceLocation:
        pidlocation = self._findAndBindFirst(lxmlNode, '%s',
        '//didl:DIDL/didl:Item/didl:Component/didl:Resource/@ref',
        '//didl:DIDL/didl:Item/didl:Component/didl:Resource/text()',
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1
        "//mods:mods/mods:location/mods:url[contains(.,'://')]/text()", #fallback MODS
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref' #fallback DIDL 2.3.1
        )

        if pidlocation == '':
            raise ValidateException("Mandatory resource location not found in top level Item.")

        return """<didl:Item>
        <didl:Descriptor><didl:Statement mimeType="application/xml"><dii:Identifier>%s</dii:Identifier></didl:Statement></didl:Descriptor>
        <didl:Descriptor><didl:Statement mimeType="application/xml"><dcterms:modified>%s</dcterms:modified></didl:Statement></didl:Descriptor>
        <didl:Component><didl:Resource mimeType="%s" ref="%s"/></didl:Component>""" % (escapeXml(pid), modified, escapeXml(mimetype), pidlocation)        


    def _getMODSmetadata(self, lxmlNode):
        metadataItem = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/descriptiveMetadata"]', namespaces=self._nsMap)
        if not metadataItem:
            metadataItem = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/descriptiveMetadata"]', namespaces=self._nsMap)
            if metadataItem: self.do.logMsg(self._identifier, "Found descriptiveMetadata in dip:ObjectType. This should have been: rdf:type/@rdf:resource")
        if metadataItem:
            mods_template = """<didl:Item>
                                    <didl:Descriptor>
                                        <didl:Statement mimeType="application/xml">
                                            <rdf:type rdf:resource="info:eu-repo/semantics/descriptiveMetadata"/>
                                        </didl:Statement>
                                    </didl:Descriptor>
                                    %s
                                    <didl:Component>
                                        <didl:Resource mimeType="application/xml">
                                           %s 
                                        </didl:Resource>
                                    </didl:Component>
                                </didl:Item>""" % (self._getDateModifiedDescriptor(metadataItem[0]), self._getNormalizedMODS(metadataItem[0]))
        else:
            raise ValidateException("Mandatory Metadata element not found in DIDL record.")          
        return mods_template  


    def _getNormalizedMODS(self, lxmlNode):    
        #1: Get MODS node from DIDL descr. metadata Item:
        mods = lxmlNode.xpath('self::didl:Item//mods:mods', namespaces=self._nsMap)
        if mods:
            return self._convertFullMods2GHMods(mods[0])
        else:
            raise ValidateException("Mandatory MODS in descriptiveMetadata Item element not found in DIDL record.")


    def _convertFullMods2GHMods(self, lxmlNode):        
        returnxml = ''
        e_root = deepcopy(lxmlNode) #We need a deepcopy; otherwise we'll modify the lxmlnode by reference!!
        #assert MODS:
        if self._nsMap['mods'] in e_root.nsmap.values(): #Check of MODS is available.
            #Assert version set to 3.3:            
            e_root.set("version", "3.3")
            e_root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-3.xsd")
            
            for child in e_root.iterchildren():
                #print child.tag 
                for eroot_name in allowed_mods_rootelem:
                    #print 'Allowed Element name:', ('{%s}'+eroot_name) % self._nsMap['mods']
                    if child.tag == ('{%s}'+eroot_name) % self._nsMap['mods']:
                        break
                else: #Wordt alleen geskipped als ie uit 'break' komt...
                    e_root.remove(child)                
            returnxml = etree.tostring(e_root, pretty_print=True, encoding=XML_ENCODING)
            return returnxml
   
    def _getDateModifiedDescriptor(self, lxmlNode): #TODO: Refactor, method is same as DIDL (#4)...        
        #4: Check geldige datemodified (feitelijk verplicht, hoewel vaak niet geimplemeteerd...)
        modified = lxmlNode.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:modified/text()', namespaces=self._nsMap)
        if modified and self._validateISO8601(modified[0]):
            #print "DIDL MODS Item modified:", modified[0]
            return descr_templ % ('<dcterms:modified>'+modified[0].strip()+'</dcterms:modified>')
        else:
            return ''     

    def _getDIDLObjectfiles(self, lxmlNode):              
        of_container = ''          
        objectfiles = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]', namespaces=self._nsMap)
        if not objectfiles:
            objectfiles = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]', namespaces=self._nsMap)              
        for objectfile in objectfiles:
        #1:Define correct ObjectFile descriptor:
            of_container += '<didl:Item><didl:Descriptor><didl:Statement mimeType="application/xml"><rdf:type rdf:resource="info:eu-repo/semantics/objectFile"/></didl:Statement></didl:Descriptor>'           
            #print 'OBJECTFILE: ', etree.tostring(objectfile, encoding=XML_ENCODING)
            
        #2: Check geldige Identifier (feitelijk verplicht, hoewel vaak niet geimplemeteerd...) 
            pi = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dii:Identifier/text()', namespaces=self._nsMap)
            if pi: #TODO: URN pattern check?
                #print "pi:", pi[0]
                of_container += descr_templ % ('<dii:Identifier>'+escapeXml(pi[0].strip().lower())+'</dii:Identifier>') 
                            
        #3: Check op geldige AccessRights:
            arights = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:accessRights/text()', namespaces=self._nsMap)
            if arights:
                #print "arights:", arights[0]
                for key, value in accessRights.iteritems():
                    if arights[0].strip().lower().find(key) >= 0:  
                        of_container += descr_templ % ('<dcterms:accessRights>'+value+'</dcterms:accessRights>')                        
                        break
                                                
        #4: Check geldige datemodified (feitelijk verplicht, hoewel vaak niet geimplemeteerd...)
            modified = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:modified/text()', namespaces=self._nsMap)
            if modified and self._validateISO8601(modified[0]):
                #print "modified:", modified[0]
                of_container += descr_templ % ('<dcterms:modified>'+modified[0].strip()+'</dcterms:modified>')   
                
            
        #5: Check for 'file' description:
            descr = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dc:description/text()', namespaces=self._nsMap)
            if descr:
                of_container += descr_templ % ('<dc:description>'+escapeXml(descr[0].strip())+'</dc:description>')  
                
            
        #6: Check for embargo:
            embargo = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:available/text()', namespaces=self._nsMap)
            if embargo and self._validateISO8601(embargo[0]):
                #print "embargo:", embargo[0]
                of_container += descr_templ % ('<dcterms:available>'+embargo[0].strip()+'</dcterms:available>')  

            
        #7: Check for published version(author/publisher):
            pubVersion = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/rdf:type/@rdf:resource', namespaces=self._nsMap)
            if pubVersion: #both (author/publisher) may be available: we'll take the first one...
                #print "publicationVersion:", pubVersion[0]
                for key, value in pubVersions.iteritems():
                    #print key, value
                    if pubVersion[0].strip().lower().find(key) >= 0:
                        of_container += descr_templ % ('<rdf:type rdf:resource="'+value+'"/>')                                
                        break
            
        #8:Check for MANDATORY resources and mimetypes:
            didl_resources = objectfile.xpath('self::didl:Item/didl:Component/didl:Resource', namespaces=self._nsMap)
            resources = ''
            #print "Checking resources..."
            for resource in didl_resources:
                #print "found resource..."
                mimeType = resource.xpath('self::didl:Resource/@mimeType', namespaces=self._nsMap)
                uri = resource.xpath('self::didl:Resource/@ref', namespaces=self._nsMap)
                if mimeType and uri: #TODO: valid ref check??
                    resources += """<didl:Resource mimeType="%s" ref="%s"/>""" % (escapeXml(mimeType[0].strip().lower()), escapeXml(uri[0].strip())) #uri not .lower()!
            if resources != '':
                of_container += """<didl:Component>
                %s
            </didl:Component>""" % (resources)
            else:
                #print "NO resources found..."
                raise ValidateException("Mandatory Resource not found in ObjectFile Item.")            
            
            of_container += '</didl:Item>'
            #laatste: Sluit container af als er geldige objectfiles objecten gevonden zijn...                        
#            if hasValidResources and hasValidPID:
#                of_container += '</didl:Item>'
#            else:
#                of_container = ''
                
        return of_container
    
    
    def _getDIDLHumanStartPage(self, lxmlNode): #TODO: check completeness
        
        uriref, mimetype = None, 'text/html'
        
        uriref = self._findAndBindFirst(lxmlNode,
        '%s',
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1     
        "//mods:mods/mods:location/mods:url[contains(.,'://')]/text()") #, #fallback MODS
        #'//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 3.0
        #'//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1
        #"//dc:identifier[1]/text()") #Greedy fallback DC. If all else fails...

        mimetype = self._findAndBindFirst(lxmlNode,
        '%s',
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@mimeType', #DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@mimeType') #fallback DIDL 2.3.1     

        #'//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 3.0
        #'//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1
        #"//dc:identifier[1]/text()") #Greedy fallback DC. If all else fails...
        
        #        
        if uriref != None: # and mimetype!= None:
            return """<didl:Item>
                        <didl:Descriptor>
                            <didl:Statement mimeType="application/xml">
                                <rdf:type rdf:resource="info:eu-repo/semantics/humanStartPage"/>
                            </didl:Statement>
                        </didl:Descriptor>
                        <didl:Component>
                            <didl:Resource ref="%s" mimeType="%s"/>
                        </didl:Component>
                    </didl:Item>""" % (uriref, mimetype)
        else:
            return ""

    def _checkURNFormat(self, pid):
        p = compile('^[uU][rR][nN]:[nN][bB][nN]:[nN][lL]:[uU][iI]:\d{1,3}-.*')
        m = p.match(pid)
        if not m:
            raise ValidateException("Invalid format for mandatory persistent identifier (urn:nbn) in top level Item: " + pid)
        return True     

    def _validateISO8601(self, datestring):
        try:
            parseDate(datestring)
        except ValueError:
            return False
        return True


    def _findAndBindFirst(self, node, template, *xpaths):
        # Will bind only the FIRST (xpath match/record) to the template. It will never return more than one templated element...
        items = []
        for p in xpaths:
            items += node.xpath(p, namespaces=self._nsMap)
            if len(items)>1:
                break
        for item in items:
            return template % escapeXml(item)
        return ''

    def __str__(self):
        return 'NL_DIDL_normalized'