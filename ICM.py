#########################################################################################################
####                                                                                                 ####
####                                FUNCTIONS USED BY ICM.PY                                         ####
####                                                                                                 ####
#########################################################################################################

def file_len(fname):
    # this function counts the number of lines in a text file
    # this function returns an integer value that is the number of lines in the file 'fname'

    # 'fname' is a string variable that contains the full path to a text file with an unknown number of lines

    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


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


def daily2max(all_sd,ave_sd,ave_ed,input_file):
    # this function reads a portion of the ICM-Hydro daily timeseries file into a numpy array and then computes the maximum for the time slice read in
    # this function returns a dictionary 'comp_max' that has ICM-Hydro compartment ID as the key and a temporal maximum for each compartment as the value
    # the key is of type integer and the values are of type float

    # if looping through the whole file and batch generating for a bunch of timeslices it will be faster to read in the whole file to a numpy array and iterating over the whole array rather than iteratively calling this function

    # 'all_sd' is the start date of all data included in the daily timeseries file - all_sd is a datetime.date object
    # 'ave_sd' is the start date of averaging/maximum window, inclusive - ave_sd is a datetime.date object
    # 'ave_ed' is the end date of averaging/maximum window, inclusive - ave_ed is a datetime.date object

    all_rows = file_len(input_file)
    ave_n = (ave_ed - ave_sd).days + 1  # number of days to be used for averaging
    skip_head = (ave_sd - all_sd).days  # number of rows at top of daily timeseries to skip until start date for averaging window is met
    skip_foot = all_rows - skip_head - ave_n
    data = np.genfromtxt(input_file,dtype='str',delimiter=',',skip_header=skip_head,skip_footer=skip_foot)
    comp_max = {}
    nrow = 0
    for row in data:
        if nrow == 0:
            for comp in range(1,len(row)+1):
                comp_max[comp]= -99999.0
        for col in range(0,len(row)):
            comp = col + 1
            val = float(row[col])
            comp_max[comp] = max(comp_max[comp],val)
        nrow += 1
    return comp_max


def daily2day(all_sd,day2get,input_file):
    # this function reads a portion of the ICM-Hydro daily timeseries and extracts a single daily value for the day passed into the fuction as day2get

    # if looping through the whole file and batch generating for a bunch of timeslices it will be faster to read in the whole file to a numpy array and iterating over the whole array rather than iteratively calling this function

    # 'all_sd' is the start date of all data included in the daily timeseries file - all_sd is a datetime.date object
    # 'day2get' is the date to extract  - day2get is a datetime.date object


    all_rows = file_len(input_file)
    skip_head = (day2get - all_sd).days  # number of rows at top of daily timeseries to skip until date to extract is met
    skip_foot = all_rows - skip_head - 1
    dataline = np.genfromtxt(input_file,dtype='str',delimiter=',',skip_header=skip_head,skip_footer=skip_foot)
    comp_day = {}
    ncol = 0
    for col in dataline:
        comp_day[ncol+1]=col        # ICM-Hydro timeseries output files have column numbers with 1-index that corresponds to the ICM-Hydro compartment number
        ncol += 1
    return comp_day


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
                    gid_val = float(mapping_dict[gid_map] )
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


def dict2asc_int(mapping_dict,outfile,asc_grid,asc_header,write_mode):
    # this function maps a dictionary of integer data into XY space and saves as a raster file of ASCII grid format
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
                    gid_val = float(mapping_dict[gid_map] )
                else:
                    gid_val = float(gid_map)
                if nc == 0:
                    rowout = '%d'  % gid_val
                else:
                    rowout = '%s %d' % (rowout,gid_val)
                nc += 1
            outf.write('%s\n' % rowout)
            msg = '\nsuccessfully saved %s' % (outfile)
    return msg


def forward2backslash(fs_file):
    # this function reads every line in a text file and replaces any forward slash '/' to a backslash '\'
    # this is used to convert filepaths passed into Fortran I/O text files for interoperability on Windows and Linux

    # 'fs_file' is the filename path that will have all forward slash characters converted to backslash charcters

    # note that this function is crude and does not check that the / are actually in a file path - it is a brute force conversion use with caution

    os.rename(fs_file,'%s.fs' % fs_file)    # rename file that contains forward slashes
    bs_file = fs_file                       # file with backslashes will keep the original file name passed into function
    with open('%s.fs' % fs_file,mode='r') as fsf:
        with open(bs_file,mode='w') as bsf:
            for line in fsf:
                str2wrt = ''
                for char in line:
                    if char == '/':
                        char = '\\'
                    str2wrt = '%s%s' % (str2wrt,char)
                wrtline = bsf.write(str2wrt)
    print(' Replaced all / with \\ in %s.\n' % fs_file)
    os.remove('%s.fs' % fs_file)
    return


def bidem_interp2xyz(irregular_xyz_in,fixed_xyz_in,fixed_xyz_out):
    # This function reads an irregular XYZ file and linearly interpolates the z values to
    # a regular grid that is pre-defined.
    #
    # This function currently assumes that all XYZ model output files do not have a header and are comma delimited
    # The fixed grid XYZ file snapped to the DEM raster does not have a header and is space delimited
    # The output can have headers printed by changing the .to_csv() function call

    # irregular_xyz_in:  randomly spaced XYZ file to be interpolated to a fixed grid
    # fixed_xyz_in:      fixed, regular grid that has the desired resolution to interpolate to
    # fixed_xyz_out:     file name for the output file that saves the interpolation output

    # function originally coded by Diana Dileonardo


    # read in irregular and regular grids
    results = pandas.read_csv( irregular_xyz_in,delim_whitespace=False,names=['x','y','z','trans'] )
    fixed_grid = pandas.read_csv( fixed_xyz_in,delim_whitespace=True,names=['x','y','z'] )

    # restructure input arrays so that they align for passing into scipy.griddata function
    results_xy = np.vstack((results.x,results.y)).T
    results_z = np.array(results.z)
    fixed_grid_array = np.vstack((fixed_grid.x,fixed_grid.y)).T  #array of fixed output xy locations

    # linearly interpolate to fixed grid using scipy.griddata()
    # returns a 1-D array with interpolated values for each x-y pair in fixed_grid_array
    # note that points on the edges of the grid domain *may* return NaN from griddata()
    # could be handled by passing a default fill value into griddata via fill_value variable
    # instead it will be handled lower to keep previous values
    interp_results = griddata(results_xy,results.z,fixed_grid_array,method='linear')

    with open(fixed_xyz_out,mode='w') as interp2write:
        nanflag = 0
        for ni in range(0,len(interp_results)):
            x = fixed_grid_array[ni][0]
            y = fixed_grid_array[ni][1]
            z = interp_results[ni]
            if np.isnan(z):
                nanflag = 1
                if ni == 0:
                    z = np.mean(interp_results)
                else:
                    z = last_good_z
            else:
                last_good_z = z
            writeout = interp2write.write( '%d %d %0.4f\n' % (x,y,z) )

    if nanflag == 1:
        print('\n***************************************************')
        print('*******  INTERPOLATION RETURNED NaN VALUES  *******')
        print('***************************************************')
        print('\nAt least one interpolated profile had a NaN value returned at the edge of the interpolation grid domain.')
        print('The NaN was filled with the last known interpolated Z value. This could result in holes or spikes if the last')
        print('known good interpolated value was from a different profile.')
        print('')
        print('However, based on visual QA - the NaNs appeared to be on the back-end of each grid domain, so this *should* be')
        print('a fairly safe NaN-filling approach.\n')
        print('***************************************************')
        print('*******  INTERPOLATION RETURNED NaN VALUES  *******')
        print('***************************************************\n')

    return


def write_1d_fine_inp(FineConfigFile,i,year,lq):
    fine_inp    = os.path.normpath(r'./%s/input/fine.inp'   %   FineConfigFile[i])         # input file used by hydro.exe
    fine_inp_og = os.path.normpath(r'./%s/input/fine.inp.o'  %  FineConfigFile[i])         # original input file to read lines from
    fine_inp_yr = os.path.normpath(r'./%s/input/fine_%s.inp' % (FineConfigFile[i],year) )  # annual file that is written then copied

    with open(fine_inp_og, mode='r') as orig_file:
        nl = 0
        with open(fine_inp_yr, mode='w') as ann_file:
            for line in orig_file:
                nl += 1
                if nl ==12:
                    ann_file.write("%sinput/Upstream/upstream_fine_%s.txt%s           ! File that contains upstream concentration BC for all particle classes considered (1, 2, 3, ...)\n" % (lq,year,lq))
                elif nl == 13:
                    ann_file.write("%sinput/Downstream/downstream_fine_%s.txt%s       ! File that contains downstream concentration BC for all particle classes considered (1, 2, 3, ...)\n" % (lq,year,lq))
                elif nl == 16:
                    ann_file.write("%sinput/Lateral/lateral_q_con_%s.txt%s            ! File that contains lateral Q and Con (1, 2, ..., Nlat)\n" % (lq,year,lq))
                else:
                    ann_file.write(line)


    # convert filepath delimiter to backslash if running on Windows (this is for text I/O passed into Fortran executables)
    if os.name == 'nt':
        forward2backslash(fine_inp_yr)

    try:
        if os.path.isfile(fine_inp):
            os.remove(fine_inp)
        shutil.copyfile(fine_inp_yr,fine_inp)
    except:
        if os.path.isfile(fine_inp):
            os.remove(fine_inp)
        subprocess.call( ['cp','-p',fine_inp_yr,fine_inp] )

    return


def write_1d_hyd_inp(HydroConfigFile,i,year,lq):
    hyd_inp    = os.path.normpath(r'%s/%s/input/hydro.inp'   % (ecohydro_dir,HydroConfigFile[i]) )          # input file used by hydro.exe
    hyd_inp_og = os.path.normpath(r'%s/%s/input/hydro.inp.o' % (ecohydro_dir,HydroConfigFile[i]) )        # original input file to read lines from
    hyd_inp_yr = os.path.normpath(r'%s/%s/input/hydro_%s.inp'% (ecohydro_dir,HydroConfigFile[i],year) )  # annual file that is written then copied

    with open(hyd_inp_og, mode='r') as orig_file:
        nl = 0
        with open(hyd_inp_yr, mode='w') as ann_file:
            for line in orig_file:
                nl += 1
                if nl ==5:
                    ann_file.write("%sinput/Upstream/Discharge_%s.txt%s            ! upstream_path\n" % (lq,year,lq))
                elif nl == 6:
                    ann_file.write("%sinput/Downstream/WL_%s.txt%s            ! downstream_path\n" % (lq,year,lq))
                elif nl == 9:
                    ann_file.write("%sinput/Lateral/%s/%s            ! lateralFlow_path\n" % (lq,year,lq))
                else:
                    ann_file.write(line)

    # convert filepath delimiter to backslash if running on Windows (this is for text I/O passed into Fortran executables)
    if os.name == 'nt':
        forward2backslash(hyd_inp_yr)

    try:
        if os.path.isfile(hyd_inp):
           os.remove(hyd_inp)
        shutil.copyfile(hyd_inp_yr,hyd_inp)
    except:
        if os.path.isfile(hyd_inp):
           os.remove(hyd_inp)
        subprocess.call( ['cp','-p',hyd_inp_yr,hyd_inp] )

    return


def write_1d_sal_inp(SalConfigFile,i,year,lq):
    sal_inp    = os.path.normpath(r'./%s/input/sal.inp'   %   SalConfigFile[i])         # input file used by hydro.exe
    sal_inp_og = os.path.normpath(r'./%s/input/sal.inp.o'  %  SalConfigFile[i])         # original input file to read lines from
    sal_inp_yr = os.path.normpath(r'./%s/input/sal_%s.inp' % (SalConfigFile[i],year) )  # annual file that is written then copied

    with open(sal_inp_og, mode='r') as orig_file:
        nl = 0
        with open(sal_inp_yr, mode='w') as ann_file:
            for line in orig_file:
                nl += 1
                if nl ==5:
                    ann_file.write("%sinput/Upstream/upstream_sal_%s.txt%s            ! File that contains upstream concentration BC \n" % (lq,year,lq))
                elif nl == 6:
                    ann_file.write("%sinput/Downstream/downstream_sal_%s.txt%s        ! File that contains downstream concentration BC \n" % (lq,year,lq))
                elif nl == 8:
                    ann_file.write("%sinput/Lateral/lateral_q_con_%s.txt%s            ! File that contains lateral Q and Con (1, 2, ..., Nlat)\n" % (lq,year,lq))
                else:
                    ann_file.write(line)


    # convert filepath delimiter to backslash if running on Windows (this is for text I/O passed into Fortran executables)
    if os.name == 'nt':
        forward2backslash(sal_inp_yr)

    try:
        if os.path.isfile(sal_inp):
           os.remove(sal_inp)
        shutil.copyfile(sal_inp_yr,sal_inp)
    except:
        if os.path.isfile(sal_inp):
           os.remove(sal_inp)
        subprocess.call( ['cp','-p',sal_inp_yr,sal_inp] )

    return


def write_1d_sand_inp(SandConfigFile,i,year,lq):
    sand_inp    = os.path.normpath(r'./%s/input/sand.inp'   %   SandConfigFile[i])         # input file used by hydro.exe
    sand_inp_og = os.path.normpath(r'./%s/input/sand.inp.o'  %  SandConfigFile[i])         # original input file to read lines from
    sand_inp_yr = os.path.normpath(r'./%s/input/sand_%s.inp' % (SandConfigFile[i],year) )  # annual file that is written then copied

    with open(sand_inp_og, mode='r') as orig_file:
        nl = 0
        with open(sand_inp_yr, mode='w') as ann_file:
            for line in orig_file:
                nl += 1
                if nl ==12:
                    ann_file.write("%sinput/Upstream/upstream_sand_%s.txt%s           ! File that contains upstream concentration BC for all particle classes considered (1, 2, 3, ...)\n" % (lq,year,lq))
                elif nl == 13:
                    ann_file.write("%sinput/Downstream/downstream_sand_%s.txt%s       ! File that contains downstream concentration BC for all particle classes considered (1, 2, 3, ...)\n" % (lq,year,lq))
                elif nl == 16:
                    ann_file.write("%sinput/Lateral/lateral_q_con_%s.txt%s            ! File that contains lateral Q and Con (1, 2, ..., Nlat)\n" % (lq,year,lq))
                else:
                    ann_file.write(line)


    # convert filepath delimiter to backslash if running on Windows (this is for text I/O passed into Fortran executables)
    if os.name == 'nt':
        forward2backslash(sand_inp_yr)

    try:
        if os.path.isfile(sand_inp):
            os.remove(sand_inp)
        shutil.copyfile(sand_inp_yr,sand_inp)
    except:
        if os.path.isfile(sand_inp):
            os.remove(sand_inp)
        subprocess.call( ['cp','-p',sand_inp_yr,sand_inp] )

    return


def write_1d_tmp_inp(TempConfigFile,i,year,lq):
    tmp_inp    = os.path.normpath(r'./%s/input/tmp.inp'   %   TempConfigFile[i])         # input file used by hydro.exe
    tmp_inp_og = os.path.normpath(r'./%s/input/tmp.inp.o'  %  TempConfigFile[i])         # original input file to read lines from
    tmp_inp_yr = os.path.normpath(r'./%s/input/tmp_%s.inp' % (TempConfigFile[i],year) )  # annual file that is written then copied

    with open(tmp_inp_og, mode='r') as orig_file:
        nl = 0
        with open(tmp_inp_yr, mode='w') as ann_file:
            for line in orig_file:
                nl += 1
                if nl ==5:
                    ann_file.write("%sinput/Upstream/upstream_temp_%s.txt%s           ! File that contains upstream BC \n" % (lq,year,lq))
                elif nl == 6:
                    ann_file.write("%sinput/Downstream/downstream_temp_%s.txt%s      ! File that contains downstream BC \n" % (lq,year,lq))
                elif nl == 8:
                    ann_file.write("%sinput/Lateral/lateral_q_con_%s.txt%s            ! File that contains lateral Q and Con (1, 2, ..., Nlat)\n" % (lq,year,lq))
                elif nl == 10:
                    ann_file.write("%sinput/Wind/U10_%s.txt%s                 !Wind U10 input\n" % (lq,year,lq))
                elif nl ==11:
                    ann_file.write("%sinput/Tbk/Tback_%s.txt%s                !Tback input\n"  % (lq,year,lq))

                else:
                    ann_file.write(line)

    # convert filepath delimiter to backslash if running on Windows (this is for text I/O passed into Fortran executables)
    if os.name == 'nt':
        forward2backslash(tmp_inp_yr)


    try:
        if os.path.isfile(tmp_inp):
            os.remove(tmp_inp)
        shutil.copyfile(tmp_inp_yr,tmp_inp)
    except:
        if os.path.isfile(tmp_inp):
            os.remove(tmp_inp)
        subprocess.call( ['cp','-p',tmp_inp_yr,tmp_inp] )


    return



#########################################################################################################
####                                                                                                 ####
####                                START GENERAL ICM.PY PROGRAM                                     ####
####                                                                                                 ####
#########################################################################################################

import os
import platform
import sys
import subprocess
import shutil
import math
import time
import errno
import random
import datetime as dt
import numpy as np
import xlrd
import pandas
from builtins import Exception as exceptions
from scipy.interpolate import griddata




#HPCmode# ## Save Python's console output to a log file
#HPCmode# class Logger(object):
#HPCmode#     def __init__(self, filename="Default.log"):
#HPCmode#         self.terminal = sys.stdout
#HPCmode#         self.log = open(filename, "a")
#HPCmode#
#HPCmode#     def write(self, message):
#HPCmode#         self.terminal.write(message)
#HPCmode#         self.log.write(message)
#HPCmode#
#HPCmode# ## Activate log text file
#HPCmode# logfile ='ICM_%s_ICM_Veg_Morph_HSI.log' % time.strftime('%Y%m%d_%H%M', time.localtime())
#HPCmode# sys.stdout = Logger(logfile)

hydro_logfile = 'ICM_%s_Hydro.log' % time.strftime('%Y%m%d_%H%M', time.localtime())


## NOTE: all directory paths and filenames (when appended to a directory path) are normalized
##          in this ICM routine using os.path.normpath(). This is likely a bit redundant, but it
##          was instituted so that file path directory formatting in the input parameters is forgiving.
##          If converted to Linux, this should allow for flexibility between the forward-slash vs.
##          back-slash differences between Windows and Linux.
##          This approach does not work for filepaths that are written to input text files that are passed
##          into Fortran executables. Python will convert / to \ when run on Windows...so all filepaths
##          now utilize Posix filepath convention with /. There is a function call forward2backslash that
##          can be used to convert to Windows-specific slash characters for specific files for use in Windows Fortran.

