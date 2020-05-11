import numpy as np
import datetime as dt

print('\n\n mapping some stuff. how exciting...\n\n')
# input file paths and filenames here
input_directory = r'D:\ICM\S04\G400'
daily_timeseries_file = r'%s\hydro\output_timeseries\MPM2017_S04_G400_C000_U00_V00_SLA_O_01_50_H_TMPxx.out' % input_directory
output_directory = r'D:\ICM\S04\G400'

# input appropriate dates for all_sd, ave_sd, & ave_ed
data_start = dt.date(2015,1,1)          # start date of all data included in the daily timeseries file (YYYY,M,D)
ave_start = dt.date(2015,1,1)          # start date of averaging window, inclusive (YYYY,M,D)
ave_end = dt.date(2015,1,2)          # end date of averaging window, inclusive (YYYY,M,D)

# set output filename based on date range in average
output_asc = r'%s\MPM2017_S04_G400_C000_U00_V00_SLA_O_%s_%s_H_TMPxx.asc' % ( output_directory, ave_start.strftime('%Y%m%d'), ave_end.strftime('%Y%m%d') )

# confirm details for ascii grid details - check that files exist at location and header text is correct
grid_lookup_file = r'%s\hydro\grid_lookup_500m.csv' % input_directory
asc_grid_file = r'%s\veg\veg_grid.asc' % input_directory
asc_head = 'ncols 1259\nnrows 615\nxllcorner 390500\nyllcorner 3125000\ncellsize 500\nNODATA_value -9999\n'




# function definitions below - edit at your own risk, or preferably not at all - they're already perfect.

# STOP - TURN AROUND - GO HOME

def daily2ave(all_sd,ave_sd,ave_ed,input_file): 
    # this function reads a portion of the ICM-Hydro daily timeseries file into a numpy array and then computes the average for the time slice read in
    # this function returns a dictionary 'comp_ave' that has ICM-Hydro compartment ID as the key and a temporal average for each compartment as the value
    
    # if looping through the whole file and batch generating averages for a bunch of timeslices it will be faster to read in the whole file to a numpy array and iterating over the whole array rather than iteratively calling this function
    
    # 'all_sd' is the start date of all data included in the daily timeseries file - all_sd is a datetime.date object   
    # 'ave_sd' is the start date of averaging window, inclusive - ave_sd is a datetime.date object                       
    # 'ave_ed' is the end date of averaging window, inclusive - ave_ed is a datetime.date object                           

    all_rows = file_len(input_file)
    ave_n = (ave_ed - ave_sd).days + 1  # number of days to be used for averaging
    skip_head = (ave_sd - all_sd).days  # number of rows at top of daily timeseries to skip until start date for averaging window is met
    skip_foot = all_rows - skip_head - ave_n
    data = np.genfromtxt(daily_timeseries_file,dtype='str',delimiter=',',skip_header=skip_head,skip_footer=skip_foot)
    comp_ave = {}
    nrow = 0
    for row in data:
        if nrow == 0:
            for comp in range(1,len(row)+1):
                comp_ave[comp]=0.0
        for col in range(0,len(row)):
            comp = col + 1
            val = float(row[col])
            comp_ave[comp] += val/ave_n
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
    
    
    
    
def dict2asc(mapping_dict,outfile,asc_grid,asc_header):
    # this function maps a dictionary of data into XY space and saves as a raster file of ASCII grid format
    # this function does not return anything but it will save 'outfile' to disk
    
    # ASCII grid format description: http://resources.esri.com/help/9.3/arcgisengine/java/GP_ToolRef/spatial_analyst_tools/esri_ascii_raster_format.htm 
    
    # 'mapping_dict' is a dictionary with grid cell ID as the key and some value for each key
    # 'outfile' is the filename (full path) of the output .asc raster text file to be saved
    # 'asc_grid' is a numpy array that is the grid structure of an ASCII text raster
    # 'asc_header' is a string that includes the 6 lines of text required by the ASCII grid format
    
    msg = '\ndid not save %s' % (outfile)
    with open(outfile, mode='w') as outf:
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
                    rowout = '%0.4f'  % gid_val
                else:
                    rowout = '%s %0.4f' % (rowout,gid_val)
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


# read in daily timeseries and calculate averages for each ICM-Hydro compartment
comp_ave_dict = daily2ave(data_start,ave_start,ave_end,daily_timeseries_file)

# map the ICM-hydro compartment averages to a grid cell
map_dict = comp2grid(comp_ave_dict,grid_comp)

# write ascii output text file from dictionary with grid values
print(dict2asc(map_dict,output_asc,asc_grid_ids,asc_head) )