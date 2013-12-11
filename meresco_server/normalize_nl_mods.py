# -*- coding: utf-8 -*-

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
STR_MODS = "MODS:"

MARC_ROLES=['act','adp','aft','ann','ant','app','aqt','arc','arr','art','asg','asn','att','auc','aud','aui','aus','aut','bdd','bjd','bkd','bkp','bnd','bpd','bsl','ccp','chr','clb','cli','cll','clt','cmm','cmp','cmt','cnd','cns','coe','col','com','cos','cot','cpc','cpe','cph','cpl','cpt','cre','crp','crr','csl','csp','cst','ctb','cte','ctg','ctr','cts','ctt','cur','cwt','dfd','dfe','dft','dgg','dis','dln','dnc','dnr','dpt','drm','drt','dsr','dst','dte','dto','dub','edt','egr','elt','eng','etr','exp','fac','flm','fmo','fnd','frg','-gr','hnr','hst','ill','ilu','ins','inv','itr','ive','ivr','lbt','lee','lel','len','let','lie','lil','lit','lsa','lse','lso','ltg','lyr','mdc','mod','mon','mte','mus','nrt','opn','org','orm','oth','own','pat','pbd','pbl','pfr','pht','plt','pop','ppm','prc','prd','prf','prg','pro','prt','pta','pte','ptf','pth','ptt','rbr','rce','rcp','red','ren','res','rev','rse','rsp','rst','rth','rtm','sad','sce','scr','scl','sec','sgn','sng','spk','spn','srv','stn','str','ths','trc','trl','tyd','tyg','voc','wam','wdc','wde','wit']

##MODS root elements:

#abstract
#accessCondition
#classification
#extension
#genre
#identifier
#language
#location
#name
#note
#originInfo
#part
#physicalDescription
#recordInfo
#relatedItem
#subject
#tableOfContents
#targetAudience
#titleInfo
#typeOfResource

mods_edu_extentions_ns = {
    'gal': "info:eu-repo/grantAgreement",
    'dai': "info:eu-repo/dai",
    'hbo': "info:eu-repo/xmlns/hboMODSextension",
    'wmp': "http://www.surfgroepen.nl/werkgroepmetadataplus",
}

# , ('hbo/hboMODSextension.xsd', 'self::hbo:hbo')
mods_edu_extentions = [('dai/dai-extension.xsd', 'self::dai:daiList'), ('gal/gal-extension.xsd', 'self::gal:grantAgreementList'), ('wmp/wmp-extension.xsd', 'self::wmp:rights')]

## Do not list "extension" here. So it will be removed by default. <extension> is handeled by a different function. 
mods_edu_tlelements = ["titleInfo", "relatedItem", "name", "language", "typeOfResource", "genre", "physicalDescription", "abstract", "location", "identifier", "classification", "subject", "originInfo"]


