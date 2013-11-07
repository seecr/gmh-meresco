# -*- coding: utf-8 -*-
#from lxml.etree import parse, _ElementTree, tostring, XMLSchema, parse as lxmlParse
from lxml import etree
from lxml.etree import parse, XMLSchema, XMLSchemaParseError, _ElementTree, tostring
from xml.sax.saxutils import escape as escapeXml
from meresco.core import Observable
from copy import deepcopy
from StringIO import StringIO
from meresco.components.xml_generic.validate import ValidateException
from xml_validator import formatExceptionLine
from re import compile, IGNORECASE
from dateutil.parser import parse as parseDate
from datetime import *;
from normalize_nl_didl import XML_ENCODING

#Schema validatie:
from os.path import abspath, dirname, join

# This component handles ADD messages only.
# It will try to convert the supplied data (KNAWLong) from the 'metadata' part into KNAWshort. All other parts and data formats are ignored (blocked).
# If it fails in doing so, it will block (NOT pass) the ADD message.
# Returns: xml-string!


#Taken from: http://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt
ISO639 = ["aar", "abk", "ace", "ach", "ada", "ady", "afa", "afh", "afr", "ain", "aka", "akk", "alb", "ale", "alg", "alt", "amh", "ang", "anp", "apa", "ara", "arc", "arg", "arm", "arn", "arp", "art", "arw", "asm", "ast", "ath", "aus", "ava", "ave", "awa", "aym", "aze", "bad", "bai", "bak", "bal", "bam", "ban", "baq", "bas", "bat", "bej", "bel", "bem", "ben", "ber", "bho", "bih", "bik", "bin", "bis", "bla", "bnt", "bos", "bra", "bre", "btk", "bua", "bug", "bul", "bur", "byn", "cad", "cai", "car", "cat", "cau", "ceb", "cel", "cha", "chb", "che", "chg", "chi", "chk", "chm", "chn", "cho", "chp", "chr", "chu", "chv", "chy", "cmc", "cop", "cor", "cos", "cpe", "cpf", "cpp", "cre", "crh", "crp", "csb", "cus", "cze", "dak", "dan", "dar", "day", "del", "den", "dgr", "din", "div", "doi", "dra", "dsb", "dua", "dum", "dut", "dyu", "dzo", "efi", "egy", "eka", "elx", "eng", "enm", "epo", "est", "ewe", "ewo", "fan", "fao", "fat", "fij", "fil", "fin", "fiu", "fon", "fre", "frm", "fro", "frr", "frs", "fry", "ful", "fur", "gaa", "gay", "gba", "gem", "geo", "ger", "gez", "gil", "gla", "gle", "glg", "glv", "gmh", "goh", "gon", "gor", "got", "grb", "grc", "gre", "grn", "gsw", "guj", "gwi", "hai", "hat", "hau", "haw", "heb", "her", "hil", "him", "hin", "hit", "hmn", "hmo", "hrv", "hsb", "hun", "hup", "iba", "ibo", "ice", "ido", "iii", "ijo", "iku", "ile", "ilo", "ina", "inc", "ind", "ine", "inh", "ipk", "ira", "iro", "ita", "jav", "jbo", "jpn", "jpr", "jrb", "kaa", "kab", "kac", "kal", "kam", "kan", "kar", "kas", "kau", "kaw", "kaz", "kbd", "kha", "khi", "khm", "kho", "kik", "kin", "kir", "kmb", "kok", "kom", "kon", "kor", "kos", "kpe", "krc", "krl", "kro", "kru", "kua", "kum", "kur", "kut", "lad", "lah", "lam", "lao", "lat", "lav", "lez", "lim", "lin", "lit", "lol", "loz", "ltz", "lua", "lub", "lug", "lui", "lun", "luo", "lus", "mac", "mad", "mag", "mah", "mai", "mak", "mal", "man", "mao", "map", "mar", "mas", "may", "mdf", "mdr", "men", "mga", "mic", "min", "mis", "mkh", "mlg", "mlt", "mnc", "mni", "mno", "moh", "mon", "mos", "mul", "mun", "mus", "mwl", "mwr", "myn", "myv", "nah", "nai", "nap", "nau", "nav", "nbl", "nde", "ndo", "nds", "nep", "new", "nia", "nic", "niu", "nno", "nob", "nog", "non", "nor", "nqo", "nso", "nub", "nwc", "nya", "nym", "nyn", "nyo", "nzi", "oci", "oji", "ori", "orm", "osa", "oss", "ota", "oto", "paa", "pag", "pal", "pam", "pan", "pap", "pau", "peo", "per", "phi", "phn", "pli", "pol", "pon", "por", "pra", "pro", "pus", "que", "raj", "rap", "rar", "roa", "roh", "rom", "rum", "run", "rup", "rus", "sad", "sag", "sah", "sai", "sal", "sam", "san", "sas", "sat", "scn", "sco", "sel", "sem", "sga", "sgn", "shn", "sid", "sin", "sio", "sit", "sla", "slo", "slv", "sma", "sme", "smi", "smj", "smn", "smo", "sms", "sna", "snd", "snk", "sog", "som", "son", "sot", "spa", "srd", "srn", "srp", "srr", "ssa", "ssw", "suk", "sun", "sus", "sux", "swa", "swe", "syc", "syr", "tah", "tai", "tam", "tat", "tel", "tem", "ter", "tet", "tgk", "tgl", "tha", "tib", "tig", "tir", "tiv", "tkl", "tlh", "tli", "tmh", "tog", "ton", "tpi", "tsi", "tsn", "tso", "tuk", "tum", "tup", "tur", "tut", "tvl", "twi", "tyv", "udm", "uga", "uig", "ukr", "umb", "und", "urd", "uzb", "vai", "ven", "vie", "vol", "vot", "wak", "wal", "war", "was", "wel", "wen", "wln", "wol", "xal", "xho", "yao", "yap", "yid", "yor", "ypk", "zap", "zbl", "zen", "zha", "znd", "zul", "zun", "zxx", "zza", "bod", "ces", "cym", "deu", "ell", "eus", "fas", "fra", "hye", "isl", "kat", "mkd", "mri", "msa", "mya", "nld", "ron", "slk", "sqi", "zho", "aa", "ab", "ae", "af", "ak", "am", "an", "ar", "as", "av", "ay", "az", "ba", "be", "bg", "bh", "bi", "bm", "bn", "bo", "br", "bs", "ca", "ce", "ch", "co", "cr", "cs", "cu", "cv", "cy", "da", "de", "dv", "dz", "ee", "el", "en", "eo", "es", "et", "eu", "fa", "ff", "fi", "fj", "fo", "fr", "fy", "ga", "gd", "gl", "gn", "gu", "gv", "ha", "he", "hi", "ho", "hr", "ht", "hu", "hy", "hz", "ia", "id", "ie", "ig", "ii", "ik", "io", "is", "it", "iu", "ja", "jv", "ka", "kg", "ki", "kj", "kk", "kl", "km", "kn", "ko", "kr", "ks", "ku", "kv", "kw", "ky", "la", "lb","lg", "li", "ln", "lo", "lt", "lu", "lv", "mg", "mh", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "na", "nb", "nd", "ne", "ng", "nl", "nn", "no", "nr", "nv", "ny", "oc", "oj", "om", "or", "os", "pa", "pi", "pl", "ps", "pt", "qu", "rm", "rn", "ro", "ru", "rw", "sa", "sc", "sd", "se", "sg", "si", "sk", "sl", "sm", "sn", "so", "sq", "sr", "ss", "st", "su", "sv", "sw", "ta", "te", "tg", "th", "ti", "tk", "tl", "tn", "to", "tr", "ts", "tt", "tw", "ty", "ug", "uk", "ur", "uz", "ve", "vi", "vo", "wa", "wo", "xh", "yi", "yo", "za", "zh", "zu"]

