#Python imports
import datetime as dt
import numpy as np
import os
import pandas
import platform
from scipy.interpolate import griddata
import shutil
import subprocess
import sys
import time

#########################################################################################################
####                                                                                                 ####
####                                FUNCTIONS USED BY ICM                                            ####
####                                                                                                 ####
#########################################################################################################


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


def check_var_lengths(links_to_change, link_years, mc_elementIDs, mc_years, mc_links, mc_links_years, sp_projectIDs, sp_years, rr_projectIDs, rr_years, act_del_files, act_del_years):
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


def check_versions():
    ## Check Versions ##
    vs=sys.version_info
    npvs=np.__version__
    npvsarray = np.fromstring(npvs,sep='.',dtype=int)
    npver=float(npvsarray[0])+float(npvsarray[1])/10.0
    ## Check if Python version is 64-bit
    if sys.maxsize > 2**32:
        arch = '64-bit'
        print(' This run is utilizing %s Python %s.%s.%s with NumPy %s' %(arch,vs.major,vs.minor,vs.micro,npvs) )
    ## Check that NumPy version is 1.7 or newer
        if npver < 1.7:
            print(' NumPy version is earlier than NumPy 1.7.0 - this version of NumPy is not supported.')
            print(' Install 64-bit NumPy 1.7.0 (or newer) and re-run ICM.')
            print('\n Press <ENTER> to cancel run.')
            input()
            sys.exit()
        else:
                print('\n This Python configuration is supported.')
    else:
        arch = '32-bit'
        print(' This run is utilizing %s Python %s.%s.%s with NumPy %s' %(arch,vs.major,vs.minor,vs.micro,npvs) )
        print(' Install 64-bit Python with NumPy 1.7.0 (or newer) and re-run ICM.')
        print('\n Press ENTER to cancel run.')
        input()
        sys.exit()

    del (vs,arch,npvs, npvsarray,npver)


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


def print_credits():
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


def write_1d_hyd_inp(ecohydro_dir,HydroConfigFile,i,year,lq):
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
####                             FUNCTIONS USED BY HSI MODELS                                        ####
####                                                                                                 ####
#########################################################################################################


def build_dictionaries(gridIDs):
    # build empty dictionaries that will be filled with monthly average values
    # key will be grid ID
    # value will be an array of 12 monthly values
    saldict = {}
    tmpdict = {}
    stgmndict = {}
    
    for n in gridIDs:
        saldict[n] = []
        tmpdict[n] = []
        stgmndict[n] = []
    
    return saldict, tmpdict, stgmndict


def check_HSI_standalone(HSI_standalone,year,endyear):
    # TODO delete this function when the naming convention in morph gets updated
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

    return new_grid_file


def create_ASCII_grid_vals(vegetation_dir,n500rows,n500cols,yll500,xll500):
    grid_ascii_file = os.path.normpath(vegetation_dir + '/veg_grid.asc')    
    print( ' Reading in ASCII grid template.')

    ascii_grid_lookup = np.genfromtxt(grid_ascii_file,delimiter=' ',  skip_header=6)
    ascii_header='nrows %s \nncols %s \nyllcorner %s \nxllcorner %s \ncellsize 480.0 \nnodata_value -9999.00' % (n500rows,n500cols,yll500,xll500)
    ascii_header_nrows = 6 #TODO check to see if this is needed
    
    return ascii_grid_lookup,ascii_header,ascii_header_nrows,n500rows,n500cols 


def create_domdict(year):
    dom = {}
    dom[1]=31
    if year in range(2000,4000,4):
        dom[2]=29
    else:
        dom[2]=28
    dom[3]=31
    dom[4]=30
    dom[5]=31
    dom[6]=30
    dom[7]=31
    dom[8]=31
    dom[9]=30
    dom[10]=31
    dom[11]=30
    dom[12]=31
    
    return dom


def HSIascii_grid(HSIcsv,HSIasc,map2grid,ascii_grid_lookup,n500cols,n500rows,ascii_header):
    if map2grid:
        print(' - mapping HSI to ASCII grid')    
        
        # read HSI csv file into numpy array - usecol = column of csv file that has HSI value
        newHSI = np.genfromtxt(HSIcsv,delimiter=',',usecols=[0,1],  skip_header=1)
        newHSIdict = dict((newHSI[n][0],newHSI[n][1])for n in range(0,len(newHSI)))
        
        # prepare zero array in same shape of original Veg output ASCII grid
        newHSIgrid=np.zeros([n500rows,n500cols])
                        
        for m in range(0,n500rows):
            for n in range(0,n500cols):
                cellID = ascii_grid_lookup[m][n]
                if cellID == -9999:
                    newHSIgrid[m][n] = -9999
                else:
                    try:
                        newHSIval = newHSIdict[cellID] 
                        if np.isnan(newHSIval):
                            newHSIgrid[m][n] = -1.0
                        elif np.isinf(newHSIval):
                            newHSIgrid[m][n] = -1.0
                        else:
                            newHSIgrid[m][n] = newHSIval
                    except:   # if cellID is not a key in the newLULCdictionay - assign cell to NoData
                        newHSIgrid[m][n] = -9999
        
        print( " - saving new HSI ASCII raster file")
        
        # save formatted grid to ascii file with appropriate ASCII raster header
        np.savetxt(HSIasc,newHSIgrid,fmt='%.2f',delimiter=' ',header=ascii_header,comments='')
        
        newHSI = 0
        newHSIdict = {}
    else:
        print(' - skipping: mapping HSI to ASCII grid - will need to post-process from CSVs')


