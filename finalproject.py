#-----------------------------------------------
#
# Geog 181c Final Project
# Mari Bouwman, Chalsea Montellano, Ryuichi Utsu, Ophelia Sin, Daisy Yan
#
#-----------------------------------------------
import arcpy, os

folderpath = ""

#set up environment
arcpy.env.workspace = folderpath
arcpy.env.overwriteOutput = True

# receive user input
# import requests
# geo_url = 'http://maps.googleapis.com/maps/api/geocode/json'
# my_address = {'address': '1600 Amphitheatre Parkway, Mountain View, CA',
#              'language': 'en'}
# response = requests.get(geo_url, params = my_address)
# results = response.json()['results']
# print results
# my_geo = results[0]['geometry']['location']
# print("Longitude:",my_geo['lng'],"\n","Latitude:",my_geo['lat'])

import geopy, geopanda
from geopy.geocoders import Nominatim

locator = Nominatim(user_agent= "myGeocoder")
location = locator.geocode("Champ de Mars, Paris, France")
print("Latitude = {}, Longitude = {}".format(location.latitude, location.longitude))


#create search radius

#method 1) buffer analysis


coordinates = [-118.450501, 34.065215] # input 1 lat,long

pointList=[]
for x,y in coordinates:
    point = arcpy.Point(x,y)
    pointGeometry = arcpy.PointGeometry(point)
    pointList.append(pointGeometry)

bufferOutput = folderpath + "bufferOutput.shp"
arcpy.Buffer_analysis(pointList, bufferOutput, "100000")

del coordinates, pointList, point, pointGeometry
print "done with using geometry object."

#method 2) service area analysis
#Check out the Network Analyst extension license
# if arcpy.CheckOutExtension("Network") == "CheckedOut":
#     arcpy.na.MakeServiceAreaLayer(in_network_dataset, out_network_analysis_layer, impedance_attribute, {travel_from_to}, {default_break_values}, {polygon_type}, {merge}, {nesting_type}, {line_type}, {overlap}, {split}, {excluded_source_name}, {accumulate_attribute_name}, {UTurn_policy}, {restriction_attribute_name}, {polygon_trim}, {poly_trim_value}, {lines_source_fields}, {hierarchy}, {time_of_day})
#
# #select by attribute to narrow down
# arcpy.da.SearchCursor(in_table, field_names, {where_clause}, {spatial_reference}, {explode_to_points}, {sql_clause})

#Insert cursor to create and display new table showing 10 nearest vaccination
#sites with most relevant information for user 

# # # Network Analysis # # # In Progress -DY # # #

#Import system modules
import arcpy
from arcpy import env

try:
    #Check out the Network Analyst extension license
    arcpy.CheckOutExtension("Network")

    #Set environment settings
    env.workspace = folderpath
    env.overwriteOutput = True
    
    #Set local variables
    inNetworkDataset = "//Covid-19_Vaccination_Provider_Locations_in_the_United_States_cleaned_Mari.shp"
    outNALayerName = "Vac_Sites"
    impedanceAttribute = "Drivetime" #where is this attribute? -DY
    accumulateAttributeName = ["Meters"] 
    inFacilities = "//Warehouses" #change -DY
    inIncidents = "//Stores" #change -DY
    outLayerFile = "C://" + "/" + outNALayerName + ".lyr"
    
    #Create a new closest facility analysis layer. Apart from finding the drive 
    #time to the closest warehouse, we also want to find the total distance. So
    #we will accumulate the "Meters" impedance attribute.
    outNALayer = arcpy.na.MakeClosestFacilityLayer(inNetworkDataset,outNALayerName,
                                                   impedanceAttribute,"TRAVEL_TO",
                                                   "",1, accumulateAttributeName,
                                                   "NO_UTURNS")
    
    #Get the layer object from the result object. The closest facility layer can 
    #now be referenced using the layer object.
    outNALayer = outNALayer.getOutput(0)
    
    #Get the names of all the sublayers within the closest facility layer.
    subLayerNames = arcpy.na.GetNAClassNames(outNALayer)
    #Stores the layer names that we will use later
    facilitiesLayerName = subLayerNames["Facilities"] #change attribute -DY
    incidentsLayerName = subLayerNames["Incidents"] #change attribute -DY
    
    ##Load the warehouses as Facilities using the default field mappings and 
    ##search tolerance
    #arcpy.na.AddLocations(outNALayer, facilitiesLayerName, inFacilities, "", "")
    
    ##Load the Stores as Incidents. Map the Name property from the NOM field
    ##using field mappings
    #fieldMappings = arcpy.na.NAClassFieldMappings(outNALayer, incidentsLayerName)
    #fieldMappings["Name"].mappedFieldName = "NOM"
    #arcpy.na.AddLocations(outNALayer, incidentsLayerName, inIncidents,
                          #fieldMappings,"")
    
    #Solve the closest facility layer
    arcpy.na.Solve(outNALayer)
    
    #Save the solved closest facility layer as a layer file on disk with 
    #relative paths
    arcpy.management.SaveToLayerFile(outNALayer,outLayerFile,"RELATIVE")
    
    print "Script completed successfully"

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print "An error occurred on line %i" % tb.tb_lineno
    print str(e)

 # # # # # # #

folderPath = r"C:\Users\cnmre\OneDrive\Documents\181C GIS Programming and Dev\geog181cproject"

import arcpy, os

arcpy.env.workspace = folderPath
arcpy.overwriteOutput = True

vaccinationSites = os.path.join(folderPath, "Covid-19_Vaccination_Provider_Locations_in_the_United_States.shp")
outTable = "Top_Ten_Nearest_Vaccination_Sites.dbf"
newFields = [('NAME', 'TEXT'),('DISTANCE', 'FLOAT'), ('ADDRESS', 'TEXT'), \
             ('OPERATIONAL_HRS', 'TEXT'),('DRIVE_THROUGH', 'TEXT'), \
             ('APPT_REQUIRED', 'TEXT'),('CALL_REQUIRED', 'TEXT'), \
             ('PHONE', 'TEXT'), ('WEBSITE', 'TEXT')]  

arcpy.CreateTable_management(folderPath, outTable)
for field in newFields:
    arcpy.AddField_management(outTable, field[0], field[1])
del field

insert = ['NAME', 'DISTANCE', 'ADDRESS', 'OPERATIONAL_HRS', 'DRIVE_THROUGH', \
          'APPT_REQUIRED', 'CALL_REQUIRED', 'PHONE', 'WEBSITE']
insertCursor = arcpy.da.InsertCursor(outTable, insert)
SQL = arcpy.AddFieldDelimiters(vaccinationSites, "Distance") + ">= Value"

originalFields = ['name', 'distance', 'fulladdr', 'operhours',\
                  'drive_thro', 'appt_only', 'call_first', \
                  'phone', 'agencyurl')
searchCursor = arcpy.da.SearchCursor(vaccinationSites, originalFields, SQL)
for row in searchCursor:
    rows = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
    outcursor.insertRow(rows)
del row, rows

rows = arcpy.da.SearchCursor(outTable, insert)
for row in rows:
    i = 0
    for field in insert:
        print (field, row[i])
        i = i + 1
del insertCursor, searchCursor, row, rows


