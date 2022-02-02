import numpy as np

def dict2asc_flt(mapping_dict,outfile,asc_grid,asc_header,write_mode):
    # this function maps a dictionary of floating point data into XY space and saves as a raster file of ASCII grid format
    # this function does not return anything but it will save 'outfile' to disk

    # ASCII grid format description: http://resources.esri.com/help/9.3/arcgisengine/java/GP_ToolRef/spatial_analyst_tools/esri_ascii_raster_format.htm

    # 'mapping_dict' is a dictionary with grid cell ID as the key and some value for each key
    # 'outfile' is the filename (full path) of the output .asc raster text file to be saved
    # 'asc_grid' is a numpy array that is the grid structure of an ASCII text raster
    # 'asc_header' is a string that includes the 6 lines of text required by the ASCII grid format

    msg = '\ndid not save %s' % (outfile)
    with open(outfile, mode=write_mode) as outf:
        outf.write(asc_header)
        for row in asc_grid:
            nc = 0
            for col in row:
                gid_map = row[nc]
                if gid_map > 0:                     # if the ASC grid has a no data cell (-9999) there will be no dictionary key, the else criterion is met and it keeps the no data value (-9999)
                    try:
                        gid_val = float(mapping_dict[gid_map] )
                    except:
                        gid_val = -9999
                else:
                    gid_val = float(gid_map)
                if nc == 0:
                    rowout = '%0.4f'  % gid_val
                else:
                    rowout = '%s %0.4f' % (rowout,gid_val)
                nc += 1
            outf.write('%s\n' % rowout)
            msg = '\nsuccessfully saved %s' % (outfile)
    return msg



# input files
sav_data_file = 'E:/ICM/S07/G500/MP2023_S07_G500_C000_U00_V00_SLA_O_16_16_W_SAV_LAVegModScale.csv'
asc_grid_file = 'E:/ICM/S07/G500/veg_grid.asc'

# output file
sav_grid_file = 'E:/ICM/S07/G500/MP2023_S07_G500_C000_U00_V00_SLA_O_16_16_W_SAV_LAVegModScale.asc'

# read in asci grid structure
asc_grid_ids = np.genfromtxt(asc_grid_file,skip_header=6,delimiter=' ',dtype='int')
asc_grid_head = 'ncols 1052\nnrows 365\nxllcorner 404710\nyllcorner 3199480\ncellsize 480\nNODATA_value -9999\n'

# read SAV csv file and map to ASCI raster grid
sav_dict = {}
with open(sav_data_file,mode='r') as grid_data:
    nline = 0
    for line in grid_data:
        if nline > 0:
            gr = int(float(line.split(',')[0]))
            sav = line.split(',')[1]
            sav_dict[gr] = sav
        nline += 1

print(dict2asc_flt(sav_dict,sav_grid_file,asc_grid_ids,asc_grid_head,write_mode='w') )