class Normalize_nl_MODS(Observable):
    """A class that normalizes MODS metadata to the Edustandaard applicationprofile"""
    
    def __init__(self, nsMap={}):
        Observable.__init__(self)
             
        self._nsMap = mods_edu_extentions_ns.copy()
        self._nsMap.update(nsMap or {})        
        self._bln_success = False
        
        self._patternURN = compile('^[uU][rR][nN]:[nN][bB][nN]:[nN][lL]:[uU][iI]:\d{1,3}-.*')
        self._patternURL = compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        #r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', IGNORECASE)
        
        self._edu_extension_schemas = []
        
        ## Fill the schemas list for later use:
        for schemaPath, xPad in mods_edu_extentions:
            print 'schema init:' ,schemaPath, xPad
            try:
                self._edu_extension_schemas.append((XMLSchema(parse(join(dirname(abspath(__file__)), 'xsd/'+ schemaPath) ) ), xPad))
            except XMLSchemaParseError, e:
                print 'XMLSchemaParseError.', e.error_log.last_error
                raise
        
    def _detectAndConvert(self, anObject):
        if type(anObject) == _ElementTree:
            return self.convert(anObject)
        return anObject

    def convert(self, lxmlNode):
        self._bln_success = False
        self._bln_hasTypOfResource = False
        result_tree = self._normalizeRecord(lxmlNode)
        if result_tree != None:
            self._bln_success = True            
        return result_tree

    def all_unknown(self, method, *args, **kwargs):
        self._identifier = kwargs.get('identifier')        
        
        newArgs = [self._detectAndConvert(arg) for arg in args]     
        newKwargs = dict((key, self._detectAndConvert(value)) for key, value in kwargs.items())
        if self._bln_success:
            yield self.all.unknown(method, *newArgs, **newKwargs)

    def _normalizeRecord(self, lxmlNode):
        
        # MODS normalisation in 4 steps:
        # 1. Get Mods from the lxmlNode.
        # 2. Normalize it
        # 3. Put it back in place.
        # 4. return the lxmlNode containing the normalized MODS.
        
        #1: Get Mods from the lxmlNode:
        lxmlMODS = lxmlNode.xpath('(//mods:mods)[1]', namespaces=self._nsMap)
        
        ## Our normalisation functions to call:
        modsFunctions = [ self._convertFullMods2GHMods ]
        
        if len(lxmlMODS) > 0:
            #print 'Found MODS, starting MODS normalization...'
        #2: Normalize it
            str_norm_mods = ''            
            for function in modsFunctions:
                str_norm_mods += function(lxmlMODS[0])            
            #print "MODS Element normalization succeeded."
            
        #3: Put it back in place:        
            lxmlMODS[0].getparent().replace(lxmlMODS[0], etree.fromstring(str_norm_mods) )
            #print "BACK IN DIDL:", etree.tostring(lxmlNode, pretty_print=True)                 

        else: #This should never happen @runtime: record should have been validated up front...
            raise ValidateException(formatExceptionLine("Mandatory MODS metadata NOT found in DIDL record.", prefix=STR_MODS))

        #4: Return the lxmlNode containing the normalized MODS:
        #print(etree.tostring(lxmlNode, pretty_print=True))
        return lxmlNode


    def _convertFullMods2GHMods(self, lxmlMODSNode):
        returnxml = ''
        ## We need a deepcopy, otherwise we'll modify the lxmlnode by reference!!
        e_modsroot_copy = deepcopy(lxmlMODSNode)
        
        ## Check if version 3.4 was supplied: correct otherwise.
        self._normalizeModsVersion(e_modsroot_copy)
        
        ## Valideer en normaliseer alle extension tags in 1 tag en bewaar deze voor later....
        e_extensions = self._getValidModsExtension(e_modsroot_copy)
        ## LET OP: Alle <extension> tags worden hieronder verwijdert doordat _tlExtension() 'None' terug geeft.       
        
        ## Valideer en normaliseer alle titleInfo tags:
        self._normalizeTitleinfo(e_modsroot_copy)

        ## Valideer en normaliseer alle <name> tags op e_modsrppt_copy...
        self._validateNames(e_modsroot_copy)
        ## LET OP: Alle <name> tags worden hieronder verwijderd doordat _tlNames() 'None' terug geeft.
        
        #N Normaliseer alle Genre tags...       
        self._validateGenre(e_modsroot_copy)

        ## Itereer over ALLE toplevel elementen:
        for child in e_modsroot_copy.iterchildren():
            
            for tlelement in mods_edu_tlelements: ## Iterate over all top level elements...
                if child.tag == ('{%s}'+tlelement) % self._nsMap['mods']:
                    ## Call normalisation function on current child:
                    returnChild = eval("self._tl" + tlelement.capitalize())(child)
                    
                    if returnChild is None:
                        e_modsroot_copy.remove(child)
                    else:
                        child.getparent().replace(child, returnChild)
                    break
            else: #Wordt alleen geskipped als ie uit 'break' komt...
                e_modsroot_copy.remove(child)
                
        ## Append our <extension> child elements to the root:
        if e_extensions is not None:
            for child in e_extensions.iterfind(('{%s}extension') % self._nsMap['mods']):
                e_modsroot_copy.append(child)
        
        ## Append one typeOfResource to root, if it does not exist:
        if not self._bln_hasTypOfResource:
            self._addTypeOfResource(e_modsroot_copy)
        
        ## We'll add the MODS node to a new custom element and remove it again, so that lxml will use the mods prefix used in the namespacemap.
        ## Otherwise default namespaces may be used for MODS...
        root = etree.Element('{'+self._nsMap['mods']+'}temp', nsmap=self._nsMap)
        root.append(e_modsroot_copy)       
                
        ## Some namespaces may not be in use anymore after normalisation: remove them...
        etree.cleanup_namespaces(root)
        
        returnxml = tostring(root.find( ('{%s}mods') % self._nsMap['mods'] ) , pretty_print=True, encoding=XML_ENCODING)
        #returnxml = etree.tostring(e_modsroot_copy, pretty_print=True, encoding=XML_ENCODING)
        
        return returnxml

