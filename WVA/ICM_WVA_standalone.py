def daily2ave(all_sd,ave_sd,ave_ed,input_file,input_nrows=-9999): 
    # this function reads a portion of the ICM-Hydro daily timeseries file into a numpy array and then computes the average for the time slice read in
    # this function returns a dictionary 'comp_ave' that has ICM-Hydro compartment ID as the key and a temporal average for each compartment as the value
    # the key is of type integer and the values are of type float
    
    # if looping through the whole file and batch generating averages for a bunch of timeslices it will be faster to read in the whole file to a numpy array and iterating over the whole array rather than iteratively calling this function
    
    # 'all_sd' is the start date of all data included in the daily timeseries file - all_sd is a datetime.date object   
    # 'ave_sd' is the start date of averaging window, inclusive - ave_sd is a datetime.date object                       
    # 'ave_ed' is the end date of averaging window, inclusive - ave_ed is a datetime.date object                           

    # check if number of rows in input file was passed into function
    if input_nrows == -9999:                # if not passed in, calculate number of rows by calling file_len function
        all_rows = file_len(input_file)
    else:                                 # if passed in, do not call file_len function
        all_rows = input_nrows

    ave_n = (ave_ed - ave_sd).days + 1  # number of days to be used for averaging
    skip_head = (ave_sd - all_sd).days  # number of rows at top of daily timeseries to skip until start date for averaging window is met
    skip_foot = all_rows - skip_head - ave_n
    data = np.genfromtxt(input_file,dtype='str',delimiter=',',skip_header=skip_head,skip_footer=skip_foot)
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

def file_len(fname):
    # this function counts the number of lines in a text file
    # this function returns an integer value that is the number of lines in the file 'fname'
    
    # 'fname' is a string variable that contains the full path to a text file with an unknown number of lines
    
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

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

def calculate_growing_season_salinity(data_start, daily_timeseries_file, ndays_run, year):
    growing_season_start = dt.date(year, 3, 1)
    growing_season_end = dt.date(year, 10, 31)
    salinity_dict = {comp: [] for comp in
                     range(1, len(np.genfromtxt(daily_timeseries_file, dtype='str', delimiter=',', max_rows=1)) + 1)}

    # Read data for the growing season
    ave_n = (growing_season_end - growing_season_start).days + 1
    skip_head = (growing_season_start - data_start).days
    skip_foot = ndays_run - skip_head - ave_n
    data = np.genfromtxt(daily_timeseries_file, dtype='str', delimiter=',', skip_header=skip_head,
                         skip_footer=skip_foot)

    for row in data:
        for col, val in enumerate(row):
            comp = col + 1
            salinity_dict[comp].append(float(val))

    # Calculate the mean of the highest 33% consecutive salinity readings for each compartment
    mean_salinity_dict = {}
    for comp, values in salinity_dict.items():
        sorted_values = sorted(values, reverse=True)
        top_33_percent = sorted_values[:int(len(sorted_values) * 0.33)]
        mean_salinity_dict[comp] = np.mean(top_33_percent)

    return mean_salinity_dict

def calculate_annual_salinity(data_start, daily_timeseries_file, ndays_run, year):
    year_start = dt.date(year, 1, 1)
    year_end = dt.date(year, 12, 31)
    salinity_dict = {comp: [] for comp in
                     range(1, len(np.genfromtxt(daily_timeseries_file, dtype='str', delimiter=',', max_rows=1)) + 1)}

    # Read data for the growing season
    ave_n = (year_end - year_start).days + 1
    skip_head = (year_start - data_start).days
    skip_foot = ndays_run - skip_head - ave_n
    data = np.genfromtxt(daily_timeseries_file, dtype='str', delimiter=',', skip_header=skip_head,
                         skip_footer=skip_foot)

    for row in data:
        for col, val in enumerate(row):
            comp = col + 1
            salinity_dict[comp].append(float(val))

    # Calculate the mean of the salinity readings for each compartment
    mean_salinity_dict = {}
    for comp, values in salinity_dict.items():
        sorted_values = sorted(values, reverse=True)
        mean_salinity_dict[comp] = np.mean(sorted_values)

    return mean_salinity_dict

def filepath_zip(filepath):
    if os.path.exists(filepath) == False:
        zip_path = f'{filepath}.zip'
        file_name = os.path.basename(filepath)
        extract_path = os.path.dirname(filepath)
        if os.path.exists(zip_path) == False:
            print(f"File not found: {filepath}")
            return 'NoPath'
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extract(file_name, path=extract_path)
        opened_files.append(filepath)
    return filepath


    
##################################
####
####
####
####    Run ICM standalone for WVA
####
####
####
##################################

