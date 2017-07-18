"""
Created on Wed Jul 12 13:34:32 2017

This code can create a grid at specified spatial reference.
The grid can be created by resolution of by square number at
x and y coordinates.

@author: Dijun Guo
"""

import arcpy
import numpy as np


################################### INPUT ##################################
direcory = r'E:\project\Apollo_basin'
srf = direcory+r'\auxiliary_data\apollo_basin_TransMercator.prj'

arcpy.env.workspace = direcory+r'\features.gdb'

#[left, right, up, down] unit as the unit in spatial reference
extent = [-320000, 425000, 490000, -320000]

resolution = [40000, 40000] #[x-resolution, y-resolution]
number = [15, 18] #[x-number, y-number], square number in x and y direction

method = 'number' #Which way to define the grid, by 'number' or 'resolution'

featureType = 'POLYGON' #'POLYGON' or 'POLYLINE'
fc = 'investigation_grid_'+featureType # The name of featureclass file
###########################################################################
#
#
################################# FUNCTION ################################


##:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def vertic_to_geometry(vertics, featureType):
    '''
    Create a geometry from given vertics.

    <input>
    vertics: array of vertics to create geometry,1st column is longitude, 2nd
             column is latitude. [[longitude1, latitute1],[longitude2, latitute2]]
    featureType: which type of geometry to make. string, can be 'POLYINE',
                'POLYGON'
    </input>

    Return a geometry.

    '''
    array = arcpy.Array()

    for idx in range(vertics.shape[0]):
        X = vertics[idx, 0]
        Y = vertics[idx, 1]

        array.add(arcpy.Point(X, Y))

    if featureType is 'POLYGON':
        geometry = arcpy.Polygon(array)

    if featureType is 'POLYLINE':
        geometry = arcpy.Polyline(array)

    return geometry

##:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def create_square(featureClass, cursorFields, rows):
    '''
    Function to insert rows to a feature class.

    <input>
    featureClass: the feature class to insert geometries to
    cursorFields: the field list for insertcursor
    rows: the geometries. Format is [[row1],[row2]]
    </input>

    No return.
    '''

    cursor = arcpy.da.InsertCursor(featureClass, cursorFields)

    for row in rows:
        #print(row)
        cursor.insertRow(row)

    del cursor

###########################################################################
#
#
################################ MAIN #####################################

# Create featureclass of output grid
print('Delete the featureclass if it is exist\n')
try:
    arcpy.Delete_management(fc)
except:
    print('\n No grid featureclass exist before process\n')

sr = arcpy.SpatialReference(srf)
arcpy.CreateFeatureclass_management(arcpy.env.workspace, fc, featureType,
                                    spatial_reference=sr)

# Add fieldname
arcpy.AddField_management(fc, 'icol', 'SHORT')
arcpy.AddField_management(fc, 'irow', 'SHORT')

#
#

# Create grid intersection points' coordinates
if method == 'number':
    xlist = np.linspace(extent[0], extent[1], number[0])
    ylist = np.linspace(extent[2], extent[3], number[1])

elif method == 'resolution':
    xlist = np.arange(extent[0], extent[1], resolution[0])
    ylist = np.arange(extent[2], extent[3], -resolution[1])

    # Deal with the last boundary
    if (extent[1]-xlist[-1])>(resolution[0]/2.0):
        xlist = np.r_[xlist, extent[1]]
    else:
        xlist[-1] = extent[1]

    if (ylist[-1]-extent[3])>(resolution[1]/2.0):
        ylist = np.r_[ylist, extent[3]]
    else:
        ylist[-1] = extent[3]

#
#

# Create grid
rows = []
print('Create feature records!\n')

for icol in range(len(xlist)-1):

    xl = xlist[icol]  #left
    xr = xlist[icol+1] #right

    for irow in range(len(ylist)-1):

        print('Create number %d col, number %d row square\n'%(icol, irow))

        yu = ylist[irow]  #upper
        yl = ylist[irow+1]  #lower

        #
        if featureType == 'POLYLINE':
            vertics = np.array([[xl, yu], [xr, yu], [xr, yl],
                                [xl, yl],[xl, yu]])
        else:
            vertics = np.array([[xl, yu], [xr, yu], [xr, yl], [xl, yl]])        
        geometry = vertic_to_geometry(vertics, featureType)

        #
        row = [geometry, icol, irow]
        rows.append(row)

#
#

print('Write records to featureclass file\n')
cursorFields = ['SHAPE@', 'icol', 'irow']
create_square(fc, cursorFields, rows)

#
print('Assignment is done!')
