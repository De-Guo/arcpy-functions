# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 17:41:49 2017

@author: Dijun Guo
"""
import numpy as np
import arcpy, os

def create_geometry(coords, featureType):
    '''
    Create a geometry from given coords.

    <input>
    coords: array of coordinates to create geometry,1st column is longitude, 2nd
             column is latitude.[[longitude1, latitute1],[longitude2, latitute2]]
    featureType: which type of geometry to make. strim, can be 'Point', 'Polyline',
                'Polygon'
    </input>

    Return a geometry.

    '''

    if featureType is 'Point':
        X = float(coords[0, 0])
        Y = float(coords[0, 1])
        point = arcpy.Point(X, Y)
        geometry = arcpy.PointGeometry(point)

    else:
        array = arcpy.Array()

        for idx in range(coords.shape[0]):
            X = float(coords[idx, 0])
            Y = float(coords[idx, 1])
            array.add(arcpy.Point(X, Y))

        if featureType is 'Polygon':
            geometry = arcpy.Polygon(array)

        if featureType is 'Polyline':
            geometry = arcpy.Polyline(array)

    return geometry


##:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::##

def insert_feature(featureClass, cursorField, rows):
    '''
    Function to insert rows to a feature class.

    <input>
    featureClass: the feature class to insert geometries to
    cursorField: the field list for insertcursor
    rows: the geometries. Format is [[row1],[row2]]
    </input>

    No return.
    '''

    cursor = arcpy.da.InsertCursor(featureClass, cursorField)

    for row in rows:
        print(row)
        cursor.insertRow(row)

    del cursor



##:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::##
def add_field(featureClass, columnName, columnFormat, strLength):
    '''
    Function to add field to a feature class.

    <input>
    featureClass: the feature class to add field to
    columnName: the attribute field to add
    columnFormat: the format of attribute field
    strLength: length of string if the field format is string
    </input>

    '''
    #for idx in range(len(columnName)):
    for idx in range(len(columnName)):
        name = columnName[idx]
        fmt = columnFormat[idx]
        print(name, fmt)
        if fmt is 'i':
            fmt = 'LONG'
            arcpy.AddField_management(featureClass,name,fmt)
        elif fmt is 'f':
            fmt = 'DOUBLE'
            arcpy.AddField_management(featureClass,name,fmt)
        elif fmt[0] is 'S':
            fmt = 'TEXT'
            arcpy.AddField_management(featureClass,name,fmt, field_length=strLength)
        else:
            raise('Add field type choice')


###############################################################################
path =  r'E:\project\secondary_detection\shapefile'
os.chdir(path)

columnName = ['index']
columnFormat = ['S20']


#Create feature class#########################
sr = arcpy.SpatialReference(104903) #GCS Moon 2000
featureClass = 'grid_polygon.shp'
arcpy.CreateFeatureclass_management(path, featureClass,
                                "POLYGON", spatial_reference=sr)
add_field(featureClass, columnName, columnFormat, 50)


x = np.arange(-180, 181, 20)
y = np.arange(90, -91, -20)


for r in range(len(y)-1):
    for c in range(len(x)-1):
        print('Run %rRow_%rCol'%(r, c))
        xLeft = x[c]
        xRight  = x[c+1]
        yUpper = y[r]
        yLower = y[r+1]

        longitude = np.array([xLeft, xRight, xRight, xLeft]).reshape([4,1])
        latitude = np.array([yUpper, yUpper, yLower, yLower]).reshape([4,1])
        
        coords = np.c_[longitude, latitude]
        print(coords)

        geometry = create_geometry(coords, 'Polygon')

        ##write geometry to  feature class
        cursorField = ['SHAPE@', 'index']
        rows = [[geometry, 'Row%r_Col%r'%(r, c)]]
        

        insert_feature(featureClass, cursorField, rows)

        
print('Assignment done')        
#arcpy.management.Delete(featureClass)
        


