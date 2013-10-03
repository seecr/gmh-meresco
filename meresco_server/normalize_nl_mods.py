# -*- coding: utf-8 -*-
from lxml.etree import parse, _ElementTree, tostring, XMLSchema, parse as lxmlParse
from lxml import etree
from xml.sax.saxutils import escape as escapeXml
from meresco.core import Observable
from copy import deepcopy
from StringIO import StringIO
from meresco.components.xml_generic.validate import ValidateException
from xml_validator import formatExceptionLine
from re import compile
from dateutil.parser import parse as parseDate
from normalize_nl_didl import XML_ENCODING

#Schema validatie:
from os.path import abspath, dirname, join

# This component handles ADD messages only.
# It will try to convert the supplied data (KNAWLong) from the 'metadata' part into KNAWshort. All other parts and data formats are ignored (blocked).
# If it fails in doing so, it will block (NOT pass) the ADD message.
# Returns: xml-string!


#Taken from: http://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt
ISO639 = ["aar", "abk", "ace", "ach", "ada", "ady", "afa", "afh", "afr", "ain", "aka", "akk", "alb", "ale", "alg", "alt", "amh", "ang", "anp", "apa", "ara", "arc", "arg", "arm", "arn", "arp", "art", "arw", "asm", "ast", "ath", "aus", "ava", "ave", "awa", "aym", "aze", "bad", "bai", "bak", "bal", "bam", "ban", "baq", "bas", "bat", "bej", "bel", "bem", "ben", "ber", "bho", "bih", "bik", "bin", "bis", "bla", "bnt", "bos", "bra", "bre", "btk", "bua", "bug", "bul", "bur", "byn", "cad", "cai", "car", "cat", "cau", "ceb", "cel", "cha", "chb", "che", "chg", "chi", "chk", "chm", "chn", "cho", "chp", "chr", "chu", "chv", "chy", "cmc", "cop", "cor", "cos", "cpe", "cpf", "cpp", "cre", "crh", "crp", "csb", "cus", "cze", "dak", "dan", "dar", "day", "del", "den", "dgr", "din", "div", "doi", "dra", "dsb", "dua", "dum", "dut", "dyu", "dzo", "efi", "egy", "eka", "elx", "eng", "enm", "epo", "est", "ewe", "ewo", "fan", "fao", "fat", "fij", "fil", "fin", "fiu", "fon", "fre", "frm", "fro", "frr", "frs", "fry", "ful", "fur", "gaa", "gay", "gba", "gem", "geo", "ger", "gez", "gil", "gla", "gle", "glg", "glv", "gmh", "goh", "gon", "gor", "got", "grb", "grc", "gre", "grn", "gsw", "guj", "gwi", "hai", "hat", "hau", "haw", "heb", "her", "hil", "him", "hin", "hit", "hmn", "hmo", "hrv", "hsb", "hun", "hup", "iba", "ibo", "ice", "ido", "iii", "ijo", "iku", "ile", "ilo", "ina", "inc", "ind", "ine", "inh", "ipk", "ira", "iro", "ita", "jav", "jbo", "jpn", "jpr", "jrb", "kaa", "kab", "kac", "kal", "kam", "kan", "kar", "kas", "kau", "kaw", "kaz", "kbd", "kha", "khi", "khm", "kho", "kik", "kin", "kir", "kmb", "kok", "kom", "kon", "kor", "kos", "kpe", "krc", "krl", "kro", "kru", "kua", "kum", "kur", "kut", "lad", "lah", "lam", "lao", "lat", "lav", "lez", "lim", "lin", "lit", "lol", "loz", "ltz", "lua", "lub", "lug", "lui", "lun", "luo", "lus", "mac", "mad", "mag", "mah", "mai", "mak", "mal", "man", "mao", "map", "mar", "mas", "may", "mdf", "mdr", "men", "mga", "mic", "min", "mis", "mkh", "mlg", "mlt", "mnc", "mni", "mno", "moh", "mon", "mos", "mul", "mun", "mus", "mwl", "mwr", "myn", "myv", "nah", "nai", "nap", "nau", "nav", "nbl", "nde", "ndo", "nds", "nep", "new", "nia", "nic", "niu", "nno", "nob", "nog", "non", "nor", "nqo", "nso", "nub", "nwc", "nya", "nym", "nyn", "nyo", "nzi", "oci", "oji", "ori", "orm", "osa", "oss", "ota", "oto", "paa", "pag", "pal", "pam", "pan", "pap", "pau", "peo", "per", "phi", "phn", "pli", "pol", "pon", "por", "pra", "pro", "pus", "que", "raj", "rap", "rar", "roa", "roh", "rom", "rum", "run", "rup", "rus", "sad", "sag", "sah", "sai", "sal", "sam", "san", "sas", "sat", "scn", "sco", "sel", "sem", "sga", "sgn", "shn", "sid", "sin", "sio", "sit", "sla", "slo", "slv", "sma", "sme", "smi", "smj", "smn", "smo", "sms", "sna", "snd", "snk", "sog", "som", "son", "sot", "spa", "srd", "srn", "srp", "srr", "ssa", "ssw", "suk", "sun", "sus", "sux", "swa", "swe", "syc", "syr", "tah", "tai", "tam", "tat", "tel", "tem", "ter", "tet", "tgk", "tgl", "tha", "tib", "tig", "tir", "tiv", "tkl", "tlh", "tli", "tmh", "tog", "ton", "tpi", "tsi", "tsn", "tso", "tuk", "tum", "tup", "tur", "tut", "tvl", "twi", "tyv", "udm", "uga", "uig", "ukr", "umb", "und", "urd", "uzb", "vai", "ven", "vie", "vol", "vot", "wak", "wal", "war", "was", "wel", "wen", "wln", "wol", "xal", "xho", "yao", "yap", "yid", "yor", "ypk", "zap", "zbl", "zen", "zha", "znd", "zul", "zun", "zxx", "zza", "bod", "ces", "cym", "deu", "ell", "eus", "fas", "fra", "hye", "isl", "kat", "mkd", "mri", "msa", "mya", "nld", "ron", "slk", "sqi", "zho", "aa", "ab", "ae", "af", "ak", "am", "an", "ar", "as", "av", "ay", "az", "ba", "be", "bg", "bh", "bi", "bm", "bn", "bo", "br", "bs", "ca", "ce", "ch", "co", "cr", "cs", "cu", "cv", "cy", "da", "de", "dv", "dz", "ee", "el", "en", "eo", "es", "et", "eu", "fa", "ff", "fi", "fj", "fo", "fr", "fy", "ga", "gd", "gl", "gn", "gu", "gv", "ha", "he", "hi", "ho", "hr", "ht", "hu", "hy", "hz", "ia", "id", "ie", "ig", "ii", "ik", "io", "is", "it", "iu", "ja", "jv", "ka", "kg", "ki", "kj", "kk", "kl", "km", "kn", "ko", "kr", "ks", "ku", "kv", "kw", "ky", "la", "lb","lg", "li", "ln", "lo", "lt", "lu", "lv", "mg", "mh", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "na", "nb", "nd", "ne", "ng", "nl", "nn", "no", "nr", "nv", "ny", "oc", "oj", "om", "or", "os", "pa", "pi", "pl", "ps", "pt", "qu", "rm", "rn", "ro", "ru", "rw", "sa", "sc", "sd", "se", "sg", "si", "sk", "sl", "sm", "sn", "so", "sq", "sr", "ss", "st", "su", "sv", "sw", "ta", "te", "tg", "th", "ti", "tk", "tl", "tn", "to", "tr", "ts", "tt", "tw", "ty", "ug", "uk", "ur", "uz", "ve", "vi", "vo", "wa", "wo", "xh", "yi", "yo", "za", "zh", "zu"]

