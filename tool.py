#-----------------------------------------------
#
# Geog 181c Final Project Tool
# Mari Bouwman, Chalsea Montellano, Ryuichi Utsu, Ophelia Sin, Daisy Yan
#
#-----------------------------------------------

import arcpy, os

folderpath = ""

#set up environment
arcpy.env.workspace = folderpath
arcpy.env.overwriteOutput = True

vac_sites = arcpy.GetParameterAsText(0)
arcpy.MakeFeatureLayer_management(vac_sites, "vac_sites")
boundary = arcpy.GetParameterAsText(1)
arcpy.MakeFeatureLayer_management(boundary, "boundary")
arcpy.SelectLayerByLocation_management("vac_sites", "intersect", "boundary")

long = arcpy.GetParameterAsText(2) 
lat = arcpy.GetParameterAsText(3)
#p =[]
#p.extend(long, lat)
pt = arcpy.Point()
ptGeom = [] 
pt.X = long #p[0] #can i simplify this code? 
pt.Y = lat #p[1]
ptGeom.append(arcpy.PointGeometry(pt))

out_path = folderpath
out_name = "origin_point.shp"
geometry_type = "POINT"
template = ""
has_m = "DISABLED"
has_z = "DISABLED"
spatial_reference = arcpy.SpatialReference("NAD 1983")

arcpy.CreateFeatureclass_management(out_path, out_name, geometry_type, template, has_m, has_z, spatial_reference)
arcpy.CopyFeatures_management(ptGeoms, out_name)









