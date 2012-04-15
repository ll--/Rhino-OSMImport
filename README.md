OSMImport Command - for Rhino3d
===============================
RhinoPython script that imports OpenStreetMap file to Rhinoceros 5

Input format
-----------
* .osm (xml file)
* TODO: direct imput from local database

Geometry 
--------

* ways as Rhino polylines
* multypoligons as grouped Rhino polylines

Install 
-------
see 5th question @ [RhinoPython forums](http://python.rhino3d.com/threads/67-7-questions-other-new-Rhino.Python-users-might-have-like-me)

Map features
------------
Rules that converts map features to Rhino layes are defined in default_conditions.py file as list of dictionaries with following format:

	{'layer_name':'<NAME FOR RHINO LAYER>',  
   	 'conditions': [ ['KEY','VALUE'], <…> ]}
There can be one or more key-value pair.

---
* *You can obtain OpenStreetMap data under Creative Commons Attribution-ShareAlike 2.0* 
* *Rhinoceros is a registered trademark of Robert McNeel & Associates.*
