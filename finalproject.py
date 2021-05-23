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

folder_path = "C:/Users/daisyyan/Desktop/Network_Analysis"

import arcpy
from arcpy import env
import os

try:
    #Check out the Network Analyst extension license
    arcpy.CheckOutExtension("Network")

    #Set environment settings
    env.workspace = folder_path
    env.overwriteOutput = True
    
    #Set local variables
    inNetworkDataset = folder_path+"/Clipped_Streets/SDC_Edge_Source.shp"
    outNALayerName = "Vac_Sites"
    impedanceAttribute = "Drivetime"
    accumulateAttributeName = ["Meters"] 
    inFacilities = folder_path+"/Covid-19_Vaccination_Provider_Locations_in_the_United_States_cleaned_Mari/Covid-19_Vaccination_Provider_Locations_in_the_United_States_cleaned_Mari.shp"
    #inIncidents = "//Stores"
    outLayerFile = folder_path + "/" + outNALayerName + ".lyr"
    
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

 # # # # # # # Insert Cursor and Search Cursor # # # # # # #

#Insert cursor to create and display new table showing 10 nearest vaccination
#sites with most relevant information for user

folderPath = r"C:\Users\cnmre\OneDrive\Documents\181C GIS Programming and Dev\covid19_vaccination_sites_la_county"

import arcpy, os

arcpy.env.workspace = folderPath
arcpy.overwriteOutput = True

#define local variables
vaccinationSites = os.path.join(folderPath, "covid19_vaccination_sites_la_county.shp")
outTable = "Top_Ten_Nearest_Vaccination_Sites.dbf"
newFields = [('NAME', 'TEXT'), ('ADDRESS', 'TEXT'), ('MUNICIPAL', 'TEXT'),('OPER_HRS', 'TEXT'),('DRIVE_THRU', 'TEXT'),\
             ('APPT_REQ', 'TEXT'),('CALL_REQ', 'TEXT'), ('PHONE', 'TEXT'),('WEBSITE', 'TEXT')]

#create a new table and add 8 new fields
arcpy.CreateTable_management(folderPath, outTable)
for field in newFields:
    arcpy.AddField_management(outTable, field[0], field[1])

#insert cursor
insert = ['NAME', 'ADDRESS', 'MUNICIPAL', 'OPER_HRS', 'DRIVE_THRU', 'APPT_REQ', 'CALL_REQ', 'PHONE', 'WEBSITE']
insertCursor = arcpy.da.InsertCursor(outTable, insert)

#search cursor and populate rows for top 10 rows (given that original table is sorted by distance)
SQL = arcpy.AddFieldDelimiters(vaccinationSites, "fid_1") + "<= 10"
originalFields = ['name', 'fulladdr', 'municipali', 'operhours', 'drive_thro', 'appt_only', 'call_first', 'phone', 'agencyurl']
searchCursor = arcpy.da.SearchCursor(vaccinationSites, originalFields, SQL)
for row in searchCursor:
    rows = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
    insertCursor.insertRow(rows)

#clean up and unlock
del field, insertCursor, searchCursor, row, rows

print "Table successfully created!"

# # # # # # # End of Insert Cursor and Search Cursor # # # # # # # 

