#######PLEASE TYPE YOUR CODE UNDER YOUR RESPECTIVE SECTION##########

####################MARI##################################################


########################DAISY#############################################



###########################RYUICHI########################################
import arcpy, os
from arcpy import env
folderpath = r"C:\Users\RU313697\Desktop\GIS Programming\Final Project"
arcpy.env.workspace = folderpath  
arcpy.env.overwriteOutput = True 

# get the mxd and the layout element list
mxd = arcpy.mapping.MapDocument(folderpath+"/Network_Analysis.mxd")

mxd.title = "GEOG181C Group Project Maps"
mxd.author = "Mari Bouwman, Chalsea Montellano, Ryuichi Utsu, Ophelia Sin, Daisy Yan"

lyr_list = arcpy.mapping.ListLayers(mxd)

print lyr_list

for lyr in lyr_list:
    if lyr.name == "Selected Vaccination Site":
        Vaccination_Site = lyr
        if Vaccination_Site.supports("LABELCLASSES"):
            Vaccination_Site.showClassLabels = True
            Vaccination_Site.expression = "{}".format("name")
            Vaccination_Site.showLabels = True
            
    if lyr.name == "Optimal Route":
        Route = lyr

# Create a new, empty pdf document for the mapbook
pdf_filename = folderpath + r"\AutomatedMapping.pdf" #create empty pdf to store tmp maps
if os.path.exists(pdf_filename):
    os.remove(pdf_filename)
finalPDF = arcpy.mapping.PDFDocumentCreate(pdf_filename)

tmpPDF = folderpath + "/tmp.pdf" #create temp pdf to store maps
    
for row in arcpy.da.SearchCursor(Vaccination_Site, ["SHAPE@","name","fulladdr"]):
    #get data frame
    layout_frame = arcpy.mapping.ListLayoutElements(mxd, "DATAFRAME_ELEMENT")[0]
    
    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[3]
    title.text = "The Optimal Route from UCLA to a Vaccination Site"
    elm1 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1] 
    elm1.text = "Name: " + str(row[1])
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[2] 
    elm2.text = "Address: " + str(row[2])
    elm3 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
    elm3.text = "Total Travel Time: 7min, Total Distance: 3.4mil"

for route in arcpy.da.SearchCursor(Route, ["SHAPE@"]):
    layout_frame.extent = route[0].extent # customize extent
    layout_frame.scale = layout_frame.scale * 1.8 #customize zoom scale
    
    arcpy.mapping.ExportToPDF(mxd, tmpPDF)
    finalPDF.appendPages(tmpPDF)

finalPDF.saveAndClose( )
if os.path.exists(tmpPDF):
    os.remove(tmpPDF)

del mxd, tmpPDF, finalPDF, row,

print "End of map production."


###########################CHALSEA########################################
#Insert cursor to create and display new table showing 10 nearest vaccination sites with most relevant information for user
#need a table that is sorted by 'distance' beforehand

folderPath = r"C:\Users\cnmre\OneDrive\Documents\181C GIS Programming and Dev\Covid-19_Vaccination_Provider_Locations_in_the_United_States"

import arcpy, os

arcpy.env.workspace = folderPath
arcpy.overwriteOutput = True

#define local variables
vaccinationSites = os.path.join(folderPath, "Covid-19_Vaccination_Provider_Locations_in_the_United_States.shp")
outTable = "Top_Ten_Nearest_Vaccination_Sites.dbf"
newFields = [('NAME', 'TEXT'), ('ADDRESS', 'TEXT'), ('MUNICIPAL', 'TEXT'), ('PHONE', 'TEXT'), ('OPER_HRS', 'TEXT'),\
             ('DRIVE_THRU', 'TEXT'),('APPT_REQ', 'TEXT'),('CALL_REQ', 'TEXT'), ('WHEELCHAIR', 'TEXT'), ('WEBSITE', 'TEXT')]

#create a new table and add 10 new fields
arcpy.CreateTable_management(folderPath, outTable)
for field in newFields:
    arcpy.AddField_management(outTable, field[0], field[1])

#insert cursor
insert = ['NAME', 'ADDRESS', 'MUNICIPAL', 'PHONE', 'OPER_HRS', 'DRIVE_THRU', 'APPT_REQ', 'CALL_REQ', 'WHEELCHAIR', 'WEBSITE']
insertCursor = arcpy.da.InsertCursor(outTable, insert)

#search cursor and populate rows for top 10 rows (function to acquire only the top 10 rows still a work in progress)
originalFields = ['name', 'fulladdr', 'municipali', 'phone', 'operhours', 'drive_thro', 'appt_only', 'call_first', \
                  'Wheelchair', 'vaccine_ur']
searchCursor = arcpy.da.SearchCursor(vaccinationSites, originalFields)
for row in searchCursor:
    rows = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]
    insertCursor.insertRow(rows)

#clean up and unlock
del field, insertCursor, searchCursor, row, rows

#to signal end of program
print "Table successfully created!"


###########################OPHELIA########################################
vac_sites = folderpath + "/data/Covid-19_Vaccination_Provider_Locations_in_the_United_States/Covid-19_Vaccination_Provider_Locations_in_the_United_States.shp"
arcpy.MakeFeatureLayer_management(vac_sites, "vac_sites")
la_county = folderpath + "/data/County_Boundary/County_Boundary.shp"
arcpy.MakeFeatureLayer_management(la_county, "la_county")
arcpy.SelectLayerByLocation_management("vac_sites", "intersect", "la_county")

p =[34.067565101060275, -118.45344143556794]
pt = arcpy.Point()
ptGeom = [] 
pt.X = p[0]
pt.Y = p[1]
ptGeom.append(arcpy.PointGeometry(pt))

out_path = folderpath
out_name = "origin_point.shp"
geometry_type = "POINT"
template = ""
has_m = "DISABLED"
has_z = "DISABLED"
spatial_reference = arcpy.SpatialReference("NAD 1983")

if os.path.exists(out_name):
    os.remove(out_name)

arcpy.CreateFeatureclass_management(out_path, out_name, geometry_type, template, has_m, has_z, spatial_reference)
arcpy.CopyFeatures_management(ptGeoms, out_name)

where_clause = arcpy.AddFieldDelimiters("vac_sites", "appt_only") + "= 'No'"

arcpy.SelectLayerByAttribute_management("vac_sites", "SUBSET_SELECTION", where_clause)

vac_sites_selected = "vac_sites_selected.shp"
arcpy.CreateFeatureclass_management(folderpath, vac_sites_selected, geometry_type, template, has_m, has_z, spatial_reference)
arcpy.CopyFeatures_management("vac_sites", vac_sites_selected)

