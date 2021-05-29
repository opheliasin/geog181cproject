#######PLEASE TYPE YOUR CODE UNDER YOUR RESPECTIVE SECTION##########

####################MARI##################################################


########################DAISY#############################################



###########################RYUICHI########################################



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
