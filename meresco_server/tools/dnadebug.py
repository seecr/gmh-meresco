# -*- coding: utf-8 -*-
from meresco.core import Observable
from lxml.etree import parse, _ElementTree, tostring
from lxml import etree
import gc

class DNADebug(Observable):

    def __init__(self, enabled=True, prefix='DEBUG', gc=False):
        Observable.__init__(self)
        #assert len(allowed) == 0 or len(disallowed) == 0, 'Use disallowed or allowed'        
        self._enabled = enabled
        self._add_prefix = '[%s]'%(prefix)
        self._gc = gc
        #gc.enable()
        #gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
        #gc.DEBUG_LEAK - DEBUG_COLLECTABLE
        
    def unknown(self, method, *args, **kwargs):
        
        if self._enabled:
            
            print self._add_prefix, 'Method:', method
            for value in args:
                print self._add_prefix, 'Value:', value
            for key in kwargs:
                kwargkey = kwargs[key]
                if type(kwargs[key]) == _ElementTree:                    
                    kwargkey = etree.tostring(kwargs[key], encoding='UTF-8')                    
                print self._add_prefix, "Key: %s,  Value: %s" % (key, kwargkey)
        
        if self._gc:
            #gc.enable()
            gc.set_debug(gc.DEBUG_LEAK)
            # force collection            
            gc.collect()
            #print self._add_prefix, "GARBAGE collected...:"

            #print self._add_prefix, "Uncollected Objects!:",
            for x in gc.garbage:
                s = str(x)
                if len(s) > 80: s = s[:80]
                print "Uncollected Object!:", type(x),"->", s            

        yield self.all.unknown(method, *args, **kwargs)