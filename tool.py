#-----------------------------------------------
#
# Geog 181c Final Project Tool
# Mari Bouwman, Chalsea Montellano, Ryuichi Utsu, Ophelia Sin, Daisy Yan
#
#-----------------------------------------------
import os

#set up environment
TEMP = os.getenv("TEMP") # this is a folder Windows promises will exist
arcpy.env.scratchWorkspace = TEMP
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
pt.X = long #p[0] 
pt.Y = lat #p[1]
ptGeom.append(arcpy.PointGeometry(pt))

out_name = "starting_point.shp"
geometry_type = "POINT"
template = ""
has_m = "DISABLED"
has_z = "DISABLED"
sr = arcpy.GetParameterAsText(4)

scratch_name = arcpy.CreateScratchName("temp",
                                       "",
                                       "Shapefile",
                                       TEMP)

#arcpy.CreateFeatureclass_management(TEMP, scratch_name, geometry_type, template, has_m, has_z, sr)
out_geom = os.path.join(TEMP, scratch_name)
arcpy.CopyFeatures_management(ptGeom, out_geom)

arcpy.AddMessage("Finish setting up starting point.")

# arcpy.CreateFeatureclass_management(folderpath, out_name, geometry_type, template, has_m, has_z, sr)
# out_geom = os.path.join(folderpath, out_name)
# arcpy.CopyFeatures_management(ptGeom, out_geom)

drive_thro = arcpy.GetParameterAsText(5)
appt_only = arcpy.GetParameterAsText(6) 
call_first = arcpy.GetParameterAsText(7) 
wheelchair = arcpy.GetParameterAsText(8) 

where_clause = "" #declare where_clause 

if drive_thro == 'Yes':
    where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "drive_thro") + "= 'Yes'"
elif drive_thro == 'No':
    where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "drive_thro") + "= 'No'"
if appt_only == 'Yes':
    where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "appt_only") + "= 'Yes'"
elif appt_only == 'No':
    where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "appt_only") + "= 'No'"
if call_first == 'Yes':
    where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "call_first") + "= 'Yes'"
elif call_first == 'No':
    where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "call_first") + "= 'No'"
if wheelchair == 'Yes':
    where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "wheelchair") + "= 'Yes'"
elif wheelchair == 'No':
    where_clause = where_clause + arcpy.AddFieldDelimiters("vac_sites", "wheelchair") + "= 'No'"

arcpy.SelectLayerByAttribute_management("vac_sites", "SUBSET_SELECTION", where_clause)
vac_sites_selected = arcpy.GetParameterAsText(10)

vac_sites_selected_dir = os.path.dirname(vac_sites_selected)
vac_sites_selected_basename = os.path.basename(vac_sites_selected)

arcpy.CreateFeatureclass_management(vac_sites_selected_dir, vac_sites_selected_basename, geometry_type, template, has_m, has_z, sr)

#out_fc = os.path.join(folderpath, vac_sites_selected)
arcpy.CopyFeatures_management("vac_sites", vac_sites_selected)

arcpy.Delete_management(scratch_name)

arcpy.AddMessage("{0} has successfully outputted to .".format(vac_sites_selected_basename, vac_sites_selected_dir))




