## mods version:
    def _normalizeModsVersion(self, e_modsroot):
        version_orig = e_modsroot.get("version")
        if version_orig != MODS_VERSION:
            e_modsroot.set("version", MODS_VERSION)
            e_modsroot.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-"+ MODS_VERSION.replace(".", "-") +".xsd")
            #print "Normalized MODS version from", version_orig, "to", MODS_VERSION
        return e_modsroot

## titleInfo:
    def _normalizeTitleinfo(self, modsNode):
        ## Select all titleInfo's
        hasTitleInfo = False
        for child in modsNode.iterfind(('{%s}titleInfo') % self._nsMap['mods']):
            hasTitleInfo = True 
            if not self._isValidTitleInfoTag(child):
                modsNode.remove(child)
        if not hasTitleInfo:
            raise ValidateException(formatExceptionLine("Mandatory titleInfo not found.", prefix=STR_MODS))

    def _isValidTitleInfoTag(self, lxmlNode):
        #Correct @type:
        #if lxmlNode.get('type') != 'translated':
        #    if lxmlNode.attrib.has_key('type'):
        #        del lxmlNode.attrib['type'] # Remove 'type' attribute if value other than 'translated'...
        #Throw Exception if no or empty title tag:
        for title in lxmlNode.iterfind(('{%s}title') % self._nsMap['mods']):
            if not title.text:
                raise ValidateException(formatExceptionLine("titleInfo/title has empty text-node.", prefix=STR_MODS))
        return True

    def _tlTitleinfo(self, childNode):
        ## Pass thru all (normalized) titleInfo nodes...
        return childNode

## Name:
    def _validateNames(self, modsNode): 
        for name in modsNode.iterfind(('{%s}name') % self._nsMap['mods']):
            role = name.xpath("self::mods:name/mods:role/mods:roleTerm[@type='code' and @authority='marcrelator']/text()", namespaces=self._nsMap)
            if not role or len(role) < 1: ## Geen roleterm gevonden, of lege string voor type code en authority marcrelator: Verwijder dit name element:
                modsNode.remove(name)
            elif len(role) > 0 and not self.__isValidRoleTerm(role[0]):
                raise ValidateException(formatExceptionLine("Invalid marcrelator role: " + role[0], prefix=STR_MODS))        
        if len(modsNode.xpath("//mods:mods/mods:name", namespaces=self._nsMap)) <= 0:
            raise ValidateException(formatExceptionLine("Mandatory name element not found! ", prefix=STR_MODS))

    def __isValidRoleTerm(self, str_roleTerm):
        return True if str_roleTerm.strip() in MARC_ROLES else False
        
    def _tlName(self, childNode):
        ## Pass thru all (normalized) name nodes...
        return childNode

## Language:
    def _tlLanguage(self, childNode):
        ## SSDC mandates iso639-1, SSMODS mandates iso639-1 or iso639-2 if iso639-1 is not available, but we'll settle for either 2 or 3 chars.
        rfc3066_lang = childNode.xpath("self::mods:language/mods:languageTerm[@type='code' and @authority='rfc3066']/text()", namespaces=self._nsMap)
        txt_lang = childNode.xpath("self::mods:language/mods:languageTerm[@type='text']/text()", namespaces=self._nsMap)
        if len(rfc3066_lang) > 0:
            #See also: ftp://ftp.rfc-editor.org/in-notes/rfc3066.txt
            #match = self._patternRFC3066.match(rfc3066_lang[0])
            #if match and match.group(1).lower() in ISO639:
            if rfc3066_lang[0].strip() in ISO639:
                return childNode
            self.do.logMsg(self._identifier, rfc3066_lang[0] + ' is not a valid RFC3066 language code.', prefix=STR_MODS)
            return None
        elif len(txt_lang) > 0:
            return childNode
        else:
            return None