import os
import sys
import numpy as np
import pandas as pd
import datetime as dt
import zipfile

s = int(sys.argv[1])
g_fwa = int(sys.argv[2])
year = int(sys.argv[3])
project = sys.argv[4]

global opened_files

opened_files = []


HSI_standalone = True     #for these re-runs, using grid_data with YYYYend nomenclature, so set this flag to False

project_location = os.path.normpath('/ocean/projects/bcs200002p/ewhite12/%s/ICM/S0%s/G%s' % (project,s, g_fwa)) #Test String

os.chdir(project_location)

par_dir = os.getcwd()

inputs = np.genfromtxt('ICM_HSI_control.csv',dtype=str,comments='#',delimiter=',')
# Parent directory locations for various ICM components
# These directories must exist in the model folder
# Other directories are created throughout the ICM run - but they are all based on these parent directories
ecohydro_dir = os.path.normpath('%s/%s' % (par_dir,inputs[1,1].lstrip().rstrip()))
wetland_morph_dir = os.path.normpath('%s/%s' % (par_dir,inputs[2,1].lstrip().rstrip()))
vegetation_dir = os.path.normpath('%s/%s' % (par_dir,inputs[3,1].lstrip().rstrip()))
bimode_dir = os.path.normpath('%s/%s' % (par_dir,inputs[4,1].lstrip().rstrip()))
HSI_dir = os.path.normpath('%s/%s' % (par_dir,inputs[5,1].lstrip().rstrip()))

# Configuration files used by various ICM components

grid_output_file= 'grid_500m_out.csv'

## Simulation Settings
startyear = int(inputs[29,1].lstrip().rstrip())
endyear = int(inputs[30,1].lstrip().rstrip())
nvegtype = int(inputs[35,1].lstrip().rstrip())


## grid information for Veg ASCII grid files
n500grid= int(inputs[37,1].lstrip().rstrip())
n500rows = int(inputs[38,1].lstrip().rstrip())
n500cols = int(inputs[39,1].lstrip().rstrip())
xll500 = int(inputs[40,1].lstrip().rstrip())
yll500 = int(inputs[41,1].lstrip().rstrip())

## grid information for EwE ASCII grid files


# file naming convention settings
mpterm = inputs[47,1].lstrip().rstrip()
cterm = inputs[50,1].lstrip().rstrip()
uterm = inputs[51,1].lstrip().rstrip()
vterm = inputs[52,1].lstrip().rstrip()
rterm = inputs[53,1].lstrip().rstrip()
runprefix = '%s_S0%s_G%s_%s_%s_%s_%s' % (mpterm,s,g_fwa,cterm,uterm,vterm,rterm)

EHtemp_path = os.path.normpath(r'%s/TempFiles' % ecohydro_dir)

# read in grid-to-compartment lookup table into a dictionary
# key is grid ID and value is compartment
grid_lookup_file = filepath_zip(r'%s/grid_lookup_500m.csv' % ecohydro_dir)
grid_lookup = np.genfromtxt(grid_lookup_file,skip_header=1,delimiter=',',dtype='int',usecols=[0,1])
grid_comp = {row[0]:row[1] for row in grid_lookup}

# Save list of GridIDs into an array for use in some loops later # ultimately can replace with grid_comp.keys() in loops
gridIDs=grid_comp.keys()

print(' Configuring WVA Model.')
# change working directory to veg folder
#WVA_dir = os.path.normpath('%s/%s' % (par_dir, 'WVA_v4'))
WVA_dir = os.path.normpath(f'/ocean/projects/bcs200002p/ewhite12/MP2029/MP-29.3.1_landscape_metrics/WVA/Outputs/G{g_fwa}')

if os.path.exists(WVA_dir):
    os.chdir(WVA_dir)
else:
    os.mkdir(WVA_dir)
    os.chdir(WVA_dir)

daily_timeseries_file = filepath_zip(os.path.normpath(r'%s/SAL.out' % ecohydro_dir))
if not os.path.exists(daily_timeseries_file):
    daily_timeseries_file = filepath_zip(os.path.normpath(r'%s/%s_O_01_%02d_H_SAL.out' % (ecohydro_dir, runprefix, endyear - startyear + 1)))

ndays_run = file_len(daily_timeseries_file)
data_start = dt.date(startyear, 1, 1)

# Calculate growing season salinity
growing_season_salinity_comp = calculate_growing_season_salinity(data_start, daily_timeseries_file, ndays_run, year)
annual_salinity_comp = calculate_annual_salinity(data_start, daily_timeseries_file, ndays_run, year)

growing_season_salinity = comp2grid(growing_season_salinity_comp, grid_comp)
annual_salinity = comp2grid(annual_salinity_comp, grid_comp)