print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('~~                                                           ~~')
print('~~      LOUISIANA MASTER PLAN FOR A SUSTAINABLE COAST        ~~')
print('~~                Integrated Compartment Model               ~~')
print('~~   Louisiana Coastal Restoration and Protection Authority  ~~')
print('~~                                                           ~~')
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('~~                                                           ~~')
print('~~ ICM updated for 2023 Master Plan                          ~~')
print('~~                                                           ~~')
print('~~ Developed under Cooperative Endeavor Agreement Number:    ~~')
print('~~      2503-12-58, Task Order No. 03 (subtask 4.8)          ~~')
print('~~                                                           ~~')
print('~~ Original Development team (2017 Master Plan)              ~~')
print('~~   CB&I                                                    ~~')
print('~~   Fenstermaker                                            ~~')
print('~~   Moffatt & Nichol                                        ~~')
print('~~   University of Louisiana at Lafayette                    ~~')
print('~~   University of New Orleans                               ~~')
print('~~   USGS National Wetlands Research Center                  ~~')
print('~~   The Water Institute of the Gulf                         ~~')
print('~~                                                           ~~')
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('~~                                                           ~~')
print('~~                                                           ~~')
print('~~                                                           ~~')
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('')
print(' ICM run started at:       %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) )
print(' ICM running on computer:  %s' % platform.node() )
print('')


## Check Versions ##
## Check Versions ## #########################################################
## Check Versions ## ##           CHECK PYTHON AND NUMPY VERSIONS           ##
## Check Versions ## #########################################################
## Check Versions ## vs=sys.version_info
## Check Versions ## npvs=np.__version__
## Check Versions ## npvsarray = np.fromstring(npvs,sep='.',dtype=int)
## Check Versions ## npver=float(npvsarray[0])+float(npvsarray[1])/10.0
## Check Versions ## ## Check if Python version is 64-bit
## Check Versions ## if sys.maxsize > 2**32:
## Check Versions ##     arch = '64-bit'
## Check Versions ##     print(' This run is utilizing %s Python %s.%s.%s with NumPy %s' %(arch,vs.major,vs.minor,vs.micro,npvs) )
## Check Versions ## ## Check that NumPy version is 1.7 or newer
## Check Versions ##     if npver < 1.7:
## Check Versions ##         print(' NumPy version is earlier than NumPy 1.7.0 - this version of NumPy is not supported.')
## Check Versions ##         print(' Install 64-bit NumPy 1.7.0 (or newer) and re-run ICM.')
## Check Versions ##         print('\n Press <ENTER> to cancel run.')
## Check Versions ##         input()
## Check Versions ##         sys.exit()
## Check Versions ##     else:
## Check Versions ##             print('\n This Python configuration is supported.')
## Check Versions ## else:
## Check Versions ##     arch = '32-bit'
## Check Versions ##     print(' This run is utilizing %s Python %s.%s.%s with NumPy %s' %(arch,vs.major,vs.minor,vs.micro,npvs) )
## Check Versions ##     print(' Install 64-bit Python with NumPy 1.7.0 (or newer) and re-run ICM.')
## Check Versions ##     print('\n Press ENTER to cancel run.')
## Check Versions ##     input()
## Check Versions ##     sys.exit()
## Check Versions ##
## Check Versions ## del (vs,arch,npvs, npvsarray,npver)
## Check Versions ##

#########################################################
## INPUT VARIABLES TO BE READ FROM CONFIGURATION FILES ##
#########################################################
print('--------------------------------------------------')
print('\n CONFIGURING ICM MODEL FILES.')
print('--------------------------------------------------')

#Years to implement new files for hydro model
hyd_switch_years = []
hyd_file_orig = []
hyd_file_new = []
hyd_file_bk = []

# Link numbers to be activated or deactivated in Hydro model
links_to_change = []
# Years (calendar year) to activate or deactivate each respective Hydro model links listed above
link_years = []

# full path to directory with FWA project GIS data files
FWA_prj_input_dir_MC = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/FWA_project_data/MC_elev_rasters'
FWA_prj_input_dir_RR = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/FWA_project_data/Ridge_Levee_elev_rasters'
FWA_prj_input_dir_BS = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/FWA_project_data/BS_SP_edge_erosion_multiplier_rasters'

# Marsh creation project element IDs that are implemented in this simulation
mc_elementIDs = []
# Years (calendar year) to implement each respective marsh creation element IDs listed above
mc_years = []
# Marsh creation project element IDs that have deep water areas filled in (leave array empty if all use default shallow water fill threshold)
mc_eid_with_deep_fill = []
mc_depth_threshold_def = 0.762
mc_depth_threshold_deep = 9999.999


# link ID numbers for 'composite' marsh flow links (type 11) that need to be updated due to marsh creation projects
mc_links = []
# Years (calendar year) to update each respective'composite' marsh flow links (type 11) for marsh creation projects - this value should be the year after the project is implemented in the morphology model
mc_links_years = []

# Shoreline protection project IDs that are implemented in this simulation
sp_projectIDs = []
# Years (calendar year) to implement each respective shoreline protection project listed above
sp_years = []

# Levee and ridge project IDs that are implemented in this simulation
rr_projectIDs = []
# Years (calendar year) to implement each respective levee and ridge restoration project listed above
rr_years = []

# Compartment numbers to have new bed elevations assigned (e.g. dredging)
comps_to_change_elev = []
# New bed elevation for compartments that will be updated for dredging
comp_elevs = []
# Years (calendar year) when compartments will have new elevations updated
comp_years = []

# Active deltaic compartment file names that are used by ICM-Morph (all files must be saved in S##/G###/geomorph/input directory)
act_del_files = []
# Years (calendar year) to implement each respective active deltaic compartment file listed above
act_del_years = []


# check that project implementation variables are of the correct lengths
InputErrorFlag = 0
InputErrorMsg = ''
if len(link_years) != len(links_to_change):
    InputErrorFlag = 1
    InputErrorMsg = '%sNumber of links to activate/deactivate and implementation years are not equal in length!\n' % InputErrorMsg
if len(mc_links_years) != len(mc_links):
    InputErrorFlag = 1
    InputErrorMsg = '%sNumber of links to update for marsh creation projects and implementation years are not equal in length!\n' % InputErrorMsg
if len(mc_years) != len(mc_elementIDs):
    InputErrorFlag = 1
    InputErrorMsg = '%sMarsh Creation Project Implementation variables are not of equal length!\n' % InputErrorMsg
if len(sp_years) != len(sp_projectIDs):
    InputErrorFlag = 1
    InputErrorMsg = '%sShoreline Protection Project Implementation variables are not of equal length!\n' % InputErrorMsg
if len(rr_years) != len(rr_projectIDs):
    InputErrorFlag = 1
    InputErrorMsg = '%sLevee & Ridge Project Implementation variables are not of equal length!\n' % InputErrorMsg
if len(act_del_years) != len(act_del_files):
    InputErrorFlag = 1
    InputErrorMsg = '%sActive Deltaic Compartment project variables are not of equal length!\n' % InputErrorMsg

    
if InputErrorFlag == 1:
    print(' ***********Error with Project Implementation variables! Fix and re-run!\n')
    sys.exit(InputErrorMsg)


par_dir = os.getcwd()

inputs = np.genfromtxt('ICM_control.csv',dtype=str,comments='#',delimiter=',')

# Parent directory locations for various ICM components
# These directories must exist in the model folder
# Other directories are created throughout the ICM run - but they are all based on these parent directories
ecohydro_dir = os.path.normpath('%s/%s' % (par_dir,inputs[1,1].lstrip().rstrip()))
wetland_morph_dir = os.path.normpath('%s/%s' % (par_dir,inputs[2,1].lstrip().rstrip()))
vegetation_dir = os.path.normpath('%s/%s' % (par_dir,inputs[3,1].lstrip().rstrip()))
bimode_dir = os.path.normpath('%s/%s' % (par_dir,inputs[4,1].lstrip().rstrip()))
HSI_dir = os.path.normpath('%s/%s' % (par_dir,inputs[5,1].lstrip().rstrip()))
HDI_dir = os.path.normpath('%s/%s' % (par_dir,inputs[6,1].lstrip().rstrip()))
ewe_dir = 'null'    #os.path.normpath('%s/%s' % (par_dir,inputs[6,1].lstrip().rstrip()))

#default# hydro_exe_path = './hydro_v23.4.0' 
#default# bidem_exe_path = './bidem_v23.0.0'
#default# morph_exe_path = './morph_v23.1.0' 

hydro_exe_path      = inputs[7,1].lstrip().rstrip()         # path to hydro executable - ** path is relative to the S##/G###/hydro        ** - use './' if running copy of executable that is saved in /hydro directory 
bidem_exe_path      = inputs[8,1].lstrip().rstrip()         # path to bidem executable - ** path is relative to the S##/G###/bidem/REGION ** - use './' if running copy of executable that is saved in /bidem/REGION directory
morph_exe_path      = inputs[9,1].lstrip().rstrip()         # path to morph executable - ** path is relative to the S##/G###              ** - use './' if running copy of executable that is saved in /G## directory
veg_exe_path        = inputs[10,1].lstrip().rstrip()        # path to veg executable - ** path is relative to the S##/G###              ** - use './' if running copy of executable that is saved in /G## directory
sav_submit_exe_path = inputs[11,1].lstrip().rstrip()        # path to exectuable to submit SAV job to queue  # '/ocean/projects/bcs200002p/ewhite12/code/git/ICM/submit_SAV.py'
run_sav             = int(inputs[12,1].lstrip().rstrip())   # 1 to submit SAV simulations to queue at end of year; 0 to not run SAV
wva_submit_exe_path = inputs[13,1].lstrip().rstrip()        # path to exectuable to submit WVA job to queue
run_wva             = int(inputs[14,1].lstrip().rstrip())   # 1 to submit WVA simulations to queue at end of year (after SAV); 0 to not run WVA


# Configuration files used by various ICM components
VegConfigFile = inputs[15,1].lstrip().rstrip()
WMConfigFile = inputs[16,1].lstrip().rstrip()
EHConfigFile = inputs[17,1].lstrip().rstrip()
EHCellsFile = inputs[18,1].lstrip().rstrip()
EHLinksFile = inputs[19,1].lstrip().rstrip()
BIMHWFile = inputs[20,1].lstrip().rstrip()
exist_cond_tag = inputs[21,1].lstrip().rstrip()
fwoa_init_cond_tag = inputs[22,1].lstrip().rstrip()
shallow_subsidence_column = int(inputs[23,1].lstrip().rstrip())

compartment_output_file = 'compartment_out.csv'
grid_output_file        = 'grid_500m_out.csv'
EHInterfaceFile         = 'ICM_info_into_EH.txt'
dem_res = 30.0

# Filenames for Veg model input
WaveAmplitudeFile = inputs[24,1].lstrip().rstrip()
MeanSalinityFile = inputs[25,1].lstrip().rstrip()
SummerMeanWaterDepthFile = inputs[26,1].lstrip().rstrip()
SummerMeanSalinityFile = inputs[27,1].lstrip().rstrip()
SummerMeanTempFile = inputs[28,1].lstrip().rstrip()
TreeEstCondFile = inputs[29,1].lstrip().rstrip()
HtAbvWaterFile = inputs[30,1].lstrip().rstrip()
PerLandFile = inputs[31,1].lstrip().rstrip()
PerWaterFile = inputs[32,1].lstrip().rstrip()
AcuteSalFile = inputs[33,1].lstrip().rstrip()
acute_sal_threshold = 5.5

## Simulation Settings
startyear = int(inputs[34,1].lstrip().rstrip())
endyear = int(inputs[35,1].lstrip().rstrip())
ncycle = int(inputs[36,1].lstrip().rstrip())
startyear_cycle = int(inputs[37,1].lstrip().rstrip())
endyear_cycle = int(inputs[38,1].lstrip().rstrip())
inputStartYear = int(inputs[39,1].lstrip().rstrip())
nvegtype = int(inputs[40,1].lstrip().rstrip())
update_hydro_attr = int(inputs[41,1].lstrip().rstrip())

# convert calendar years to elapsed years
hotstart_year = startyear_cycle
elapsed_hotstart = hotstart_year - startyear
cycle_start_elapsed = startyear_cycle - startyear
cycle_end_elapsed = endyear_cycle - startyear + 1

hotstart_year = startyear_cycle
cycle_start_elapsed = startyear_cycle - startyear + 1
cycle_end_elapsed = endyear_cycle - startyear + 1


## grid information for Veg ASCII grid files
n500grid= int(inputs[42,1].lstrip().rstrip())
# n500gridveg = int(inputs[25,1].lstrip().rstrip()) #total number of grid cells in Veg model - including NoData cells
n500rows = int(inputs[43,1].lstrip().rstrip())
n500cols = int(inputs[44,1].lstrip().rstrip())
xll500 = int(inputs[45,1].lstrip().rstrip())
yll500 = int(inputs[46,1].lstrip().rstrip())

## grid information for EwE ASCII grid files
n1000grid = int(inputs[47,1].lstrip().rstrip())
n1000rows = int(inputs[48,1].lstrip().rstrip())
n1000cols = int(inputs[49,1].lstrip().rstrip())
xll1000 = inputs[50,1].lstrip().rstrip()
yll1000 = inputs[51,1].lstrip().rstrip()

# file naming convention settings
mpterm = inputs[52,1].lstrip().rstrip()
sterm = inputs[53,1].lstrip().rstrip()
gterm = inputs[54,1].lstrip().rstrip()
cterm = inputs[55,1].lstrip().rstrip()
uterm = inputs[56,1].lstrip().rstrip()
vterm = inputs[57,1].lstrip().rstrip()
rterm = inputs[58,1].lstrip().rstrip()


# build some file naming convention tags
runprefix = '%s_%s_%s_%s_%s_%s_%s' % (mpterm,sterm,gterm,cterm,uterm,vterm,rterm)
file_prefix_cycle = r'%s_N_%02d_%02d' % (runprefix,cycle_start_elapsed,cycle_end_elapsed)
file_o_01_end_prefix = r'%s_O_01_%02d' % (runprefix,endyear-startyear+1)




# 1D Hydro model information
n_1D = int(inputs[59,1].lstrip().rstrip())
RmConfigFile = inputs[60,1].lstrip().rstrip()

## Barrier Island Model settings
BITIconfig = inputs[61,1].lstrip().rstrip()
n_bimode = int(inputs[62,1].lstrip().rstrip())
bimode_folders=[]
for row in range(63,63+n_bimode):
    bimode_folders.append(inputs[row,1].lstrip().rstrip())
bidem_fixed_grids=[]
for row in range(63+n_bimode,63+2*n_bimode):
    bidem_fixed_grids.append(inputs[row,1].lstrip().rstrip())

# read in asci grid structure
asc_grid_file = os.path.normpath(r'%s/veg_grid.asc' % vegetation_dir)
asc_grid_ids = np.genfromtxt(asc_grid_file,skip_header=6,delimiter=' ',dtype='int')
asc_grid_head = 'ncols 1052\nnrows 365\nxllcorner 404710\nyllcorner 3199480\ncellsize 480\nNODATA_value -9999\n'

# read in compartment-to-grid structure
grid_lookup_file = '%s/grid_lookup_500m.csv' % ecohydro_dir
grid_comp_np = np.genfromtxt(grid_lookup_file,delimiter=',',skip_header=1,usecols=[0,1],dtype='int')
grid_comp_dict = {rows[0]:rows[1] for rows in grid_comp_np}
del(grid_comp_np)



#########################################################
##            SETTING UP ICM-HYDRO MODEL               ##
#########################################################

print(' Configuring ICM-Hydro.')


# Load 1D River Model Configuration file

if n_1D > 0:
    f = open(RmConfigFile, "r")
    templine = f.readlines()
    f.close()

    HydroConfigFile=[]
    SalConfigFile=[]
    TempConfigFile=[]
    FineConfigFile=[]
    SandConfigFile=[]
    Sub_Sal=[]
    Sub_Temp=[]
    Sub_Fine=[]
    Sub_Sand=[]
    n_xs=[]
    Hydro_dt=[]
    Sal_dt=[]
    Tmp_dt=[]
    Fine_dt=[]
    Sand_dt=[]
    n_lc=[]

    if n_1D != int(templine[0].split("!")[0].lstrip().rstrip()):
        exitmsg='\n Number of 1D regions defined in ICM_control.csv and region_input.txt are not consistent. Please check.'
        sys.exit(exitmsg)

    idx = 1
    for i in range (0,n_1D):
        n_xs.append(int(templine[idx].split()[0].lstrip().rstrip()))
        Hydro_dt.append(int(templine[idx].split()[1].lstrip().rstrip()))
        n_lc.append(int(templine[idx].split()[2].lstrip().rstrip()))
        idx = idx+1
        HydroConfigFile.append(templine[idx].split("!")[0].lstrip().rstrip())
        idx = idx+1
        Sub_Sal.append(templine[idx].split()[0].lstrip().rstrip())
        Sub_Temp.append(templine[idx].split()[1].lstrip().rstrip())
        Sub_Fine.append(templine[idx].split()[2].lstrip().rstrip())
        Sub_Sand.append(templine[idx].split()[3].lstrip().rstrip())
        if Sub_Sal[i]=="1":
            idx = idx+1
            Sal_dt.append(templine[idx].split("!")[0].lstrip().rstrip())
            idx = idx+1
            SalConfigFile.append(templine[idx].split("!")[0].lstrip().rstrip())
        else:
            Sal_dt.append("na")
            SalConfigFile.append("na")
        if Sub_Temp[i]=="1":
            idx = idx+1
            Tmp_dt.append(templine[idx].split("!")[0].lstrip().rstrip())
            idx = idx+1
            TempConfigFile.append(templine[idx].split("!")[0].lstrip().rstrip())
        else:
            Tmp_dt.append("na")
            TempConfigFile.append("na")
        if Sub_Fine[i]=="1":
            idx = idx+1
            Fine_dt.append(templine[idx].split("!")[0].lstrip().rstrip())
            idx = idx+1
            FineConfigFile.append(templine[idx].split("!")[0].lstrip().rstrip())
        else:
            Fine_dt.append("na")
            FineConfigFile.append("na")
        if Sub_Sand[i]=="1":
            idx = idx+1
            Sand_dt.append(templine[idx].split("!")[0].lstrip().rstrip())
            idx = idx+1
            SandConfigFile.append(templine[idx].split("!")[0].lstrip().rstrip())
        else:
            Sand_dt.append("na")
            SandConfigFile.append("na")
        idx = idx+1

    # In the input file passed into Fortran, there needs to be quotes around the filepath
    # Those quotes need to be removed in for Python
    # Run this loop twice - checking for both single and double quotation marks
    # this could be updated using the variable "lq" defined below
    for i in range (0,n_1D):
        HydroConfigFile[i]   = HydroConfigFile[i].replace("'","")
        SandConfigFile[i]    = SandConfigFile[i].replace("'","")
        FineConfigFile[i]    = FineConfigFile[i].replace("'","")
        TempConfigFile[i]    = TempConfigFile[i].replace("'","")
        SalConfigFile[i]     = SalConfigFile[i].replace("'","")
    for i in range (0,n_1D):
        HydroConfigFile[i]   = HydroConfigFile[i].replace('"','')
        SandConfigFile[i]    = SandConfigFile[i].replace('"','')
        FineConfigFile[i]    = FineConfigFile[i].replace('"','')
        TempConfigFile[i]    = TempConfigFile[i].replace('"','')
        SalConfigFile[i]     = SalConfigFile[i].replace('"','')



# change working directory to hydro folder
os.chdir(ecohydro_dir)

## Check if output files from Ecohydro model exist in the project directory.
## These are opened and written to in 'append' mode in the Fortran code, so they cannot exist in the model
## directory before ICM year 1 is run.
## In the first model year, these files will not exist, so Fortran will automatically generate them.
## In all subsequent model years, results will be appended to end of existing output files.
eh_outfiles = os.listdir(ecohydro_dir)

ehflag = 0
for files in eh_outfiles:
        if files.endswith('.out'):
                ehflag = 1

if elapsed_hotstart > 0:
    ehflag = 0

if ehflag == 1:
    print('\n**************ERROR**************')
    print('\n Hydro output files already exist in Hydro project directory.')

    exitmsg='\n Manually remove *.out files and re-run ICM.'
    sys.exit(exitmsg)

## repeat check for output files - but look in Veg folder for files generated by hydro.exe Fortran program
## change working directory to veg folder
os.chdir(vegetation_dir)

## Need to select path delimiter since this is getting written to a file to be read into Fortran that is not flexible when running in Windows.
## Also need to set whether a leading quote is needed when writing filepaths to a file that will be read as Input to Fortran program
if os.name == 'nt':
    path_del = '\\'
    lq = "" # I do not think that a leading quote is required for Windows Fortran when \\ is used - possibly need to delete this
else:
    path_del = '/'
    lq = "'"

# LAVegMod files that are written by ICM-Hydro Fortran (need special leading quotes and path delimiters for passing into Fortran via text I/O files)
VegWaveAmpFile     = r"%s%s%s%s_H_%s%s" % (lq,vegetation_dir,path_del,file_prefix_cycle,WaveAmplitudeFile,lq)
VegMeanSalFile     = r"%s%s%s%s_H_%s%s" % (lq,vegetation_dir,path_del,file_prefix_cycle,MeanSalinityFile,lq)
VegSummerDepthFile = r"%s%s%s%s_H_%s%s" % (lq,vegetation_dir,path_del,file_prefix_cycle,SummerMeanWaterDepthFile,lq)
VegSummerSalFile   = r"%s%s%s%s_H_%s%s" % (lq,vegetation_dir,path_del,file_prefix_cycle,SummerMeanSalinityFile,lq)
VegSummerTempFile  = r"%s%s%s%s_H_%s%s" % (lq,vegetation_dir,path_del,file_prefix_cycle,SummerMeanTempFile,lq)
VegTreeEstCondFile = r"%s%s%s%s_H_%s%s" % (lq,vegetation_dir,path_del,file_prefix_cycle,TreeEstCondFile,lq)
VegBIHeightFile    = r"%s%s%s%s_H_%s%s" % (lq,vegetation_dir,path_del,file_prefix_cycle,HtAbvWaterFile,lq)
VegPerLandFile     = r"%s%s%s%s_H_%s%s" % (lq,vegetation_dir,path_del,file_prefix_cycle,PerLandFile,lq)
ehveg_outfiles = [VegWaveAmpFile,VegMeanSalFile,VegSummerDepthFile,VegSummerSalFile,VegSummerTempFile,VegTreeEstCondFile,VegBIHeightFile,VegPerLandFile]

# LAVegMod files that are written later by ICM.py (no need for special quotation/path delimiters since not being passed into Fortran)
pwatr_grid_file     = os.path.normpath(r'%s/%s_H_%s'     % (vegetation_dir,file_prefix_cycle,PerWaterFile) )
acute_sal_grid_file = os.path.normpath(r'%s/%s_H_%s' % (vegetation_dir,file_prefix_cycle,AcuteSalFile) )

vegflag = 0

for veginfile in ehveg_outfiles:
    if os.path.isfile(veginfile.replace(lq,"")) == True:               # remove any leading quotes from vegfile path
        vegflag = 1

if elapsed_hotstart > 0:
    vegflag = 0


if vegflag == 1:
    print('\n**************ERROR**************')
    print('\n Hydro output files formatted for Veg model already exist in Veg project directory.\n Move or delete files and re-run ICM.')
    exitmsg='\n Manually remove files from Veg directory and re-run ICM.'
    sys.exit(exitmsg)

## change working directory to hydro folder
os.chdir(ecohydro_dir)

# create temporary files folder - where ICM files will be saved for examination or debugging
# Temporary file location must not exist
## errno.EEXIST is a cross-platform 'existing file' error flag
EHtemp_path = os.path.normpath(r'%s/TempFiles' % ecohydro_dir)

rnflag = 0

if os.path.isdir(EHtemp_path):
        rnflag=1

if elapsed_hotstart > 0:
    rnflag = 0

if rnflag == 1:
    print('\n**************ERROR**************')
    print('\n Temporary folder for Hydro files already exists.')
    exitmsg='\n Manually delete TempFiles directory and re-run ICM.'
    sys.exit(exitmsg)

if elapsed_hotstart == 0:
    try:
        os.makedirs(EHtemp_path)

    except OSError as Exception:
        print('******ERROR******'       )
        error_msg = ' Error encountered during Hydrology Model configuration.\n'+str(Exception)+'\n Check error and re-run ICM.'
        ## re-write error message if it was explictily an 'existing file' error.
        if Exception.errno == errno.EEXIST:
            error_msg = '\n Temporary folder for Hydro files already exists.\n Rename existing folder if files are needed, otherwise delete and re-run ICM.'


del (ehflag,vegflag,rnflag)
print(' Writing file to be passed to Hydro routine containing location of files shared with Vegetation Model.')


max_string = max(len(VegWaveAmpFile),len(VegMeanSalFile),len(VegSummerDepthFile),len(VegSummerSalFile),len(VegSummerTempFile),len(VegTreeEstCondFile),len(VegPerLandFile))

## Write input file with directories for use in Hydro Fortran module
## This will overwrite any ICM_directories.txt file already saved in the Hydro folder
## length limit of 200 is set due to the character string size declared in the compiled Fortran code
## If the directory location HAS to be longer than 200 characters, this flag will have to be updated
## AND the Fortran Hydro code will have to be updated to allocate a larger variable (in 'params' module)
if max_string > 300:
    error_msg1 ='\n **************ERROR**************'
    error_msg2 = 'The directory location string for the Vegetation files are longer than 300 characters, it will not be correctly passed to the compiled Fortran program. Either rename the directory or edit ICM.py and params.f source code files and recompile.'
    print(error_msg1)
    sys.exit(error_msg2)
else:
    file_for_hydro = os.path.normpath(r'%s/%s' % (ecohydro_dir,EHInterfaceFile))
    ## Exclamation point in write statments indicate comments in file that are ignored by the Ecohydro Fortran code ("!" is comment character in Fortran)
    ## Filepaths are set above and should be full path and include any opening/closing quotation marks that may be required to be passed into Fortran IO (Fortran will skip over / path delimiters unless within quotations)
    with open(file_for_hydro,'w') as f:
        f.write(VegWaveAmpFile+'\t\t!Annual water level variability file for LAVegMod')
        f.write('\n')
        f.write(VegMeanSalFile+'\t\t!Annual mean salinity file for LAVegMod')
        f.write('\n')
        f.write(VegSummerDepthFile+'\t\t!Summer mean water depth file for LAVegMod')
        f.write('\n')
        f.write(VegSummerSalFile+'\t\t!Summer mean salinity file for LAVegMod')
        f.write('\n')
        f.write(VegSummerTempFile+'\t\t!Summer mean water temperature file for LAVegMod')
        f.write('\n')
        f.write(VegTreeEstCondFile+'\t\t!Tree establishment conditions flag file for LAVegMod')
        f.write('\n')
        f.write(VegBIHeightFile+'\t\t!Height above annual mean water level file for LAVegMod')
        f.write('\n')
        f.write(VegPerLandFile+'\t\t!Percentage of grid cell that is land file for LAVegMod')
        f.write('\n')
        f.write(str(n500grid)+'\t\t!Number of cells in 500m grid')
        f.write('\n')
        f.write(str(n500rows)+'\t\t!Number of rows in formatted ASCI file passed to LAVegMod')
        f.write('\n')
        f.write(str(n500cols)+'\t\t!Number of columns in formatted ASCI file passed to LAVegMod')
        f.write('\n')
        f.write(str(xll500)+'\t\t!UTM-X for lower left corner of 500m grid')
        f.write('\n')
        f.write(str(yll500)+'\t\t!UTM-Y for lower left corner of 500m grid')
        f.write('\n')
        f.write(str(n1000grid)+'\t\t!Number of cells in 1000m grid')
        f.write('\n')
        f.write(str(n1000rows)+'\t\t!Number of rows in formatted ASCI file passed to EwE')
        f.write('\n')
        f.write(str(n1000cols)+'\t\t!Number of columns in formatted ASCI file passed to EwE')
        f.write('\n')
        f.write(str(xll1000)+'\t\t!UTM-X for lower left corner of 1000m grid')
        f.write('\n')
        f.write(str(yll1000)+'\t\t!UTM-Y for lower left corner of 1000m grid')
        f.write('\n')
        f.write(str(hydro_logfile)+'\t\t!Name of hydro log file to write messages to')

## file containing percentage land, and land/water elevations for each 500-m grid cell as it is used by hydro (file is generated by Morph)
## when in the main Hydro directory, this file does not have a calendar year in the file name
## and it represents the landscape at the end of the previous year
## when the file is originally generated by ICM-Morph at the end of the year, the calendar year will be in the filename
## after Hydro is run, the calendar year is added back to the filename and it is moved to the TempFiles folder with other Hydro annual filesl
EH_grid_file = 'grid_data_500m.csv' # this must match file name used in hydro.exe
EH_grid_filepath = os.path.normpath('%s/%s' % (ecohydro_dir,EH_grid_file)) # location of grid_data_500m.csv when used by hydro.exe


# check that Hydro input files exist - if not, try and get them from the TempFiles for the previous year
if os.path.isfile(EHConfigFile) == False:
    print('\n******File check failed*********\n%s not found - checking for previous year file in hydro\Tempfiles' % EHConfigFile)
    try:
        prv_EHConfigFile = os.path.normpath(r"%s/%s_%04d.%s" % (EHtemp_path,str.split(EHConfigFile,'.')[0],startyear_cycle-1,str.split(EHConfigFile,'.')[1]))
        shutil.copyfile(prv_EHConfigFile,EHConfigFile)
    except:
        sys.exit('\n******File copy failed*********\nCould not find %s - exiting run.'% EHConfigFile) 

if os.path.isfile(EHCellsFile) == False:
    print('\n******File check failed*********\n%s not found - checking for previous year file in hydro\Tempfiles' % EHCellsFile)
    try:
        prv_EHCellsFile = os.path.normpath(r"%s/%s_%04d.%s" % (EHtemp_path,str.split(EHCellsFile,'.')[0],startyear_cycle-1,str.split(EHCellsFile,'.')[1]))
        shutil.copyfile(prv_EHCellsFile,EHCellsFile)
    except:
        sys.exit('\n******File copy failed*********\nCould not find %s - exiting run.' % EHCellsFile) 

if os.path.isfile(EHLinksFile) == False:
    print('\n******File check failed*********\n%s not found - checking for previous year file in hydro\Tempfiles' % EHLinksFile)
    try:
        prv_EHLinksFile = os.path.normpath(r"%s/%s_%04d.%s" % (EHtemp_path,str.split(EHLinksFile,'.')[0],startyear_cycle-1,str.split(EHLinksFile,'.')[1]))
        shutil.copyfile(prv_EHLinksFile,EHLinksFile)
    except:
        sys.exit('\n******File copy failed*********\nCould not find %s - exiting run.' % EHLinksFile) 

if os.path.isfile(EH_grid_file) == False:
    print('\n******File check failed*********\n%s not found - checking for previous year file in hydro\Tempfiles' % EH_grid_file)
    try:
        prv_EH_grid_file = os.path.normpath(r"%s/%s_end%04d.%s" % (EHtemp_path,str.split(EH_grid_file,'.')[0],startyear_cycle-1,str.split(EH_grid_file,'.')[1]))
        shutil.copyfile(prv_EH_grid_file,EH_grid_file)
    except:
        sys.exit('\n******File copy failed*********\nCould not find %s - exiting run.' % EH_grid_file) 

# EH_hs_file = 'hotstart_in.dat'
# if os.path.isfile(EH_hs_file) == False:
#     print('\n******File check failed*********\n%s not found - checking for previous year file in hydro\Tempfiles' % EH_hs_file)
#     try:
#         prv_EH_hs_file = 'hotstart_out.dat'
#         shutil.copyfile(prv_EH_hs_file,EH_hs_file)
#         os.remove(prv_EH_hs_file)
#     except:
#         sys.exit('\n******File copy failed*********\nCould not find %s - exiting run.' % EH_hs_file) 


## Read Ecohydro's initial configuration, compartmentm and link attributes file into an arrayfile into an array of strings
cellsheader='Compartment,TotalArea,AreaWaterPortion,AreaUplandPortion,AreaMarshPortion,MarshEdgeLength,WSEL_init,bed_elev,bed_depth,bed_bulk_density,percentForETcalc,initial_sand,initial_salinity,RainGage,WindGage,ETGage,CurrentsCoeff_ka,bedFricCoeff_cf,NonSandExp_sedn,NonSandCoeff_sedcalib,SandCoeff_alphased,Marsh_Flow_roughness_Kka,Minimum_Marsh_Flow_Depth_Kkdepth,MarshEdgeErosionRate_myr,initial_stage_marsh,marsh_elev_mean,marsh_elev_stdv,soil_moisture_depth_Esho,depo_on_off,marh_elev_adjust'
cells_ncol = range(0,30)

linksheader='ICM_ID,USnode_ICM,DSnode_ICM,USx,USy,DSx,DSy,Type,attr01,attr02,attr03,attr04,attr05,attr06,attr07,attr08,Exy,attr09,attr10,fa_multi'
links_ncol = range(0,20)

EHConfigArray=np.genfromtxt(EHConfigFile,dtype=str,delimiter='!',autostrip=True)
EHCellsArray = np.genfromtxt(EHCellsFile,dtype=float,delimiter=',',skip_header=1,usecols=cells_ncol)
EHLinksArray = np.genfromtxt(EHLinksFile,dtype=float,delimiter=',',skip_header=1,usecols=links_ncol)

# read in initial Cell/Link settings for first year of entire run, not just current cycle
if startyear_cycle == startyear: 
    EHCellsArrayOrig = EHCellsArray
    EHLinksArrayOrig = EHLinksArray
else:
    EHCellsFileOrig  = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EHCellsFile,'.')[0],startyear,str.split(EHCellsFile,'.')[1]))
    EHLinksFileOrig  = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EHLinksFile,'.')[0],startyear,str.split(EHLinksFile,'.')[1]))

    EHCellsArrayOrig = np.genfromtxt(EHCellsFileOrig,dtype=float,delimiter=',',skip_header=1,usecols=cells_ncol)
    EHLinksArrayOrig = np.genfromtxt(EHLinksFileOrig,dtype=float,delimiter=',',skip_header=1,usecols=links_ncol)

