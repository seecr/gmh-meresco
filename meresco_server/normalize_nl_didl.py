# -*- coding: utf-8 -*-
from lxml.etree import parse, _ElementTree, tostring, XMLSchema, parse as lxmlParse
from lxml import etree
from xml.sax.saxutils import escape as escapeXml
from meresco.core import Observable
from copy import deepcopy
from StringIO import StringIO
from meresco.components.xml_generic.validate import ValidateException
from xml_validator import formatExceptionLine
from re import compile, IGNORECASE
from dateutil.parser import parse as parseDate

#Schema validatie:
from os.path import abspath, dirname, join

# This component handles ADD messages only.
# It will try to convert the supplied data (KNAWLong) from the 'metadata' part into KNAWshort. All other parts and data formats are ignored (blocked).
# If it fails in doing so, it will block (NOT pass) the ADD message.
# Returns: xml-string!

## Default xml-encoding:
XML_ENCODING = 'utf-8'


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


class Normalize_nl_DIDL(Observable):
    """A class that normalizes DIDL container to the Edustandaard applicationprofile"""
    
    def __init__(self, nsMap={}):
        Observable.__init__(self)
        self._nsMap=nsMap
        self._bln_success = False
        self._patternURN = compile('^[uU][rR][nN]:[nN][bB][nN]:[nN][lL]:[uU][iI]:\d{1,3}-.*')
        self._patternURL = compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        #r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', IGNORECASE)
        
    def _detectAndConvert(self, anObject):
        if type(anObject) == _ElementTree:
            return self.convert(anObject)
        return anObject

    def convert(self, lxmlNode):
        self._bln_success = False       
        result_tree = self._normalizeRecord(lxmlNode)
        if result_tree != None:
            self._bln_success = True            
        return result_tree

    def all_unknown(self, method, *args, **kwargs):
        self._identifier = kwargs.get('identifier')
        newArgs = [self._detectAndConvert(arg) for arg in args]     
        newKwargs = dict((key, self._detectAndConvert(value)) for key, value in kwargs.items())
        if self._bln_success:
            return self.all.unknown(method, *newArgs, **newKwargs)

    def _normalizeRecord(self, lxmlNode):
        #print 'Starting DIDL normalization...'
        str_didl = ''
        
        # Call our functions:
        didlFunctions = [ self._getRootElement, self._getTopItem, self._getDescriptiveMetadata, self._getObjectfiles, self._getHumanStartPage ]     
        for function in didlFunctions:
            str_didl += function(lxmlNode)
        
        #Close DIDL:
        str_didl += "</didl:Item></didl:DIDL>"
                
        #define our parser:
        parser = etree.XMLParser(remove_blank_text=True, ns_clean=True)
        
        try:
            e_didl = parse(StringIO(str_didl), parser)
            item_to_focus = e_didl.xpath('//didl:Item/didl:Item', namespaces=self._nsMap)
          
            for item in item_to_focus:
                resource_to_focus = item.xpath('self::didl:Item/didl:Component/didl:Resource', namespaces=self._nsMap)
                
                if len(resource_to_focus) > 1:
                    new_resource_to_focus = deepcopy(resource_to_focus)
                    comp = resource_to_focus[0].getparent()  #<component>
                    item.remove(comp) #item without component tag
                    parent_item = item.getparent()
                    
                    for r in resource_to_focus:
                        comp.remove(r) #remove all children from the component tag

                    for nr in new_resource_to_focus:
                        new_comp = deepcopy(comp) #copy the original(empty) component tag
                        new_comp.append(nr) #add the Resource tag to the empty copied component tag
                        new_item = deepcopy(item) #copy the original item tag
                        new_item.append(new_comp) # add to the copied item
                        parent_item.append(new_item) #add the copied item to the parent

                    parent_item.remove(item)
            
            etree.cleanup_namespaces(e_didl)
            #print "DIDL normalization succeeded.", etree.tostring(e_didl, encoding=XML_ENCODING)

            #root = etree.Element('temp', nsmap=self._nsMap)
            #root.append(e_didl)
            #etree.cleanup_namespaces(root)            
            #return root.find( ('{%s}DIDL') % self._nsMap['didl']
            
            return e_didl
        except: #TODO: WST: what does this do?
            print 'Error while parsing: ', str_didl
            raise
        
        
    def _getRootElement(self, lxmlNode):
        #Check if DIDLDocumentId is available, if so, if it is valid: not in use elsewhere in the document.
        didlDocumentId = lxmlNode.xpath('//didl:DIDL/@DIDLDocumentId', namespaces=self._nsMap)
        strDocId = ''
        
        if len(didlDocumentId) > 0:
            #check if it is valid: not in use elsewhere in the document (as an identifier):            
            diiIdentifiers = lxmlNode.xpath('//dii:Identifier/text()', namespaces=self._nsMap)
            blnIDexists = False
            for idee in diiIdentifiers: #lower-case() xpath 2.0 function not available???
                #print idee
                if idee.lower() == didlDocumentId[0].lower():
                    blnIDexists = True
                    break
            # Als niet als id elders gevonden, oai-identifier checken.
            if not blnIDexists:
                if didlDocumentId[0].lower() == self._identifier.split(':', 1 )[0].lower():
                    blnIDexists = True
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


    def _getTopItem(self, lxmlNode):
        # Wrappers:
        pid, modified, mimetype, pidlocation = '', '', "application/xml", ''
        
