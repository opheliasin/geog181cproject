#-----------------------------------------------
#
# Geog 181c Final Project Tool
# Mari Bouwman, Chalsea Montellano, Ryuichi Utsu, Ophelia Sin, Daisy Yan
#
#-----------------------------------------------
import os
import arcpy

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

#-----------------------------------------------

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

#-----------------------------------------------
# Network Analysis

#Check out the Network Analyst extension license
arcpy.CheckOutExtension("Network")

#Set environment settings
env.workspace = TEMP
env.overwriteOutput = True
    
#Set local variables
#inNetworkDataset = ... #insert network dataset here
outNALayerName = "Closest_Facilities"
#impedanceAttribute = "" #insert corresponding impendance attribute here
#accumulateAttributeName = [] #insert corresponding accumulate attribute name here
inFacilities = vac_sites_selected
inIncidents = TEMP+"/starting_point" #insert location shp file here
outLayerFile = TEMP + "/" + outNALayerName + ".lyr"
    
#Create a new closest facility analysis layer. Apart from finding the drive 
#time to the closest warehouse, we also want to find the total distance. So
#we will accumulate the "Miles" impedance attribute.
outNALayer = arcpy.na.MakeClosestFacilityLayer(inNetworkDataset,outNALayerName,
                                                   impedanceAttribute,"TRAVEL_TO",
                                                   "",10, accumulateAttributeName,
                                                   "NO_UTURNS")
    
#Get the layer object from the result object. The closest facility layer can 
#now be referenced using the layer object.
outNALayer = outNALayer.getOutput(0)

#Get the names of all the sublayers within the closest facility layer.
sublayer_names = arcpy.na.GetNAClassNames(outNALayer)

#Stores the layer names that we will use later
facilitiesLayerName = sublayer_names["Facilities"]
incidentsLayerName = sublayer_names["Incidents"]
    
#Load the warehouses as Facilities using the default field mappings and 
#search tolerance
arcpy.na.AddLocations(outNALayer, facilitiesLayerName, inFacilities, "", "")
    
#Load user location as incident. Map the Name property from the NOM field
#using field mappings
fieldMappings = arcpy.na.NAClassFieldMappings(outNALayer, incidentsLayerName)
fieldMappings["Name"].mappedFieldName = "NOM"
arcpy.na.AddLocations(outNALayer, incidentsLayerName, inIncidents,
                          fieldMappings,"")

#Solve the closest facility layer
arcpy.na.Solve(outNALayer, "SKIP", "CONTINUE")
    
#Save the solved closest facility layer as a layer file on disk with 
#relative paths
arcpy.management.SaveToLayerFile(outNALayer,outLayerFile,"RELATIVE")
    
print "Closest facilities analysis is complete."

#convert layer to shapefile
arcpy.conversion.FeatureClassToShapefile(outNAlayer, TEMP)

routes = arcpy.mapping.ListLayers(outNALayer, "Routes")[0]
arcpy.conversion.FeatureClassToShapefile(routes, TEMP)



