ncomp = len(EHCellsArray)




# check to see if hydro input data start date is different than ICM start year
if inputStartYear > startyear:
    exitmsg='\n Invalid configuration! ICM model set to start before Hydro input data coverage. Check ICM_control.csv file and re-run.'
    sys.exit(exitmsg)

# startrun is row of ICM-Hydro input data files to import into ICM-Hydro.exe
# used to skip over data in input files for years greater than the initial model year
# will be 0 if the first year of the simulation matches the first year of the ICM-Hydro input files
startrun = 0
for year in range(inputStartYear,hotstart_year):
    if year in range(1984,4000,4):
        ndays = 366
    else:
        ndays = 365
    startrun = startrun + ndays


#########################################################
##               SETTING UP ICM-LAVegMod               ##
#########################################################
# change to Veg directory
os.chdir(vegetation_dir)

print(' Writing ICM-LAVegMod Configuration file for current cycle for years %02d:%02d'  % (cycle_start_elapsed,cycle_end_elapsed))
# write csv string of all years included in this LAVegMod run cycle
yrstr = '%02d' % (cycle_start_elapsed)
for vy in range(cycle_start_elapsed+1,cycle_end_elapsed+1):
    yrstr = '%s,%02d' % (yrstr,vy)


# write config file for ICM-LAVegMod given the current years being simulated for model cycle
# only lines that have dynamic variable names are updated here
# if not dynamic, original line from lavegmod_proto.config.og will be re-written


with open('lavegmod_proto.config.og',mode='r') as lvcr:
    with open('lavegmod_proto.config',mode='w') as lvcw:
        for line in lvcr:
            if '=' in line:
                lvm_var = line.split('=')[0]
                lvm_val = line.split('=')[1]
                
                if lvm_var.strip() == 'StartYear':
                    if startyear_cycle == startyear:
                        dm = lvcw.write('%s= 00\n' % lvm_var )
                    else:
                        dm = lvcw.write('%s= %02d\n' % (lvm_var,cycle_start_elapsed-1) ) # start year should the year which is represented by the initial conditions file
                
                elif lvm_var.strip() == 'EndYear':
                    dm = lvcw.write('%s= %02d\n' % (lvm_var,cycle_end_elapsed) )
                
                elif lvm_var.strip() == 'NumYears':
                    dm = lvcw.write('%s= %02d\n' % (lvm_var,cycle_end_elapsed-cycle_start_elapsed+1) )
                
                elif lvm_var.strip() == 'InitialConditionFile':
                    if startyear_cycle == startyear:
                        dm = lvcw.write(line)
                    else:
                        dm = lvcw.write( '%s= %s_O_%02d_%02d_V_vegty.asc+\n' % (lvm_var,runprefix,cycle_start_elapsed-1,cycle_start_elapsed-1 ) )

                elif lvm_var.strip() == 'WetlandMorphLandWaterFile':
                    dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,PerWaterFile) )

                elif lvm_var.strip() == 'WetlandMorphYears':
                    dm = lvcw.write( '%s= %02d:%02d\n' % (lvm_var,cycle_start_elapsed,cycle_end_elapsed) )
                
                elif lvm_var.strip() == 'WaveAmplitudeFile':
                    dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,WaveAmplitudeFile) )
                
                elif lvm_var.strip() == 'MeanSalinityFile':
                    dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,MeanSalinityFile) )
                
                elif lvm_var.strip() == 'SummerMeanWaterDepthFile':
                    dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,SummerMeanWaterDepthFile) )
                
                elif lvm_var.strip() == 'SummerMeanSalinityFile':
                    dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,SummerMeanSalinityFile) )
                
                elif lvm_var.strip() == 'SummerMeanTempFile':
                    dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,SummerMeanTempFile) )
                
                elif lvm_var.strip() == 'TreeEstCondFile':
                    dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,TreeEstCondFile) )

                elif lvm_var.strip() == 'AcuteSalinityStressFile':
                    dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,AcuteSalFile) )
                
                elif lvm_var.strip() == 'BarrierIslandHeightAboveWaterFile':
                    dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,HtAbvWaterFile) )
                
                elif lvm_var.strip() == 'HeightAboveWaterFile':
                    dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,HtAbvWaterFile) )

                elif lvm_var.strip() == 'OutputTemplate':
                    dm = lvcw.write( '%s= %s_O_<YEAR>_<YEAR>_V_vegty.asc+\n' % (lvm_var,runprefix) )
                   
                elif lvm_var.strip() == 'OutputYears':
                    dm = lvcw.write( '%s= %s\n' % (lvm_var,yrstr) )
                
                elif lvm_var.strip() == 'DeadFloatingTemplate':
                    dm = lvcw.write( '%s= %s_O_<YEAR>_<YEAR>_V_deadf.asc\n' % (lvm_var,runprefix) )                    
                
                elif lvm_var.strip() == 'DeadFloatingYears':
                    dm = lvcw.write( '%s= %s\n' % (lvm_var,yrstr) )
                
                else:           # if line does not include a dynamic field - just re-write the file from the original config file
                    dm = lvcw.write(line)
            else:               # if line does not have an =, it is blank for formatting - re-write the empty line for consistency
                dm = lvcw.write(line)

#########################################################
##        SETTING UP ICM-BARRIER ISLAND MODEL          ##
#########################################################
# change back to Hydro directory
os.chdir(ecohydro_dir)

print(' Configuring sea level rise rate files for ICM-BIDEM.')

tide_file = os.path.normpath(r'%s/TideData.csv' % ecohydro_dir)
tide_data = np.genfromtxt(tide_file,skip_header=1,delimiter=',',dtype='str')

annual_mean_mm = []
for year in range(inputStartYear,endyear):
    n = 0
    annual_total = 0
    for r in tide_data:
        if int(r[0][0:4]) == year:                  # 1st column in TideData is YYYYMMDD HH:MM
            annual_total += float(r[3])             # 4th column in TideData is Amerada Pass, LA
            n+=1                                    # 8760 hours or 8784 hours if leap year
    annual_mean_mm.append((annual_total/n)*1000)    # take the mean of the hourly data and convert from m to mm
yrs4polyfit = range(inputStartYear,endyear)
p = np.polyfit(yrs4polyfit, np.asarray(annual_mean_mm),2) # fit a quadratic to the annual mean data
ESLR_rate_mmyr = []
for year in range(inputStartYear,endyear):
    ESLR_rate_mmyr.append((p[0]*2*year)+(p[1]))     # take the first derivative and plug in years to get the rate

for fol in bimode_folders:
    ESLR_out_file = r'%s/%s/input/SLR_record4modulation.txt' %(bimode_dir,fol)
    with open(ESLR_out_file, mode='w') as outf:
        i = 0
        for year in range(inputStartYear,endyear):
            outf.write("%d %0.2f\n" % (year,ESLR_rate_mmyr[i]))
            i += 1

print(' Configuring tidal inlet settings for ICM-BITI.')
# Barrier Island Tidal Inlet (BITI) input file
# The input file only needs to be read once
# It contains the comp IDs, link IDs, depth to width ratios, partition coefficients, and basin-wide factors.
# The Pandas.iloc pointer is used below and must be updated if input file changes structure

BITI_input_filename = os.path.normpath(r'%s/%s' % (bimode_dir,BITIconfig) )

BITI_Terrebonne_setup = pandas.read_excel(BITI_input_filename, 'Terrebonne',index_col=None)
BITI_Barataria_setup = pandas.read_excel(BITI_input_filename, 'Barataria',index_col=None)
BITI_Pontchartrain_setup = pandas.read_excel(BITI_input_filename, 'Pontchartrain',index_col=None)

# Barrier Island Tidal Inlet (BITI) compartment IDs
# These are the compartments that make up each basin
BITI_Terrebonne_comp = list( BITI_Terrebonne_setup.iloc[3::,0] )
BITI_Barataria_comp = list( BITI_Barataria_setup.iloc[3::,0] )
BITI_Pontchartrain_comp = list( BITI_Pontchartrain_setup.iloc[3::,0] )

# Barrier Island Tidal Inlet (BITI) link IDs
# These are the links that respresent the tidal inlets in each basin
BITI_Terrebonne_link = list(BITI_Terrebonne_setup.iloc[0,1:-2])
BITI_Barataria_link = list(BITI_Barataria_setup.iloc[0,1:-2])
BITI_Pontchartrain_link = list(BITI_Pontchartrain_setup.iloc[0,1:-2])

BITI_Links = [BITI_Terrebonne_link,BITI_Barataria_link,BITI_Pontchartrain_link]

# Barrier Island Tidal Inlet (BITI) partition coefficients
# Each basin has it's own array of partition coefficients with size m by n,
# where m = number of compartments in the basin and n = the number of links in the basin
BITI_Terrebonne_partition = np.asarray(BITI_Terrebonne_setup)[3::,1:-2]
BITI_Barataria_partition = np.asarray(BITI_Barataria_setup)[3::,1:-2]
BITI_Pontchartrain_partition = np.asarray(BITI_Pontchartrain_setup)[3::,1:-2]

