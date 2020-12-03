import numpy as np
import datetime as dt

print('\n\n mapping some stuff. how exciting...\n\n')
# input file paths and filenames here
input_directory = r'D:\ICM\S03\G028'
output_directory = r'D:\ICM\S03\G028'

output_asc = r'%s\veg\MP2023_S03_G028_C000_U00_V00_SLA_N_01_50_H_acsal.asc' % output_directory


# confirm details for ascii grid details - check that files exist at location and header text is correct
grid_lookup_file = r'%s\hydro\grid_lookup_500m.csv' % input_directory
asc_grid_file = r'%s\veg\veg_grid.asc' % input_directory
asc_head = 'ncols 1259\nnrows 615\nxllcorner 390500\nyllcorner 3125000\ncellsize 500\nNODATA_value -9999\n'




# function definitions below - edit at your own risk, or preferably not at all - they're already perfect.

# STOP - TURN AROUND - GO HOME

def compout2dict(input_file,import_column): 
    # this function reads the compartment-based summary output file 'input_file' into a dictionary
    # the first row in input_file must contain header text - this will be skipped on import
    # the first column in 'input_file' must contain ICM-Hydro compartment ID numbers (this will be used as keys in the dict)
    # the key is of type integer and the values are of type float
    
    # 'import_column'  is the zero-indexed column number that contains the data to be imported and mapped
    # import_column = 7 will import the the maximum 2-week mean salinity in compartment_out_YYYY.csv
    
    # this function returns a dictionary 'comp_ave' that has ICM-Hydro compartment ID as the key and a single average for each compartment as the value

    data = np.genfromtxt(input_file,dtype='str',delimiter=',',skip_header=1)
    comp_ave = {}
    nrow = 0
    for row in data:
        comp = int(float(row[0]))
        val = float(row[import_column])
        comp_ave[comp] = val
        nrow += 1
    
    return comp_ave

def comp2grid(comp_data_dict,grid_comp_dict):
    # this function maps ICM-Hydro compartment level data to the 500-m grid
    # this function returns a dictionary 'grid_data' that has grid ID as the key and the respective compartment-level data as the value
    
    # 'comp_data_dict' is a dictionary with ICM-Hydro compartment as the key and some value to be mapped to the grid as the value
    # 'grid_comp_dict' is a dictionary with grid ID as the key and the corresponding ICM-Hydro compartment number as the value
    
        
    grid_data = {}
    for gid in grid_comp_dict.keys():
        cid = grid_comp_dict[gid]
        grid_data[gid] = comp_data_dict[cid]
    
    return grid_data

def dict2asc_int(mapping_dict,outfile,asc_grid,asc_header,write_mode):
    # this function maps a dictionary of data into XY space and saves as a raster file of ASCII grid format
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
                    gid_val = mapping_dict[gid_map] 
                else:
                    gid_val = gid_map
                if nc == 0:
                    rowout = '%d'  % gid_val
                else:
                    rowout = '%s %d' % (rowout,gid_val)
                nc += 1
            outf.write('%s\n' % rowout)
            msg = '\nsuccessfully saved %s' % (outfile)
    return msg

def file_len(fname):
    # this function counts the number of lines in a text file
    # this function returns an integer value that is the number of lines in the file 'fname'
    
    # 'fname' is a string variable that contains the full path to a text file with an unknown number of lines
    
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

## RUN THE FUNCTIONS BELOW ##    
    
# read in asci grid structure
asc_grid_ids = np.genfromtxt(asc_grid_file,skip_header=6,delimiter=' ',dtype='int')

# read in grid to compartment lookup
grid_lookup = np.genfromtxt(grid_lookup_file,skip_header=1,delimiter=',',dtype='int',usecols=[0,1])
grid_comp = {row[0]:row[1] for row in grid_lookup}



for year in range(2015,2015+50):
    print('\nprocessing %4d...' % year)
    # read in maximum 2-week mean salinity data by ICM-Hydro compartment (8th column in compartment_out_YYYY.csv)
    comp_summary_file = r'%s\hydro\TempFiles\compartment_out_%4d.csv' % (input_directory,year)
    comp_summary_dict = compout2dict(comp_summary_file,7)
    
    # convert maximum 2-week mean salinity value to acute salinity threshold flag
    # value of 1 indicates that the acute salinity threshold value was met or exceeded
    comp_thresh_dict = {}
    sal_threshold = 5.5
    
    for comp in comp_summary_dict.keys():
        v = comp_summary_dict[comp]
        if v >= sal_threshold:
            t = 1
        else:
            t = 0
        comp_thresh_dict[comp] = t
    
    # map the ICM-hydro compartment data to a grid cell
    map_dict = comp2grid(comp_thresh_dict,grid_comp)
    
    # write ascii output text file from dictionary with grid values
    # looping to append each annual asc grid to the bottom of a single file (ICM-LAVegMod format)

    # write year tag for veg input file
    yr_str = '# Year = %4d\n' % year
    if year == 2015:
        with open(output_asc, mode='w') as outf:
            outf.write(yr_str)
    else:
        with open(output_asc, mode='a') as outf:
            outf.write(yr_str)

    filemode = 'a'
    print(dict2asc_int(map_dict,output_asc,asc_grid_ids,asc_head,filemode) )