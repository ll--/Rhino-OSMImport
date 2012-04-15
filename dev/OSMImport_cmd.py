# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------
import sys, math

import scriptcontext
import Rhino.DocObjects
import rhinoscriptsyntax as rs

from osm_parser import osmNetHandler
from default_conditions import layer_conditions

# ----------------------------------------------------------------------------

__commandname__ = "[OSMImport]"

# ----------------------------------------------------------------------------
# RMap projection (mercator)
# ----------------------------------------------------------------------------
def degToRad(deg):
    return (deg / 180.0 * math.pi)
def lat2coord(lat):  
    return 6378137.0 * math.log(
        (math.sin(degToRad(lat))+1.0) / math.cos(degToRad(lat))
    )
def long2coord(lon):
    return 6378137.0 * degToRad(lon)

# ----------------------------------------------------------------------------
# OSM routines
# ----------------------------------------------------------------------------
def getLayerName(attributes):
    layer_name = 'Default'
    for layer_condition in layer_conditions:
        pass_layer = False
        for condition in layer_condition["conditions"]:
            if condition[0] != "*" and condition[0] not in attributes:
                pass_layer = True
            elif condition[1] != '*' and attributes[condition[0]] != condition[1]:
                pass_layer = True
    
        if not pass_layer:
            return layer_condition["layer_name"]
    
    return layer_name

def getWayPoints(children_id, model):
    """Get way nodes and project coordiates
    """
    lon = model.lon
    lat = model.lat
    result = []
    
    for x in children_id:
        if x in lon and x in lat:
            result.append([long2coord(lon[x]), lat2coord(lat[x]), 0])
    
    return result

# ----------------------------------------------------------------------------
# Rhino routines
# ----------------------------------------------------------------------------
def setName(obj, newName):
    if not obj: 
        return None
    objref = Rhino.DocObjects.ObjRef(obj)
    Rhino.DocObjects.ObjectAttributes(o)
    o = objref.Object()
    attr = Rhino.DocObjects.ObjectAttributes(o)
    attr.Name = newName
    scriptcontext.doc.Objects.ModifyAttributes(o, attr, True)

def createCurve(waypoints, layer=None):
    if not waypoints or len(waypoints) < 2:
        return
    elif len(waypoints) <= 3 and waypoints[0][:] == waypoints[-1][:]:
        return
    curve = rs.AddPolyline(waypoints)
    if curve and layer:
        rs.ObjectLayer(curve, layer)
    return curve
      

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
    
def RunCommand(is_interactive, debug=False):
    """Creates geometry from OpenStreetMap data
    
    You can take the data from a .osm XML file 
    (ie. via the site's Export tab)
    """ 
    
    # ------------------------------------------------------------------------ 
    # initial Rhino settings
    initial_layers = rs.LayerNames();
    
    # ------------------------------------------------------------------------ 
    # get datamodel
    input_file_name = rs.OpenFileName()
    if not input_file_name:
        return
    
    osm_model = osmNetHandler(input_file_name)
    model_elements = osm_model.elements
    
    if not debug:
        rs.EnableRedraw(False)
    
    # ------------------------------------------------------------------------
    # create layers
    for layer_condition in layer_conditions:
        rs.AddLayer(layer_condition["layer_name"])
    
    # ------------------------------------------------------------------------
    # create nodes
    # todo
    
    # create boundaries and routes
    # todo
    
    # ------------------------------------------------------------------------
    # crete multipolygons 
    
    # storing duplicates from multipolygon relation
    used_ways = []
    
    for id, relation in model_elements['relation']['multipolygon'].iteritems():
        curves = []
        
        # obtain layer_name
        layer_name = getLayerName(relation["attributes"]) 
        if layer_name in ["Default", "other"]:
            for outer_member in relation["outer_members"]:
                if outer_member not in model_elements['way']:
                  continue
                layer_name = getLayerName(
                    model_elements['way'][outer_member]["attributes"])
                if layer_name not in ["Default", "other"]:
                    break
        
        # for child in children
        for way_id in relation["children"]:
            used_ways.append(way_id)
            
            if way_id not in model_elements["way"]:
                continue
            waypoints = getWayPoints(
                model_elements["way"][way_id]["children"], osm_model)
            curve = createCurve(waypoints, layer_name)
            if curve:
                curves.append(curve)
            
        # group children
        if "name" in relation["attributes"]:
            group_name = relation["attributes"]["name"]
        else:
            group_name = None
        
        group = rs.AddGroup(group_name)
        rs.AddObjectsToGroup(curves, group)
    
    # ------------------------------------------------------------------------
    # create ways
    for id, way in model_elements['way'].iteritems():
        if id in used_ways:
            continue
        
        waypoints = getWayPoints(way["children"], osm_model)
        curve = createCurve(
            waypoints,
            getLayerName(way["attributes"]) 
        )

    # ------------------------------------------------------------------------
    # purge unused layers
    for layer in rs.LayerNames():
        if layer == 'Default' or layer in initial_layers:
          continue
        rs.DeleteLayer(layer)
        
    rs.EnableRedraw(True)


if __name__ == '__main__':
    RunCommand(False, True)
    