def monthly_avg_dict(valdict, subsetdict):
    # val_dict:         dictionary of values (salinity, temperature, etc.) arranged by grid cell on a monthly time scale
    # subset_dict:      a dictionary of month abbreviations as: ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'octb', 'nov', 'dec']
    #                   this array does not need consecutive months to function
    
    avgdict = {}
    array_of_key_values = [x for x in subsetdict]
    for n in range(1, len(valdict) + 1):
        # Extract the values for the specified months
        mon_avgs = [valdict[n][month] for month in array_of_key_values]
        avgdict[n] = np.mean(mon_avgs)
    return avgdict


def monthly_dictAbbrev(subset_months):
    month_abbreviations = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    # Create the full dictionary using a for loop
    months_dict = {month_abbreviation: month_number + 1 for month_number, month_abbreviation in enumerate(month_abbreviations)}

    subsetdict = {month: months_dict[month] for month in subset_months if month in months_dict}

    return subsetdict


def monthly_dictKeys(month_keys):
    month_abbreviations = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'octb', 'nov', 'dec']
    # Create the full dictionary using a for loop
    months_dict = {}
    for month_number in range(0, 12):
        month_abbreviation = month_abbreviations[month_number]
        months_dict[month_number] = month_abbreviation

    subsetdict = {key: months_dict[key] for key in month_keys}

    return subsetdict


def monthly_mean_salinity(saldict,ecohydro_dir,runprefix,endyear,startyear,ndays_run, data_start,ave_end,ave_start,gridIDs,grid_comp):
    # read in daily salinity and calculate monthly mean for compartment then map to grid using daily2ave and comp2grid functions
    daily_timeseries_file = os.path.normpath(r'%s/SAL.out' % ecohydro_dir)
    if os.path.exists(daily_timeseries_file) == False:
        daily_timeseries_file = os.path.normpath(r'%s/%s_O_01_%02d_H_SAL.out' % (ecohydro_dir,runprefix,endyear-startyear+1) )
    comp_month_ave_dict = daily2ave(data_start,ave_start,ave_end,daily_timeseries_file,ndays_run)
    mon_ave = comp2grid(comp_month_ave_dict,grid_comp)
    # loop through monthly average and append to array of monthly averages in dictionary to be passed into HSI.py
    for n in gridIDs:
        saldict[n].append(round(mon_ave[n],1)) # this will save monthly mean to the tenths decimal #.# precision
    
    return saldict


def monthly_mean_stage(stgmndict,ecohydro_dir,runprefix,endyear,startyear,ndays_run, data_start,ave_end,ave_start,gridIDs,grid_comp):
    # read in daily temperature and calculate monthly mean for compartment then map to grid using daily2ave and comp2grid functions
    daily_timeseries_file = os.path.normpath(r'%s/STG.out' % ecohydro_dir)
    if os.path.exists(daily_timeseries_file) == False:
        daily_timeseries_file = os.path.normpath(r'%s/%s_O_01_%02d_H_STG.out' % (ecohydro_dir,runprefix,endyear-startyear+1) )
    comp_month_ave_dict = daily2ave(data_start,ave_start,ave_end,daily_timeseries_file,ndays_run)
    mon_ave = comp2grid(comp_month_ave_dict,grid_comp)
    # loop through monthly average and append to array of monthly averages in dictionary to be passed into HSI.py
    for n in gridIDs:
        stgmndict[n].append(mon_ave[n])

    return stgmndict


def monthly_mean_temp(tmpdict,ecohydro_dir,runprefix,endyear,startyear,ndays_run, data_start,ave_end,ave_start,gridIDs,grid_comp):
    # read in daily temperature and calculate monthly mean for compartment then map to grid using daily2ave and comp2grid functions
    daily_timeseries_file = os.path.normpath(r'%s/TMP.out' % ecohydro_dir)
    if os.path.exists(daily_timeseries_file) == False:
        daily_timeseries_file = os.path.normpath(r'%s/%s_O_01_%02d_H_TMP.out' % (ecohydro_dir,runprefix,endyear-startyear+1) )
    comp_month_ave_dict = daily2ave(data_start,ave_start,ave_end,daily_timeseries_file,ndays_run)
    mon_ave = comp2grid(comp_month_ave_dict,grid_comp)
    # loop through monthly average and append to array of monthly averages in dictionary to be passed into HSI.py
    for n in gridIDs:
        tmpdict[n].append(round(mon_ave[n],1)) # this will save monthly mean to the tenths decimal #.# precision

    return tmpdict


#########################################################################################################
####                                                                                                 ####
####                             FUNCTIONS USED BY ICM & HSI                                         ####
####                                                                                                 ####
#########################################################################################################


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




    