#1:     Get persistentIdentifier:
        pidlist = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Descriptor/didl:Statement/dii:Identifier/text()', namespaces=self._nsMap)
        if len(pidlist) > 0:
            pid = pidlist[0].strip().lower()
            self._checkURNFormat(pid)                
        else:
            raise ValidateException(formatExceptionLine("Mandatory persistent identifier (urn:nbn) not found in top level Item.", self._identifier))

#2:     Get toplevel modificationDate: self._validateISO8601()
        tl_modified = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Descriptor/didl:Statement/dcterms:modified/text()', namespaces=self._nsMap)
        #check op geldig/aanwezigheid tlModified, anders exception:
        if len(tl_modified) > 0 and not self._validateISO8601(tl_modified[0]):
            raise ValidateException(formatExceptionLine("Mandatory date modified in toplevelItem not a valid ISO8601 date: " + tl_modified[0], self._identifier))
        elif len(tl_modified) == 0:
            raise ValidateException(formatExceptionLine("No mandatory date dcterms:modified in toplevelItem.", self._identifier))

        #get all modified dates:
        all_modified = lxmlNode.xpath('//didl:Item/didl:Descriptor/didl:Statement/dcterms:modified/text()', namespaces=self._nsMap)
        
        #Get most recent date from all items, to add to toplevelItem:
        if len(all_modified) > 0:
            datedict = {}
            for date in all_modified:
                if self._validateISO8601(date.strip()):
                    datedict[parseDate(date.strip())] = date.strip()
            #Get first sorted key:
            for key in reversed(sorted(datedict.iterkeys())):
                modified = datedict[key]
                break
            
        if not tl_modified[0].strip() == modified:
            self.do.logMsg(self._identifier, "Top level Item date modified replaced by more recent child Item date modified.")
            print "Top level Item date modified replaced by more recent child Item date modified."
            
#3:     Get PidResourceMimetype
        mimetypelist = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Component/didl:Resource/@mimeType', namespaces=self._nsMap)
        if len(mimetypelist) > 0: #TODO controle op geldige mimetype? http://www.iana.org/assignments/media-types/media-types.xhtml
            mimetype = mimetypelist[0].strip().lower()
            if "/" not in mimetype:
                self.do.logMsg(self._identifier, "Normalized invalid mimeType: " +mimetype+ " to default: text/html")
                mimetype = "text/html" #overrides the default init value...
        else: # Schema validation Error if it does not exist ...
            mimetype = "text/html" #overrides the default init value...

