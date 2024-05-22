# clips ICM input rasters based on template test domain raster. Checks that clipped rasters match and outputs summary file for xyz.
# last run with rasters pulled from ftp on 12/06
# Eric mentioned something about manually fixing blanks in the lavegmod clipped rasters
#from mp29MN_functions import *
import os
import arcpy
import csv
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
from osgeo import gdal


# inputs
username = 'tnelson'
path_rasterstoclip = r'C:\Users\{}\Moffatt & Nichol\2029 LA Coastal Master Plan - MP29_GIS\InputRasters\MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_M'.format(username)
envraster = os.path.join(path_rasterstoclip, 'MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_W_lndtyp.tif')
path_out = r'C:\Users\{}\Moffatt & Nichol\2029 LA Coastal Master Plan - MP29_GIS\TestDomain\temptesting'.format(username)
#path_out = r'C:\Users\{}]\Moffatt & Nichol\2029 LA Coastal Master Plan - MP29_GIS\TestDomain\TestDomainInputRasters\MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_M'.format(username)
rast_testdomain = r'C:\Users\{}\Moffatt & Nichol\2029 LA Coastal Master Plan - MP29_GIS\InputRasters\TestDomain\MP2029_test_domain.tif'.format(username)  # 1 for coverage, -9999 for no data

outprefix = 'testdomain_'
scratchgdb = r'C:\Users\{}\Moffatt & Nichol\2029 LA Coastal Master Plan - MP29_GIS\Mp29_master.gdb'.format(username)

nullvalue = -9999

csv_output_path = os.path.join(path_out, 'xyz_summary_data.csv')

# env
arcpy.env.overwriteOutput = True
arcpy.env.workspace = scratchgdb
arcpy.env.snapRaster = envraster
arcpy.env.cellSize = envraster
arcpy.env.extent = envraster

def describe_raster_properties(raster_path):
    # creates a dictionary of raster properties to check against the template
    desc = arcpy.Describe(raster_path)
    properties = {
        "columns": desc.width,
        "rows": desc.height,
        "cell_size": desc.meanCellWidth,
        "format": desc.format,
        "no_data_value": desc.noDataValue,
        "extent": desc.extent,
        "coordinate_system": desc.spatialReference.name
    }
    return properties

# consider moving to generic function script
def writecsv(csv_output_path, datatowrite, headerrow=None):
    with open(csv_output_path, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headerrow)
        if headerrow is not None:
            writer.writeheader()
        writer.writerows(datatowrite)


# list of rasters 
rasterstocliplist = arcpy.ListRasters()

# todo add step to pull rasters from ftp if thats beneficial, see ftppull function

# Get metadata from the template raster # todo make this a function
template_properties = describe_raster_properties(rast_testdomain)
summary_data = []

for raster in rasterstocliplist:
    print(raster.split("_")[-1])
    output_raster = os.path.join(path_out, f"clipped_{raster}")
    dq = "Value = " + str(nullvalue)
    clippedrast = Con(rast_testdomain, nullvalue, raster, dq)
    clippedrast.save(output_raster)
    # check stuff
    clippedraster_properties = describe_raster_properties(output_raster)
    for prop in template_properties:
        if template_properties[prop] != clippedraster_properties[prop]:
            print(f"{output_raster}: '{prop}' doesn't match the template")
    # Convert to xyz with gdal
    name_out = raster.split(".")[0]
    output_xyz = os.path.join(path_out, f"{outprefix}_{name_out}.xyz")
    input_ds = gdal.Open(output_raster)
    driver = gdal.GetDriverByName("XYZ")
    output_ds = driver.CreateCopy(output_xyz, input_ds)
    with open(output_xyz, 'r') as xyz_file:
        lines = xyz_file.readlines()
        x_values = [float(line.split()[0]) for line in lines]
        y_values = [float(line.split()[1]) for line in lines]
        z_values = [float(line.split()[2]) for line in lines]
        summary = {
            'Filename': f"clipped_{name_out}.xyz",
            'Min_X': min(x_values),
            'Max_X': max(x_values),
            'Min_Y': min(y_values),
            'Max_Y': max(y_values),
            'Min_Z': min(z_values),
            'Max_Z': max(z_values),
            'Number_of_Rows': len(lines)
        }
        summary_data.append(summary)
    # Close datasets
    input_ds = None
    output_ds = None

# output summary csv
csvheader = ['Filename', 'Min_X', 'Max_X', 'Min_Y', 'Max_Y', 'Min_Z', 'Max_Z', 'Number_of_Rows']
writecsv(csv_output_path, summary_data, csvheader)