## Genre:
    def _validateGenre(self, modsNode):
    
        fqGenre = None
        bln_hasValid = False        
        ## Select all 'genre' elements as separate nodes:
        for genre in modsNode.iterfind('{'+self._nsMap.get('mods')+'}genre'):      
            ## Check for valid Genre
            prefixus = (genre.text.strip().rfind("/") + 1) if (genre.text.strip().rfind("/") > -1) else len(INFO_EU_REPO_SEMANTICS)
            for i, value in enumerate(GENRES):
                if genre.text.strip()[prefixus:]  == value:
                    if genre.text.strip().startswith(INFO_EU_REPO_SEMANTICS):
                        fqGenre = genre.text.strip() #Perfect Match, do nothing...
                    else:
                        fqGenre = INFO_EU_REPO_SEMANTICS+GENRES[i]
                    break
                elif genre.text.strip().lower() == value.lower() or genre.text.strip().lower()[prefixus:]  == value.lower():
                    fqGenre = INFO_EU_REPO_SEMANTICS+GENRES[i]
                    break
            if fqGenre is not None and not bln_hasValid:
                bln_hasValid = True
                genre.text = fqGenre
            else:
                modsNode.remove(genre)
        if not bln_hasValid:
            print 'Raise error: No valid genre was found... '
            raise ValidateException(formatExceptionLine("No valid genre found!", prefix=STR_MODS))

    def _tlGenre(self, childNode):
        return childNode ## Genres have been normalised already by _validateGenre()

## OriginInfo:
    def _tlOrigininfo(self, childNode):
        hasDateIssued = False
        ## Select all children from originInfo having 'encoding' attribute:
        children = childNode.xpath("self::mods:originInfo/child::*[@encoding='w3cdtf' or @encoding='iso8601']", namespaces=self._nsMap)
        if len(children) > 0:
            for child in children:
                if self._validateISO8601( child.text ):                    
                    child.text = self._granulateDate(child.text)
                    child.set('encoding', 'w3cdtf')
                    if child.tag == ('{%s}dateIssued') % self._nsMap['mods']: hasDateIssued = True
                else:
                    child.getparent().remove(child)
        if not hasDateIssued:
            raise ValidateException(formatExceptionLine("Missing mandatory valid originInfo/dateIssued element.", prefix=STR_MODS))
        return childNode if len(childNode) > 0 else None


    def _validateISO8601(self, datestring):
        ## See: http://labix.org/python-dateutil
        try:
            parseDate(datestring, ignoretz=True, fuzzy=True)
        except ValueError:
            return False
        return True
        
        
    def _granulateDate(self, str_date):
        """returns only date parts that are succesfully parsed."""
        di_1 = parseDate(str_date, ignoretz=True, fuzzy=True, default=datetime(1900, 12, 28, 0, 0)) #1900-12-28 default year, month and day. (day 28 exists for every month:-)
        di_2 = parseDate(str_date, ignoretz=True, fuzzy=True, default=datetime(2000, 01, 01, 0, 0)) #2000-01-01 default year, month and day.
        
        ## Parsed date with no defaults used:
        if str(di_1.date()) == str(di_2.date()):
            return str(di_1.date()) # Dates are the same: date is parsed completely.
        
        ## Check for dft day and month:
        if di_1.date().day != di_2.date().day and di_1.date().month != di_2.date().month:
            return str(di_1.date().year) # Only year has been parsed succesfully.
        if di_1.date().day != di_2.date().day and di_1.date().month == di_2.date().month:
            return ('%s-%s') % (di_1.date().year, di_1.date().month) # Only year and month have been parsed succesfully.

## Location:
    def _tlLocation(self, childNode):
        for url in childNode.iterfind(('{%s}url') % self._nsMap['mods']):
            if not self._isURL(url.text): childNode.remove(url)
        return childNode if len(childNode) > 0 else None

## Abstract:
    def _tlAbstract(self, childNode):
        ## Pass thru all abstract nodes: xml-schema validation of MODS has already taken place...
        return childNode


## PhysicalDescription:
    def _tlPhysicaldescription(self, childNode): #Extent check, skip otherwise...
        pages = childNode.xpath('self::mods:physicalDescription/mods:extent/text()', namespaces=self._nsMap)
        if len(pages) <= 0:
            return childNode
        elif not pages[0].strip():
            return None
        return childNode

