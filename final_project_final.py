
import arcpy, os
from arcpy import env

# Check out the Network Analyst extension license
arcpy.CheckOutExtension("Network")

# Set environment settings
folder_path = r"C:\Users\Ophelia\geog181cproject"
env.workspace = folder_path
env.overwriteOutput = True

vac_sites = folder_path + "/data/Covid-19_Vaccination_Provider_Locations_in_the_United_States/Covid-19_Vaccination_Provider_Locations_in_the_United_States.shp"
arcpy.MakeFeatureLayer_management(vac_sites, "vac_sites")
la_county = folder_path + "/data/County_Boundary/County_Boundary.shp"
arcpy.MakeFeatureLayer_management(la_county, "la_county")
arcpy.SelectLayerByLocation_management("vac_sites", "intersect", "la_county")

long = -118.45344143556794
lat = 34.067565101060275
pt = arcpy.Point()
ptGeom = []
pt.X = long
pt.Y = lat
ptGeom.append(arcpy.PointGeometry(pt))

starting_point_base = "starting_point.shp"
geometry_type = "POINT"
template = ""
has_m = "DISABLED"
has_z = "DISABLED"
sr = arcpy.SpatialReference(4269)

starting_point = os.path.join(folder_path, starting_point_base)

if os.path.exists(starting_point):
    os.remove(starting_point)

arcpy.CreateFeatureclass_management(folder_path, starting_point_base, geometry_type, template, has_m, has_z, sr)
arcpy.CopyFeatures_management(ptGeom, starting_point)

starting_point_spatial_ref = arcpy.Describe(starting_point).spatialReference
if starting_point_spatial_ref.name == "Unknown":
    arcpy.management.DefineProjection(starting_point, sr)
arcpy.RecalculateFeatureClassExtent_management(starting_point)

where_clause = arcpy.AddFieldDelimiters("vac_sites", "appt_only") + "= 'No'"

arcpy.SelectLayerByAttribute_management("vac_sites", "SUBSET_SELECTION", where_clause)

vac_sites_selected_base = "vac_sites_selected.shp"
vac_sites_selected = os.path.join(folder_path, vac_sites_selected_base)

arcpy.CreateFeatureclass_management(folder_path, vac_sites_selected_base, geometry_type, template, has_m, has_z,
                                    sr)

vac_sites_selected_spatial_ref = arcpy.Describe(vac_sites_selected).spatialReference
if vac_sites_selected_spatial_ref.name == "Unknown":
    arcpy.management.DefineProjection(vac_sites_selected, sr)
arcpy.CopyFeatures_management("vac_sites", vac_sites_selected)


# Set local variables
inNetworkDataset = folder_path + "/LA network/Other related dataset/LA_Network1_ND.nd"
outNALayerName = "Vac_Sites"
impedanceAttribute = "Time"
accumulateAttributeName = ["Miles"]
inFacilities = vac_sites_selected
inIncidents = starting_point  # insert location shp file here
outLayerFile = folder_path + "/" + outNALayerName + ".lyr"

# Create a new closest facility analysis layer. Apart from finding the drive
# time to the closest warehouse, we also want to find the total distance. So
# we will accumulate the "Miles" impedance attribute.
outNALayer = arcpy.na.MakeClosestFacilityLayer(inNetworkDataset, outNALayerName,
                                               impedanceAttribute, "TRAVEL_TO",
                                               "", 10, accumulateAttributeName,
                                               "NO_UTURNS")

# Get the layer object from the result object. The closest facility layer can
# now be referenced using the layer object.
outNALayer = outNALayer.getOutput(0)

# Get the names of all the sublayers within the closest facility layer.
sublayer_names = arcpy.na.GetNAClassNames(outNALayer)

# Stores the layer names that we will use later
facilitiesLayerName = sublayer_names["Facilities"]
incidentsLayerName = sublayer_names["Incidents"]

# Load the warehouses as Facilities using the default field mappings and
# search tolerance
arcpy.na.AddLocations(outNALayer, facilitiesLayerName, inFacilities, "", "")

# Load user location as incident. Map the Name property from the NOM field
# using field mappings
fieldMappings = arcpy.na.NAClassFieldMappings(outNALayer, incidentsLayerName)
fieldMappings["Name"].mappedFieldName = "NOM"
arcpy.na.AddLocations(outNALayer, incidentsLayerName, inIncidents,
                      fieldMappings, "")

# Solve the closest facility layer
arcpy.na.Solve(outNALayer)

