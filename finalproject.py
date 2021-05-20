#-----------------------------------------------
#
# Geog 181c Final Project
# Mari Bouwman, Chalsea Montellano, Ryuichi Utsu, Ophelia Sin, Daisy Yan
#
#-----------------------------------------------
import arcpy, os

folderpath = r"C:\Users\Ophelia\geog181cproject"

### CREATE SHAPEFILE
#set up environment
arcpy.env.workspace = folderpath
arcpy.env.overwriteOutput = True

# receive user input
#
ptList =[[34.067565101060275, -118.45344143556794],
         [34.067883050530135, -118.45348171778397],
         [34.02082743884116, -118.38886493992615]]
pt = arcpy.Point()
ptGeoms = []
for p in ptList:
    pt.X = p[0]
    pt.Y = p[1]
    ptGeoms.append(arcpy.PointGeometry(pt))

# Set local variables
out_path = folderpath
out_name = "startingpoint.shp"
geometry_type = "POINT"
template = ""
has_m = "DISABLED"
has_z = "DISABLED"

#get spatial reference
spatial_reference = arcpy.SpatialReference("NAD 1983 UTM Zone 11N")

#create feature class
arcpy.CreateFeatureclass_management(out_path, out_name, geometry_type, template, has_m, has_z, spatial_reference)

arcpy.CopyFeatures_management(ptGeoms, "startingpoint.shp")

startingpoint = "startingpoint.shp"
#sr = arcpy.SpatialReference(104024)
arcpy.DefineProjection_management(infc, spatial_reference)

# import requests
# geo_url = 'http://maps.googleapis.com/maps/api/geocode/json'
# my_address = {'address': '1600 Amphitheatre Parkway, Mountain View, CA',
#              'language': 'en'}
# response = requests.get(geo_url, params = my_address)
# results = response.json()['results']
# print results
# my_geo = results[0]['geometry']['location']
# print("Longitude:",my_geo['lng'],"\n","Latitude:",my_geo['lat'])

# import geopy, geopanda
# from geopy.geocoders import Nominatim
#
# locator = Nominatim(user_agent= "myGeocoder")
# location = locator.geocode("Champ de Mars, Paris, France")
# print("Latitude = {}, Longitude = {}".format(location.latitude, location.longitude))

#create search radius

# #method 2) service area analysis
# #Check out the Network Analyst extension license

# in_network_dataset =
# out_network_analysis_layer = folderpath + "out_network_analysis"
# impedance_attribute = "DriveTime"
# travel_from_to = "TRAVEL_FROM"

# if arcpy.CheckOutExtension("Network") == "CheckedOut":
#     arcpy.na.MakeServiceAreaLayer(in_network_dataset,
#                                   out_network_analysis_layer,
#                                   impedance_attribute,
#                                   travel_from_to,
#                                   )
# else:
#     print("Network analysis tool is not available.")

# # #select by attribute to narrow down
# in_table = #table generated from list of vaccination sites that are located within the buffer zone or within the service area
# field_names = [] #attributes we'd like to choose
#
# arcpy.da.SearchCursor(in_table, field_names)

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