## RelatedItem:
    def _tlRelateditem(self, childNode):
        #1: Remove all non-Edustandaard 'types':
        if not childNode.get('type').strip() in ['preceding', 'host', 'succeeding', 'series', 'otherVersion']:
            return None
        
        #2: Check if <start>, <end> and <total> tags are integers:
        children = childNode.xpath("self::mods:relatedItem/mods:part/mods:extent[@unit='page']/child::*", namespaces=self._nsMap)
        if len(children) > 0:
            for child in children: # <start>, <end>, <total> tags...
                if child.tag in [('{%s}start') % self._nsMap['mods'], ('{%s}end') % self._nsMap['mods'], ('{%s}total') % self._nsMap['mods']] and not self._isInt(child.text):
                    ouder = child.getparent()
                    ouder.remove(child)
                    if len(ouder) == 0:
                        ouder.getparent().remove(ouder)                    
        
        
        #3: Normalize <part><date encoding=""> tag:
        children = childNode.xpath("self::mods:relatedItem/mods:part/mods:date", namespaces=self._nsMap)
        # print "RELATED DATE:", len(children)
        if len(children) > 0:
            for child in children:
                if self._validateISO8601( child.text ):                    
                    child.text = self._granulateDate(child.text)
                    child.set('encoding', 'w3cdtf')
                    #if child.tag == ('{%s}dateIssued') % self._nsMap['mods']: hasDateIssued = True
                else:
                    child.getparent().remove(child)
        
        return childNode if len(childNode) > 0 else None

## Part (relatedItem):
    def _isValidPart(self, partNode):
        return False


## TypeOfResource:
    def _tlTypeofresource(self, childNode):
        terug = childNode if not self._bln_hasTypOfResource else None
        self._bln_hasTypOfResource = True
        return terug

    def _addTypeOfResource(self, modsNode):
        ## Adds exactly one typeOfResource element to the mods node.
        tor = etree.SubElement(modsNode, ('{%s}typeOfResource') % self._nsMap['mods'])
        tor.text = 'text'

## Identifier:
    def _tlIdentifier(self, childNode):
        if len(childNode.attrib) == 0 or childNode.text is None:
            return None
        return childNode ## Transfer 'as is'.

## Classification:        
    def _tlClassification(self, childNode):
        if not (childNode.attrib.has_key('authority') or childNode.attrib.has_key('authorityURI') ) or childNode.text is None:
            return None
        return childNode ## Transfer 'as is'.

## Subject:
    def _tlSubject(self, childNode):
        if len(childNode.xpath('mods:topic', namespaces=self._nsMap)) < 1:
            return None      
        return childNode ## Transfer 'as is'.

## Extension:
    def _tlExtension(self, childNode):
        ## All <extension> tags will be removed, when returning None!
        return None

    def _getValidModsExtension(self, modsNode):
        ## Select all 'extension' child elements as separate nodes:        
        extensions = modsNode.xpath('self::mods:mods/mods:extension/child::*', namespaces=self._nsMap)
        e_rootExten = etree.Element(('{%s}extension') % self._nsMap['mods'])
        for extension in extensions:
            if self._isValidEduStandaardExtension(extension):
                e_ext = etree.SubElement(e_rootExten, ('{%s}extension') % self._nsMap['mods']) #Create extension sub-element. 
                e_ext.append(extension)
                e_rootExten.append(e_ext)
        return e_rootExten if len(e_rootExten) > 0 else None

    #TODO: Find out why HBO.xsd (lxml) doesnt validate, but Oxygen (Xerces) does?!?
    def _isValidEduStandaardExtension(self, lxmlNode):
        for schema, xpad in self._edu_extension_schemas:
            extent = lxmlNode.xpath(xpad, namespaces=self._nsMap)
            if len(extent) > 0: ## Validate found EduStandaard extension:
                schema.validate(lxmlNode)
                if schema.error_log:
                    #print 'SchemaValidationError EduStandaard extension IS NOT VALID:', schema.error_log.last_error
                    return False
                else:
                    #print "EduStandaard extension IS VALID", lxmlNode.tag 
                    return True
        ## Looped over all allowed Edustandaard extensions types: None was found...
        self.do.logMsg(self._identifier, 'No Extension recognized as EDUstandaard...', prefix=STR_MODS)
        return False

   
## Helper methods:   
    def _checkURNFormat(self, pid):
        m = self._patternURN.match(pid)
        if not m:
            raise ValidateException(formatExceptionLine("Invalid format for mandatory persistent identifier (urn:nbn) in top level Item: " + pid, prefix=STR_MODS))
        return True     

    def _isInt(self, s):
        if s is None:
            return False
        try: 
            int(s)            
        except ValueError:
            return False
        return True

    def _isURL(self, string):
        bln_isValid = False
        m = self._patternURL.match(string)
        if m:
            bln_isValid = True
        return bln_isValid

    def __str__(self):
        return 'Normalize_nl_MODS'