# Save the solved closest facility layer as a layer file on disk with
# relative paths
arcpy.management.SaveToLayerFile(outNALayer, outLayerFile, "RELATIVE")

print "Script completed successfully"

#convert "routes" layer to shapefile
routes = arcpy.mapping.ListLayers(outNALayer, "Routes")[0]
arcpy.conversion.FeatureClassToShapefile(routes, folder_path)

print "Shape file of routes has been exported."

### Table Manipulation with Cursors - create new table showing 10 nearest vaccination sites with most relevant information for user ###

# define local variables
originalSites = vac_sites_selected
naSites = os.path.join(folder_path, "outNAlayer.shp")
top_10_closest_facilities = folder_path + "top_10_closest_facilities.shp" 
outTable = "Ten_Nearest_Vaccination_Sites.dbf"
newFields = [('NAME', 'TEXT'), ('ADDRESS', 'TEXT'), ('MUNICIPAL', 'TEXT'), ('PHONE', 'TEXT'), ('OPER_HRS', 'TEXT'), \
             ('DRIVE_THRU', 'TEXT'), ('APPT_REQ', 'TEXT'), ('CALL_REQ', 'TEXT'), ('WHEELCHAIR', 'TEXT'), ('WEBSITE', 'TEXT'), \
            ('TOTAL_MILE', 'DOUBLE'), ('TOTAL_TIME', 'DOUBLE')]

#join original table and network analysis table
arcpy.SpatialJoin_analysis(originalSites, naSites, top_10_closest_facilities, "JOIN_ONE_TO_ONE", "KEEP_COMMON")

# create a new table and add 8 new fields
arcpy.CreateTable_management(folder_path, outTable)
for field in newFields:
    arcpy.AddField_management(outTable, field[0], field[1])

# insert cursor for new table
insert = ['NAME', 'ADDRESS', 'MUNICIPAL', 'PHONE', 'OPER_HRS', 'DRIVE_THRU', 'APPT_REQ', 'CALL_REQ', 'WHEELCHAIR', 'WEBSITE', 'TOTAL_MILE', 'TOTAL_TIME']
insertCursor = arcpy.da.InsertCursor(outTable, insert)

# search cursor and populate rows of new table using first 10 rows of sorted table
originalFields = ['name', 'fulladdr', 'municipali', 'phone', 'operhours', 'drive_thro', 'appt_only', 'call_first',
                  'Wheelchair', 'vaccine_ur', 'Total_Mile', 'Total_Time']
searchCursor = arcpy.da.SearchCursor(sortedSites, originalFields)
for row in searchCursor:
    rows = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]
    insertCursor.insertRow(rows)

# clean up local variables, cursors and cursor-related variables and unlock
del originalSites, naSites, sortedSites, outTable, newFields, field, insert, insertCursor, originalFields, searchCursor, row, rows

# to signal end of program
print "Table successfully created!"


### RYUICHI
# get the mxd and the layout element list
mxd = arcpy.mapping.MapDocument(folderpath + "/Final_Project_Mapping.mxd")

mxd.title = "GEOG181C Group Project Maps"
mxd.author = "Mari Bouwman, Chalsea Montellano, Ryuichi Utsu, Ophelia Sin, Daisy Yan"

lyr_list = arcpy.mapping.ListLayers(mxd)

site_names = ['CVS_Pharmacy_Westwood_Blvd', 'CVS_Pharmacy_SantaMonica_Blvd', 'Brent_Air_Pharmacy',
              'West_Los_Angeles_VA_Medical_Center',
              'Total_Testing_Solutions_Century_City', 'Rite_Aid', 'CVS_Weyburn', 'CVS_Wellworth', 'CVS_SanVicente',
              'Ralphs_Pharmacy_Weyburn']

route_names = ['Brent_Air_Pharmacy_Route', 'Rite_Aid_Route', 'CVS_San_Vicente_Route', 'Total_Testing_Solution_Route',
               'CVS_Santa_Monica_Route', 'CVS_Weyburn_Route',
               'CVS_Westwood_Route', 'Ralphs_Weyburn', 'West_LA_Medical_Center_Route', 'CVS_Wellworth_Route']

# Create a new, empty pdf document for the mapbook
pdf_filename = folderpath + r"\Final_Project_Mapbook.pdf"  # create empty pdf to store tmp maps
if os.path.exists(pdf_filename):
    os.remove(pdf_filename)
finalPDF = arcpy.mapping.PDFDocumentCreate(pdf_filename)

