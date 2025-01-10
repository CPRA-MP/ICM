# Assesses the contiguity of land in the the ICMs lndtype output by determining the number of cell expansions needed for a given land cell to be contiguous with the largest landmass
# todo turn some of the repetitive gdal stuff into functions
# todo overrides are written into the output, it probably doesnt matter but that really should be just intermediate

import numpy as np
from osgeo import gdal, ogr
import os
#from datetime import datetime
from scipy.ndimage import label, binary_erosion, binary_dilation, maximum_filter

# Inputs
workspace = r"C:\Users\tnelson\Moffatt & Nichol\2029 LA Coastal Master Plan - MP29_GIS\LandContiguity"
input_raster_path = os.path.join(workspace, 'test_in', "MP2023_S08_G521_C000_U00_V00_SLA_O_52_52_W_lndtyp.tif")
override_shapefile_path = os.path.join(workspace, 'test_in',"overridepoly.shp") # overrides values to manually allow contiguity (e.g. across the intracoastal)
override_field = "override" # field in override_shapefile with override values (0 or 1)
output_raster_path = os.path.join(workspace, 'test_out', "Contiguity_G521_52_sag0.tif")

max_iterations = 40 # everything left unassigned at the end gets "999"

do_preprocess = True # true if using landuse as input, can change to false if inputing a prepped binary
shrinkandgrow_number = 0# Number of cycles to shrink and regrow input to reduce small isolated cells & thin ridges during preprocessing; 0 to skip the process; 2 = shrink shrink grow grow; bypassing preprocessing bypasses this too

# maps land use values to binary (land use code: binary assignment)
value_mapping = {
    -9999: 1,
    1: 1,
    2: 0,
    3: 0,
    4: 1,
    5: 0}

do_exportintermediates = False
# Intermediates
## only exported if do_exportintermediates = True
debug_largest_component_path = os.path.join(workspace, "test_out", "largest_component.tif")
debug_distance_raster_0_path = os.path.join(workspace, "test_out", "distance_raster_0.tif")
debug_mapped_input_path = os.path.join(workspace, "test_out", "mapped_input_raster.tif")
debug_override_raster_path = os.path.join(workspace, "test_out", "override_raster.tif")
debug_shrinkandgrow_path = os.path.join(workspace, "test_out", "shrinkandgrow_raster.tif")

# Start timing
#start_time = datetime.now()

# open input raster
input_raster = gdal.Open(input_raster_path)
band = input_raster.GetRasterBand(1)
data = band.ReadAsArray()
rows, cols = data.shape
geotransform = input_raster.GetGeoTransform()
projection = input_raster.GetProjection()
driver = gdal.GetDriverByName("GTiff")

# land use to binary preprocessing
if do_preprocess:
    mapped_data = np.full_like(data, -999, dtype=np.int32)
    for original_value, binary_value in value_mapping.items():
        mapped_data[data == original_value] = binary_value
    data = mapped_data

# shrink and grow preprocessing
if shrinkandgrow_number > 0:
    structure = np.ones((3, 3), dtype=np.int32)
    current_data = data.copy()
    for _ in range(shrinkandgrow_number):
        shrunk_data = binary_erosion(current_data == 1, structure=structure).astype(np.int32)
        current_data = binary_dilation(shrunk_data, structure=structure).astype(np.int32)
    data = current_data
    if do_exportintermediates:
        shrinkandgrow_raster = driver.Create(debug_shrinkandgrow_path, cols, rows, 1, gdal.GDT_Int32)
        shrinkandgrow_raster.SetGeoTransform(geotransform)
        shrinkandgrow_raster.SetProjection(projection)
        shrinkandgrow_raster.GetRasterBand(1).WriteArray(data)
        shrinkandgrow_raster.GetRasterBand(1).SetNoDataValue(-999)
        shrinkandgrow_raster = None

# apply overrides from override polygon
override_array = np.full((rows, cols), -999, dtype=np.int32)
mem_driver = gdal.GetDriverByName("MEM")
override_raster = mem_driver.Create("", cols, rows, 1, gdal.GDT_Int32)
override_raster.SetGeoTransform(geotransform)
override_raster.SetProjection(projection)
override_band = override_raster.GetRasterBand(1)
override_band.SetNoDataValue(-999)
override_shapefile = ogr.Open(override_shapefile_path)
override_layer = override_shapefile.GetLayer()
gdal.RasterizeLayer(override_raster, [1], override_layer, options=["ATTRIBUTE=" + override_field])
override_array = override_raster.GetRasterBand(1).ReadAsArray()
override_raster = None

# Apply overrides
valid_override_mask = override_array != -999
data[valid_override_mask & (override_array == 1)] = 1
data[valid_override_mask & (override_array == 0)] = 0

if do_exportintermediates:
    override_raster = driver.Create(debug_override_raster_path, cols, rows, 1, gdal.GDT_Int32)
    override_raster.SetGeoTransform(geotransform)
    override_raster.SetProjection(projection)
    override_raster.GetRasterBand(1).WriteArray(override_array)
    override_raster.GetRasterBand(1).SetNoDataValue(-999)
    override_raster = None

# Expansion and Contiguity Analysis
structure = np.ones((3, 3), dtype=np.int32)
# get mode
labeled_raster, num_features = label(data == 1, structure=structure)
unique_labels, counts = np.unique(labeled_raster, return_counts=True)
# get largest landmass
largest_label = unique_labels[np.argmax(counts[1:]) + 1]  # Exclude background
expansioncount_raster = np.full_like(data, 999, dtype=np.int32)
largest_landmass = (labeled_raster == largest_label)
expansioncount_raster[largest_landmass] = 0

# write intermediates
if do_exportintermediates:
    # initial largest group
    largest_component = largest_landmass.astype(np.int32)
    largest_component_raster = driver.Create(debug_largest_component_path, cols, rows, 1, gdal.GDT_Int32)
    largest_component_raster.GetRasterBand(1).WriteArray(largest_component)
    largest_component_raster.SetProjection(projection)
    largest_component_raster.SetGeoTransform(geotransform)
    largest_component_raster = None
    # first expansion
    distance_raster_0_raster = driver.Create(debug_distance_raster_0_path, cols, rows, 1, gdal.GDT_Int32)
    distance_raster_0_raster.GetRasterBand(1).WriteArray(expansioncount_raster)
    distance_raster_0_raster.SetProjection(projection)
    distance_raster_0_raster.SetGeoTransform(geotransform)
    distance_raster_0_raster = None

current_raster = data.copy()

for iteration in range(1, max_iterations + 1):
    print(f"Iteration: {iteration}")
    expanded_raster = maximum_filter(current_raster, size=3)
    expanded_raster = np.where(data == 1, 1, expanded_raster)
    labeled_expanded_raster, _ = label(expanded_raster == 1, structure=structure)
    newly_connected = (labeled_expanded_raster == largest_label) & (expansioncount_raster == 999)
    expansioncount_raster[newly_connected] = iteration
    current_raster = expanded_raster

expansioncount_raster[data != 1] = -999
output_raster = driver.Create(output_raster_path, cols, rows, 1, gdal.GDT_Int32)
output_raster.GetRasterBand(1).WriteArray(expansioncount_raster)
output_raster.SetProjection(projection)
output_raster.SetGeoTransform(geotransform)
output_raster = None

#end_time = datetime.now()
#print(f"Runtime: {end_time - start_time}")
print(f"done")