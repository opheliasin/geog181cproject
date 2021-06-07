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

starting_point_base = "starting_point.shp"
geometry_type = "POINT"
template = ""
has_m = "DISABLED"
has_z = "DISABLED"
sr = arcpy.GetParameterAsText(4)


starting_point_temp_name = arcpy.CreateScratchName("temp",
                                       "",
                                       "Shapefile",
                                       TEMP)


#arcpy.CreateFeatureclass_management(TEMP, scratch_name, geometry_type, template, has_m, has_z, sr)
out_starting_point = os.path.join(TEMP, starting_point_temp_name)
arcpy.CopyFeatures_management(ptGeom, out_starting_point)

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

arcpy.Delete_management(starting_point_temp_name)

arcpy.AddMessage("{0} has successfully outputted to .".format(vac_sites_selected_basename, vac_sites_selected_dir))

#-----------------------------------------------
# Network Analysis

#Check out the Network Analyst extension license
arcpy.CheckOutExtension("Network")

#Set environment settings
env.workspace = TEMP
env.overwriteOutput = True
    
#Set local variables
inNetworkDataset = arcpy.GetParameterAsText(11)
#def getParameterInfo(self):
    #Define parameter definitions

 #   inNetworkDataset = arcpy.Parameter(
  #      displayName="Network Dataset",
  #     name="in_features",
   #    datatype="GPFeatureLayer",
    #    parameterType="Required",
     #   direction="Input")

#return [inNetworkDataset]

outNALayerName = "Closest_Facilities"
impedanceAttribute = arcpy.GetParameterAsText(12)
accumulateAttribute = arcpy.GetParameterAsText(13)
inFacilities = vac_sites_selected
inIncidents = starting_point_temp_name #insert location shp file here
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

ID = ‘ObjectID’
arcpy.CheckOutExtension("Spatial")

arcpy.MakeFeatureLayer_management (routes, “CFRoutes”)

with arcpy.da.SearchCursor(‘CFRoutes’,[ID]) as cursor:
    for row in cursor:
        ID = str(row[0])
        #print ID
        selRoutes = arcpy.SelectLayerByAttribute_management (“CFRoutes”, "NEW_SELECTION", '"ID" = {}'.format(ID))
       arcpy.conversion.FeatureClassToShapefile(selRoutes, TEMP)

#-------------------------------------------------------
#Table Manipulation with Cursors - create new table showing 10 nearest vaccination sites with most relevant information for user

# define local variables
originalSites = vac_sites_selected
naSites = os.path.join(TEMP, "outNAlayer.shp")
top_10_closest_facilities = TEMP + "top_10_closest_facilities.shp" 
outTable = arcpy.GetParameterAsText(14) #path 
newFields = [('NAME', 'TEXT'), ('ADDRESS', 'TEXT'), ('MUNICIPAL', 'TEXT'), ('PHONE', 'TEXT'), ('OPER_HRS', 'TEXT'),
             ('DRIVE_THRU', 'TEXT'), ('APPT_REQ', 'TEXT'), ('CALL_REQ', 'TEXT'), ('WHEELCHAIR', 'TEXT'), ('WEBSITE', 'TEXT'), ('TOTAL_MILE', 'DOUBLE'),\
            ('TOTAL_TIME', 'DOUBLE')]

#join original table and network analysis table 
arcpy.SpatialJoin_analysis(originalSites, naSites, top_10_closest_facilities, "JOIN_ONE_TO_ONE", "KEEP_COMMON")

outTable_dir = os.path.dirname(outTable)
outTable_base = os.path.basename(outTable)

# create a new table and add 8 new fields
arcpy.CreateTable_management(outTable_dir, outTable_base)
for field in newFields:
    arcpy.AddField_management(outTable, field[0], field[1])

# insert cursor for new table
insert = ['NAME', 'ADDRESS', 'MUNICIPAL', 'PHONE', 'OPER_HRS', 'DRIVE_THRU', 'APPT_REQ', 'CALL_REQ', 'WHEELCHAIR', 'WEBSITE', 'TOTAL_MILE', 'TOTAL_TIME']
insertCursor = arcpy.da.InsertCursor(outTable, insert)

#search cursor and populate rows of new table using first 10 rows of sorted table
originalFields = ['name', 'fulladdr', 'municipali', 'phone', 'operhours', 'drive_thro', 'appt_only', 'call_first', 'Wheelchair', 'vaccine_ur', 'Total_Mile', 'Total_Time']
searchCursor = arcpy.da.SearchCursor(sortedSites, originalFields)
for row in searchCursor:
    rows = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]
    insertCursor.insertRow(rows)

    # clean up local variables, cursors and cursor-related variables and unlock
del originalSites, naSites, sortedSites, outTable, newFields, field, insert, insertCursor, originalFields, searchCursor, row, rows

# to signal end of program
print "Table successfully created!"