tmpPDF = folderpath + "/tmp.pdf"  # create temp pdf to store maps

# Cover Page
for layer in lyr_list:
    if layer.name in site_names:
        layer.visible = False
    if layer.name in route_names:
        layer.visible = False
    if layer.name == 'Top_Ten_Nearest_Sites':
        layer.visible == True
        Vaccination_Sites = layer

layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]
layout_frame.extent = [-118.47278579903, 34.0290659746133, -118.433498230254, 34.0780797244016]
layout_frame.scale = layout_frame.scale * 1.4

title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
title.text = "The Locations of the 10 Nearest Vaccination Sites from UCLA"
elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
elm1.text = "Project by " + mxd.author
elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2]
elm2.text = mxd.title
elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
elm3.text = "Data Source: ArcGIS Hub and City of Los Angeles Hub"

arcpy.mapping.ExportToPDF(mxd, tmpPDF)
finalPDF.appendPages(tmpPDF)

# 1
for layer in lyr_list:
    if layer.name in site_names:
        layer.visible = False
    if layer.name in route_names:
        layer.visible = False
    if layer.name == 'CVS_Pharmacy_Westwood_Blvd':
        layer.visible = True
        CVS_Westwood = layer
    if layer.name == 'CVS_Westwood_Route':
        layer.visible = True
        CVS_Westwood_Route = layer

for row in arcpy.da.SearchCursor(CVS_Westwood, ["name", "fulladdr"]):
    # get data frame
    layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]

    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
    title.text = "The Optimal Route from UCLA to One of the Nearest Vaccination Sites"
    elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
    elm1.text = "Name: " + str(row[0])
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2]
    elm2.text = "Address: " + str(row[1])
    elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
    elm3.text = "Total Travel Time: 3 min, Total Distance: 1.2 mil"

for route in arcpy.da.SearchCursor(CVS_Westwood_Route, ["SHAPE@"]):
    layout_frame.extent = route[0].extent  # customize extent
    layout_frame.scale = layout_frame.scale * 1.8  # customize zoom scale

    arcpy.mapping.ExportToPDF(mxd, tmpPDF)
    finalPDF.appendPages(tmpPDF)
# 2
for layer in lyr_list:
    if layer.name in site_names:
        layer.visible = False
    if layer.name in route_names:
        layer.visible = False
    if layer.name == 'CVS_Pharmacy_SantaMonica_Blvd':
        layer.visible = True
        CVS_Santa_Monica = layer
    if layer.name == 'CVS_Santa_Monica_Route':
        layer.visible = True
        CVS_Santa_Monica_Route = layer

for row in arcpy.da.SearchCursor(CVS_Santa_Monica, ["name", "fulladdr"]):
    # get data frame
    layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]

    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
    title.text = "The Optimal Route from UCLA to One of the Nearest Vaccination Sites"
    elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
    elm1.text = "Name: " + str(row[0])
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2]
    elm2.text = "Address: " + str(row[1])
    elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
    elm3.text = "Total Travel Time: 6 min, Total Distance: 4.4 mil"

for route in arcpy.da.SearchCursor(CVS_Santa_Monica_Route, ["SHAPE@"]):
    layout_frame.extent = route[0].extent  # customize extent
    layout_frame.scale = layout_frame.scale * 1.8  # customize zoom scale

    arcpy.mapping.ExportToPDF(mxd, tmpPDF)
    finalPDF.appendPages(tmpPDF)

# 3
for layer in lyr_list:
    if layer.name in site_names:
        layer.visible = False
    if layer.name in route_names:
        layer.visible = False
    if layer.name == 'Brent_Air_Pharmacy':
        layer.visible = True
        Brent_Air_Pharmacy = layer
    if layer.name == 'Brent_Air_Pharmacy_Route':
        layer.visible = True
        Brent_Air_Pharmacy_Route = layer

for row in arcpy.da.SearchCursor(Brent_Air_Pharmacy, ["name", "fulladdr"]):
    # get data frame
    layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]

    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
    title.text = "The Optimal Route from UCLA to One of the Nearest Vaccination Sites"
    elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
    elm1.text = "Name: " + str(row[0])
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2]
    elm2.text = "Address: " + str(row[1])
    elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
    elm3.text = "Total Travel Time: 4 min, Total Distance: 2.2 mil"