GENRES = ['annotation','article','bachelorThesis','book','bookPart','bookReview','conferencePaper','contributionToPeriodical','doctoralThesis','researchProposal','lecture','masterThesis','patent','preprint','report','studentThesis','technicalDocumentation','workingPaper','conferenceObject','review','other', 'reportPart', 'conferenceProceedings','conferenceItem', 'conferenceItemNotInProceedings','conferencePoster','conferenceContribution']

INFO_EU_REPO_SEMANTICS = "info:eu-repo/semantics/"

MODS_VERSION = '3.4'

MARC_ROLES=['act','adp','aft','ann','ant','app','aqt','arc','arr','art','asg','asn','att','auc','aud','aui','aus','aut','bdd','bjd','bkd','bkp','bnd','bpd','bsl','ccp','chr','clb','cli','cll','clt','cmm','cmp','cmt','cnd','cns','coe','col','com','cos','cot','cpc','cpe','cph','cpl','cpt','cre','crp','crr','csl','csp','cst','ctb','cte','ctg','ctr','cts','ctt','cur','cwt','dfd','dfe','dft','dgg','dis','dln','dnc','dnr','dpt','drm','drt','dsr','dst','dte','dto','dub','edt','egr','elt','eng','etr','exp','fac','flm','fmo','fnd','frg','-gr','hnr','hst','ill','ilu','ins','inv','itr','ive','ivr','lbt','lee','lel','len','let','lie','lil','lit','lsa','lse','lso','ltg','lyr','mdc','mod','mon','mte','mus','nrt','opn','org','orm','oth','own','pat','pbd','pbl','pfr','pht','plt','pop','ppm','prc','prd','prf','prg','pro','prt','pta','pte','ptf','pth','ptt','rbr','rce','rcp','red','ren','res','rev','rse','rsp','rst','rth','rtm','sad','sce','scr','scl','sec','sgn','sng','spk','spn','srv','stn','str','ths','trc','trl','tyd','tyg','voc','wam','wdc','wde','wit']