# Barrier Island Tidal Inlet (BITI) depth to width ratio (dwr) for each link in each basin (Depth/Width)
BITI_Terrebonne_dwr = list(BITI_Terrebonne_setup.iloc[1,1:-2])
BITI_Barataria_dwr = list(BITI_Barataria_setup.iloc[1,1:-2])
BITI_Pontchartrain_dwr = list(BITI_Pontchartrain_setup.iloc[1,1:-2])

# Barrier Island Tidal Inlet (BITI) basin-wide factor (BWF) for each basin
BITI_Terrebonne_BWF = float(BITI_Terrebonne_setup.iloc[1,-1])
BITI_Barataria_BWF = float(BITI_Barataria_setup.iloc[1,-1])
BITI_Pontchartrain_BWF = float(BITI_Pontchartrain_setup.iloc[1,-1])

# BITI effective tidal prism and inlet area
# kappa and alpha are the Gulf of Mexico constants for unjettied systems (units = metric)
kappa = 6.99e-4
alpha = 0.86

# BITI Links - initial channel dimensions
# Create a dictionary where key is link ID, first value is inlet depth, second value is inlet width
BITI_inlet_dimensions_init = {}
for n in range(0,len(BITI_Links)):
    for k in range(0,len(BITI_Links[n])):
        BITI_Link_ID = BITI_Links[n][k]
        EHLinks_index = int(BITI_Link_ID) - 1                        ## EHLinks is a numpy 0-based index, not dictionary with lookup
        orig_depth = 0.3 - EHLinksArrayOrig[EHLinks_index,8]        ## invert elevation is attribute1 for Type 1 links (column 8 in links array) - subtract invert from 0.3 meters to convert from invert to link depth (assuming that initial MWL in GoM is +0.3 m)
        orig_width = EHLinksArrayOrig[EHLinks_index,11]             ## channel width is attribute4 for Type 1 links (column 11 in links array)
        BITI_inlet_dimensions_init[BITI_Link_ID] = (orig_depth,orig_width)  



#########################################################
##              START YEARLY TIMESTEPPING              ##
#########################################################

for year in range(startyear+elapsed_hotstart,endyear_cycle+1):
    print('\n--------------------------------------------------')
    print('  START OF MODEL TIMESTEPPING LOOP - YEAR %s' % year)
    print('--------------------------------------------------\n')

    ## calculate elapsed years of model run
    elapsedyear = year - startyear + 1

    ## assign number of days in each month and length of year
    dom = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

    if year in range(1984,4000,4):
        print(r' Current model year (%s) is a leap year - input timeseries must include leap day' % year)
        ndays = 366
        dom[2] = 29
    else:
        ndays = 365
        dom[2] = 28

    # set year-specific file name prefixes
    file_prefix     = r'%s_N_%02d_%02d' % (runprefix,elapsedyear,elapsedyear)
    file_iprefix    = r'%s_I_%02d_%02d' % (runprefix,elapsedyear,elapsedyear)
    file_oprefix    = r'%s_O_%02d_%02d' % (runprefix,elapsedyear,elapsedyear)
    file_oprefix_prv = r'%s_O_%02d_%02d' % (runprefix,elapsedyear-1,elapsedyear-1)
    file_prefix_prv = r'%s_N_%02d_%02d' % (runprefix,elapsedyear-1,elapsedyear-1)


    #########################################################
    ##     SETTING UP 1D HYDRO MODEL FOR CURRENT YEAR      ##
    #########################################################
    os.chdir(ecohydro_dir)

    for i in range (0,n_1D):
        print(r' Preparing 1D Channel Hydro Input Files for reach %d - Year %s' % (i,year))

        print(HydroConfigFile[i])

        wr = write_1d_hyd_inp(HydroConfigFile,i,year,lq)
#        try:
#            wr = write_1d_hyd_inp(HydroConfigFile,i,year,lq)
#        except:
#            print('  - failed to write HYDRO input file for %s.   Retrying after 5 seconds.' % HydroConfigFile[i])
#            time.sleep(5)
#            try:
#                wr = write_1d_hyd_inp(HydroConfigFile,i,year,lq)
#            except:
#                print('  - failed on second attempt to write HYDRO input file for %s.   Quitting.' % HydroConfigFile[i])
#                sys.exit()
#

        if Sub_Sal[i]=="1":
            print(SalConfigFile[i])

            try:
                wr = write_1d_sal_inp(SalConfigFile,i,year,lq)
            except:
                print('  - failed to write SAL input file for %s.   Retrying after 5 seconds.' % SalConfigFile[i])
                time.sleep(5)
                try:
                    wr = write_1d_sal_inp(SalConfigFile,i,year,lq)
                except:
                    print('  - failed on second attempt to write SAL input file for %s.   Quitting.' % SalConfigFile[i])
                    sys.exit()



        if Sub_Temp[i]=="1":
            print(TempConfigFile[i])

            try:
                wr = write_1d_tmp_inp(TempConfigFile,i,year,lq)
            except:
                print('  - failed to write TMP input file for %s.   Retrying after 5 seconds.' % TempConfigFile[i])
                time.sleep(5)
                try:
                    wr = write_1d_tmp_inp(TempConfigFile,i,year,lq)
                except:
                    print('  - failed on second attempt to write TMP input file for %s.   Quitting.' % TempConfigFile[i])
                    sys.exit()


        if Sub_Fine[i]=="1":
            print(FineConfigFile[i])

            try:
                wr = write_1d_fine_inp(FineConfigFile,i,year,lq)
            except:
                print('  - failed to write FINES input file for %s.   Retrying after 5 seconds.' % FineConfigFile[i])
                time.sleep(5)
                try:
                    wr = write_1d_fine_inp(FineConfigFile,i,year,lq)
                except:
                    print('  - failed on second attempt to write FINES input file for %s.   Quitting.' % FineConfigFile[i])
                    sys.exit()

        if Sub_Sand[i]=="1":
            print(SandConfigFile[i])

            try:
                wr = write_1d_sand_inp(SandConfigFile,i,year,lq)
            except:
                print('  - failed to write SAND input file for %s.   Retrying after 5 seconds.' % SandConfigFile[i])
                time.sleep(5)
                try:
                    wr = write_1d_sand_inp(SandConfigFile,i,year,lq)
                except:
                    print('  - failed on second attempt to write SAND input file for %s.   Quitting.' % SandConfigFile[i])
                    sys.exit()

    #########################################################
    ##               SET UP HYDRO MODEL                    ##
    #########################################################
    print(r' Preparing Hydro Input Files - Year %s' % year)

    #change working directory to ecohydro folder
    os.chdir(ecohydro_dir)

    # set last day of Ecohydro run (inclusive)
    endrun = startrun + ndays - 1

    ##set year in Ecohydro input array
    EHConfigArray[0,0]=str(year)

    ##set start and end days in Ecohydryo input array
    EHConfigArray[8,0]=str(startrun)
    EHConfigArray[9,0]=str(endrun)

    ##write new fixed width Ecohydro Configuration file from updated array
    np.savetxt(EHConfigFile,EHConfigArray,fmt="%-11s !%s")  # Fortan '!' comment character needed between columns

    ## run various steps that update Ecohydro input files with new values
    ## skip if this is first year of ICM run
    if year != startyear:#+elapsed_hotstart:
        print(' Importing updated landscape attributes from Morphology output files - Year %s' % year)
        ## set output hotstart file generated from last model timestep to be new input hotstart file
        os.rename('hotstart_out.dat', 'hotstart_in.dat')
        ## update LW ratio in Cells.csv (compartment attributes table)
        # new pct water from WM output saved in temp folder during last model year (year-1)
        PctWaterFile = os.path.normpath(r'%s/PctWater_%s.csv' % (EHtemp_path,year-1))  # this must match filename set as 'comp_wat_file' variable written to ICM-Morph input_params.csv
        new_pctwater = np.genfromtxt(PctWaterFile,delimiter=',')
        new_pctwater_dict=dict((new_pctwater[n,0],new_pctwater[n,1]) for n in range(0,len(new_pctwater)))

        # move grid data file from location saved by previous year's Morph run to the Hydro directory (new_grid_filepath not defined until after Morph is run each year)
        # prev_new_grid_filepath will have the "endYYYY" in filename - EH_grid_filepath will not
        # this is then renamed with calendar year when moved to TempFiles after Hydro run is complete
        prev_new_grid_filepath  = os.path.normpath(r'%s/grid_data_500m_end%d.csv'  % (EHtemp_path,year-1) )  # this is the grid file generated by zonal statistics in the previous model year
        os.rename(prev_new_grid_filepath,EH_grid_filepath)

        # new pct upland from WM output saved in temp folder during last model year (year-1)
        PctUplandFile = os.path.normpath(r'%s/PctUpland_%s.csv' % (EHtemp_path,year-1))  # this must match filename set as 'comp_upl_file' variable written to ICM-Morph input_params.csv
        new_pctupland = np.genfromtxt(PctUplandFile,delimiter=',')
        new_pctupland_dict=dict((new_pctupland[n,0],new_pctupland[n,1]) for n in range(0,len(new_pctupland)))

        ## read in original bed and land elevation values for compartments as calculated from DEM- save in dictionaries where compartment ID is the key
        ## column 1 = compartment ID, column 2 = bed elev, column 3 = land elev, column 4 - marsh edge length
        # this file is used to calcualte elevation change for the year, which is then applied to the values in Cells.csv
        # this will allow for any manual manipulation of landscape elevations to the ICM-Hydro comps made during calibration to remain in place
        OrigCompElevFile = os.path.normpath(r'%s/compelevs_initial_conditions.csv' % ecohydro_dir )
        orig_compelev = np.genfromtxt(OrigCompElevFile,delimiter=',',skip_header=1)
        orig_OWelev_dict = dict((orig_compelev[n,0],orig_compelev[n,1]) for n in range(0,len(orig_compelev)))
        orig_Melev_dict = dict((orig_compelev[n,0],orig_compelev[n,2]) for n in range(0,len(orig_compelev)))

        ## read in updated bed and land elevation values for compartments - save in dictionaries where compartment ID is the key
        ## column 1 = compartment ID, column 2 = bed elev, column 3 = land elev, column 4 - marsh edge length
        # The marsh elevation value is filtered in WM.CalculateEcohydroAttributes() such that the average marsh elevation can be no lower than the average bed elevation
        CompElevFile = os.path.normpath(r'%s/compelevs_end_%s.csv' % (EHtemp_path,year-1))  # this must match filename set as 'comp_elev_file' variable written to ICM-Morph input_params.csv
        new_compelev = np.genfromtxt(CompElevFile,delimiter=',',skip_header=1)

        new_OWelev_dict = dict((new_compelev[n,0],new_compelev[n,1]) for n in range(0,len(new_compelev)))
        new_Melev_dict = dict((new_compelev[n,0],new_compelev[n,2]) for n in range(0,len(new_compelev)))
        new_Medge_dict = dict((new_compelev[n,0],new_compelev[n,3]) for n in range(0,len(new_compelev)))

        ## create blank dictionaries that will save changes in compartment attributes and initialize flags for counting updated compartments
        bedchange_dict={}
        marshchange_dict={}
        new_bed_dict={}
        new_marsh_dict={}

        orig_marsh_area_dict = {}
        new_marsh_area_dict = {}

        flag_cell_wat = 0
        flag_cell_upl = 0
        flag_bed_ch = 0
        flag_mar_ch = 0
        flag_edge_ch = 0

        ## update Hydro compartment water/upland/marsh area attributes
        print(' Updating land/water ratios and bed/marsh elevation attributes for Hydro compartments - Year %s' % year)
        
        # open list of compartments that should not have land attributes updated (e.g. open water Gulf, 1D channels, and upland non-tidal areas)
        LWupdate = {}
        staticLW_file = os.path.normpath('%s/comp_LW_update.csv' % ecohydro_dir)
        with open(staticLW_file,mode='r') as staticLW:
            nl = 0
            for line in staticLW:
                if nl >= 1:
                    cID =float(line.split(',')[0])
                    LWup = int(line.split(',')[2])
                    LWupdate[cID] = LWup
                nl +=1 
        
        for nn in range(0,len(EHCellsArray)):
            cellID = EHCellsArray[nn,0]
            cellarea = EHCellsArray[nn,1]
            orig_marsh_area_dict[cellID] = EHCellsArray[nn,4]*cellarea   # store original marsh area for link adjustment calculations later
            
            # check that Hydro Compartment should have landscape areas updated 
            if LWupdate[cellID] == 1:
                # update land percentages only if new value for percent water was calculated in Morph (e.g. dicitionary has a key of cellID and value that is not -9999), otherwise keep last year value
                try:
                    if new_pctwater_dict[cellID] != -9999:
                        orig_water = EHCellsArrayOrig[nn,2]
                        orig_upland = EHCellsArrayOrig[nn,3]
                        orig_wetland = EHCellsArrayOrig[nn,4]

                        # set minimum percentage of water allowed in Hydro compartment - if comp started with small water, it won't be allowed to get any smaller
                        # if it started with more than 10% water, it won't be allowed to get any smaller than 10% water
                        # this filter is only applied to Cells.csv for stability purposes - the Morph landscape will still be updated
                        
                        min_water = min(orig_water,0.1)
                        
                        new_water = max(min_water, new_pctwater_dict[cellID])
                        new_upland = orig_upland                                                    # don't allow any changes to upland percentage
                        new_marsh = max(0.0, min(1.0, (1.0 - new_water - new_upland) ) )
                        
                        EHCellsArray[nn,2] = new_water
                        EHCellsArray[nn,3] = new_upland
                        EHCellsArray[nn,4] = new_marsh
                    else:
                        flag_cell_wat =+ 1
                except:
                    flag_cell_wat += 1
            
                new_marsh_area_dict[cellID] = EHCellsArray[nn,4]*cellarea  # store updated marsh area for link adjustment calculations later

                # update marsh edge area, in attributes array
                try:
                    if new_Medge_dict[cellID] != -9999:
                        EHCellsArray[nn,5] = new_Medge_dict[cellID]
                except:
                        flag_edge_ch += 1
            
            # if not being updated (LWupdate <> 1) , keep original values
            else:
                new_marsh_area_dict[cellID] = orig_marsh_area_dict[cellID]


        # update Hydro compartment/link elevation attributes (if turned on as model option)
        if update_hydro_attr == 0:
            print(' Hydro link and compartment attributes are not being updated (update_hydro_attr = 0)')

        else:
            # calculate change in bed elevation if new value was calculated in Morph (e.g. dictionary has a key of cellID and value that is not -9999)
            # set change value to zero if value is NoData or if key does not exist
            try:
                if new_OWelev_dict[cellID] != -9999:
                    bedchange_dict[cellID] = new_OWelev_dict[cellID] - orig_OWelev_dict[cellID] # EHCellsArray[nn,7]
                else:
                    bedchange_dict[cellID] = 0.0
                    flag_bed_ch += 1
            except:
                bedchange_dict[cellID] = 0.0
                flag_bed_ch += 1

            # calculate change in marsh elevation if new value was calculated in Morph (e.g. dictionary has a key of cellID and value that is not -9999)
            # set change value to zero if value is NoData or if key does not exist
            # as noted above, the new marsh elevation value is filtered in WM.CalculateEcohydroAttributes() such that the average marsh elevation can never be below average bed elevation
            try:
                if new_Melev_dict[cellID] != -9999:
                    marshchange_dict[cellID] = new_Melev_dict[cellID] - orig_Melev_dict[cellID] # EHCellsArray[nn,25]
                else:
                    marshchange_dict[cellID] = 0.0
                    flag_mar_ch += 1
            except:
                marshchange_dict[cellID] = 0.0
                flag_mar_ch += 1

            # update elevation of marsh area, in attributes array
            EHCellsArray[nn,25] += marshchange_dict[cellID]
            # update bed elevation of open water area in attributes array
            EHCellsArray[nn,7] += bedchange_dict[cellID]

            # save updated elevations into dictionaries to use for filtering link elevations in next section
            new_bed_dict[cellID] = EHCellsArray[nn,7]
            new_marsh_dict[cellID] = EHCellsArray[nn,25]


            ## update Hydro link attributes
            print(' Updating elevation attributes for Hydro links - Year %s' % year)
            for mm in range(0,len(EHLinksArray)):
                linkID = EHLinksArray[mm,0]
                linktype = EHLinksArray[mm,7]
                us_comp = EHLinksArray[mm,1]
                ds_comp = EHLinksArray[mm,2]

                # determine maximum of updated upstream and downstream bed elevations
                limiting_bed_elev = max(new_bed_dict[us_comp],new_bed_dict[ds_comp])
                limiting_marsh_elev = max(new_marsh_dict[us_comp],new_marsh_dict[ds_comp])

                ## update link invert elevations for channels
                if linktype == 1:
                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
                    ## invert elevation is attribute1 for channels (column 8 in links array)
                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
                    EHLinksArray[mm,8] = newelev

                    ## only one channel bank elevation, it is equal to the lower of the US or DS marsh elevations
                    ## channel bank elevation is attribute2 for channels (column 9 in links array)
                    EHLinksArray[mm,9] = limiting_marsh_elev

                ## update bed elevations for weirs
                elif linktype == 2:
                    ## upstream elevations are not allowed to be below the US bed elevation
                    ## upstream elevation is attribute2 for weirs and ridges/levees (column 9 in links array)
                    newelevus = max((EHLinksArray[mm,9] + bedchange_dict[us_comp]),new_bed_dict[us_comp])
                    EHLinksArray[mm,9] = newelevus

                    ## downstream elevations are not allowed to be below the DS bed elevation
                    ## downstream elevation is attribute3 for weirs (column 10 in links array)
                    newelevds = max((EHLinksArray[mm,10] + bedchange_dict[ds_comp]),new_bed_dict[ds_comp])
                    EHLinksArray[mm,10] = newelevds

                ## update link invert elevations for locks
                elif linktype == 3:
                    ## updated from change in OW bed elevation in upstream compartment
                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
                    EHLinksArray[mm,8] = newelev

                ## update elevations for tide gates
                elif linktype == 4:
                    ## invert elevation is attribute1 for tide gates (column 8 in links array)
                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
                    EHLinksArray[mm,8] = newelev

                    ## invert elevation is attribute3 for tide gates (column 10 in links array)
                    ## upstream elevation is not allowed to be below either the US bed elevation
                    newelevus = max((EHLinksArray[mm,10] + bedchange_dict[us_comp]),new_bed_dict[us_comp])
                    EHLinksArray[mm,10] = newelevus

                    ## invert elevation is attribute5 for tide gates (column 12 in links array)
                    ## downstream elevation is not allowed to be below either the DS bed elevation
                    newelevds = max((EHLinksArray[mm,12] + bedchange_dict[us_comp]),new_bed_dict[ds_comp])
                    EHLinksArray[mm,12] = newelevds

                ## update elevations for orifices
                elif linktype == 5:
                    ## invert elevation is attribute1 for orifices (column 8 in links array)
                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
                    EHLinksArray[mm,8] = newelev

                    ## invert elevation is attribute3 for orifices (column 10 in links array)
                    ## upstream elevation is not allowed to be below either the US bed elevation
                    newelevus = max((EHLinksArray[mm,10] + bedchange_dict[us_comp]),new_bed_dict[us_comp])
                    EHLinksArray[mm,10] = newelevus

                    ## invert elevation is attribute5 for orifices (column 12 in links array)
                    ## downstream elevation is not allowed to be below either the DS bed elevation
                    newelevds = max((EHLinksArray[mm,12] + bedchange_dict[us_comp]),new_bed_dict[ds_comp])
                    EHLinksArray[mm,12] = newelevds

                ## update elevations for culverts
                elif linktype == 6:
                    ## invert elevation is attribute1 for culverts (column 8 in links array)
                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
                    EHLinksArray[mm,8] = newelev

                ## don't need to update anything for pumps
                ##  elif linktype == 7:

                ## update marsh elevation for marsh links
                elif linktype == 8:
                    ## only one invert elevation, it is not allowed to be below either the US or DS marsh elevation
                    ## unlike the bank elevation calculation for link type 1 this calculates the change from the original invert elevation (as opposed to just using the new marsh elevation) in case the original elevation defining marsh overland flow is above the average marsh elevation
                    newelev = max((EHLinksArray[mm,8] + marshchange_dict[us_comp]),(EHLinksArray[mm,8] + marshchange_dict[ds_comp]),limiting_marsh_elev)
                    EHLinksArray[mm,8] = newelev

                ## update bed elevations for ridge/levee link types
                elif linktype ==9:
                    ## upstream elevations are not allowed to be below the US bed elevation
                    ## upstream elevation is attribute2 for ridges/levees (column 9 in links array)
                    ## unlike the bank elevation calculation for link type 1 this calculates the change from the original invert elevation (as opposed to just using the new marsh elevation) because the original elevation defining ridge overland flow is above the average marsh elevation
                    newelevus = max((EHLinksArray[mm,9] + bedchange_dict[us_comp]),new_bed_dict[us_comp])
                    EHLinksArray[mm,9] = newelevus

                    ## downstream elevations are not allowed to be below the DS bed elevation
                    ## downstream elevation is attribute10 for ridges/levees (column 18 in links array)
                    ## unlike the bank elevation calculation for link type 1 this calculates the change from the original invert elevation (as opposed to just using the new marsh elevation) because the original elevation defining ridge overland flow is above the average marsh elevation
                    newelevds = max((EHLinksArray[mm,18] + bedchange_dict[ds_comp]),new_bed_dict[ds_comp])
                    EHLinksArray[mm,18] = newelevds

                ## update link invert elevations for regime channels
                elif linktype == 10:
                    ## updated from change in OW bed elevation in upstream compartment
                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
                    EHLinksArray[mm,8] = newelev


        ## end update of Hydro compartment attributes
        print(' %s Hydro compartments have updated percent land values for model year %s.' % ((len(EHCellsArray)-flag_cell_upl),year) )
        print(' %s Hydro compartments have updated percent water values for model year %s.' % ((len(EHCellsArray)-flag_cell_wat),year) )
        print(' %s Hydro compartments have updated average bed elevations for model year %s.' % ((len(EHCellsArray)-flag_bed_ch),year) )
        print(' %s Hydro compartments have updated average marsh elevations for model year %s.' % ((len(EHCellsArray)-flag_mar_ch),year) )
        print(' %s Hydro compartments have updated marsh edge lengths for model year %s.' % ((len(EHCellsArray)-flag_edge_ch),year) )

        # update links for project implmentation
        # if project links are to be changed during model year update those links by looping through link attributes array
        if year in link_years:
            print('  Some links are set to be activated or deactivated for this model year due to project implementation.')
            for mm in range(0,len(EHLinksArray)):
                linkID = EHLinksArray[mm,0]
                if linkID in links_to_change:
                    yearindex = links_to_change.index(linkID)
                    if year == link_years[yearindex]:
                        print(' Link type for link %s is being activated (or deactivated if already active).' % linkID)
                        oldlinktype = EHLinksArray[mm,7]
                        newlinktype = -1*oldlinktype
                        EHLinksArray[mm,7] = newlinktype

        ## update link width for 'composite' marsh links if marsh creation project was implemented in previous year
        # link length is attribute 3 (column 11 in links array)
        # link width is attribute 4 (column 12 in links array)
        if year in mc_links_years:
            print('  Some composite marsh flow links are being updated due to marsh creation projects implemented during last year.')
            for mm in range(0,len(EHLinksArray)):
                linkID   = int(EHLinksArray[mm,0])
                linktype = int(EHLinksArray[mm,7])
                us_comp  = int(EHLinksArray[mm,1])
                ds_comp  = int(EHLinksArray[mm,2])
                if linktype == 11:
                    if linkID in mc_links:
                        linkindex = mc_links.index(linkID)
                        if year == mc_links_years[linkindex]:
                            print(' Updating composite marsh flow link (link %s) for marsh creation project implemented in previous year.' % linkID)
                            darea_us = new_marsh_area_dict[us_comp] - orig_marsh_area_dict[us_comp]
                            darea_ds = new_marsh_area_dict[ds_comp] - orig_marsh_area_dict[ds_comp]
                            origwidth = EHLinksArray[mm,11]
                            length = EHLinksArray[mm,10]
                            # change in link area is equal to the increase in marsh area between the two compartments
                            newwidth = origwidth - (darea_us + darea_ds)/length

                            # set min/max width thresholds on marsh creation link updates
                            # minimum width is currently hard-set to be no smaller than 30-m wide
                            # maximum width is currently set to the square root of the smaller of the two compartments connected by the link
                            # this assumes that the compartment is completely square and the width is not allowed to be wider than one of the four sides of the assumed-square compartment
                            min_allowable_width = 30
                            max_allowable_width = min( EHCellsArray[us_comp,1], EHCellsArray[ds_comp,1] )**0.5
                            EHLinksArray[mm,11] = min(max_allowable_width,max(newwidth,min_allowable_width)) # do not let marsh link go to zero - allow some flow, minimum width is one pixel wide
        
        ## update compartment bed elevation for projects that have dredging and update open water elevation
        # bed elevation is column 8 in cells array
        if year in comp_years:
            print('  Some Hydro comparments have a bed elevation being updated due to dredging projects implemented during year.')
            for nn in range(0,len(EHCellsArray)):
                cellID = EHCellsArray[nn,0]
                if cellID in comps_to_change_elev:
                    cellindex = comps_to_change_elev.index(cellID)
                    if year == comp_years[cellindex]:
                        new_bed_elev = comp_elevs[cellindex]
                        EHCellsArray[nn,7] = new_bed_elev   # update bed elevation of open water area in attributes array
                            
                            
        ## save updated Cell and Link attributes to text files read into Hydro model
        np.savetxt(EHCellsFile,EHCellsArray,fmt='%.12f',header=cellsheader,delimiter=',',comments='')
        np.savetxt(EHLinksFile,EHLinksArray,fmt='%.12f',header=linksheader,delimiter=',',comments='')


    ######################################################### 
    ##                  RUN HYDRO MODEL                    ## 
    ######################################################### 