for route in arcpy.da.SearchCursor(Brent_Air_Pharmacy_Route, ["SHAPE@"]):
    layout_frame.extent = route[0].extent  # customize extent
    layout_frame.scale = layout_frame.scale * 1.8  # customize zoom scale

    arcpy.mapping.ExportToPDF(mxd, tmpPDF)
    finalPDF.appendPages(tmpPDF)
# 4
for layer in lyr_list:
    if layer.name in site_names:
        layer.visible = False
    if layer.name in route_names:
        layer.visible = False
    if layer.name == 'West_Los_Angeles_VA_Medical_Center':
        layer.visible = True
        West_LA_Medical_Center = layer
    if layer.name == 'West_LA_Medical_Center_Route':
        layer.visible = True
        West_LA_Medical_Center_Route = layer

for row in arcpy.da.SearchCursor(West_LA_Medical_Center, ["name", "fulladdr"]):
    # get data frame
    layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]

    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
    title.text = "The Optimal Route from UCLA to One of the Nearest Vaccination Sites"
    elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
    elm1.text = "Name: " + str(row[0])
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2]
    elm2.text = "Address: " + str(row[1])
    elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
    elm3.text = "Total Travel Time: 5 min, Total Distance: 2.3 mil"

for route in arcpy.da.SearchCursor(West_LA_Medical_Center_Route, ["SHAPE@"]):
    layout_frame.extent = route[0].extent  # customize extent
    layout_frame.scale = layout_frame.scale * 1.8  # customize zoom scale

    arcpy.mapping.ExportToPDF(mxd, tmpPDF)
    finalPDF.appendPages(tmpPDF)

# 5
for layer in lyr_list:
    if layer.name in site_names:
        layer.visible = False
    if layer.name in route_names:
        layer.visible = False
    if layer.name == 'Total_Testing_Solutions_Century_City':
        layer.visible = True
        Total_Testing_Solutions = layer
    if layer.name == 'Total_Testing_Solution_Route':
        layer.visible = True
        Total_Testing_Solutions_Route = layer

for row in arcpy.da.SearchCursor(Total_Testing_Solutions, ["name", "fulladdr"]):
    # get data frame
    layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]

    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
    title.text = "The Optimal Route from UCLA to One of the Nearest Vaccination Sites"
    elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
    elm1.text = "Name: " + str(row[0])
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2]
    elm2.text = "Address: " + str(row[1])
    elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
    elm3.text = "Total Travel Time: 5 min, Total Distance: 2.3 mil"

for route in arcpy.da.SearchCursor(Total_Testing_Solutions_Route, ["SHAPE@"]):
    layout_frame.extent = route[0].extent  # customize extent
    layout_frame.scale = layout_frame.scale * 1.8  # customize zoom scale

    arcpy.mapping.ExportToPDF(mxd, tmpPDF)
    finalPDF.appendPages(tmpPDF)

# 6
for layer in lyr_list:
    if layer.name in site_names:
        layer.visible = False
    if layer.name in route_names:
        layer.visible = False
    if layer.name == 'Rite_Aid':
        layer.visible = True
        Rite_Aid = layer
    if layer.name == 'Rite_Aid_Route':
        layer.visible = True
        Rite_Aid_Route = layer

for row in arcpy.da.SearchCursor(Rite_Aid, ["name", "fulladdr"]):
    # get data frame
    layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]

    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
    title.text = "The Optimal Route from UCLA to One of the Nearest Vaccination Sites"
    elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
    elm1.text = "Name: " + str(row[0])
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2]
    elm2.text = "Address: " + str(row[1])
    elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
    elm3.text = "Total Travel Time: 3 min, Total Distance: 1.3 mil"

for route in arcpy.da.SearchCursor(Rite_Aid_Route, ["SHAPE@"]):
    layout_frame.extent = route[0].extent  # customize extent
    layout_frame.scale = layout_frame.scale * 1.8  # customize zoom scale

    arcpy.mapping.ExportToPDF(mxd, tmpPDF)
    finalPDF.appendPages(tmpPDF)

# 7
for layer in lyr_list:
    if layer.name in site_names:
        layer.visible = False
    if layer.name in route_names:
        layer.visible = False
    if layer.name == 'CVS_Weyburn':
        layer.visible = True
        CVS_Weyburn = layer
    if layer.name == 'CVS_Weyburn_Route':
        layer.visible = True
        CVS_Weyburn_Route = layer