##MODS root elements allwed by GH normalized:
#allowed_mods_rootelem = ["abstract", "classification", "extension", "genre", "identifier", "language", "location", "name", "originInfo", "physicalDescription", "relatedItem", "subject", "titleInfo", "typeOfResource"]


#mandatory = ['/mods:titleInfo/mods:title', '/mods:typeOfResource', '/mods:genre', '/mods:originInfo/dateIssued']


# Wellicht handiger om alle rootelementen met xPath te pakken: voordeel is dan dat je alle toplevel-elementen van 1 type tegelijk tot je beschikking hebt.
# i.p.v. iteratief, waarbij je nooit weet of er nog eenzelfde type element later voorbijkomt.

mods_edu_extentions_ns = {
    'gal': "info:eu-repo/grantAgreement",
    'dai': "info:eu-repo/dai",
    'hbo': "info:eu-repo/xmlns/hboMODSextension",
    'wmp': "http://www.surfgroepen.nl/werkgroepmetadataplus",
}
# , ('hbo/hboMODSextension.xsd', 'self::hbo:hbo')
mods_edu_extentions = [('dai/dai-extension.xsd', 'self::dai:daiList'), ('gal/gal-extension.xsd', 'self::gal:grantAgreementList'), ('wmp/wmp-extension.xsd', 'self::wmp:rights')]

# Do not list "extension", so it will be removed by default. <extension> is handeled by a different function. 
mods_edu_tlelements = ["relatedItem", "language", "titleInfo", "typeOfResource", "genre", "physicalDescription", "abstract", "location", "identifier", "classification", "subject", "originInfo"] #, "name", 


