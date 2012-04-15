# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys

import clr
clr.AddReferenceByPartialName('System.Xml')
from System.Xml import XmlTextReader, XmlNodeType

# ----------------------------------------------------------------------------
# Parser
# ----------------------------------------------------------------------------    

class ipyNetParser():
    """ 
    System.Xml.XmlTextReader parser 
    """

    def __init__( self, xml_doc, root ):
        self.__reader = None
        result = None
        try:
            try:
                self.__reader = XmlTextReader( xml_doc )
                result = self.parse( root )
            finally:
                if self.__reader != None:
                    self.__reader.Close()
                del self.__reader
        except ValueError:
            raise ValueError
        return result
    
    def parse(self,element):
        r = self.__reader
        r.Read()
        while r.Read():
            if r.LocalName.Equals( element ):
                while r.Read():
                    if r.NodeType == XmlNodeType.Element:
                        self.startElement( r.LocalName )
                    elif r.NodeType == XmlNodeType.EndElement:
                        self.endElement( r.LocalName )

    def startElement( self, elementName):
        """
        Abstract method: Implemented by sub-classes to match pattern 
        on element's start

        MUST be implemented by handler subclass.
        """

    def endElement( self, elementName):
        """
        Abstract method: Implemented by sub-classes to match pattern 
        on element's end

        MUST be implemented by handler subclass.
        """

    def getAttribute( self, attrName ):
        """
        Returns value of inserted attribute.
        """
        if self.__reader.HasAttributes:
            self.__reader.MoveToAttribute(attrName)
            return self.__reader.Value

# ----------------------------------------------------------------------------
# Handler 
# ----------------------------------------------------------------------------

class osmNetHandler( ipyNetParser ):
    """
    A handler to deal with nodes in OSM file 

    example:
      m = osmNetHandler("~/maps/data.osm")
      for id, way in m.elements['way'].iteritems():
        #do something
    """
  
    _inside_element = None
    _relation_types = ["multipolygon", "boundary", "route"]


    def __init__( self, xml_doc ):
        self.elements = {
            "node": {},
            "way": {},
            "relation": {} 
        }
    
        for relation_type in self._relation_types:
            self.elements["relation"][relation_type] = {}
    
        self.lat = {}   
        self.lon = {}  
    
        ipyNetParser.__init__( self, xml_doc, "osm" )

    def startElement( self, name ):
        if name in ["node", "way", "relation"]:
            self._inside_element = name
            self._current_id = int(self.getAttribute("id"))
            self._current_attributes = {}
            self._current_children = []
      
            if name == "node":
                self.lat[self._current_id]=float(self.getAttribute("lat"))
                self.lon[self._current_id]=float(self.getAttribute("lon"))
            elif name == "relation":
                self._relation_type = None
                self._outer_members = []
        
        elif self._inside_element:
            if name in ["nd", "member"]:
                # ignore other children [ehm nodes?] of relation than way
                if name == "member" and self.getAttribute("type") != "way":
                    return
                ref = int(self.getAttribute("ref"))
                self._current_children.append(ref)
                if name == "member" and self.getAttribute("role") == "outer":
                    self._outer_members.append(ref)
        
            elif name == "tag":
                attr_key = self.getAttribute("k")
                if attr_key == "created_by":
                    return
          
                self._current_attributes[attr_key]=self.getAttribute("v")
        
                if self._inside_element == "relation" and \
                   self.getAttribute("v") in self._relation_types:
                    self._relation_type = self.getAttribute("v")
    
    
    def endElement(self, name):
        id = self._current_id
        if name in ["node", "way", "relation"]:
            self._inside_element = None
      
            # ignore unattributed nodes
            if name == "node" and self._current_attributes:
                return
      
            element = {
                "attributes": self._current_attributes
            }
      
            if name != "node":
                element["children"] = self._current_children
      
            if name == "relation":
                if self._relation_type:
                    if self._relation_type == "multipolygon":
                        element["outer_members"] = self._outer_members
                    self.elements[name][self._relation_type][id] = element
            else:
                self.elements[name][id] = element
      
