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

out_name = arcpy.GetParameterAsText(5) 
geometry_type = "POINT"
template = ""
has_m = "DISABLED"
has_z = "DISABLED"
spatial_reference = arcpy.GetParameterAsText(6) 

arcpy.CreateFeatureclass_management(folderpath, out_name, geometry_type, template, has_m, has_z, spatial_reference)
arcpy.CopyFeatures_management(ptGeoms, out_name)

drive_thro =  arcpy.GetParameterAsText(6) 
appt_only = arcpy.GetParameterAsText(7) 
call_first = arcpy.GetParameterAsText(8) 
wheelchair = arcpy.GetParameterAsText(9) 

where_clause = "" #declare where_clause 

if drive_thro: 
  where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "drive_thro") + " r\ = ' " + drive_thro + " r\' " 
if appt_only: 
  where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "appt_only") + " r\ = ' " + appt_only + " r\' " 
  #where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "appt_only") + "= 'appt_only'"
if call_first:
  where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "call_first") + " r\ = ' " + call_first + " r\' " 
  #where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "call_first") + "= 'call_first'"
if wheelchair: 
  where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "wheelchair") + " r\ = ' " + wheelchair + " r\' " 
  #where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "Wheelchair") + "= 'Wheelchair'"
  
arcpy.SelectLayerByAttribute_management("vac_sites", "SUBSET_SELECTION", where_clause)

vac_sites_selected =  arcpy.GetParameterAsText(10) 
arcpy.CreateFeatureclass_management(folderpath, vac_sites_selected, geometry_type, template, has_m, has_z, spatial_reference)
arcpy.CopyFeatures_management("vac_sites", vac_sites_selected)