elapsedyear = year - startyear + 1

veg_output_file = '%s_O_%02d_%02d_V_vegty.asc+' % (runprefix,elapsedyear,elapsedyear)
veg_output_filepath = filepath_zip(os.path.normpath(vegetation_dir + '/' + veg_output_file))
    

# update name of grid data file generated by Morph to include current year in name
# the file represents the end of the year landscape and is originally named 'endYYYY' by morph
# before running Hydro in the following year, the filename is changed
# here that re-naming is checked to make sure correct file is used that represents the end of the year conditions
# if HSI is run in standalone mode, the grid data file has already been re-named and file for year YYYY represents the landscape after morph was run in year YYYY-1
if HSI_standalone == False:
    new_grid_file = 'grid_data_500m_end%s.csv' % (year)  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year) here instead of CurrentYear
else:
    if year == endyear:
        new_grid_file = 'grid_data_500m_end%s.csv' % (year)  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year) here instead of CurrentYear
    else:
        new_grid_file = 'grid_data_500m_%s.csv' % (year+1)  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year) here instead of CurrentYear

new_grid_filepath = filepath_zip(os.path.normpath('%s/%s' % (EHtemp_path,new_grid_file))) # location of Morph output data grid file after it is generated in "WM.CalculateEcohydroAttributes"

EH_grid_out_newfile = '%s_%s.%s' % (str.split(grid_output_file,'.')[0],year,str.split(grid_output_file,'.')[1])
EH_grid_results_filepath = filepath_zip(os.path.normpath('%s/%s' % (EHtemp_path,EH_grid_out_newfile))) # location of Hydro output data grid file

print('\n--------------------------------------------------')
print( '  Wetland Value Assesment - Year %s' % year)
print('--------------------------------------------------\n')
os.chdir(ecohydro_dir)

# read in Morph output file
print(' Reading in Morphology output files to be used for HSIs:')
print('   - gridded summary data representing end-of-year conditions after Hydro-Veg-Morph')
# import grid summary file (percent land, elevations) generated by Morphology
griddata = np.genfromtxt(new_grid_filepath,delimiter=',',skip_header=1)
bedelevdict = dict((int(griddata[n][0]),griddata[n][1]) for n in range(0,n500grid)) # bedelevdict is a dictionary of mean elevation of water bottom (bed) portion of grid, key is gridID, noData = -9999
melevdict   = dict((int(griddata[n][0]),griddata[n][2]) for n in range(0,n500grid))# melevdict is a dictionary of mean elevation of marsh surface portion of grid, key is gridID, noData = -9999
landdict    = dict((int(griddata[n][0]),griddata[n][3]) for n in range(0,n500grid))# landdict is a dictionary of percent land (0-100) in each 500-m grid cell, key is gridID
waterdict   = dict((int(griddata[n][0]),griddata[n][5]) for n in range(0,n500grid))# waterdict is a dictionary of percent water (0-100) in each 500-m grid cell, key is gridID


# import annual Ecohydro output that is summarized by grid ID (Column 0 corresponds to 500m ID#, Column 7 is percent sand, and  Column 17 is average depth)    
EH_grid_out = np.genfromtxt(EH_grid_results_filepath,delimiter=',',skip_header=1)
stagedict = dict((int(EH_grid_out[n][0]),EH_grid_out[n][12]) for n in range(0,n500grid))
#pctsanddict = dict((int(EH_grid_out[n][0]),EH_grid_out[n][7]) for n in range(0,n500grid))

del(EH_grid_out)

# Calculate monthly averages from Hydro output daily timeseries 
# read in daily timeseries and calculate averages for each ICM-Hydro compartment for a variety of variables

# check length of timeseries.out files once for year and save total length of file
daily_timeseries_file = filepath_zip(os.path.normpath(r'%s/SAL.out' % ecohydro_dir))
if os.path.exists(daily_timeseries_file) == False:
    daily_timeseries_file = filepath_zip(os.path.normpath(r'%s/%s_O_01_%02d_H_SAL.out' % (ecohydro_dir,runprefix,endyear-startyear+1)))

ndays_run = file_len(daily_timeseries_file)
    
# run HSI function (run in HSI directory so output files are saved there)
os.chdir(WVA_dir)

# import percent edge output from geomorph routine that is summarized by grid ID
pctedge_file = filepath_zip(os.path.normpath('%s/%s_N_%02d_%02d_W_pedge.csv'% (HSI_dir,runprefix,elapsedyear,elapsedyear))) # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year) here instead of CurrentYear
pedge = np.genfromtxt(pctedge_file,delimiter = ',',skip_header = 1)
pctedgedict = dict((int(pedge[n][0]),pedge[n][1]) for n in range(0,n500grid))
del(pedge)


