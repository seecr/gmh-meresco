# -*- coding: utf-8 -*-
from meresco.core import Observable
from datetime import datetime

from time import gmtime, strftime
from xml.sax.saxutils import escape as xmlEscape
from os.path import join, isdir, isfile, basename, abspath, getsize
from os import rename, listdir, remove, makedirs, link
import mmap
from escaping import escapeFilename, unescapeFilename


RSS_TEMPLATE = """<item>
    <description>%(description)s</description>
    <guid>%(oai_id)s</guid>
    <pubDate>%(date)s</pubDate>
</item>"""

#http://ip048.niwi.knaw.nl:4480/?verb=GetRecord&identifier=PRS1250477

class Logger(Observable):

    def __init__(self, logfileDir, enabled=True, prefix=''):
        Observable.__init__(self)
        self._enabled = enabled
        self._msg_prefix = prefix #'[%s]'%(prefix)
        self._logfileDir = logfileDir
        print "logfileDir:" ,self._logfileDir 
        if not isdir(self._logfileDir):
            makedirs(self._logfileDir)


    def logMsg(self, identifier, logmsg):
        if self._enabled:
            #print "RECEIVED:", identifier, (self._msg_prefix + logmsg)
            with open(join(self._logfileDir, escapeFilename(identifier.split(':', 1 )[0])), "a") as logFile:
                try:
                    logFile.write(str(strftime("%Y%m%dT%H:%M:%SZ", gmtime())) + " " + identifier + " " + self._msg_prefix+logmsg + "\n")
                    logFile.flush()
                finally:                    
                    logFile.close()
                                                        
    def getLogLinesAsRssItems(self, rId, maxlines):
        """Geeft RSS <item> representatie van loglines terug"""
        buffer = ''
        lines = self._tail(rId, maxlines)
        if lines:
            for line in reversed(lines):
                #print "LINE: ", line
                lineparts = line.split(' ', 2)
                rssData = {
                'description': xmlEscape( lineparts[2] ),
                'oai_id': xmlEscape( lineparts[1] ),
                'date': xmlEscape( lineparts[0] )
                }
                buffer += str(RSS_TEMPLATE % rssData)
            
        return buffer
            #https://github.com/seecr/meresco-components/blob/master/meresco/components/rss.py

    def _tail(self, rgId, n):
        """Returns last n lines from the filename. No exception handling.
        http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
        """
        if isfile(join(self._logfileDir, rgId)):
            size = getsize(join(self._logfileDir, rgId))
            with open(join(self._logfileDir, rgId), "rb") as f:
                # for Windows the mmap parameters are different
                fm = mmap.mmap(f.fileno(), 0, mmap.MAP_SHARED, mmap.PROT_READ)
                try:
                    for i in xrange(size - 1, -1, -1):
                        if fm[i] == '\n':
                            n -= 1
                            if n == -1:
                                break
                    return fm[i + 1 if i else 0:].splitlines()
                except (OSError, IOError):
                    return[]
                finally:
                    fm.close()
        else:
            return[]    