for row in arcpy.da.SearchCursor(CVS_Weyburn, ["name", "fulladdr"]):
    # get data frame
    layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]

    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
    title.text = "The Optimal Route from UCLA to One of the Nearest Vaccination Sites"
    elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
    elm1.text = "Name: " + str(row[0])
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2]
    elm2.text = "Address: " + str(row[1])
    elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
    elm3.text = "Total Travel Time: 3 min, Total Distance: 1.3 mil"

for route in arcpy.da.SearchCursor(CVS_Weyburn_Route, ["SHAPE@"]):
    layout_frame.extent = route[0].extent  # customize extent
    layout_frame.scale = layout_frame.scale * 1.8  # customize zoom scale

    arcpy.mapping.ExportToPDF(mxd, tmpPDF)
    finalPDF.appendPages(tmpPDF)

# 8
for layer in lyr_list:
    if layer.name in site_names:
        layer.visible = False
    if layer.name in route_names:
        layer.visible = False
    if layer.name == 'CVS_Wellworth':
        layer.visible = True
        CVS_Wellworth = layer
    if layer.name == 'CVS_Wellworth_Route':
        layer.visible = True
        CVS_Wellworth_Route = layer

for row in arcpy.da.SearchCursor(CVS_Wellworth, ["name", "fulladdr"]):
    # get data frame
    layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]

    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
    title.text = "The Optimal Route from UCLA to One of the Nearest Vaccination Sites"
    elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
    elm1.text = "Name: " + str(row[0])
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2]
    elm2.text = "Address: " + str(row[1])
    elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
    elm3.text = "Total Travel Time: 4 min, Total Distance: 1.6 mil"

for route in arcpy.da.SearchCursor(CVS_Wellworth_Route, ["SHAPE@"]):
    layout_frame.extent = route[0].extent  # customize extent
    layout_frame.scale = layout_frame.scale * 1.8  # customize zoom scale

    arcpy.mapping.ExportToPDF(mxd, tmpPDF)
    finalPDF.appendPages(tmpPDF)

# 9
for layer in lyr_list:
    if layer.name in site_names:
        layer.visible = False
    if layer.name in route_names:
        layer.visible = False
    if layer.name == 'CVS_SanVicente':
        layer.visible = True
        CVS_San_Vicente = layer
    if layer.name == 'CVS_San_Vicente_Route':
        layer.visible = True
        CVS_San_Vicente_Route = layer

for row in arcpy.da.SearchCursor(CVS_San_Vicente, ["name", "fulladdr"]):
    # get data frame
    layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]

    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
    title.text = "The Optimal Route from UCLA to One of the Nearest Vaccination Sites"
    elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
    elm1.text = "Name: " + str(row[0])
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2]
    elm2.text = "Address: " + str(row[1])
    elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
    elm3.text = "Total Travel Time: 6 min, Total Distance: 3.2 mil"

for route in arcpy.da.SearchCursor(CVS_San_Vicente_Route, ["SHAPE@"]):
    layout_frame.extent = route[0].extent  # customize extent
    layout_frame.scale = layout_frame.scale * 1.8  # customize zoom scale

    arcpy.mapping.ExportToPDF(mxd, tmpPDF)
    finalPDF.appendPages(tmpPDF)

# 10
for layer in lyr_list:
    if layer.name in site_names:
        layer.visible = False
    if layer.name in route_names:
        layer.visible = False
    if layer.name == 'Ralphs_Pharmacy_Weyburn':
        layer.visible = True
        Ralphs_Weyburn = layer
    if layer.name == 'Ralphs_Weyburn':
        layer.visible = True
        Ralphs_Weyburn_Route = layer

for row in arcpy.da.SearchCursor(Ralphs_Weyburn, ["name", "fulladdr"]):
    # get data frame
    layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]

    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
    title.text = "The Optimal Route from UCLA to One of the Nearest Vaccination Sites"
    elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
    elm1.text = "Name: " + str(row[0])
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2]
    elm2.text = "Address: " + str(row[1])
    elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
    elm3.text = "Total Travel Time: 3 min, Total Distance: 1.3 mil"

for route in arcpy.da.SearchCursor(Ralphs_Weyburn_Route, ["SHAPE@"]):
    layout_frame.extent = route[0].extent  # customize extent
    layout_frame.scale = layout_frame.scale * 1.8  # customize zoom scale

    arcpy.mapping.ExportToPDF(mxd, tmpPDF)
    finalPDF.appendPages(tmpPDF)

finalPDF.saveAndClose()
if os.path.exists(tmpPDF):
    os.remove(tmpPDF)

del mxd, tmpPDF, finalPDF, row,

print
"End of map production."