def isInt(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False


class Normalize_nl_MODS(Observable):
    """A class that normalizes MODS metadata to the Edustandaard applicationprofile"""
    
    def __init__(self, nsMap={}):
        Observable.__init__(self)
        
        #self._nsMap=nsMap        
        self._nsMap = mods_edu_extentions_ns.copy()
        self._nsMap.update(nsMap or {})
        
        self._bln_success = False
        # http://www.schemacentral.com/sc/xsd/t-xsd_language.html
        self._patternRFC3066 = compile('^([A-Za-z]{2,3})(-[a-zA-Z0-9]{1,8})?$')# Captures first 2 or 3 language chars if nothing else OR followed by '-' and 1 to 8 alfanum chars.
        self._patternURN = compile('^[uU][rR][nN]:[nN][bB][nN]:[nN][lL]:[uU][iI]:\d{1,3}-.*')
        self._patternURL = compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        #r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', IGNORECASE)
        
        self._edu_extension_schemas = []
        
#Fill the schemas list for later use:
        for schemaPath, xPad in mods_edu_extentions:
            print 'schema init:' ,schemaPath, xPad
            try:
                self._edu_extension_schemas.append((XMLSchema(parse(join(dirname(abspath(__file__)), 'xsd/'+ schemaPath) ) ), xPad))
            except XMLSchemaParseError, e:
                print 'XMLSchemaParseError.............', e.error_log.last_error
                raise
        
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
        #1: Get Mods from the lxmlNode:
        lxmlMODS = lxmlNode.xpath('(//mods:mods)[1]', namespaces=self._nsMap)
        
        #Our normalisation functions to call: TODO: complement the functions list.
        #self._chkMandatoryFields, 
        modsFunctions = [ self._convertFullMods2GHMods ]
        
        if len(lxmlMODS) > 0:
            print 'Found MODS, starting MODS normalization...'
        #2: Normalize it
            str_norm_mods = ''            
            for function in modsFunctions:
                str_norm_mods += function(lxmlMODS[0])            
            print "MODS Element normalization succeeded."
            
        #3: Put it back in place:        
            print 'Replacing original MODS with normalized MODS element...'
            lxmlMODS[0].getparent().replace(lxmlMODS[0], etree.fromstring(str_norm_mods) )
#            print etree.tostring(lxmlNode, pretty_print=True)                 

        else: #This should never happen @runtime: record should have been validated up front...
            print 'NO MODS element found!'
            raise ValidateException(formatExceptionLine("Mandatory MODS metadata NOT found in DIDL record.", self._identifier))

        #4: Return the lxmlNode containing the normalized MODS:
        #print(etree.tostring(lxmlNode, pretty_print=True))
        return lxmlNode

    def _chkMandatoryFields(self, lxmlNode):
        tor = lxmlNode.xpath('/mods:typeOfResource', namespaces=self._nsMap)
    

    def _convertFullMods2GHMods(self, lxmlMODSNode):
        returnxml = ''
        #TODO: Check if we need a deepcopy; otherwise we'll modify the lxmlnode by reference!!
        e_modsroot_copy = deepcopy(lxmlMODSNode) 
        
        #Check if version 3.4 was supplied: correct otherwise.
        self._normalizeModsVersion(e_modsroot_copy)
        
        # Valideer en normaliseer alle extension tags in 1 tag en bewaar deze voor later....
        e_extensions = self._getValidModsExtension(e_modsroot_copy)
        # LET OP: Alle <extension> tags worden hieronder verwijdert doordat _tlExtension() 'None' terug geeft.       
        
        # Valideer en normaliseer alle titleInfo tags:
        self._normTitleinfo(e_modsroot_copy)

        # Valideer en normaliseer alle <name> tags op e_modsrppt_copy...
        self._validateNames(e_modsroot_copy)
        # LET OP: Alle <name> tags worden hieronder verwijdert doordat _tlNames() 'None' terug geeft.
        
        # normaliseer alle Genre tags...       
        self._validateGenre(e_modsroot_copy)

        #TODO: Create logic to check for availability of all mandatory fields. 

        # Itereer over ALLE toplevel elementen:
        for child in e_modsroot_copy.iterchildren():
            
            for tlelement in mods_edu_tlelements: #Iterate over all top level elements...
                #print 'Allowed Element name:', ('{%s}'+tlelement) % self._nsMap['mods']
                if child.tag == ('{%s}'+tlelement) % self._nsMap['mods']: #TODO: refactor all templates like this...
                    #call normalisation function on current child:
                    returnChild = eval("self._tl" + tlelement.capitalize())(child)
                    
                    if returnChild is None:
                        e_modsroot_copy.remove(child)
                    else:
                        child.getparent().replace(child, returnChild)
                    break
            else: #Wordt alleen geskipped als ie uit 'break' komt...
                e_modsroot_copy.remove(child)
                
        # Append our <extension> element to root:
        if e_extensions is not None: e_modsroot_copy.append(e_extensions)
        
        # Append one typeOfResource to root:
        self._addTypeOfResource(e_modsroot_copy)
        
        returnxml = etree.tostring(e_modsroot_copy, pretty_print=True, encoding=XML_ENCODING)
        print returnxml
        return returnxml

    def _normalizeModsVersion(self, e_modsroot):
        version_orig = e_modsroot.get("version")
        if version_orig != MODS_VERSION:
            e_modsroot.set("version", MODS_VERSION)
            e_modsroot.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-"+ MODS_VERSION.replace(".", "-") +".xsd")
            print "Normalized MODS version from", version_orig, "to", MODS_VERSION
        return e_modsroot

    def _tlRelateditem(self, childNode):
        if not childNode.get('type') in ['preceding', 'succeeding', 'host', 'series', 'otherVersion']:
            return None
        #TODO: recursive check of allowed elements...
        return childNode


    #TODO check if all x-paths use proper axis (i.e: self::mods:element v.s //mods:element
    def _tlLanguage(self, childNode):
        #print 'self._tlLanguage'
        #SSDC mandates iso639-1, SSMODS mandates iso639-1 or iso639-2 if iso639-1 is not available, but we'll settle for either 2 or 3 chars.
        rfc3066_lang = childNode.xpath("self::mods:languageTerm[@type='code' and @authority='rfc3066']/text()", namespaces=self._nsMap)
        if len(rfc3066_lang) > 0:
            #See also: ftp://ftp.rfc-editor.org/in-notes/rfc3066.txt
            #match = self._patternRFC3066.match(rfc3066_lang[0])
            #if match and match.group(1).lower() in ISO639:
            if rfc3066_lang[0] in ISO639:
                return childNode
            self.do.logMsg(self._identifier, rfc3066_lang[0] + ' is not a valid languageTerm.')
            return None
        else:
            self.do.logMsg(self._identifier, 'No rfc3066 language code found.')
            return None


    def _tlOrigininfo(self, childNode):
        hasDateIssued = False
        # Select all children from originInfo having 'encoding' attribute:
        children = childNode.xpath("self::mods:originInfo/child::*[@encoding='w3cdtf' or @encoding='iso8601']", namespaces=self._nsMap)
        if len(children) > 0:
            for child in children:
                if self._validateISO8601( child.text ):
                    di = parseDate(child.text, ignoretz=True, fuzzy=True, default=datetime(1900, 12, 28, 0, 0)) #1900-12-28 default year, month and day. (day 28 exists for every month:-)
                    child.text = str(di.date())
                    child.set('encoding', 'w3cdtf')
                    if child.tag == ('{%s}dateIssued') % self._nsMap['mods']: hasDateIssued = True
                    #TODO: Check format, return only year if only year was given, etc.
                else:
                    child.getparent().remove(child)
        if not hasDateIssued: #TODO: Raise error if, and only if no dateIssed child is present in the complete document, instead of one originInfo tag...
            raise ValidateException(formatExceptionLine("Missing mandatory valid element originInfo/dateIssued", self._identifier))
            
        return childNode if len(childNode) > 0 else None


    def _validateISO8601(self, datestring):
        #http://labix.org/python-dateutil
        try:
            parseDate(datestring, ignoretz=True, fuzzy=True)
        except ValueError:
            return False
        return True
    
    def _validateGenre(self, modsNode):
    
        fqGenre = None
        bln_hasValid = False
        
        #select all 'genre' elements as separate nodes:
        for genre in modsNode.iterfind('{'+self._nsMap.get('mods')+'}genre'):
            print 'GENRE iterfind', genre.text            
            # Check for valid Genre
            prefixus = (genre.text.strip().rfind("/") + 1) if (genre.text.strip().rfind("/") > -1) else len(INFO_EU_REPO_SEMANTICS)
            for i, value in enumerate(GENRES):
                if genre.text.strip()[prefixus:]  == value:
                    if genre.text.strip().startswith(INFO_EU_REPO_SEMANTICS):
                        fqGenre = genre.text.strip() #Perfect Match, do nothing...
                    else:
                        fqGenre = INFO_EU_REPO_SEMANTICS+GENRES[i]
                        print "Normalized genre:", genre.text.strip(), "to", fqGenre
                    break
                elif genre.text.strip().lower() == value.lower() or genre.text.strip().lower()[prefixus:]  == value.lower():
                    fqGenre = INFO_EU_REPO_SEMANTICS+GENRES[i]
                    print "Normalized genre:", genre.text.strip(), "to", fqGenre
                    break
            if fqGenre is not None and not bln_hasValid:
                bln_hasValid = True
                genre.text = fqGenre
                print 'Found valid Genre:', fqGenre
            else:
                print 'removing superfluous OR inValid genre', genre.text
                modsNode.remove(genre)
        if not bln_hasValid:
            print 'Raise error: No valid genre was found... '          

    def _tlGenre(self, childNode):
        return childNode # Genres have been normalised already by _validateGenre()

    def _tlLocation(self, childNode):
        for url in childNode.iterfind('{'+self._nsMap.get('mods')+'}url'):
            if not self._isURL(url.text): childNode.remove(url)
        return childNode if len(childNode) > 0 else None


    def _tlAbstract(self, childNode):
        # Pass thru all abstract nodes: xml-schema validation of MODS has already taken place...
        #if (childNode.attrib.has_key('{http://www.w3.org/XML/1998/namespace}lang') and childNode.get('{http://www.w3.org/XML/1998/namespace}lang').lower() in ISO639 ):
        #    return childNode
        #if childNode.attrib.has_key('{http://www.w3.org/XML/1998/namespace}lang'): # No IsoLanguage: remove xml:lang tag...
        #    del childNode.attrib['{http://www.w3.org/XML/1998/namespace}lang']
        return childNode


    def _tlPhysicaldescription(self, childNode): #Extent check, skip otherwise...
        pages = childNode.xpath('//mods:extent/text()', namespaces=self._nsMap)
        if len(pages) <= 0:
            return childNode
        elif not isInt(pages[0]):
            self.do.logMsg(self._identifier, pages[0] + ' does not represent an Integer.')
            return None
        return childNode
        

    def _tlTitleinfo(self, childNode):
        #print 'TitleInfo', etree.tostring(childNode, pretty_print=True)
        title = childNode.xpath('self::mods:titleInfo/mods:title/text()', namespaces=self._nsMap)
        
        if len(title) == 0:
            print "Empty title string, or no title at all..."
            raise ValidateException(formatExceptionLine("Missing mandatory title element...", self._identifier))
        
        sub = childNode.xpath('self::mods:titleInfo/mods:subTitle/text()', namespaces=self._nsMap)
        if len(sub) > 0 and not title[0]:
            print "Empty title string..."
            raise ValidateException(formatExceptionLine("", self._identifier))        
        return childNode


    def _tlTypeofresource(self, childNode):
        return None # Beware, all elements are removed from the document!

    def _tlIdentifier(self, childNode):
        if len(childNode.attrib) == 0 or childNode.text is None:
            return None
        return childNode #transfer 'as is'.
        
    def _tlClassification(self, childNode):
        if not childNode.attrib.has_key('authority') or childNode.text is None:
            return None
        return childNode #transfer 'as is'.

    def _tlSubject(self, childNode):
        if not childNode.attrib.has_key('authority') or len(childNode.xpath('mods:topic', namespaces=self._nsMap)) < 1:
            return None      
        return childNode #transfer 'as is'.


#TODO: alle xpaden checken vanaf mods root: /mods/tlelement
    def _addTypeOfResource(self, modsNode):
        #Check if element exists:
        #if len(modsNode.xpath('//mods:mods/mods:typeOfResource', namespaces=self._nsMap)) == 0:
        tor = etree.SubElement(modsNode, "typeOfResource")
        tor.text = 'text'

    def _getValidModsExtension(self, modsNode):
        #select all 'extension' child elements as separate nodes:
        extensions = modsNode.xpath('//mods:extension/child::*', namespaces=self._nsMap)        
        e_rootExten = etree.Element("extension")
        for extension in extensions:
            if self._isValidEduStandaardExtension(extension):
                e_ext = etree.SubElement(e_rootExten, "extension") #Create extension sub-element. 
                e_ext.append(extension)
                e_rootExten.append(e_ext)
        return e_rootExten if len(e_rootExten) > 0 else None


    def _tlName(self, childNode):
        return childNode

    def _validateNames(self, modsNode): #TODO: check op minimaal 1 name element. TODO: check if it selects name elements in relatedItem as well...
        #select all 'name' elements as separate nodes:
        for name in modsNode.iterfind('{'+self._nsMap.get('mods')+'}name'):
            role = name.xpath("self::mods:name/mods:role/mods:roleTerm[@type='code' and @authority='marcrelator']/text()", namespaces=self._nsMap)            
            if not role: #Geen roleterm gevonden, of lege string voor type code en authority marcrelator of wel gevonden maar niet geldig: Verwijder dit name element:
                modsNode.remove(name)
            elif len(role) > 0 and not self.__isValidRoleTerm(role[0]):
                raise ValidateException(formatExceptionLine("Invalid marcrelator role: " + role[0], self._identifier))


    def __isValidRoleTerm(self, str_roleTerm):
        return True if str_roleTerm in MARC_ROLES else False
     

    def _normTitleinfo(self, modsNode):
        #select all extensions available as separate nodes:
        for child in modsNode.iterfind('{'+self._nsMap.get('mods')+'}titleInfo'): #findall
            #print "TITLEINFO:", etree.tostring(child, pretty_print=True, encoding=XML_ENCODING)
            if not self._isValidEduStandaardTitleInfoTag(child):
                modsNode.remove(child)
            #else:
                #modsNode.replace(child, returnChild)

    def _isValidEduStandaardTitleInfoTag(self, lxmlNode):
        #correct @type:
        if lxmlNode.get('type') != 'translated':
            if lxmlNode.attrib.has_key('type'):
                del lxmlNode.attrib['type']
        #throw Exception if no or empty title tag:
        for title in lxmlNode.iterfind('{'+self._nsMap.get('mods')+'}title'):
            if not title.text:
                print "No Text found"
        return True

    def _tlExtension(self, childNode):
        #BEWARE: All <extension> tags will be removed, when returning None!
        return None


    #TODO: ERROR logging + find out why HBO.xsd (lxml) doesnt validate, but Oxygen (Xerces) does?!?
    def _isValidEduStandaardExtension(self, lxmlNode):
        for schema, xpad in self._edu_extension_schemas:
            extent = lxmlNode.xpath(xpad, namespaces=self._nsMap)
            if len(extent) > 0: #validate found EduStandaard extension: this is not done by mods validation:
                schema.validate(lxmlNode)
                if schema.error_log:
                    print 'SchemaValidationError EduStandaard extension IS NOT VALID:', schema.error_log.last_error
                    return False
                else:
                    print "EduStandaard extension IS VALID", lxmlNode.tag 
                    return True
        #Looped over all allowed Edustandaard extensions types: None was found...
        self.do.logMsg(self._identifier, 'Extension not recognized as EDUstandaard...')
        return False
   
   
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

    def _isURL(self, string):
        bln_isValid = False
        m = self._patternURL.match(string)
        if m:
            bln_isValid = True
        return bln_isValid

    def __str__(self):
        return 'Normalize_nl_MODS'