#switch exe code#    if year in hyd_switch_years:
#switch exe code#        for nnn in range(0,len(hyd_file_orig)):
#switch exe code#            oldfile = hyd_file_orig[nnn]
#switch exe code#            newfile = hyd_file_new[nnn]
#switch exe code#            bkfile = hyd_file_bk[nnn]
#switch exe code#            print(' Copying %s to use as the new %s.' % (newfile, oldfile))
#switch exe code#            print(' Saving original %s as %s.' % (oldfile,bkfile))
#switch exe code#            os.rename(oldfile,bkfile)
#switch exe code#            os.rename(newfile,oldfile)

    print('\n--------------------------------------------------')
    print('  RUNNING HYDRO MODEL - Year %s' % year)
    print('--------------------------------------------------\n' )
    print(' See %s for Hydro runtime logs.' % hydro_logfile)

    # run compiled Fortran executable - will automatically return to Python window when done running
    hydrorun = subprocess.call(hydro_exe_path)

    if hydrorun != 0:
        print('******ERROR******')
        error_msg = '\n Hydro model run for year %s was unsuccessful.' % year
        sys.exit(error_msg)

    # Clean up and set Ecohydro up for next year model run
    print(r' Cleaning up after Hydro Model - Year %s' % year)

    ## update startrun value for next model year
    startrun = endrun + 1

    ## append year to names and move hotstart,config, cells, links, and grid files to temp folder so new ones can be written for next model year
    print(' Cleaning up Hydro input and output files.')

    # append year and move hotstart file
    move_hs = os.path.normpath(r"%s/hotstart_in_%s.dat" % (EHtemp_path,year))
    os.rename('hotstart_in.dat',move_hs)

    # append year and move Hydro config file 
    move_EHconfig = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EHConfigFile,'.')[0],year,str.split(EHConfigFile,'.')[1]))
    os.rename(EHConfigFile,move_EHconfig)

    # append year and move compartment attributes file
    move_EHcell = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EHCellsFile,'.')[0],year,str.split(EHCellsFile,'.')[1]))
    os.rename(EHCellsFile,move_EHcell)
    
    # append year and move link attributes file
    move_EHlink = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EHLinksFile,'.')[0],year,str.split(EHLinksFile,'.')[1]))
    os.rename(EHLinksFile,move_EHlink)

    # append year and move grid cell elevation files
    move_EH_gridfile = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EH_grid_file,'.')[0],year,str.split(EH_grid_file,'.')[1]))
    os.rename(EH_grid_filepath,move_EH_gridfile)
    old_grid_filepath = move_EH_gridfile
    
    # read in compartment output from hydro model to generate input file for BIMODE
    EH_comp_results_file = os.path.normpath('%s/%s') % (ecohydro_dir,compartment_output_file)
    EH_comp_out = np.genfromtxt(EH_comp_results_file,dtype='float',delimiter=',',names=True)

    #generate single string from names that will be used as header when writing output file
    compnames = EH_comp_out.dtype.names
    compheader = compnames[0]

    for n in range(1,len(compnames)):
        compheader +=',%s' % compnames[n]

    # re-write compartment output file with year appended to name - file is re-written (as opposed to moved) to ensure floating point format will be correct for Fortran formatting
    EH_comp_out_newfile = '%s_%s.%s' % (str.split(compartment_output_file,'.')[0],year,str.split(compartment_output_file,'.')[1])
    EH_comp_results_filepath = os.path.normpath('%s/%s' % (EHtemp_path,EH_comp_out_newfile))
    np.savetxt(EH_comp_results_filepath,EH_comp_out,delimiter=',',fmt='%.4f',header=compheader,comments='')

    # read in grid output from hydro model
    EH_grid_results_file = os.path.normpath('%s/%s') % (ecohydro_dir,grid_output_file)
    EH_grid_out = np.genfromtxt(EH_grid_results_file,dtype='float',delimiter=',',names=True)

    #generate single string from names that will be used as header when writing output file
    gridnames = EH_grid_out.dtype.names
    gridheader = gridnames[0]
    for n in range(1,len(gridnames)):
        gridheader +=',%s' % gridnames[n]

    # re-write grid output file with year appended to name - file is re-written (as opposed to moved) to ensure floating point format will be correct for import into WM.ImportEcohydroResults - corrects issues with Fortran formatting
    EH_grid_out_newfile = '%s_%s.%s' % (str.split(grid_output_file,'.')[0],year,str.split(grid_output_file,'.')[1])
    EH_grid_results_filepath = os.path.normpath('%s/%s' % (EHtemp_path,EH_grid_out_newfile))
    np.savetxt(EH_grid_results_filepath,EH_grid_out,delimiter=',',fmt='%.4f',header=gridheader,comments='')
    del(EH_grid_out)


    ## Copy monthly gridded output used by EwE model to temporary output folder in Hydro directory
    SalMonth = 'sal_monthly_ave_500m'
    SalMonthFile = os.path.normpath(r"%s/%s.out" % (ecohydro_dir,SalMonth))
    move_salmonth = os.path.normpath(r"%s/%s_%02d.out" % (EHtemp_path,SalMonth,elapsedyear))
    shutil.copy(SalMonthFile,move_salmonth)

    TmpMonth = 'tmp_monthly_ave_500m'
    TmpMonthFile = os.path.normpath(r"%s/%s.out" % (ecohydro_dir,TmpMonth))
    move_tmpmonth = os.path.normpath(r"%s/%s_%02d.out" % (EHtemp_path,TmpMonth,elapsedyear))
    shutil.copy(TmpMonthFile,move_tmpmonth)

    TKNMonth = 'tkn_monthly_ave_500m'
    TKNMonthFile = os.path.normpath(r"%s/%s.out" % (ecohydro_dir,TKNMonth))
    move_tknmonth = os.path.normpath(r"%s/%s_%02d.out" % (EHtemp_path,TKNMonth,elapsedyear))
    shutil.copy(TKNMonthFile,move_tknmonth)

    TSSMonth = 'TSS_monthly_ave_500m'
    TSSMonthFile = os.path.normpath(r"%s/%s.out" % (ecohydro_dir,TSSMonth))
    move_tssmonth = os.path.normpath(r"%s/%s_%02d.out" % (EHtemp_path,TSSMonth,elapsedyear))
    shutil.copy(TSSMonthFile,move_tssmonth)


    ## Cleaning up 1D River Model
    for i in range (0,n_1D):
        RmOutFile = os.path.normpath(r'%s/output/area.txt' % HydroConfigFile[i])
        RmOutFileBK = os.path.normpath(r'%s/output/area_%s.txt' % (HydroConfigFile[i],year))
        os.rename(RmOutFile,RmOutFileBK)
        RmOutFile = os.path.normpath(r'%s/output/hy.txt' % HydroConfigFile[i])
        RmOutFileBK = os.path.normpath(r'%s/output/hy_%s.txt' % (HydroConfigFile[i],year))
        os.rename(RmOutFile,RmOutFileBK)
        RmOutFile = os.path.normpath(r'%s/output/output_wl.txt' % HydroConfigFile[i])
        RmOutFileBK = os.path.normpath(r'%s/output/output_wl_%s.txt' % (HydroConfigFile[i],year))
        os.rename(RmOutFile,RmOutFileBK)
        RmOutFile = os.path.normpath(r'%s/output/q.txt' % HydroConfigFile[i])
        RmOutFileBK = os.path.normpath(r'%s/output/q_%s.txt' % (HydroConfigFile[i],year))
        os.rename(RmOutFile,RmOutFileBK)
        if Sub_Sal[i]=="1":
            RmOutFile = os.path.normpath(r'%s/output/SalCon_output.dat' % SalConfigFile[i])
            RmOutFileBK = os.path.normpath(r'%s/output/SalCon_output_%s.dat' % (SalConfigFile[i],year))
            os.rename(RmOutFile,RmOutFileBK)
        if Sub_Temp[i]=="1":
            RmOutFile = os.path.normpath(r'%s/output/Tmp_output.dat' % TempConfigFile[i])
            RmOutFileBK = os.path.normpath(r'%s/output/Tmp_output_%s.dat' % (TempConfigFile[i],year))
            os.rename(RmOutFile,RmOutFileBK)
        if Sub_Fine[i]=="1":
            RmOutFile = os.path.normpath(r'%s/output/SedConFine_output.dat' % FineConfigFile[i])
            RmOutFileBK = os.path.normpath(r'%s/output/SedConFine_output_%s.dat' % (FineConfigFile[i],year))
            os.rename(RmOutFile,RmOutFileBK)
        if Sub_Sand[i]=="1":
            RmOutFile = os.path.normpath(r'%s/output/SedConSand_output.dat' % SandConfigFile[i])
            RmOutFileBK = os.path.normpath(r'%s/output/SedConSand_output_%s.dat' % (SandConfigFile[i],year))
            os.rename(RmOutFile,RmOutFileBK)



    # set file names for files passed from Hydro into Veg and Morph
    stg_ts_file = r'%s/STG.out'              % ecohydro_dir
    sal_ts_file = r'%s/SAL.out'              % ecohydro_dir
    tss_ts_file = r'%s/TSS.out'              % ecohydro_dir
    sed_ow_file = r'%s/SedAcc.out'           % ecohydro_dir
    sed_mi_file = r'%s/SedAcc_MarshInt.out'  % ecohydro_dir
    sed_me_file = r'%s/SedAcc_MarshEdge.out' % ecohydro_dir
    monthly_file_avstg = os.path.normpath(r'%s/compartment_monthly_mean_stage_%4d.csv'       % (EHtemp_path,year) )
    monthly_file_mxstg = os.path.normpath(r'%s/compartment_monthly_max_stage_%4d.csv'        % (EHtemp_path,year) )
    monthly_file_avsal = os.path.normpath(r'%s/compartment_monthly_mean_salinity_%4d.csv'    % (EHtemp_path,year) )
    monthly_file_avtss = os.path.normpath(r'%s/compartment_monthly_mean_tss_%4d.csv'         % (EHtemp_path,year) )
    monthly_file_sdowt = os.path.normpath(r'%s/compartment_monthly_sed_dep_wat_%4d.csv'      % (EHtemp_path,year) )
    monthly_file_sdint = os.path.normpath(r'%s/compartment_monthly_sed_dep_interior_%4d.csv' % (EHtemp_path,year) )
    monthly_file_sdedg = os.path.normpath(r'%s/compartment_monthly_sed_dep_edge_%4d.csv'     % (EHtemp_path,year) )
    bidem_xyz_file     = os.path.normpath(r'%s/%s_W_dem30_bi.xyz'                           % (bimode_dir,file_prefix) )
    new_grid_filepath  = os.path.normpath(r'%s/grid_data_500m_end%d.csv'                    % (EHtemp_path,year)
    comp_elev_file     =  os.path.normpath(r'%s/compelevs_end_%d.csv'                       % (EHtemp_path,year)
    comp_wat_file      =  os.path.normpath(r'%s/PctWater_%d.csv'                            % (EHtemp_path,year)
    comp_upl_file      =  os.path.normpath(r'%s/PctUpland_%d.csv'                           % (EHtemp_path,year)
    grid_pct_edge_file  = 'hsi/%s_W_pedge.csv' % (file_prefix)
    grid_Gdw_dep_file   = 'hsi/GadwallDepths_cm_%d.csv' % (year)
    grid_GwT_dep_file   = 'hsi/GWTealDepths_cm__%d.csv' % (year)
    grid_MtD_dep_file   = 'hsi/MotDuckDepths_cm_%d.csv' % (year)
   
    dem_grid_data_outfile = 'geomorph/output/%s_W_dem_grid_data.csv' % file_prefix
    
    comp_out_file = EH_comp_results_filepath

    ########################################################
    ##  Format ICM-Hydro output data for use in ICM-Morph ##
    ########################################################

    # read in monthly water level data
    print(' - calculating mean and max monthly water levels')
    stg_mon = {}
    stg_mon_mx = {}
    for mon in range(1,13):
        print('     - month: %02d' % mon)
        data_start = dt.date(startyear,1,1)             # start date of all data included in the daily timeseries file (YYYY,M,D)
        ave_start = dt.date(year,mon,1)                 # start date of averaging window, inclusive (YYYY,M,D)
        ave_end = dt.date(year,mon,dom[mon])            # end date of averaging window, inclusive (YYYY,M,D)
        stg_mon[mon] = daily2ave(data_start,ave_start,ave_end,stg_ts_file)
        stg_mon_mx[mon] = daily2max(data_start,ave_start,ave_end,stg_ts_file)

    # write monthly mean water level file for use in ICM-Morph
    with open(monthly_file_avstg,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,stage_m_%02d' % (wrt_hdr,mon)
        mon_file.write('%s\n' % wrt_hdr)
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                wrt_string = '%s,%s' % (wrt_string,stg_mon[mon][comp])
            mon_file.write('%s\n'% wrt_string)

    # write monthly max water level file for use in ICM-Morph
    with open(monthly_file_mxstg,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,stage_mx_m_%02d' % (wrt_hdr,mon)
        mon_file.write('%s\n' % wrt_hdr)
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                wrt_string = '%s,%s' % (wrt_string,stg_mon_mx[mon][comp])
            mon_file.write('%s\n'% wrt_string)

    # read in monthly salinity data
    print(' - calculating mean monthly salinity')
    sal_mon = {}
    for mon in range(1,13):
        print('     - month: %02d' % mon)
        data_start = dt.date(startyear,1,1)             # start date of all data included in the daily timeseries file (YYYY,M,D)
        ave_start = dt.date(year,mon,1)                 # start date of averaging window, inclusive (YYYY,M,D)
        ave_end = dt.date(year,mon,dom[mon])            # end date of averaging window, inclusive (YYYY,M,D)
        sal_mon[mon] = daily2ave(data_start,ave_start,ave_end,sal_ts_file)

    # write monthly mean salinity file for use in ICM-Morph
    with open(monthly_file_avsal,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,sal_ave_ppt_%02d' % (wrt_hdr,mon)
        mon_file.write('%s\n' % wrt_hdr)
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                wrt_string = '%s,%s' % (wrt_string,sal_mon[mon][comp])
            mon_file.write('%s\n'% wrt_string)

   # read in monthly TSS data
    print(' - calculating mean monthly TSS')
    tss_mon = {}
    for mon in range(1,13):
        print('     - month: %02d' % mon)
        data_start = dt.date(startyear,1,1)             # start date of all data included in the daily timeseries file (YYYY,M,D)
        ave_start = dt.date(year,mon,1)                 # start date of averaging window, inclusive (YYYY,M,D)
        ave_end = dt.date(year,mon,dom[mon])            # end date of averaging window, inclusive (YYYY,M,D)
        tss_mon[mon] = daily2ave(data_start,ave_start,ave_end,tss_ts_file)

    # write monthly mean TSS file for use in ICM-Morph
    with open(monthly_file_avtss,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,tss_ave_mgL_%02d' % (wrt_hdr,mon)
        mon_file.write('%s\n' % wrt_hdr)
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                wrt_string = '%s,%s' % (wrt_string,tss_mon[mon][comp])
            mon_file.write('%s\n'% wrt_string)

    # read in cumulative sediment deposition data
    print(' - formatting sedimentation output for ICM-Morph')
    sed_ow = {}
    sed_mi = {}
    sed_me = {}
    for mon in range(1,13):
        print('     - month: %02d' % mon)
        data_start = dt.date(startyear,1,1)              # start date of all data included in the daily timeseries file (YYYY,M,D)
        day2get = dt.date(year,mon,dom[mon])            # end date of averaging window, inclusive (YYYY,M,D)
        sed_ow[mon] = daily2day(data_start,day2get,sed_ow_file)
        sed_mi[mon] = daily2day(data_start,day2get,sed_mi_file)
        sed_me[mon] = daily2day(data_start,day2get,sed_me_file)


    # write monthly sediment deposition in open water file for use in ICM-Morph
    with open(monthly_file_sdowt,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,sed_dp_ow_%02d' % (wrt_hdr,mon)
        mon_file.write('%s\n' % wrt_hdr)
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                if mon == 1:
                    val2write = float(sed_ow[mon][comp])
                else:
                    val2write = float(sed_ow[mon][comp]) - float(sed_ow[mon-1][comp])            # convert cumulative sediment deposited during year to amount deposited only during the current month
                wrt_string = '%s,%s' % (wrt_string,val2write)
            mon_file.write('%s\n'% wrt_string)

    # write monthly sediment deposition in marsh interior file for use in ICM-Morph
    with open(monthly_file_sdint,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,sed_dp_int_%02d' % (wrt_hdr,mon)
        mon_file.write('%s\n' % wrt_hdr)
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                if mon == 1:
                    val2write = max(0,float(sed_mi[mon][comp]))                                  # marsh deposition can only be positive - no erosion - force to zero in case of small negative values due to sigfig
                else:
                    val2write = max(0,float(sed_mi[mon][comp]) - float(sed_mi[mon-1][comp]))     # convert cumulative sediment deposited during year to amount deposited only during the current month
                wrt_string = '%s,%s' % (wrt_string,val2write)
            mon_file.write('%s\n'% wrt_string)

    # write monthly sediment deposition in marsh edge zone file for use in ICM-Morph
    with open(monthly_file_sdedg,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,sed_dp_edge_%02d' % (wrt_hdr,mon)
        mon_file.write('%s\n' % wrt_hdr)
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                if mon == 1:
                    val2write = max(0,float(sed_me[mon][comp]))                                  # marsh deposition can only be positive - no erosion - force to zero in case of small negative values due to sigfig
                else:
                    val2write = max(0,float(sed_me[mon][comp]) - float(sed_me[mon-1][comp]))     # convert cumulative sediment deposited during year to amount deposited only during the current month

                wrt_string = '%s,%s' % (wrt_string,val2write)
            mon_file.write('%s\n'% wrt_string)


    ###########################################################
    ##  Format ICM-Hydro output data for use in ICM-LAVegMod ##
    ###########################################################

    asc_head = '# Year = %04d\n%s' % (year,asc_grid_head)
    if year == startyear:
        filemode = 'w'
    else:
        filemode = 'a'

    print('   - updating percent water grid file for ICM-LAVegMod')
    pwatr_dict = {}
    with open(old_grid_filepath,mode='r') as grid_data:
        nline = 0
        for line in grid_data:
            if nline > 0:
                gr = int(float(line.split(',')[0]))
                pwatr = line.split(',')[5]          # in grid_data 6th column is percent water; 5th column is percent_wetland and is defined in morph as vegetated land + flotant marsh + unvegetated bare ground ** it does not include NotMod/Developed or water**
                pwatr_dict[gr] = pwatr
            nline += 1
    print(dict2asc_flt(pwatr_dict,pwatr_grid_file,asc_grid_ids,asc_head,write_mode=filemode) )

    print('   - updating acute salinity stress grid file for ICM-LAVegMod')
    salmx_comp = compout2dict(comp_out_file,7)
    salmx_grid = comp2grid(salmx_comp,grid_comp_dict)
    
    acute_sal_grid = {}
    for gid in salmx_grid.keys():
        val = salmx_grid[gid]
        if val < 0:
            val2write = -9999
        elif val < acute_sal_threshold:
            val2write = 0
        else:
            val2write = 1
        acute_sal_grid[gid] = val2write        
    print(dict2asc_int(acute_sal_grid,acute_sal_grid_file,asc_grid_ids,asc_head,write_mode=filemode) )





    ###########################################################
    ###       Barrier Island Tidal Inlet (BITI) Model       ###
    ###########################################################
    print('\n-------------------------------------------------------------')
    print('  RUNNING BARRIER ISLAND TIDAL INLET MODEL (ICM-BITI) - Year %s' % year)
    print('-------------------------------------------------------------\n' )

    os.chdir(bimode_dir)

    # read in mean water levels for each barrier island model domain
    EH_MHW = dict((EH_comp_out[n][0],EH_comp_out[n][2]) for n in range(0,len(EH_comp_out)))     # create dictionary where key is compartment ID, values is mean water (column 3 of Ecohydro output)
    
    # create liste of ICM compartments that will be used as MHW for each BI group (west-to-east)
    IslandMHWCompLists = [494,482,316,314,306,303]
    
    # read mean water level for each BI region
    BIMODEmhw = np.zeros(shape=len(IslandMHWCompLists))    # Initialize MHW array to zero - will write over previous year's array
    for n in range(0,len(IslandMHWCompLists)):
        comp = IslandMHWCompLists[n]
        BIMODEmhw[n] = EH_MHW[comp]

    # calculate one average water level for all BI regions to be used for BITI depth calculations
    BITI_MWL = BIMODEmhw.mean()

    # create dictionary where key is compartment ID, value is tidal prism (Column 14 of Ecohydro output)
    EH_prisms = dict((EH_comp_out[n][0],EH_comp_out[n][13]) for n in range(0,len(EH_comp_out)))
    
    # no longer need NumPy array of compartment output summary data - delete until next year
    del(EH_comp_out)
    
    
    #Barrier Island Tidal Inlet (BITI) tidal prism values
    #Get the tidal prism values for each compartment from the Hydro output
    BITI_Terrebonne_prism = [EH_prisms.get(comp) for comp in BITI_Terrebonne_comp]
    BITI_Barataria_prism = [EH_prisms.get(comp) for comp in BITI_Barataria_comp]
    BITI_Pontchartrain_prism = [EH_prisms.get(comp) for comp in BITI_Pontchartrain_comp]


    # Calculate the effective tidal prism and cross-sectional area for each link in each basin
    # effective tidal prism = sum(tidal prism * partitioning coefficient) [summed across all compartments in the basin]
    # cross-sectional area = kappa *((effective tidal prism)^alpha)
    BITI_Terrebonne_inlet_area = np.zeros(shape=len(BITI_Terrebonne_link))
    for n in range(0,len(BITI_Terrebonne_link)):
        BITI_Terrebonne_effective_prism = sum((BITI_Terrebonne_partition[:,n])*BITI_Terrebonne_prism)
        BITI_Terrebonne_inlet_area[n] = np.multiply(kappa, np.power(BITI_Terrebonne_effective_prism,alpha))*BITI_Terrebonne_BWF

    BITI_Barataria_inlet_area = np.zeros(shape=len(BITI_Barataria_link))
    for n in range(0,len(BITI_Barataria_link)):
        BITI_Barataria_effective_prism = sum((BITI_Barataria_partition[:,n])*BITI_Barataria_prism)
        BITI_Barataria_inlet_area[n] = np.multiply(kappa, np.power(BITI_Barataria_effective_prism,alpha))*BITI_Barataria_BWF

    BITI_Pontchartrain_inlet_area = np.zeros(shape=len(BITI_Pontchartrain_link))
    for n in range(0,len(BITI_Pontchartrain_link)):
        BITI_Pontchartrain_effective_prism = sum((BITI_Pontchartrain_partition[:,n])*BITI_Pontchartrain_prism)
        BITI_Pontchartrain_inlet_area[n] = np.multiply(kappa, np.power(BITI_Pontchartrain_effective_prism,alpha))*BITI_Pontchartrain_BWF

    BITI_inlet_areas = [BITI_Terrebonne_inlet_area,BITI_Barataria_inlet_area,BITI_Pontchartrain_inlet_area]

    # BITI depth for each link in each basin
    # Depth = sqrt(inlet area*(depth to width ratio))
    BITI_Terrebonne_inlet_depth = np.power(np.multiply(BITI_Terrebonne_inlet_area,BITI_Terrebonne_dwr),0.5)
    BITI_Barataria_inlet_depth = np.power(np.multiply(BITI_Barataria_inlet_area,BITI_Barataria_dwr),0.5)
    BITI_Pontchartrain_inlet_depth = np.power(np.multiply(BITI_Pontchartrain_inlet_area,BITI_Pontchartrain_dwr),0.5)

    BITI_inlet_depth = [BITI_Terrebonne_inlet_depth,BITI_Barataria_inlet_depth,BITI_Pontchartrain_inlet_depth]

    # BITI width for each link in each basin
    # Width = sqrt(inlet area/(depth to width ratio))
    BITI_Terrebonne_inlet_width = np.power(np.divide(BITI_Terrebonne_inlet_area,BITI_Terrebonne_dwr),0.5)
    BITI_Barataria_inlet_width = np.power(np.divide(BITI_Barataria_inlet_area,BITI_Barataria_dwr),0.5)
    BITI_Pontchartrain_inlet_width = np.power(np.divide(BITI_Pontchartrain_inlet_area,BITI_Pontchartrain_dwr),0.5)

    BITI_inlet_width = [BITI_Terrebonne_inlet_width,BITI_Barataria_inlet_width,BITI_Pontchartrain_inlet_width]

    # BITI dimensions
    # Create a dictionary where key is link ID, first value is inlet depth, second value is inlet width
    # This dictionary can be used to update the link attributes. All inlet links are Type 1 links.
    BITI_inlet_dimensions = {}
    for n in range(0,len(BITI_Links)):
        for k in range(0,len(BITI_Links[n])):
            BITI_inlet_dimensions[BITI_Links[n][k]] = ([BITI_inlet_depth[n][k],BITI_inlet_width[n][k]])
    
    # BITI dimensions for inlet links with jetties constraining inlet width
    # do not allow inlets that are currently jettied to change in width dimension - all areal adjustments for these two links must occur in the depth dimension
    CamPassLinkID = 529
    CamPassWidth = 900          # intial Caminada Pass width
    BarPassLinkID = 532
    BarPassWidth = 700          # intial Barataria Pass width    
    
    BITI_inlet_dimensions[CamPassLinkID][0] = (BITI_inlet_dimensions[CamPassLinkID][0] *  BITI_inlet_dimensions[CamPassLinkID][1])/CamPassWidth
    BITI_inlet_dimensions[CamPassLinkID][1] = CamPassWidth 

    BITI_inlet_dimensions[BarPassLinkID][0] = (BITI_inlet_dimensions[BarPassLinkID][0] *  BITI_inlet_dimensions[BarPassLinkID][1])/BarPassWidth
    BITI_inlet_dimensions[BarPassLinkID][1] = BarPassWidth 

        # set upper and lower limits on how much the tidal inlet dimensions can change as a ratio of the initial dimensions
    # currently, the limits are (arbitrarily) set to limit expansion to twice the original width and/or depth and limit the contraction to 1/4th the original width and/or depth
    for BITI_Link_ID in BITI_inlet_dimensions.keys():

            orig_depth = BITI_inlet_dimensions_init[BITI_Link_ID][0]
            BITI_inlet_depth_min = 0.25*orig_depth
            BITI_inlet_depth_max = 1.5*orig_depth           # based on analysis by BITI team, when basin is completely open water, maximum increase in inlet dimensions was 145% increase from initial dimensions
            new_depth = min( max( BITI_inlet_dimensions[BITI_Link_ID][0], BITI_inlet_depth_min ), BITI_inlet_depth_max)

            orig_width = BITI_inlet_dimensions_init[BITI_Link_ID][1]  
            BITI_inlet_width_min = 0.25*orig_width
            BITI_inlet_width_max = 1.5*orig_width           # based on analysis by BITI team, when basin is completely open water, maximum increase in inlet dimensions was 145% increase from initial dimensions
            new_width = min( max( BITI_inlet_dimensions[BITI_Link_ID][1], BITI_inlet_width_min ), BITI_inlet_width_max)


            EHLinks_index = int(BITI_Link_ID) - 1                                # EHLinks is a numpy 0-based index, not dictionary with lookup
            EHLinksArray[EHLinks_index,8] = BITI_MWL - new_depth                ## invert elevation is attribute1 for Type 1 links (column 8 in links array)
            EHLinksArray[EHLinks_index,11] = new_width                          ## channel width is attribute4 for Type 1 links (column 11 in links array)


           


    #########################################################
    ##              RUN BARRIER ISLAND MODEL               ##
    #########################################################

    print('\n--------------------------------------------------' )
    print('  RUNNING BARRIER ISLAND MODEL (ICM-BIDEM) - Year %s' % year)
    print('--------------------------------------------------\n')
    print(' See separate log files generated by each BI region.')

    # loop BI runs over the different folders - each with individual executables and I/O
    fol_n = 0
    for fol in bimode_folders:
        print('\n Modeling %s' % fol)
        bmdir = os.path.normpath(r'%s/%s' %(bimode_dir,fol))
        os.chdir(bmdir)

        print(' Writing mean water level file for %s region.' % fol)
        mhw_file_for_bimode = os.path.normpath(r'%s/input/%s' % (bmdir,BIMHWFile))
        with open(mhw_file_for_bimode,'w') as f:
            f.write('% MHW (m NAVD88)\t%SLR_A\t%SLR_B\t%Region ')
            f.write('\n')
            for n in range(0,len(IslandMHWCompLists)):
                bmhw = str(BIMODEmhw[n])+'\t0.000\t0.000\t'+str(n+1)
                f.write(bmhw)
                f.write('\n')


        # run compiled Fortran executable - will automatically return to Python window when done running
        print(' Running BIDEM executable for %s region.' % fol)
        bimoderun = subprocess.call(bidem_exe_path)

        if bimoderun != 0:
            error_msg = '\n BIDEM model run for region %s year %s was unsuccessful.' % (fol,year)
            sys.exit(error_msg)
        
        os.remove('input.txt')
        os.rename('input.txt.new','input.txt')
        
        print(' Interpolating BIDEM outputs for %s to ICM-Morph DEM' % fol)
        bidem_out = './results/profile_%04d' % elapsedyear
        fixed_grid_in = bidem_fixed_grids[fol_n]
        fixed_grid_out = './results/profile_%04d_interp.xyz' % elapsedyear
        bidem_interp2xyz(bidem_out,fixed_grid_in,fixed_grid_out)

        print(' Appending interpolated %s regional BIDEM output to coastwide file for use in ICM-Morph' % fol)
        with open(bidem_xyz_file,mode='a') as allout:
            with open(fixed_grid_out,mode='r') as regout:
                for line in regout:
                    allout.write(line)
        fol_n += 1

        os.remove(fixed_grid_out) # delete temp file that has region xyz snapped to DEM grid



    #########################################################
    ##         RUN VEGETATION MODEL FOR CURRENT YEAR       ##
    #########################################################

    # read in LAVegMod input file and update variables for year of simulation
    lvm_param_file = '%s/%s' % (vegetation_dir,VegConfigFile)
    
    ## REPLACE THESE TWO VARIABLES WITH UPDATED COMP/GRID FILE PATHS IN FUTURE (comp_out_file, eh_outfiles, grid_500m_out,etc.) 
    comp_out_file_yr = 'hydro/TempFiles/compartment_out_%04d.csv' % year
    grid_data_file_prv_yr = 'hydro/TempFiles/grid_data_500m_%04d.csv' % (year - 1)
    
    with open (lvm_param_file, mode='w') as lvm_ip_csv:
        lvm_ip_csv.write("%04d, start_year - first year of model run\n" % startyear)
        lvm_ip_csv.write("%d, elapsed_year - elapsed year of model run\n" % elapsed_year)
        lvm_ip_csv.write("47, ncov - the number of coverage types included in the model\n")
        lvm_ip_csv.write("%d, ngrid - number of ICM-LAVegMod grid cells - will be an array dimension for all grid-level data\n" % n500grid)
        lvm_ip_csv.write("%d, ncomp - number of ICM-Hydro compartmenets - will be an array dimension for all compartment-level data\n" % ncomp)
        lvm_ip_csv.write("%d, dem_res - XY resolution of DEM (meters)\n" % dem_res)
        lvm_ip_csv.write("'veg/%s_V_grid_XYAreaComp.csv', grid_file - csv with X and Y coordinates (UTM meters) of grid cell centroids grid cell area (sq meters) and overlaying ICM-Hydro Compartment number\n" % fwoa_init_cond_tag)
        lvm_ip_csv.write("0, build_neighbors - flag - set to 1 if near and nearest neighbor lists need to be built from Grid XY data - set to 0 if neighbor files already exist\n")
        lvm_ip_csv.write("'veg/%s_V_neighbor_grids_480m.csv',nearest_neighbors_file - text file with list of grid cells that are the defined nearest neighbors\n" % fwoa_init_cond_tag)
        lvm_ip_csv.write("679, nearest_neighbors_dist - distance in which a neighboring grid cell is considered a nearest neighbor (meters) *must be smaller magnitude than near_neighbor_dist*\n")
        lvm_ip_csv.write("'veg/%s_V_neighbor_grids_960m.csv',near_neighbors_file -  text file with list of grid cells that are the defined near neighbors\n" % fwoa_init_cond_tag)
        lvm_ip_csv.write("1358, near_neighbors_dist - distance in which a neighboring grid cell is considered a near neighbor (meters) *must be larger magnitude than nearest_neighbor_dist*\n")
        lvm_ip_csv.write("16, max_neighbors - maximum number of grid cells that will be allowed in the near and nearest neighbor lists - this will be the number of columns in the neighbor files\n")
        lvm_ip_csv.write("'veg/LAVegMod_coverage_attributes.csv',coverage_attribute_file - file name - with relative path - to csv with model attributes for each coverage type - this file row-order must match the column-order of veg_in_file below\n")
        lvm_ip_csv.write("24, n_X_bins - number of bins definiing the X-axis of the establishment and mortability input tables\n")
        lvm_ip_csv.write("39, n_Y_bins - number of bins definiing the Y-axis of the establishment and mortability input tables\n")
        if year == startyear:
            lvm_ip_csv.write("'veg/%s_V_vegty.csv', veg_in_file - file name with relative path to *vegty csv file saved by ICM-LAVegMod in previous year run\n" % fwoa_init_cond_tag)
        else:
            lvm_ip_csv.write("'veg/%s_O_%04d_V_vegty.csv', veg_in_file - file name with relative path to *vegty csv file saved by ICM-LAVegMod in previous year run\n" % (runprefix,year-1) )
        lvm_ip_csv.write("'%s', hydro_comp_out_file - file name - with relative path - to compartment_out.csv from current model year's ICM-Hydro simulation\n" % comp_out_file_yr)
        lvm_ip_csv.write("'%s', morph_grid_out_file - file name - with relative path - to grid_data.csv file from previous model year's ICM-Morph simulation\n" % grid_data_file_prv_yr)
        lvm_ip_csv.write("%s, runprefix - file naming convention prefix\n" % runprefix)
        lvm_ip_csv.write("1, write_intermediate_files - set to 1 if intermediate output files should be written - set to 0 to only write end-of-year files\n")

    veg_run = subprocess.call(veg_exe_path)

    #########################################################
    ##         SETUP MORPH MODEL FOR CURRENT YEAR          ##
    #########################################################
    os.chdir(par_dir)

    #########################################################################
    ##    IMPLEMENT MARSH CREATION PROJECTS BY ELEMENT FOR CURRENT YEAR    ##
    #########################################################################
    
    # count number of marsh creation project elements to be built during current year
    n_mc_yr = 0
    mc_eid_yr = []
    mc_project_list_yr = 'na'
    mc_project_list_VolArea_yr = 'na'
    
    mcyi = 0
    for mc_yr in mc_years:
        if year == mc_yr:
            n_mc_yr += 1
            mc_eid_yr.append( mc_elementIDs[mcyi] )
        mcyi += 1

    # unzip each TIF file and convert to XYZ format for each element of marsh creation projects implemented during current year
    if n_mc_yr > 0:
        mc_project_list_yr = 'geomorph/input/%s_MCelements.csv' % file_iprefix
        mc_project_list_VolArea_yr = 'geomorph/output/%s_MC_VolArea.csv' % file_oprefix
        
        with open (mc_project_list_yr,mode='w') as mcpl:
            mcpl.write('ElementID,xyz_file\n')
            
            for eid in mc_eid_yr:
                
                if eid in mc_eid_with_deep_fill:
                    fill_depth =  mc_depth_threshold_deep
                else:
                    fill_depth =  mc_depth_threshold_def
                
                zfile = '%s/%s/MCElementElevation_%s_%s.zip' % (FWA_prj_input_dir_MC,sterm,sterm,eid)
                print ('unzipping %s' % zfile)
                zcmd = ['unzip','-j',zfile]
                zrun = subprocess.check_output(zcmd).decode()
                
                TIFpath = zrun.split('inflating:')[1].strip()
                TIFfile = TIFpath.split('/')[-1]
                
                XYZfile = '%s_00_00_MC_%d.xyz' % (runprefix,eid)
                XYZpath = 'geomorph/input/%s' % XYZfile

                gtcmd = ['gdal_translate',TIFpath,XYZpath]
                gtrun = subprocess.call(gtcmd)
                
                rmcmd = ['rm', TIFpath]
                rmcmd = subprocess.call(rmcmd)
               
                # add element ID and location of XYZ project file to text file passed into Morph
                mcpl.write('%d,%s,%f\n' % (eid,XYZfile,fill_depth) )

    
    ###########################################################
    ##    IMPLEMENT RIDGE/LEVEE PROJECTS FOR CURRENT YEAR    ##
    ###########################################################    
    
    # count number of ridge/levee projects to be built during current year  
    n_rr_yr = 0
    rr_eid_yr = []
    rr_project_list_yr = 'na'
  
    rryi = 0
    for rr_yr in rr_years:
        if year == rr_yr:
            n_rr_yr += 1
            rr_eid_yr.append( rr_projectIDs[rryi] )
        rryi += 1

    # unzip each TIF file and convert to XYZ format for ridge/levee projects implemented during current year
    if n_rr_yr > 0:
        rr_project_list_yr = 'geomorph/input/%s_ridge_levee_projects.csv' % file_iprefix
        
        with open (rr_project_list_yr,mode='w') as rrpl:
            rrpl.write('ProjectID,xyz_file\n')
            
            for eid in rr_eid_yr:
                zfile = '%s/RR_PL_PW_ProjectElevation_%s.zip' % (FWA_prj_input_dir_RR,eid)
                print ('unzipping %s' % zfile)
                zcmd = ['unzip','-j',zfile]
                zrun = subprocess.check_output(zcmd).decode()
                
                TIFpath = zrun.split('inflating:')[1].strip()
                TIFfile = TIFpath.split('/')[-1]
                
                XYZfile = '%s_00_00_RRPL_%d.xyz' % (runprefix,eid)
                XYZpath = 'geomorph/input/%s' % XYZfile

                gtcmd = ['gdal_translate',TIFpath,XYZpath]
                gtrun = subprocess.call(gtcmd)
                
                rmcmd = ['rm', TIFpath]
                rmcmd = subprocess.call(rmcmd)
                
                # add project ID and location of XYZ project file to text file passed into Morph
                rrpl.write('%d,%s\n' % (eid,XYZfile) )
    
    ###################################################################################
    ##    IMPLEMENT SHORELINE PROTECTION PROJECTS FOR CURRENT AND PREVIOUS YEARS     ##
    ################################################################################### 
    
    # count number of shoreline protection projects built during, or prior to, current year
    n_sp_cumul = 0
    sp_eid_cumul = []
    sp_project_list_cumul = 'geomorph/input/%s_shoreline_protection_projects.csv' % file_iprefix
    
    spci = 0
    for sp_yr in sp_years:
        if year >= sp_yr:
            n_sp_cumul += 1
            sp_eid_cumul.append( sp_projectIDs[spci] )
        spci += 1
    
    # add project ID and location of XYZ project files to text file passed into Morph for all shoreline protection projects for current and previous years
    with open (sp_project_list_cumul,mode='w') as sppl:
        sppl.write('ProjectID,xyz_file\n')
        if n_sp_cumul > 0:
            for eid in sp_eid_cumul:
                XYZfile = '%s_00_00_MEEmult_%d.xyz' % (runprefix,eid)
                sppl.write('%d,%s\n' % (eid,XYZfile) )
        else:
            sppl.write('No updates to default marsh edge erosion rates\n')

   
    # count number of shoreline protection projects built during current year only
    n_sp_yr = 0
    spyi = 0
    sp_eid_yr = []
    for sp_yr in sp_years:
        if year == sp_yr:
            n_sp_yr += 1
            sp_eid_yr.append( sp_projectIDs[spyi] )
        spyi += 1

    for eid in sp_eid_yr:
        zfile = '%s/BS_SP_MEEmultiplier_%s.zip' % (FWA_prj_input_dir_BS,eid)
        print ('unzipping %s' % zfile)
        zcmd = ['unzip','-j',zfile]
        zrun = subprocess.check_output(zcmd).decode()
        
        TIFpath = zrun.split('inflating:')[1].strip()
        TIFfile = TIFpath.split('/')[-1]
        
        XYZfile = '%s_00_00_MEEmult_%d.xyz' % (runprefix,eid)
        XYZpath = 'geomorph/input/%s' % XYZfile
        
        gtcmd = ['gdal_translate',TIFpath,XYZpath]
        gtrun = subprocess.call(gtcmd)
        
        rmcmd = ['rm', TIFpath]
        rmcmd = subprocess.call(rmcmd)


    
    ############################################################################
    ##    IMPLEMENT ACTIVE DELTAIC COMPARTMENT FILES FOR DIVERSION PROJECT    ##
    ############################################################################
    # set default active deltaic compartment file
    act_del_file_2use = 'compartment_active_delta.csv'
    # loop through all past and present model years - look to see if any previous (or current) year had an updated active delta file
    # if so, the year closest (but prior) to the current model year's active deltaic file will be used
    for ady in range(startyear,year+1):
        if ady in act_del_years:
            act_del_file_2use = act_del_files[act_del_years.index(ady)]
   
        
        
    #########################################################
    ##          RUN MORPH MODEL FOR CURRENT YEAR           ##
    #########################################################

    # read in Wetland Morph input file and update variables for year of simulation
    wm_param_file = r'%s/input_params.csv' % wetland_morph_dir
    morph_zonal_stats = 0               # 1=zonal stats run in ICM-Morph; 0=zonal stats run in ICM
    
    with open (wm_param_file, mode='w') as ip_csv:
        ip_csv.write("%d, start_year - first year of model run\n" % startyear)
        ip_csv.write("%d, elapsed_year - elapsed year of model run\n" % elapsedyear)
        ip_csv.write("%d, dem_res - XY resolution of DEM (meters)\n" % dem_res)
        ip_csv.write("-9999, dem_NoDataVal - value representing nodata in input rasters and XYZ files\n")
        ip_csv.write("171284090, ndem - number of DEM pixels - will be an array dimension for all DEM-level data\n")
        ip_csv.write("2904131, ndem_bi - number of pixels in interpolated ICM-BI-DEM XYZ that overlap primary DEM\n")
        ip_csv.write("%d, ncomp - number of ICM-Hydro compartments - will be an array dimension for all compartment-level data\n" % ncomp)
        ip_csv.write("173898, ngrid - number of ICM-LAVegMod grid cells - will be an array dimension for all gridd-level data\n")
        ip_csv.write("32, neco - number of ecoregions\n")
        ip_csv.write("5, nlt - number of landtype classifications\n")
        ip_csv.write("0.10, ht_above_mwl_est - elevation (meters) relative to annual mean water level at which point vegetation can establish\n")
        ip_csv.write("0.51012, inun_thr_C0 - Y-intercept for the inundation threshold depth-salinity function Blue Line Curve [ Y = C0 + C1*x + C2*x^2 + C3*x^3 + C4*x^4 + C5*x^5 ]\n")
        ip_csv.write("-0.0758, inun_thr_C1 - X^1 coeffiecent  for the inundation threshold depth-salinity function Blue Line Curve [ Y = C0 + C1*x + C2*x^2 + C3*x^3 + C4*x^4 + C5*x^5 ]\n")
        ip_csv.write("0.0054, inun_thr_C2 - X^2 coeffiecent  for the inundation threshold depth-salinity function Blue Line Curve [ Y = C0 + C1*x + C2*x^2 + C3*x^3 + C4*x^4 + C5*x^5 ]\n")
        ip_csv.write("-0.00011, inun_thr_C3 - X^3 coeffiecent  for the inundation threshold depth-salinity function Blue Line Curve [ Y = C0 + C1*x + C2*x^2 + C3*x^3 + C4*x^4 + C5*x^5 ]\n")
        ip_csv.write("0, inun_thr_C4 - X^4 coeffiecent  for the inundation threshold depth-salinity function Blue Line Curve [ Y = C0 + C1*x + C2*x^2 + C3*x^3 + C4*x^4 + C5*x^5 ]\n")
        ip_csv.write("0, inun_thr_C5 - X^5 coeffiecent  for the inundation threshold depth-salinity function Blue Line Curve [ Y = C0 + C1*x + C2*x^2 + C3*x^3 + C4*x^4 + C5*x^5 ]\n")
        ip_csv.write("0.835, ow_bd - bulk density of water bottoms (g/cm3)\n")
        ip_csv.write("0.076, om_k1 - organic matter self-packing density (g/cm3) from CRMS soil data (see 2023 Wetlands Model Improvement report)\n")
        ip_csv.write("2.173, mn_k2- mineral soil self-packing density (g/cm3) from CRMS soil data - value derived from CRMS soil data in 2024 (MP2023 value was 2.106 g/cm3)\n")
        ip_csv.write("0, OMAR_interp - flag used to identify how to calculate OMAR: (1) interpolate between OMAR values input file or (0) use hard-coded OMAR equations [OMAR = f(FFIBS)]\n")
        ip_csv.write("0, FIBS_intvals(1) - FFIBS score that will serve as lower end for Fresh forested\n")
        ip_csv.write("0.15, FIBS_intvals(2) - FFIBS score that will serve as lower end for Fresh marsh\n")
        ip_csv.write("1.5, FIBS_intvals(3) - FFIBS score that will serve as lower end for Intermediate marsh\n")
        ip_csv.write("5, FIBS_intvals(4) - FFIBS score that will serve as lower end for Brackish marsh\n")
        ip_csv.write("18, FIBS_intvals(5) - FFIBS score that will serve as lower end for Saline marsh\n")
        ip_csv.write("24, FIBS_intvals(6) - FFIBS score that will serve as upper end for Saline marsh\n")
        ip_csv.write("10, min_accretion_limit_cm - upper limit to allowable mineral accretion on the marsh surface during any given year [cm]\n")
        ip_csv.write("50, ow_accretion_limit_cm - upper limit to allowable accretion on the water bottom during any given year [cm]\n")
        ip_csv.write("-50, ow_erosion_limit_cm - upper limit to allowable erosion of the water bottom during any given year [cm]\n")
        ip_csv.write("0.05, bg_lowerZ_m - height that bareground is lowered [m]\n")
        ip_csv.write("0.25, me_lowerDepth_m - depth to which eroded marsh edge is lowered to [m]\n")
        ip_csv.write("1.0, flt_lowerDepth_m - depth to which dead floating marsh is lowered to [m]\n")
        ip_csv.write("%0.3f, mc_depth_threshold - default water depth threshold (meters) defining deep water area to be excluded from marsh creation projects footprint - this is replaced with project-specific fill depths if provided in the separate MC Project List input file\n" % mc_depth_threshold_def)
        ip_csv.write("1.1211425, spsal_params[1] - SAV parameter - spring salinity parameter 1\n")
        ip_csv.write("-0.7870841, spsal_params[2] - SAV parameter - spring salinity parameter 2\n")
        ip_csv.write("1.5059876, spsal_params[3] - SAV parameter - spring salinity parameter 3\n")
        ip_csv.write("3.4309696, sptss_params_params[1] - SAV parameter - spring TSS parameter 1\n")
        ip_csv.write("-0.8343315, sptss_params_params_params[2] - SAV parameter - TSS salinity parameter 2\n")
        ip_csv.write("0.9781167, sptss_params[3] - SAV parameter - spring TSS parameter 3\n")
        ip_csv.write("5.934377, dfl_params[1] - SAV parameter - distance from land parameter 1\n")
        ip_csv.write("-1.957326, dfl_params[2] - SAV parameter - distance from land parameter 2\n")
        ip_csv.write("1.258214, dfl_params[3] - SAV parameter - distance from land parameter 3\n")

        if year == startyear:
            ip_csv.write("0,binary_in - read input raster datas from binary files (1) or from ASCI XYZ files (0)\n")
        else:
            ip_csv.write("1,binary_in - read input raster datas from binary files (1) or from ASCI XYZ files (0)\n")

        ip_csv.write("1,binary_out - write raster datas to binary format only (1) or to ASCI XYZ files (0)\n")

        if year == startyear:
            ip_csv.write("'geomorph/input/%s_W_dem30.xyz', dem_file - file name with relative path to DEM XYZ file\n" % fwoa_init_cond_tag)
            ip_csv.write("'geomorph/input/%s_W_lndtyp30.xyz', lwf_file - file name with relative path to land/water file that is same resolution and structure as DEM XYZ\n" % fwoa_init_cond_tag)
        else:
            ip_csv.write("'geomorph/output/%s_W_dem30.xyz', dem_file - file name with relative path to DEM XYZ file\n" % file_prefix_prv)
            ip_csv.write("'geomorph/output/%s_W_lndtyp30.xyz', lwf_file - file name with relative path to land/water file that is same resolution and structure as DEM XYZ\n" % file_prefix_prv)

           
        ip_csv.write("'geomorph/input/%s_W_meer30.xyz', meer_file - file name with relative path to marsh edge erosion rate file that is same resolution and structure as DEM XYZ\n" % fwoa_init_cond_tag)
        ip_csv.write("'geomorph/input/%s_W_polder30.xyz', pldr_file - file name with relative path to polder file that is same resolution and structure as DEM XYZ\n" % exist_cond_tag)
        ip_csv.write("'geomorph/input/%s_W_comp30.xyz', comp_file - file name with relative path to ICM-Hydro compartment map file that is same resolution and structure as DEM XYZ\n" % exist_cond_tag)
        ip_csv.write("'geomorph/input/%s_W_grid30.xyz', grid_file - file name with relative path to ICM-LAVegMod grid map file that is same resolution and structure as DEM XYZ\n" % exist_cond_tag)
        ip_csv.write("'geomorph/input/%s_W_subsidence.xyz', dsub_file - file name with relative path to deep subsidence rate map file that is same resolution and structure as DEM XYZ (mm/yr; positive value\n" % exist_cond_tag)
        ip_csv.write("'geomorph/input/ecoregion_shallow_subsidence_mm.csv', ssub_file - file name with relative path to shallow subsidence table with statistics by ecoregion (mm/yr; positive values are for downward VLM)\n")
        ip_csv.write(" %d,ssub_col - column of shallow subsidence rates to use for current scenario (1=25th percentile; 2=50th percentile; 3=75th percentile)\n" % shallow_subsidence_column)
        ip_csv.write("'geomorph/input/%s', act_del_file - file name with relative path to lookup table that identifies whether an ICM-Hydro compartment is assigned as an active delta site\n" % act_del_file_2use)
        ip_csv.write("'geomorph/input/compartment_no_land_gain.csv', no_gain_file - file name with relative path to lookup table that identifies ICM-Hydro compartments where ICM-Morph land gain functions are deactivated\n")
        ip_csv.write("'geomorph/input/ecoregion_organic_matter_accum.csv', eco_omar_file - file name with relative path to lookup table of organic accumulation rates by marsh type/ecoregion\n")
        ip_csv.write("'geomorph/input/compartment_ecoregion.csv', comp_eco_file - file name with relative path to lookup table that assigns an ecoregion to each ICM-Hydro compartment\n")
        ip_csv.write("'geomorph/input/ecoregion_sav_priors.csv', sav_priors_file - file name with relative path to CSV containing parameters defining the periors (per basin) for the SAV statistical model\n")

        ip_csv.write("'hydro/TempFiles/compartment_out_%4d.csv', hydro_comp_out_file - file name with relative path to compartment_out.csv file saved by ICM-Hydro\n" % year)

        if year == startyear:
            ip_csv.write("'hydro/TempFiles/compartment_out_%4d.csv', prv_hydro_comp_out_file - file name with relative path to compartment_out.csv file saved by ICM-Hydro for previous year\n" % (year))
        else:
            ip_csv.write("'hydro/TempFiles/compartment_out_%4d.csv', prv_hydro_comp_out_file - file name with relative path to compartment_out.csv file saved by ICM-Hydro for previous year\n" % (year-1))
        ip_csv.write("'veg/%s_O_%4d_V_vegty.csv', veg_out_file - file name with relative path to *vegty.csv file saved by ICM-LAVegMod that has species-level relative coverage values\n" %  (runprefix,year))
        ip_csv.write("'veg/%s_O_%4d_V_vegsm.csv', veg_out_summary_file - file name with relative path to *vegsm.csv file saved by ICM-LAVegMod that has the FFIBS coverage values for vegetated land area\n" % (runprefix,year))
        ip_csv.write("'%s', monthly_mean_stage_file - file name with relative path to compartment summary file with monthly mean water levels\n" % monthly_file_avstg)
        ip_csv.write("'%s', monthly_max_stage_file - file name with relative path to compartment summary file with monthly maximum water levels\n" % monthly_file_mxstg)
        ip_csv.write("'%s', monthly_ow_sed_dep_file - file name with relative path to compartment summary file with monthly sediment deposition in open water\n" % monthly_file_sdowt)
        ip_csv.write("'%s', monthly_mi_sed_dep_file - file name with relative path to compartment summary file with monthly sediment deposition on interior marsh\n" % monthly_file_sdint)
        ip_csv.write("'%s', monthly_me_sed_dep_file - file name with relative path to compartment summary file with monthly sediment deposition on marsh edge\n" % monthly_file_sdedg)
        ip_csv.write("'%s', monthly_mean_sal_file - file name with relative path to compartment summary file with monthly mean salinity values\n" % monthly_file_avsal)
        ip_csv.write("'%s', monthly_mean_tss_file - file name with relative path to compartment summary file with monthly mean suspended sediment concentrations\n" % monthly_file_avtss)
        ip_csv.write("'%s', bi_dem_xyz_file - file name with relative path to XYZ DEM file for ICM-BI-DEM model domain - XY resolution must be snapped to XY resolution of main DEM\n" % bidem_xyz_file)
        ip_csv.write("'geomorph/input/%s_W_dem30_channels.xyz', dredge_dem_xyz_file - file name, with relative path, to XYZ DEM file for raster that will have elevations for all maintained/dredged channels/locations, these elevations will be maintained for every year regardless of calculated deposition/erosion rates\n" % exist_cond_tag)
        ip_csv.write("'geomorph/output/%s_W_edge30.xyz', edge_eoy_xyz_file - file name with relative path to XYZ raster output file for edge pixels\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_dem30.xyz', dem_eoy_xyz_file - file name with relative path to XYZ raster output file for topobathy DEM\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_dz30.xyz', dz_eoy_xyz_file - file name with relative path to XYZ raster output file for elevation change raster\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_lndtyp30.xyz', lndtyp_eoy_xyz_file - file name with relative path to XYZ raster output file for land type\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_lndchg30.xyz', lndchng_eoy_xyz_file - file name with relative path to XYZ raster output file for land change flag\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_salav30.xyz', salav_xyz_file - file name with relative path to XYZ raster output file for average salinity\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_salmx30.xyz', salmx_xyz_file - file name with relative path to XYZ raster output file for maximum salinity\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_inun30.xyz', inun_xyz_file - file name with relative path to XYZ raster output file for average inundation depth\n" % file_prefix)
        ip_csv.write("'geomorph/output/grid_summary_eoy_%d.csv', grid_summary_eoy_file - file name with relative path to summary grid file for end-of-year landscape\n" % year)
        ip_csv.write("'%s', grid_data_file - file name with relative path to summary grid data file used internally by ICM\n" % new_grid_filepath)
        ip_csv.write("'%s', grid_depth_file_Gdw - file name with relative path to Gadwall depth grid data file used internally by ICM and HSI\n" % grid_Gdw_dep_file)
        ip_csv.write("'%s', grid_depth_file_GwT - file name with relative path to Greenwing Teal depth grid data file used internally by ICM and HSI\n" % grid_GwT_dep_file)
        ip_csv.write("'%s', grid_depth_file_MtD - file name with relative path to Mottled Duck depth grid data file used internally by ICM and HSI\n" % grid_MtD_dep_file)
        ip_csv.write("'%s', grid_pct_edge_file - file name with relative path to percent edge grid data file used internally by ICM and HSI\n" % grid_pct_edge_file)
        ip_csv.write("'geomorph/output/%s_W_SAV.csv', grid_sav_file - file name with relative path to csv output file for SAV presence\n" % file_oprefix)
        ip_csv.write("'%s', comp_elev_file - file name with relative path to elevation summary compartment file used internally by ICM\n" % comp_elev_file)
        ip_csv.write("'%s', comp_wat_file - file name with relative path to percent water summary compartment file used internally by ICM\n" % comp_wat_file)
        ip_csv.write("'%s', comp_upl_file - file name with relative path to percent upland summary compartment file used internally by ICM\n" % comp_upl_file)
        ip_csv.write("%d, write_zonal_stats - integer flag to indicate whether zonal statistics are to be conducted in ICM-Morph (1) or whether a CSV file will be saved to do external zonal statistics(0)\n" % morph_zonal_stats)
        ip_csv.write("'%s',dem_grid_out_summary_file - file name, with relative path, to CSV output file that will save DEM-resolution landscape data to be used in zonal statistics\n" % dem_grid_data_outfile)
        ip_csv.write("2941, nqaqc - number of QAQC points for reporting - as listed in qaqc_site_list_file\n")
        ip_csv.write("'geomorph/output_qaqc/qaqc_site_list.csv', qaqc_site_list_file - file name, with relative path, to percent upland summary compartment file used internally by ICM\n")
        ip_csv.write(" %s, file naming convention prefix\n" % file_o_01_end_prefix)
        ip_csv.write(" %d, n_mc - number of marsh creation elements to be built in current year\n" % n_mc_yr)
        ip_csv.write("'%s', project_list_MC_file - file name with relative path to list of marsh creation raster XYZ files\n" % mc_project_list_yr)
        ip_csv.write("'%s', project_list_MC_VA_file - file name with relative path to file that will report out marsh creation volumes and footprint areas\n" % mc_project_list_VolArea_yr)
        ip_csv.write(" %d, n_rr - number of ridge or levee projects to  be built in current year\n" % n_rr_yr)
        ip_csv.write("'%s', project_list_RR_file - file name with relative path to list of ridge and levee raster XYZ files\n" % rr_project_list_yr)
        ip_csv.write(" %d, n_bs - number of bank stabilization projects built in current year OR PREVIOUS years\n" % n_sp_cumul)
        ip_csv.write("'%s', project_list_BS_file - file name with relative path to list of MEE rate multiplier XYZ files for current and all previous BS projects\n" % sp_project_list_cumul)
   
    morph_run = subprocess.call(morph_exe_path)
    
    ##############################################################
    ##          RUN ZONAL STATISTICS ON MORPH OUTPUTS           ##
    ##############################################################
    
    if morph_zonal_stats == 0: # 1=zonal stats run in ICM-Morph; 0=zonal stats run here in ICM
        
        print('\n--------------------------------------------------' )
        print('  RUNNING ZONAL STATS ON ICM-MORPH OUTPUT- year %s' % year)
        print('--------------------------------------------------\n')
        Gdw_bin_n = 14    # number of water depth bins used by Gadwall HSI
        GwT_bin_n = 9     # number of water depth bins used by Greenwing Teal HSI
        MtD_bin_n = 9     # number of water depth bins used by Mottled Duck HSI
        
        print(' Reading in monthly stage data.')
        comp_mon_stg = {}   
        with open(monthly_file_avstg,mode='r') as comp_stg_data:
            nline = 0
            for line in comp_stg_data:  # comp,stage_m_01,stage_m_02,stage_m_03,stage_m_04,stage_m_05,stage_m_06,stage_m_07,stage_m_08,stage_m_09,stage_m_10,stage_m_11,stage_m_12
                if nline > 0:
                    c = int(line.split(',')[0])
                    comp_mon_stg[c] = {}
                    for n_mon in range(1,13):
                        comp_mon_stg[c][n_mon] = float(line.split(',')[n_mon])
                nline += 1
    
        # set up empty dictionaries and arrays that will hold zonal statistic values
        grid_bed_z_all = {}
        grid_bed_z = {} 
        
        grid_land_z_all = {}
        grid_land_z = {}
         
        grid_pct_land_all = {}
        grid_pct_land = {}
        
        grid_pct_land_wetl_all = {} 
        grid_pct_land_wetl = {} 
        
        grid_pct_water_all = {} 
        grid_pct_water = {} 
        
        grid_pct_edge_all = {}
        grid_pct_edge = {}
        
        grid_Gdw_depths = {}
        grid_GwT_depths = {}
        grid_MtD_depths = {}
        
        comp_water_z_all = {}
        comp_water_z = {}
        
        comp_wetland_z_all = {}
        comp_wetland_z = {}
        
        comp_edge_area_all = {}
        comp_edge_area = {}
        
        comp_pct_water_all = {}
        comp_pct_water = {}
        
        comp_pct_upland_all = {}
        comp_pct_upland = {}
        
        for g in range(1,n500grid+1):
            grid_bed_z_all[g] = []         
            grid_bed_z[g] = 0.0         
            
            grid_land_z_all[g] = []      
            grid_land_z[g] = 0.0
        
            grid_pct_land_all[g] = []    
            grid_pct_land[g] = 0.0
            
            grid_pct_land_wetl_all[g] = [] 
            grid_pct_land_wetl[g] = 0.0
            
            grid_pct_water_all[g] = []
            grid_pct_water[g] = 0.0     
            
            grid_pct_edge_all[g] = []      
            grid_pct_edge[g] = 0.0
        
            grid_Gdw_depths[g] = {}
            for Gdw_bin in range(1,Gdw_bin_n + 1):
                grid_Gdw_depths[g][Gdw_bin] = 0.0
                
            grid_GwT_depths[g] = {}
            for GwT_bin in range(1,GwT_bin_n + 1):
                grid_GwT_depths[g][GwT_bin] = 0.0
                
            grid_MtD_depths[g] = {}   
            for MtD_bin in range(1,MtD_bin_n + 1):
                grid_MtD_depths[g][MtD_bin] = 0.0
            
        for c in range(1,ncomp+1):                           
            comp_water_z_all[c] = []       
            comp_water_z[c] = 0.0
                   
            comp_wetland_z_all[c] = [] 
            comp_wetland_z[c] = 0.0    
            
            comp_edge_area_all[c] = []    
            comp_edge_area[c] = 0.0    
            
            comp_pct_water_all[c] = []    
            comp_pct_water[c] = 0.0    
            
            comp_pct_upland_all[c] = []   
            comp_pct_upland[c] = 0.0   
        
        print(' Reading in ICM-Morph output data at DEM resolution from %s' % dem_grid_data_outfile)
        with open(dem_grid_data_outfile,mode='r') as grid_data:
            nline = 0
            for line in grid_data:
                if nline > 0:   # header: ndem,ICM_LAVegMod_GridCell,ICM_Hydro_Compartment,landtype,edge,z_NAVD88_m
                    g      = int(float(line.split(',')[1]))
                    c      = int(float(line.split(',')[2]))
                    lndtyp = int(float(line.split(',')[3]))
                    edge   = int(float(line.split(',')[4]))
                    elev   = float(line.split(',')[5])
                    
                    if c > 0:
                        comp_edge_area_all[c].append(edge*dem_res*dem_res)
                        if lndtyp == 2:
                            comp_water_z_all[c].append(elev)
                            comp_pct_water_all[c].append(1)
                        else:
                            if lndtyp != 4:     # check if upland/developed
                                comp_wetland_z_all[c].append(elev)
                            else:
                                comp_pct_upland_all[c].append(1)
                    
                    if g > 0:
                        grid_pct_edge_all[g].append(edge)
                        if lndtyp == 2:
                            grid_bed_z_all[g].append(elev)
                            grid_pct_water_all[g].append(1)
                        else:
                            grid_land_z_all[g].append(elev)
                            grid_pct_land_all[g].append(1)
                            if lndtyp != 4:     # check if upland/developed
                                grid_pct_land_wetl_all[g].append(1)
                        
                       
                        if c > 0:
                            if elev > -9999:
                                dep_oct_apr = (comp_mon_stg[c][1]+comp_mon_stg[c][2]+comp_mon_stg[c][3]+comp_mon_stg[c][4]+comp_mon_stg[c][10]+comp_mon_stg[c][11]+comp_mon_stg[c][12])/7.0 - elev
                                dep_sep_mar = (comp_mon_stg[c][1]+comp_mon_stg[c][2]+comp_mon_stg[c][3]+comp_mon_stg[c][9]+comp_mon_stg[c][10]+comp_mon_stg[c][11]+comp_mon_stg[c][12])/7.0 - elev 
                                dep_ann     = (comp_mon_stg[c][1]+comp_mon_stg[c][2]+comp_mon_stg[c][3]+comp_mon_stg[c][4]+comp_mon_stg[c][5]+comp_mon_stg[c][6]+comp_mon_stg[c][7]+comp_mon_stg[c][8]+comp_mon_stg[c][9]+comp_mon_stg[c][10]+comp_mon_stg[c][11]+comp_mon_stg[c][12])/12.0 - elev
                                
                                # tabulate area of grid cell within each Gadwall depth bin; depth thresholds (in m) are: [0,0.04,0.08,0.12,0.18,0.22,0.28,0.32,0.36,0.40,0.44,0.78,1.50]     
                                if dep_oct_apr <= 0.0:
                                    grid_Gdw_depths[g][1]  = grid_Gdw_depths[g][1] + dem_res**2
                                elif dep_oct_apr <= 0.04:
                                    grid_Gdw_depths[g][2]  = grid_Gdw_depths[g][2] + dem_res**2
                                elif dep_oct_apr <= 0.08:
                                    grid_Gdw_depths[g][3]  = grid_Gdw_depths[g][3] + dem_res**2
                                elif dep_oct_apr <= 0.12:
                                    grid_Gdw_depths[g][4]  = grid_Gdw_depths[g][4] + dem_res**2
                                elif dep_oct_apr <= 0.18:
                                    grid_Gdw_depths[g][5]  = grid_Gdw_depths[g][5] + dem_res**2
                                elif dep_oct_apr <= 0.22:
                                    grid_Gdw_depths[g][6]  = grid_Gdw_depths[g][6] + dem_res**2
                                elif dep_oct_apr <= 0.28:
                                    grid_Gdw_depths[g][7]  = grid_Gdw_depths[g][7] + dem_res**2
                                elif dep_oct_apr <= 0.32:
                                    grid_Gdw_depths[g][8]  = grid_Gdw_depths[g][8] + dem_res**2
                                elif dep_oct_apr <= 0.36:
                                    grid_Gdw_depths[g][9]  = grid_Gdw_depths[g][9] + dem_res**2
                                elif dep_oct_apr <= 0.40:
                                    grid_Gdw_depths[g][10] = grid_Gdw_depths[g][10] + dem_res**2
                                elif dep_oct_apr <= 0.44:
                                    grid_Gdw_depths[g][11] = grid_Gdw_depths[g][11] + dem_res**2
                                elif dep_oct_apr <= 0.78:
                                    grid_Gdw_depths[g][12] = grid_Gdw_depths[g][12] + dem_res**2
                                elif dep_oct_apr <= 1.50:
                                    grid_Gdw_depths[g][13] = grid_Gdw_depths[g][13] + dem_res**2
                                else:
                                    grid_Gdw_depths[g][14] = grid_Gdw_depths[g][14] + dem_res**2
                                
                                # tabulate area of grid cell within each Greenwing Teal depth bin; depth thresholds (in m) are: [0,0.06,0.18,0.22,0.26,0.30,0.34,1.0]
                                if dep_sep_mar <= 0.0:
                                    grid_GwT_depths[g][1] = grid_GwT_depths[g][1] + dem_res**2
                                elif dep_sep_mar <= 0.06:
                                    grid_GwT_depths[g][2] = grid_GwT_depths[g][2] + dem_res**2
                                elif dep_sep_mar <= 0.18:
                                    grid_GwT_depths[g][3] = grid_GwT_depths[g][3] + dem_res**2
                                elif dep_sep_mar <= 0.22:
                                    grid_GwT_depths[g][4] = grid_GwT_depths[g][4] + dem_res**2
                                elif dep_sep_mar <= 0.26:
                                    grid_GwT_depths[g][5] = grid_GwT_depths[g][5] + dem_res**2
                                elif dep_sep_mar <= 0.30:
                                    grid_GwT_depths[g][6] = grid_GwT_depths[g][6] + dem_res**2
                                elif dep_sep_mar <= 0.34:
                                    grid_GwT_depths[g][7] = grid_GwT_depths[g][7] + dem_res**2
                                elif dep_sep_mar <= 1.0:
                                    grid_GwT_depths[g][8] = grid_GwT_depths[g][8] + dem_res**2
                                else:
                                    grid_GwT_depths[g][9] = grid_GwT_depths[g][9] + dem_res**2
                                
                                # tabulate area of grid cell within each Mottled Duck depth bin; depth thresholds (in m) are: [0,0.08,0.30,0.36,0.42,0.46,0.50,0.56]
                                if dep_ann <= 0.0:        
                                    grid_MtD_depths[g][1] = grid_MtD_depths[g][1] + dem_res**2
                                elif dep_ann <= 0.08:            
                                    grid_MtD_depths[g][2] = grid_MtD_depths[g][2] + dem_res**2
                                elif dep_ann <= 0.30:            
                                    grid_MtD_depths[g][3] = grid_MtD_depths[g][3] + dem_res**2
                                elif dep_ann <= 0.36:            
                                    grid_MtD_depths[g][4] = grid_MtD_depths[g][4] + dem_res**2
                                elif dep_ann <= 0.42:            
                                    grid_MtD_depths[g][5] = grid_MtD_depths[g][5] + dem_res**2
                                elif dep_ann <= 0.46:            
                                    grid_MtD_depths[g][6] = grid_MtD_depths[g][6] + dem_res**2
                                elif dep_ann <= 0.50:            
                                    grid_MtD_depths[g][7] = grid_MtD_depths[g][7] + dem_res**2
                                elif dep_ann <= 0.56:            
                                    grid_MtD_depths[g][8] = grid_MtD_depths[g][8] + dem_res**2
                                else:
                                    grid_MtD_depths[g][9] = grid_MtD_depths[g][9] + dem_res**2
        
                nline += 1
        
        # determine zonal averages over each ICM-LAVegMod grid cell
        for g in range(1,n500grid+1):
            ng = len(grid_bed_z_all[g]) + len(grid_land_z_all[g])
            
            if ng > 0:
                grid_bed_z[g]          = sum(grid_bed_z_all[g]) / ng
                grid_land_z[g]         = sum(grid_land_z_all[g]) / ng
                grid_pct_land[g]       = 100.0*sum(grid_pct_land_all[g]) / ng
                grid_pct_land_wetl[g]  = 100.0*sum(grid_pct_land_wetl_all[g]) / ng
                grid_pct_water[g]      = 100.0*sum(grid_pct_water_all[g]) / ng
                grid_pct_edge[g]       = 100.0*sum(grid_pct_edge_all[g]) / ng
            else:
                grid_bed_z[g]          = 0.0
                grid_land_z[g]         = 0.0
                grid_pct_land[g]       = 0.0
                grid_pct_land_wetl[g]  = 0.0
                grid_pct_water[g]      = 0.0
                grid_pct_edge[g]       = 0.0
                
        
        # determine zonal averages over each ICM-Hydro compartment
        for c in range(1,ncomp+1):    
            nc = len(comp_water_z_all[c]) + len(comp_wetland_z_all[c]) + len(comp_pct_upland_all[c])
        
            if nc > 0:
                comp_pct_upland[c] = sum(comp_pct_upland_all[c]) / nc
                comp_water_z[c]    = sum(comp_water_z_all[c]   ) / nc
                comp_wetland_z[c]  = sum(comp_wetland_z_all[c] ) / nc
                comp_pct_water[c]  = sum(comp_pct_water_all[c] ) / nc
                comp_edge_area[c]  = sum(comp_edge_area_all[c] )
            else:
                comp_pct_upland[c] = 0.0
                comp_water_z[c]    = 0.0
                comp_wetland_z[c]  = 0.0
                comp_pct_water[c]  = 0.0
                comp_edge_area[c]  = 0.0        
        
        print(' Writing zonal statistics output files:')
        with open(new_grid_filepath,mode='w') as gdaf:  
            print('     - %s' % new_grid_filepath)
            gdaf.write('GRID,MEAN_BED_ELEV,MEAN_LAND_ELEV,PERCENT_LAND_0-100,PERCENT_WETLAND_0-100,PERCENT_WATER_0-100\n')
            for g in grid_bed_z.keys():
                gdaf.write('%d,%0.4f,%0.4f,%0.2f,%0.2f,%0.2f\n' % (g,grid_bed_z[g],grid_land_z[g],grid_pct_land[g],grid_pct_land_wetl[g],grid_pct_water[g]) )
            
        with open(grid_pct_edge_file,mode='w') as gdef:  
            print('     - %s' % grid_pct_edge_file)
            gdef.write('GRID,PERCENT_EDGE_0-100\n')
            for g in grid_pct_edge.keys():
                gdef.write('%d,%0.4f\n' % (g,grid_pct_edge[g]) )
              
        with open(comp_elev_file,mode='w') as cef:
            print('     - %s' % comp_elev_file)
            cef.write('ICM_ID,MEAN_BED_ELEV,MEAN_MARSH_ELEV,MARSH_EDGE_AREA\n')
            for c in comp_water_z.keys():
                cef.write('%d,%0.4f,%0.4f,%d\n' % (c,comp_water_z[c],comp_wetland_z[c],comp_edge_area[c]) )
        
        with open(comp_wat_file, mode='w') as cwf:
            print('     - %s' % comp_wat_file)
            for c in comp_pct_water.keys():
                cwf.write( '%d,%0.4f\n' % (c,comp_pct_water[c]) )
        
        with open(comp_upl_file, mode='w') as cuf:
            print('     - %s' % comp_upl_file)
            for c in comp_pct_upland.keys():
                cuf.write( '%d,%0.4f\n' % (c,comp_pct_upland[c]) )
        
        with open(grid_Gdw_dep_file, mode='w') as Gdw:    
            print('     - %s' % grid_Gdw_dep_file)
            Gdw.write('GRID_ID,VALUE_0,VALUE_4,VALUE_8,VALUE_12,VALUE_18,VALUE_22,VALUE_28,VALUE_32,VALUE_36,VALUE_40,VALUE_44,VALUE_78,VALUE_150,VALUE_151\n')
            for g in grid_Gdw_depths.keys():
                linewrite = '%d' % g
                for Gdw_bin in range(1,Gdw_bin_n + 1):
                    linewrite = '%s,%d' % (linewrite,grid_Gdw_depths[g][Gdw_bin])
                Gdw.write('%s\n' % linewrite)
        
        with open(grid_GwT_dep_file, mode='w') as GwT:
            print('     - %s' % grid_GwT_dep_file)
            GwT.write('GRID_ID,VALUE_0,VALUE_6,VALUE_18,VALUE_22,VALUE_26,VALUE_30,VALUE_34,VALUE_100,VALUE_101\n')
            for g in grid_GwT_depths.keys():
                linewrite = '%d' % g
                for GwT_bin in range(1,GwT_bin_n + 1):
                    linewrite = '%s,%d' % (linewrite,grid_GwT_depths[g][GwT_bin])
                GwT.write('%s\n' % linewrite)
        
        with open(grid_MtD_dep_file, mode='w') as MtD:
            print('     - %s' % grid_MtD_dep_file)
            MtD.write('GRID_ID,VALUE_0,VALUE_8,VALUE_30,VALUE_36,VALUE_42,VALUE_46,VALUE_50,VALUE_56,VALUE_57\n')
            for g in grid_MtD_depths.keys():
                linewrite = '%d' % g
                for MtD_bin in range(1,MtD_bin_n + 1):
                    linewrite = '%s,%d' % (linewrite,grid_MtD_depths[g][MtD_bin])
                MtD.write('%s\n' % linewrite)
        
                
        print(' Deleting output file: %s' % dem_grid_data_outfile)
        os.remove(dem_grid_data_outfile)
    
    if run_sav == 1:
        try:
            snum = '%s' % int(sterm[1:])
            gnum = '%s' % int(gterm[1:])
            cmdstr = ['python',sav_submit_exe_path,snum,gnum,'%s' % year] 
            subprocess.call(cmdstr)
        except:
            print(' !! Failed to submit SAV for %s' % year)
        
        
print('\n\n\n')
print('-----------------------------------------' )
print(' ICM Model run complete!')
print('-----------------------------------------\n')



