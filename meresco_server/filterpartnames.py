# -*- coding: utf-8 -*-
from meresco.core import Observable

#TODO: partName may be present in **kwargs. But we don't know its keys? i.o.w. how can we perform a partname check?
class FilterPartNames(Observable):
    def __init__(self, allowed=[], disallowed=[]):
        Observable.__init__(self)
        assert len(allowed) == 0 or len(disallowed) == 0, 'Use disallowed or allowed'
        if allowed:
            self._allowedPartName = lambda partname: partname in allowed
        else:
            self._allowedPartName = lambda partname: partname not in disallowed

    def all_unknown(self, message, *args, **kwargs): #, **kwargs
        #add: ( 'knaw_mir:oai:depot.knaw.nl:557', 'metadata', <etree._ElementTree object at 0xa255e6c> )
        #delete: ( 'knaw_mir:oai:depot.knaw.nl:551', )

        #keyword arg: partname: metadata
        #keyword arg: identifier: meresco:record:3
        #keyword arg: lxmlNode: <lxml.etree._ElementTree object at 0x89edacc>

        #Delete heeft geen partName...
        
        #print 'FilterPartNames.message:', message
        #print 'PartName:', kwargs.get('partname', None)

        #for key in kwargs:
        #    print "Keyword in kwargs: %s: %s" % (key, kwargs[key])

        if self._allowedPartName(kwargs.get('partname', None)):
            #print '->', message, 'message wordt doorgestuurd, Partname:', kwargs.get('partname', None), kwargs.get('identifier', None) 
            yield self.all.unknown(message, *args, **kwargs)