GENRES = ['annotation','article','bachelorthesis','book','bookpart','bookreview','conferencepaper','contributiontoperiodical','doctoralthesis','researchproposal','lecture','masterthesis','patent','preprint','report','studentthesis','technicaldocumentation','workingpaper','conferenceobject']

INFO_EU_REPO_SEMANTICS = "info:eu-repo/semantics/"

##MODS root elements allwed by GH normalized:
#allowed_mods_rootelem = ["abstract", "classification", "extension", "genre", "identifier", "language", "location", "name", "originInfo", "part", "physicalDescription", "relatedItem", "subject", "titleInfo", "typeOfResource"]
allowed_mods_rootelem = ["language", "genre"]


class Normalize_nl_MODS(Observable):
    """A class that normalizes MODS metadata to the Edustandaard applicationprofile"""
    
    def __init__(self, nsMap={}):
        Observable.__init__(self)
        self._nsMap=nsMap
        self._bln_success = False
        # http://www.schemacentral.com/sc/xsd/t-xsd_language.html
        self._patternRFC3066 = compile('^([A-Za-z]{2,3})(-[a-zA-Z0-9]{1,8})?$')# Captures first 2 or 3 language chars if nothing else OR followed by '-' and 1 to 8 alfanum chars.
        self._patternURN = compile('^[uU][rR][nN]:[nN][bB][nN]:[nN][lL]:[uU][iI]:\d{1,3}-.*')
        
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
            print 'Replacing original MODS with normalized MODS element...'
            lxmlMODS[0].getparent().replace(lxmlMODS[0], etree.fromstring(str_mods) )
