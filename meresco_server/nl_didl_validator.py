# -*- coding: utf-8 -*-
from lxml.etree import parse, _ElementTree, tostring
from lxml import etree
from meresco.core import Observable
from copy import deepcopy
from StringIO import StringIO
from meresco.components.xml_generic.validate import ValidateException


# TODO: lxml staat het gebruik van conolisednames niet meer toe: gebruik kwarg: prefix="[ns_alias]"
# This component handles ADD messages only.
# It will try to validate the node to EduStandaard agreements. If so, the node will be passed forward, all other parts and invalid data formats are ignored (blocked).
# If it fails in doing so, it will block (NOT pass) the ADD message.



class NL_DIDL_validator(Observable):

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
		newArgs = [self._detectAndConvert(arg) for arg in args]     
		newKwargs = dict((key, self._detectAndConvert(value)) for key, value in kwargs.items())
		if self._bln_success:
			return self.all.unknown(method, *newArgs, **newKwargs)

	def _normalizeRecord(self, lxmlNode):
		#print 'In record normalization...'
		#Check if some rule validates. We start with PI and PI location in first DIDL Item.
		# If not available throw ValidationException:
		didl_top_urn = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Descriptor/didl:Statement/dii:Identifier/text()', namespaces=self._nsMap)
		didl_top_urn_loc = lxmlNode.xpath('//didl:DIDL/didl:Item/didl:Component/didl:Resource/@ref', namespaces=self._nsMap)
		#if didl_top_urn and didl_top_urn_loc:
			#print 'URN:', didl_top_urn[0], 'Location:', didl_top_urn_loc[0]
		#else:
		if not didl_top_urn and not didl_top_urn_loc:
			#print 'VALIDATION ERROR... either URN or Location is missing from DIDL topItem...'#, identifier
			raise ValidateException("PID or PID-location is missing from DIDL topItem in metadata. PID: " + (didl_top_urn[0] if didl_top_urn else "") + ', Location: ' + (didl_top_urn_loc[0] if didl_top_urn_loc else "") )
			
		# Else return the valid node.		
		return lxmlNode	    

	def __str__(self):
		return 'NL_DIDL_normalized'