#4:     Get PidResourceLocation:
        pidlocation = self._findAndBindFirst(lxmlNode, '%s',
        '//didl:DIDL/didl:Item/didl:Component/didl:Resource/@ref',
        '//didl:DIDL/didl:Item/didl:Component/didl:Resource/text()',
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@resource="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #DIDL 3.0, without @rdf:resource
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@resource="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 3.0, without @rdf:resource
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref' #fallback DIDL 2.3.1
        )

        if pidlocation == '':
            raise ValidateException(formatExceptionLine("Mandatory resource location not found in top level Item.", self._identifier))
        if not self._isURL(pidlocation):
            raise ValidateException(formatExceptionLine("Mandatory resource location is not a valid URL: " + pidlocation, self._identifier))
        
        return """<didl:Item>
        <didl:Descriptor><didl:Statement mimeType="application/xml"><dii:Identifier>%s</dii:Identifier></didl:Statement></didl:Descriptor>
        <didl:Descriptor><didl:Statement mimeType="application/xml"><dcterms:modified>%s</dcterms:modified></didl:Statement></didl:Descriptor>
        <didl:Component><didl:Resource mimeType="%s" ref="%s"/></didl:Component>""" % (escapeXml(pid), modified, escapeXml(mimetype), pidlocation)        


    def _getDescriptiveMetadata(self, lxmlNode):
    #TODO: This always normalizes to rdf namespace, without warning/message!
        descriptiveMetadataItem = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/descriptiveMetadata"]', namespaces=self._nsMap)
        if len(descriptiveMetadataItem) == 0: #Fallback to @resource (no rdf nmsp), if available...
            descriptiveMetadataItem = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@resource="info:eu-repo/semantics/descriptiveMetadata"]', namespaces=self._nsMap)
            if len(descriptiveMetadataItem) > 0: self.do.logMsg(self._identifier, "Found descriptiveMetadata in rdf:type/@resource. This should have been: rdf:type/@rdf:resource")
        if len(descriptiveMetadataItem) == 0: #Fallback to dip namespace, if available...
            descriptiveMetadataItem = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/descriptiveMetadata"]', namespaces=self._nsMap)
            if len(descriptiveMetadataItem) > 0: self.do.logMsg(self._identifier, "Found descriptiveMetadata in depricated dip:ObjectType. This should have been: rdf:type/@rdf:resource")
        if len(descriptiveMetadataItem) > 0:
            item_template = """<didl:Item>
                                    <didl:Descriptor>
                                        <didl:Statement mimeType="application/xml">
                                            <rdf:type rdf:resource="info:eu-repo/semantics/descriptiveMetadata"/>
                                        </didl:Statement>
                                    </didl:Descriptor>
                                    %s%s<didl:Component>
                                        <didl:Resource mimeType="application/xml">
                                           %s 
                                        </didl:Resource>
                                    </didl:Component>
                                </didl:Item>""" % (self._getIdentifierDescriptor(descriptiveMetadataItem[0]), self._getDateModifiedDescriptor(descriptiveMetadataItem[0]), self._getMODSfromDMI(descriptiveMetadataItem[0]))
        else:
            raise ValidateException(formatExceptionLine("Mandatory descriptiveMetadata item element not found!", self._identifier))
        return item_template
   
    def _getDateModifiedDescriptor(self, lxmlNode):
        #4: Check geldigheid datemodified (feitelijk verplicht, hoewel vaak niet geimplemeteerd...)
        modified = lxmlNode.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:modified/text()', namespaces=self._nsMap)
        if len(modified) > 0 and self._validateISO8601(modified[0]):
            return descr_templ % ('<dcterms:modified>'+modified[0].strip()+'</dcterms:modified>')
        else:
            return ''     

    def _getIdentifierDescriptor(self, lxmlNode):
        # Check geldige Identifier (feitelijk verplicht, hoewel vaak niet geimplemeteerd...) 
        idee = lxmlNode.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dii:Identifier/text()', namespaces=self._nsMap)
        if len(idee) > 0:
            return descr_templ % ('<dii:Identifier>'+escapeXml(idee[0].strip().lower())+'</dii:Identifier>')
        else:
            return ''

    def _getMODSfromDMI(self, lxmlNodeDMI):    
        #1: Get MODS node from DIDL descr. metadata Item (DMI):
        mods = lxmlNodeDMI.xpath('self::didl:Item//mods:mods', namespaces=self._nsMap)
        if len(mods) > 0:
            return tostring(mods[0])
        else:
            raise ValidateException(formatExceptionLine("Mandatory MODS in descriptiveMetadata element not found in DIDL record.", self._identifier))

    def _getObjectfiles(self, lxmlNode):              
        of_container = ''
        objectfiles = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]', namespaces=self._nsMap)
        if len(objectfiles) ==0:
            objectfiles = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@resource="info:eu-repo/semantics/objectFile"]', namespaces=self._nsMap)
            if len(objectfiles) > 0: self.do.logMsg(self._identifier, "Found objectFile in rdf:type/@resource. This should have been: rdf:type/@rdf:resource")
        if len(objectfiles) ==0:
            objectfiles = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]', namespaces=self._nsMap)
            if len(objectfiles) > 0: self.do.logMsg(self._identifier, "Found descriptiveMetadata in depricated dip:ObjectType. This should have been: rdf:type/@rdf:resource")
        for objectfile in objectfiles:
        #1:Define correct ObjectFile descriptor:
            of_container += '<didl:Item><didl:Descriptor><didl:Statement mimeType="application/xml"><rdf:type rdf:resource="info:eu-repo/semantics/objectFile"/></didl:Statement></didl:Descriptor>' 
            
        #2: Check geldige Identifier (feitelijk verplicht, hoewel vaak niet geimplemeteerd...) 
            pi = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dii:Identifier/text()', namespaces=self._nsMap)
            if len(pi) > 0: #TODO: URN pattern check?
                of_container += descr_templ % ('<dii:Identifier>'+escapeXml(pi[0].strip().lower())+'</dii:Identifier>') 
                            
        #3: Check op geldige AccessRights:
            arights = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:accessRights/text()', namespaces=self._nsMap)
            if len(arights) > 0:
                for key, value in accessRights.iteritems():
                    if arights[0].strip().lower().find(key) >= 0:
                        of_container += descr_templ % ('<dcterms:accessRights>'+value+'</dcterms:accessRights>')                        
                        break
            else:
                self.do.logMsg(self._identifier, "No accessRights found for objectfile.")
                #print "No accessRights found for objectfile."
                                                
        #4: Check geldige datemodified (feitelijk verplicht, hoewel vaak niet geimplemeteerd...)
            modified = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:modified/text()', namespaces=self._nsMap)
            if len(modified) > 0 and self._validateISO8601(modified[0]):
                of_container += descr_templ % ('<dcterms:modified>'+modified[0].strip()+'</dcterms:modified>')   
                
            
        #5: Check for 'file' description:
            descr = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dc:description/text()', namespaces=self._nsMap)
            if len(descr) > 0:
                of_container += descr_templ % ('<dc:description>'+escapeXml(descr[0].strip())+'</dc:description>')  
                
            
        #6.0: Check for embargo:
            embargo = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:available/text()', namespaces=self._nsMap)
            if len(embargo) > 0 and self._validateISO8601(embargo[0]):
                of_container += descr_templ % ('<dcterms:available>'+embargo[0].strip()+'</dcterms:available>')
                
        #6.1: Check for dateSubmitted:
            dembargo = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:dateSubmitted/text()', namespaces=self._nsMap)
            if len(dembargo) > 0 and self._validateISO8601(dembargo[0]):
                of_container += descr_templ % ('<dcterms:dateSubmitted>'+dembargo[0].strip()+'</dcterms:dateSubmitted>')
            else:
                #6.2: Check for issued (depricated, normalize to dateSubmitted):
                issued = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:issued/text()', namespaces=self._nsMap)
                if len(issued) > 0 and self._validateISO8601(issued[0]):
                    of_container += descr_templ % ('<dcterms:dateSubmitted>'+issued[0].strip()+'</dcterms:dateSubmitted>')  

            
        #7: Check for published version(author/publisher):
            pubVersion = objectfile.xpath('self::didl:Item/didl:Descriptor/didl:Statement/rdf:type/@rdf:resource', namespaces=self._nsMap)
            if len(pubVersion) > 0: #both (author/publisher) may be available: we'll take the first one...
                for key, value in pubVersions.iteritems():
                    if pubVersion[0].strip().lower().find(key) >= 0:
                        of_container += descr_templ % ('<rdf:type rdf:resource="'+value+'"/>')                                
                        break

        #8:Check for MANDATORY resources and mimetypes:
            didl_resources = objectfile.xpath('self::didl:Item/didl:Component/didl:Resource[@mimeType and @ref]', namespaces=self._nsMap)
            resources = ''
            _url_list = [ ]
            #print "Checking resources..."
            for resource in didl_resources:
                #print "found resource..."
                mimeType = resource.xpath('self::didl:Resource/@mimeType', namespaces=self._nsMap)
                uri = resource.xpath('self::didl:Resource/@ref', namespaces=self._nsMap)
                # We need both mimeType and URI:
                if len(mimeType) > 0 and len(uri) > 0:
                    if self._isMimeType(mimeType[0]) and self._isURL(uri[0]):
                        resources += """<didl:Resource mimeType="%s" ref="%s"/>""" % (escapeXml(mimeType[0].strip().lower()), escapeXml(uri[0].strip())) #uri not .lower()!
                        _url_list.append("""<didl:Resource mimeType="%s" ref="%s"/>""" % (escapeXml(mimeType[0].strip().lower()), escapeXml(uri[0].strip())))
                    else:
                        self.do.logMsg(self._identifier, "Invalid mimeType or URL found for objectfile Resource: skipping")
                        
            if resources != '':
                of_container += """<didl:Component>
                %s
            </didl:Component>""" % (resources)
            else:
                #print "NO (valid) resources found..."
                raise ValidateException(formatExceptionLine("Mandatory Resource(s) not found in ObjectFile Item.", self._identifier))            
            
            of_container += '</didl:Item>'
                
        return of_container
    
    
    def _getHumanStartPage(self, lxmlNode):
        
        uriref, mimetype = None, None
        
        uriref = self._findAndBindFirst(lxmlNode,
        '%s',
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@resource="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #DIDL 3.0 (zonder rdf namespace op attribuut)        
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1
        '//didl:DIDL/didl:Item/didl:Component/didl:Resource/@ref',
        '//didl:DIDL/didl:Item/didl:Component/didl:Resource/text()')
        #'//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 3.0
        #'//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1


        mimetype = self._findAndBindFirst(lxmlNode,
        '%s',
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@mimeType', #DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@resource="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@mimeType', #DIDL 3.0
        '//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/humanStartPage"]/didl:Component/didl:Resource/@mimeType') #fallback DIDL 2.3.1
        #'//didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 3.0
        #'//didl:Item/didl:Item[didl:Descriptor/didl:Statement/dip:ObjectType/text()="info:eu-repo/semantics/objectFile"]/didl:Component/didl:Resource/@ref', #fallback DIDL 2.3.1

        if not self._isMimeType(mimetype):
            mimetype = 'text/html'
            
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
            self.do.logMsg(self._identifier, "No valid HumanStartPage found!")
            return ""
         
    def _checkURNFormat(self, pid):
        m = self._patternURN.match(pid)
        if not m:
            raise ValidateException(formatExceptionLine("Invalid format for mandatory persistent identifier (urn:nbn) in top level Item: " + pid, self._identifier))
        return True
    
    def _validateISO8601(self, datestring):
        try:
            parseDate(datestring)
        except ValueError:
            return False
        return True

    def _isURL(self, string):
        bln_isValid = False
        m = self._patternURL.match(string)
        if m:
            bln_isValid = True
        return bln_isValid
                
    def _isMimeType(self, string):
        return False if string is None else "/" in string
       
        
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
        return 'Normalize_nl_DIDL'
