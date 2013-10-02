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
from normalize_nl_didl import formatException, XML_ENCODING

#Schema validatie:
from os.path import abspath, dirname, join

# This component handles ADD messages only.
# It will try to convert the supplied data (KNAWLong) from the 'metadata' part into KNAWshort. All other parts and data formats are ignored (blocked).
# If it fails in doing so, it will block (NOT pass) the ADD message.
# Returns: xml-string!

## Default xml-encoding:
#XML_ENCODING = 'utf-8'

##MODS root elements allwed by GH normalized:
#allowed_mods_rootelem = ["abstract", "classification", "extension", "genre", "identifier", "language", "location", "name", "originInfo", "part", "physicalDescription", "relatedItem", "subject", "titleInfo", "typeOfResource"]
allowed_mods_rootelem = ["extension", "genre", "identifier", "language", "typeOfResource"]


class Normalize_nl_MODS(Observable):
    """A class that normalizes MODS metadata to the Edustandaard applicationprofile"""
    
    def __init__(self, nsMap={}):
        Observable.__init__(self)
        self._nsMap=nsMap
        self._bln_success = False
        
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
        
        # MODS normalisation in 4 steps:
        # 1. Get Mods from the lxmlNode.
        # 2. Normalize it
        # 3. Put it back in place.
        # 4. return the lxmlNode containing the normalized MODS.
        
        #1: We'll retrieve the parent MODS tag directly, NOT from the descriptiveMetadataTag axis from DIDL, to keeps this component generic. NOT:
        #mods = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Item[didl:Descriptor/didl:Statement/rdf:type/@rdf:resource="info:eu-repo/semantics/descriptiveMetadata"]/mods:mods', namespaces=self._nsMap)
        
        print 'Starting MODS normalization component...'
        #1:
        lxmlMODS = lxmlNode.xpath('(//mods:mods)[1]', namespaces=self._nsMap)
        
        #Our normalisation functions to call: TODO: complement the functions list.
        modsFunctions = [ self._convertFullMods2GHMods ]        
        
        if lxmlMODS and lxmlMODS[0]:
            print 'Found MODS, starting MODS normalization...'
        #2:
            str_mods = ''            
            for function in modsFunctions:
                str_mods += function(lxmlMODS[0])            
            print "MODS Element normalization succeeded."
            
        #3:
            #f = etree.fromstring(str_mods)                        
            print 'Replacing original MODS with normalized MODS element...'
            lxmlMODS[0].getparent().replace(lxmlMODS[0], etree.fromstring(str_mods) )
#            print etree.tostring(lxmlNode, pretty_print=True)                 

        else: #This should never happen @runtime: record should have been validated up front...
            print 'NO MODS element found!'
            raise ValidateException(formatException("Mandatory MODS metadata NOT found in DIDL record.", self._identifier))
        #4:
        return lxmlNode

    def _convertFullMods2GHMods(self, lxmlNode):        
        returnxml = ''
        e_root = deepcopy(lxmlNode) #TODO: Check We need a deepcopy; otherwise we'll modify the lxmlnode by reference!!
        #assert MODS:
        if self._nsMap['mods'] in e_root.nsmap.values(): #Check of MODS namspace is declared.
            #TODO: Check if version 3.3 was supplied: correct and log otherwise.
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
        return 'Normalize_nl_MODS'
