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