#            print etree.tostring(lxmlNode, pretty_print=True)                 

        else: #This should never happen @runtime: record should have been validated up front...
            print 'NO MODS element found!'
            raise ValidateException(formatExceptionLine("Mandatory MODS metadata NOT found in DIDL record.", self._identifier))
        #4:
        print(etree.tostring(lxmlNode, pretty_print=True))
        return lxmlNode


    def _convertFullMods2GHMods(self, lxmlMODSNode):        
        returnxml = ''
        e_root = deepcopy(lxmlMODSNode) #TODO: Check We need a deepcopy; otherwise we'll modify the lxmlnode by reference!!
        #assert MODS:
        if self._nsMap['mods'] in e_root.nsmap.values(): #Check of MODS namspace is declared.
            #TODO: Check if version 3.5 was supplied: correct and log otherwise.
            #Assert version set to 3.5:
            e_root.set("version", "3.5")
            e_root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-5.xsd")
            
            for child in e_root.iterchildren():
                for eroot_name in allowed_mods_rootelem:
                    #print 'Allowed Element name:', ('{%s}'+eroot_name) % self._nsMap['mods']
                    if child.tag == ('{%s}'+eroot_name) % self._nsMap['mods']:
                        #call normalisation function on current child:
                        #Don't try this at home:-)
                        #eval("self._tl" + eroot_name.capitalize())(child)
                        returnChild = eval("self._tl" + eroot_name.capitalize())(child)
                        
                        if returnChild is None:
                            e_root.remove(child)
                        else:
                            child.getparent().replace(child, returnChild)
                        #child.getparent().replace(child, eval("self._tl" + eroot_name.capitalize())(child) )
                        break
                else: #Wordt alleen geskipped als ie uit 'break' komt...
                    e_root.remove(child)

            returnxml = etree.tostring(e_root, pretty_print=True, encoding=XML_ENCODING)
            return returnxml


    def _tlLanguage(self, childNode):
        print 'self._tlLanguage'
        #SSDC mandates iso639-1, SSMODS mandates iso639-1 or iso639-2 if iso639-1 is not available, but we'll settle for either 2 or 3 chars.
        rfc3066_lang = childNode.xpath("//mods:languageTerm[@type='code' and @authority='rfc3066']/text()", namespaces=self._nsMap)
        if rfc3066_lang and rfc3066_lang[0]:
            #See also: ftp://ftp.rfc-editor.org/in-notes/rfc3066.txt
            match = self._patternRFC3066.match(rfc3066_lang[0])
            if match and match.group(1).lower() in ISO639:
                #print 'match:', match.group(1).lower()
                e_tst = etree.SubElement(childNode, "tst")
                e_tst.text = match.group(1).lower()
        return childNode

    #TODO: implement logging and Error validation
    def _tlGenre(self, childNode):
        print 'self._tlGenre'
        qnGenre = None
        prefixus = len(INFO_EU_REPO_SEMANTICS)
        genre = childNode.xpath('//mods:genre/text()', namespaces=self._nsMap)
        if genre and genre[0]:
            if genre[0].strip().lower() in GENRES:
                qnGenre = INFO_EU_REPO_SEMANTICS+genre[0].strip()
            elif genre[0].strip().lower()[prefixus:] in GENRES:
                qnGenre = genre[0].strip()
            if qnGenre is not None:
                childNode.text = qnGenre
#        print(etree.tostring(childNode, pretty_print=True))
                return childNode
        return None
   
    def _getDateModifiedDescriptor(self, lxmlNode): #TODO: Refactor, method is same as DIDL (#4)...        
        #4: Check geldige datemodified (feitelijk verplicht, hoewel vaak niet geimplemeteerd...)
        modified = lxmlNode.xpath('self::didl:Item/didl:Descriptor/didl:Statement/dcterms:modified/text()', namespaces=self._nsMap)
        if modified and self._validateISO8601(modified[0]):
            #print "DIDL MODS Item modified:", modified[0]
            return descr_templ % ('<dcterms:modified>'+modified[0].strip()+'</dcterms:modified>')
        else:
            return ''     


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