#Import_Only_Year's worth of data
startdate =dt.date(startyear, 1, 1)
start_of_year =dt.date(year,1,1)
end_of_year = dt.date(year, 12, 31)
start_index = (start_of_year - startdate).days
end_index = (end_of_year - startdate).days + 1

#Import this years daily timeseries data of stage
daily_timeseries_file = filepath_zip(os.path.normpath(r'%s/STG.out' % ecohydro_dir))
if os.path.exists(daily_timeseries_file) == False:
    daily_timeseries_file = filepath_zip(os.path.normpath(r'%s/%s_O_01_%02d_H_STG.out' % (ecohydro_dir,runprefix,endyear-startyear+1)))
dailystg = np.genfromtxt(daily_timeseries_file, delimiter=",",skip_header=start_index,max_rows=(end_index-start_index))
dailystg = dailystg.T
stg_by_days_array = []
stg_by_days_array = comp2grid(dailystg, grid_comp) #GridID = key, array of timeseries is value

#Links Info
links_file= filepath_zip(os.path.normpath(r'%s/TempFiles/Links_%s.csv' % (ecohydro_dir, year)))
links_data = np.genfromtxt(links_file, skip_header=1,delimiter=',',usecols=(1,2))

#Flow Data by link
flow_file = filepath_zip(os.path.normpath(r'%s/FLO.out' % ecohydro_dir))
if os.path.exists(flow_file) == False:
    flow_file = filepath_zip(os.path.normpath(r'%s/%s_O_01_%02d_H_FLO.out' % (ecohydro_dir,runprefix,endyear-startyear+1)))

flow_data=np.genfromtxt(flow_file,delimiter=',',skip_header=start_index,max_rows=(end_index-start_index))

#Calcualte average compartment Volume (Pct water * Area * Stage - BevElv)
compartmentfile = filepath_zip(os.path.normpath(r'%s/TempFiles/Cells_%s.csv' % (ecohydro_dir, year)))
compinfo = np.genfromtxt(compartmentfile, skip_header=1, delimiter=',')
comp_pctwater = dict((int(compinfo[n][0]),compinfo[n][2]) for n in range(0,1787))
comp_bedelv =  dict((int(compinfo[n][0]),compinfo[n][7]) for n in range(0,1787))
comp_area = dict((int(compinfo[n][0]),compinfo[n][1]) for n in range(0,1787))
meanwaterfile = filepath_zip(os.path.normpath(r'%s/TempFiles/compartment_out_%s.csv' % (ecohydro_dir, year)))
meanwaterlevel = np.genfromtxt(meanwaterfile, skip_header=1, delimiter=',')
comp_stg = dict((int(meanwaterlevel[n][0]), meanwaterlevel[n][2]) for n in range(0,1787))
comp_volume = {}
for compID in range(1,1788):
    volume = (comp_stg[compID]-comp_bedelv[compID])*(comp_pctwater[compID]*comp_area[compID]) #(meter - meter) *( m^2 * %)
    comp_volume[compID] = volume

#Import Qmult to route Diversion flow to compartments
qmult_file = filepath_zip(os.path.normpath(r'%s/QMult.csv' % ecohydro_dir))
Qmult = np.genfromtxt(qmult_file, delimiter=',',skip_header=1)

#Import TribQ to get daily diversion flows
tribQ_file = filepath_zip(os.path.normpath(r'%s/TribQ.csv' % ecohydro_dir))
tribQ = np.genfromtxt(tribQ_file,delimiter=',',skip_header=start_index,max_rows=(end_index-start_index))

#Import Stand Age dict created from NFI spatial relationship (this is a static dictionary lookup)

stand_age_file = filepath_zip(os.path.normpath(r'%s/Stand_Age.csv' % vegetation_dir))
stand_age_import = pd.read_csv(stand_age_file)
stand_age_dict = dict(zip(stand_age_import['gridID'], stand_age_import['Std_Age']))

#cleans up opened_zipped_files
for f in opened_files:
    if os.path.exists(f):
        os.remove(f)

import WVA as WVA

WVA.WVA(gridIDs, links_data, flow_data,grid_comp, comp_volume, annual_salinity, 
        bedelevdict,melevdict,veg_output_filepath,nvegtype,
        landdict,waterdict,pctedgedict,n500grid,
        n500rows,n500cols,yll500,xll500,year,elapsedyear, HSI_dir,vegetation_dir,
        wetland_morph_dir,runprefix,growing_season_salinity, stg_by_days_array, 
        WVA_dir, stand_age_dict, Qmult, tribQ)

