import os, sys, subprocess
import numpy as np
from osgeo import gdal, ogr
from scipy.ndimage import label, binary_erosion, binary_dilation, maximum_filter
import zipfile

s = int(sys.argv[1])
g = int(sys.argv[2])
y = int(sys.argv[3])


input_raster_path_zipped = f'/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/S{s:02d}/G{g:03d}/geomorph/output/tif/MP2023_S{s:02d}_G{g:03d}_C000_U00_V00_SLA_O_{y:02d}_{y:02d}_W_lndtyp.tif.zip'
input_raster_path_unzipped = input_raster_path_zipped[:-4]  # remove .zip extension

output_raster_path = f'/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/S{s:02d}/G{g:03d}/geomorph/output/tif/MP2023_S{s:02d}_G{g:03d}_C000_U00_V00_SLA_O_{y:02d}_{y:02d}_W_contiguity.tif'
# tif used to override land values (e.g. to allow free movement over the GIWW)
override_raster_path = r'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/LandContiguity/ContiguityOverride.tif'

max_iterations = 80 # everything left unassigned at the end gets "999"
shrinkandgrow_number = 2# Number of cycles to shrink and regrow input to reduce small isolated cells & thin ridges during preprocessing; 0 to skip the process; 2 = shrink shrink grow grow; bypassing preprocessing bypasses this too
nodatavalue = -999
# maps land use values to binary (land use code: binary assignment)
value_mapping = {
    -9999: 1,
    1: 1,
    2: 0,
    3: 0,
    4: 1,
    5: 0}

#unzip
unzipped_temp = False
if os.path.exists(input_raster_path_zipped):
    with zipfile.ZipFile(input_raster_path_zipped, 'r') as zip_ref:
        # Extract only the .tif
        for file in zip_ref.namelist():
            if file.endswith('.tif'):
                zip_ref.extract(file, os.path.dirname(input_raster_path_zipped))
                # Rename extracted file to expected unzipped path if different
                extracted_path = os.path.join(os.path.dirname(input_raster_path_zipped), file)
                if extracted_path != input_raster_path_unzipped:
                    os.rename(extracted_path, input_raster_path_unzipped)
                unzipped_temp = True
                break
else:
    print(f"Zipped input raster not found, checking for unzipped raster: {input_raster_path_unzipped}")
    if not os.path.exists(input_raster_path_unzipped):
        raise FileNotFoundError(f"Neither zipped nor unzipped input raster found for S{s}, G{g}, Y{y}")


# land use to binary preprocessing
input_raster = gdal.Open(input_raster_path_unzipped)
band = input_raster.GetRasterBand(1) # note that all rasters are single band and this is used in the function below
currentiteration = band.ReadAsArray()
rows, cols = currentiteration.shape # note that this is applied to all rasters in the function below

# get common raster properties
geotransform = input_raster.GetGeoTransform()
projection = input_raster.GetProjection()
driver = gdal.GetDriverByName("GTiff")

binarylandwater = np.full_like(currentiteration, nodatavalue, dtype=np.int32)
for original_value, binary_value in value_mapping.items():
    binarylandwater[currentiteration == original_value] = binary_value
currentiteration = binarylandwater

def create_raster(output_path, array):
    raster = driver.Create(output_path, cols, rows, 1, gdal.GDT_Int32)
    raster.SetGeoTransform(geotransform)
    raster.SetProjection(projection)

    out_band = raster.GetRasterBand(1)  # Get the output raster's band
    out_band.WriteArray(array)
    out_band.SetNoDataValue(nodatavalue)

    # Flush and close
    out_band.FlushCache()
    raster = None  # This closes the file and writes to disk

# shrink and grow preprocessing
if shrinkandgrow_number > 0:
    structure = np.ones((3, 3), dtype=np.int32) # 3x3 refers to 8 neighbor expansion, not number of cells
    current_data = currentiteration.copy()
    for _ in range(shrinkandgrow_number):
        shrunk_data = binary_erosion(current_data == 1, structure=structure).astype(np.int32)
        current_data = binary_dilation(shrunk_data, structure=structure).astype(np.int32)
    currentiteration = current_data

# Load existing override raster
override_raster = gdal.Open(override_raster_path)
override_array = override_raster.GetRasterBand(1).ReadAsArray()
override_raster = None
# Apply overrides
valid_override_mask = override_array != nodatavalue
currentiteration[valid_override_mask & (override_array == 1)] = 1
currentiteration[valid_override_mask & (override_array == 0)] = 0

# Expansion and Contiguity Analysis
structure = np.ones((3, 3), dtype=np.int32)
# Get mode
labeled_raster, num_features = label(currentiteration == 1, structure=structure)
unique_labels, counts = np.unique(labeled_raster, return_counts=True)
# Get largest landmass
largest_label = unique_labels[np.argmax(counts[1:]) + 1]  # Exclude background
expansioncount_raster = np.full_like(currentiteration, 999, dtype=np.int32)
largest_landmass = (labeled_raster == largest_label)
expansioncount_raster[largest_landmass] = 0

# Expand & assign continuity
current_raster = currentiteration.copy()
for iteration in range(1, max_iterations + 1):
    print(f"Iteration: {iteration}")
    expanded_raster = maximum_filter(current_raster, size=3)
    expanded_raster = np.where(currentiteration == 1, 1, expanded_raster)
    labeled_expanded_raster, _ = label(expanded_raster == 1, structure=structure)
    newly_connected = (labeled_expanded_raster == largest_label) & (expansioncount_raster == 999)
    expansioncount_raster[newly_connected] = iteration
    current_raster = expanded_raster

# Write output
expansioncount_raster[currentiteration != 1] = nodatavalue
# debug
#print("Output array stats:")
#print("Min:", np.min(expansioncount_raster))
#print("Max:", np.max(expansioncount_raster))
#print("Unique values:", np.unique(expansioncount_raster))

create_raster(output_raster_path, expansioncount_raster)

# Zip the output raster & delete unzipped input
with zipfile.ZipFile(output_raster_path + '.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(output_raster_path, arcname=os.path.basename(output_raster_path))
os.remove(output_raster_path)
if unzipped_temp:
        os.remove(input_raster_path_unzipped)

