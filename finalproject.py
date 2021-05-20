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



# in_table = folderpath + "points.csv"
# out_feature_class = "points.shp"
# x_field = "x"
# y_field = "y"
# z_field = ""
#
# arcpy.management.XYTableToPoint(in_table, out_feature_class, x_field, y_field, z_field, arcpy.SpatialReference(3310))

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

#method 1) buffer analysis

bufferOutput = folderpath + "bufferOutput.shp"
arcpy.Buffer_analysis(startingpoint, bufferOutput, "100000")

print "done with using geometry object."

# #method 2) service area analysis
# #Check out the Network Analyst extension license

in_network_dataset =
out_network_analysis_layer = folderpath + "out_network_analysis"
impedance_attribute = "DriveTime"
travel_from_to = "TRAVEL_FROM"

if arcpy.CheckOutExtension("Network") == "CheckedOut":
    arcpy.na.MakeServiceAreaLayer(in_network_dataset,
                                  out_network_analysis_layer,
                                  impedance_attribute,
                                  travel_from_to,
                                  )
else:
    print("Network analysis tool is not available.")

# # #select by attribute to narrow down
# in_table = #table generated from list of vaccination sites that are located within the buffer zone or within the service area
# field_names = [] #attributes we'd like to choose
#
# arcpy.da.SearchCursor(in_table, field_names)
