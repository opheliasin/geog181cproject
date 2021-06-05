#-----------------------------------------------
#
# Geog 181c Final Project Tool
# Mari Bouwman, Chalsea Montellano, Ryuichi Utsu, Ophelia Sin, Daisy Yan
#
#-----------------------------------------------

import arcpy, os

folderpath = arcpy.GetParameterAsText(0)

#set up environment
arcpy.env.workspace = folderpath
arcpy.env.overwriteOutput = True

vac_sites = arcpy.GetParameterAsText(1)
arcpy.MakeFeatureLayer_management(vac_sites, "vac_sites")
boundary = arcpy.GetParameterAsText(2)
arcpy.MakeFeatureLayer_management(boundary, "boundary")
arcpy.SelectLayerByLocation_management("vac_sites", "intersect", "boundary")

long = arcpy.GetParameterAsText(3) 
lat = arcpy.GetParameterAsText(4)
#p =[]
#p.extend(long, lat)
pt = arcpy.Point()
ptGeom = [] 
pt.X = long #p[0] 
pt.Y = lat #p[1]
ptGeom.append(arcpy.PointGeometry(pt))

out_name = "origin_point.shp"
geometry_type = "POINT"
template = ""
has_m = "DISABLED"
has_z = "DISABLED"
spatial_reference = arcpy.SpatialReference("NAD 1983")

arcpy.CreateFeatureclass_management(folderpath, out_name, geometry_type, template, has_m, has_z, spatial_reference)
arcpy.CopyFeatures_management(ptGeoms, out_name)

drive_thro = arcpy.GetParameterAsText(5) 
appt_only = arcpy.GetParameterAsText(6) 
call_first = arcpy.GetParameterAsText(7) 
Wheelchair = arcpy.GetParameterAsText(8) 

where_clause = "" #declare where_clause 

if drive_thro: 
  where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "drive_thro") + " = ' " + drive_thro + "' " 
if appt_only: 
  where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "appt_only") + "= 'appt_only'"
if call_first: 
  where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "drive_thro") + "= 'call_first'"
if Wheelchair: 
  where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "drive_thro") + "= 'Wheelchair'"
  
arcpy.SelectLayerByAttribute_management("vac_sites", "SUBSET_SELECTION", where_clause)

vac_sites_selected = "vac_sites_selected.shp"
arcpy.CreateFeatureclass_management(folderpath, vac_sites_selected, geometry_type, template, has_m, has_z, spatial_reference)
arcpy.CopyFeatures_management("vac_sites", vac_sites_selected)










