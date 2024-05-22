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
        saldict[n] = {}
        tmpdict[n] = {}
        stgmndict[n] = {}
    
    return saldict, tmpdict, stgmndict


def build_temp_dictionary(gridIDs):
    tempdict = {}
    for n in gridIDs:
        tempdict[n] = []
    
    return tempdict


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
    
    return grid_ascii_file, ascii_grid_lookup,ascii_header,ascii_header_nrows,n500rows,n500cols 


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


def HSIascii_grid(HSIcsv,HSIasc,ascii_grid_lookup,n500cols,n500rows,ascii_header):
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


def create_elevdict(griddata,n500grid):
    # bedelevdict is a dictionary of mean elevation of water bottom (bed) portion of grid, key is gridID, noData = -9999
    bedelevdict = dict((int(griddata[n][0]),griddata[n][1]) for n in range(0,n500grid))
    # melevdict is a dictionary of mean elevation of marsh surface portion of grid, key is gridID, noData = -9999
    melevdict   = dict((int(griddata[n][0]),griddata[n][2]) for n in range(0,n500grid))

    return(bedelevdict,melevdict)


def create_pctdict(griddata,n500grid):
    # landdict is a dictionary of percent land (0-100) in each 500-m grid cell, key is gridID
    landdict    = dict((int(griddata[n][0]),griddata[n][3]) for n in range(0,n500grid))
    # waterdict is a dictionary of percent water (0-100) in each 500-m grid cell, key is gridID
    waterdict   = dict((int(griddata[n][0]),griddata[n][5]) for n in range(0,n500grid))
    # wetlanddict is a dictionary of percent wetland (0-100) (percet land - percent upland) in each 500-m grid cell, key is gridID
    wetlanddict = dict((int(griddata[n][0]),griddata[n][4]) for n in range(0,n500grid))

    return(landdict,waterdict,wetlanddict)


def create_seddep(gridIDs,OWseddep_mass_dict):
    OWseddep_depth_mm_dict = {}
    
    # ow_bd - bulk density of water bottoms (g/cm3)
    BDWaterVal = 0.835              
    
    # convert sediment deposition loading (kg/m2) to depth (mm) using bulk density of open water area (kg/m3)
    # if deposition is negative, that indicates erosion
    
    # sed deposition in ICM-Hydro is calculated in g/m^2
    # must convert to g/cm^2    
    # [g/cm^2] = [g/m^2]*[m/100 cm]*[m/100 cm] = [g/m^2]/10000
     
    for n in gridIDs:
        # seddep in ICM-Hydro is negative if eroded, only take positive values here for deposited depth
        depo_g_cm2 = max(0.0,OWseddep_mass_dict[n]/10000.)  
        
        # depth mineral deposition [cm] =  mineral depostion [g/cm2] / open water bed bulk density [g/cm3]
        depo_cm = depo_g_cm2/BDWaterVal 
        OWseddep_depth_mm_dict[n] = depo_cm/10.0
    
    return OWseddep_depth_mm_dict


def create_stgdict(EH_grid_out,n500grid):
    stagedict = dict((int(EH_grid_out[n][0]),EH_grid_out[n][12]) for n in range(0,n500grid))
    
    return stagedict
    

def create_pctsanddict(EH_grid_out,n500grid):
    pctsanddict = dict((int(EH_grid_out[n][0]),EH_grid_out[n][7]) for n in range(0,n500grid))
    
    return pctsanddict


def num_days_run(ecohydro_dir,runprefix,endyear,startyear):
    daily_timeseries_file = os.path.normpath(r'%s/SAL.out' % ecohydro_dir)
    if os.path.exists(daily_timeseries_file) == False:
        daily_timeseries_file = os.path.normpath(r'%s/%s_O_01_%02d_H_SAL.out' % (ecohydro_dir,runprefix,endyear-startyear+1) )
    
    ndays_run = file_len(daily_timeseries_file)

    return ndays_run


def create_pctedgedict(HSI_dir,runprefix,elapsedyear,n500grid):
    # import percent edge output from geomorph routine that is summarized by grid ID
    pctedge_file = os.path.normpath('%s/%s_N_%02d_%02d_W_pedge.csv'% (HSI_dir,runprefix,elapsedyear,elapsedyear))
     # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year) here instead of CurrentYear
    pedge = np.genfromtxt(pctedge_file,delimiter = ',',skip_header = 1)
    
    pctedgedict = dict((int(pedge[n][0]),pedge[n][1]) for n in range(0,n500grid))

    return pctedgedict


def monthly_mean_salinity(saldict,ecohydro_dir,runprefix,endyear,startyear,ndays_run, data_start,ave_end,ave_start,gridIDs,grid_comp,mon):
    # read in daily salinity and calculate monthly mean for compartment then map to grid using daily2ave and comp2grid functions
    daily_timeseries_file = os.path.normpath(r'%s/SAL.out' % ecohydro_dir)
    if os.path.exists(daily_timeseries_file) == False:
        daily_timeseries_file = os.path.normpath(r'%s/%s_O_01_%02d_H_SAL.out' % (ecohydro_dir,runprefix,endyear-startyear+1) )
    comp_month_ave_dict = daily2ave(data_start,ave_start,ave_end,daily_timeseries_file,ndays_run)
    mon_ave = comp2grid(comp_month_ave_dict,grid_comp)
    # loop through monthly average and append to array of monthly averages in dictionary to be passed into HSI.py
    for n in gridIDs:
        # this will save monthly mean to the tenths decimal #.# precision
        saldict[n][mon] = round(mon_ave[n],1)

    return saldict


def monthly_mean_temp(tmpdict,ecohydro_dir,runprefix,endyear,startyear,ndays_run, data_start,ave_end,ave_start,gridIDs,grid_comp,mon):
    # read in daily temperature and calculate monthly mean for compartment then map to grid using daily2ave and comp2grid functions
    daily_timeseries_file = os.path.normpath(r'%s/TMP.out' % ecohydro_dir)
    if os.path.exists(daily_timeseries_file) == False:
        daily_timeseries_file = os.path.normpath(r'%s/%s_O_01_%02d_H_TMP.out' % (ecohydro_dir,runprefix,endyear-startyear+1) )
    comp_month_ave_dict = daily2ave(data_start,ave_start,ave_end,daily_timeseries_file,ndays_run)
    mon_ave = comp2grid(comp_month_ave_dict,grid_comp)
    # loop through monthly average and append to array of monthly averages in dictionary to be passed into HSI.py
    for n in gridIDs:
        # this will save monthly mean to the tenths decimal #.# precision
        tmpdict[n][mon] = round(mon_ave[n],1)

    return tmpdict


def monthly_mean_stage(stgmndict,ecohydro_dir,runprefix,endyear,startyear,ndays_run, data_start,ave_end,ave_start,gridIDs,grid_comp,mon):
    # read in daily temperature and calculate monthly mean for compartment then map to grid using daily2ave and comp2grid functions
    daily_timeseries_file = os.path.normpath(r'%s/STG.out' % ecohydro_dir)
    if os.path.exists(daily_timeseries_file) == False:
        daily_timeseries_file = os.path.normpath(r'%s/%s_O_01_%02d_H_STG.out' % (ecohydro_dir,runprefix,endyear-startyear+1) )
    comp_month_ave_dict = daily2ave(data_start,ave_start,ave_end,daily_timeseries_file,ndays_run)
    mon_ave = comp2grid(comp_month_ave_dict,grid_comp)
    # loop through monthly average and append to array of monthly averages in dictionary to be passed into HSI.py
    for n in gridIDs:
        stgmndict[n][mon] = mon_ave[n]

    return stgmndict


def monthly_avg_dict(valdict, subset):
    result = {}
    n_months = len(subset)
    
    for n in range(1, len(valdict) + 1):
        result[n] = 0.0

        for month in subset:
            result[n] += valdict[n][month]/n_months
    
    return result


def monthly_min_dict(valdict, subset):
    result = {}

    for outer_key, inner_dict in valdict.items():
        templist = []

        for key in subset:
            templist.append(inner_dict[key])
        
        templist.sort()
        result[outer_key] = templist[0]
    
    return result


def check_key_format(landdict,waterdict,melevdict,wetlanddict,OWseddep_depth_mm_dict,stagedict,pctsanddict,saldict,tmpdict,pctedgedict,cultchdict):
    # print statements to check all keys are imported and correct format (should all be integers)    
    print( len(landdict.keys()),min(landdict.keys()),max(landdict.keys()) )
    print( len(waterdict.keys()),min(waterdict.keys()),max(waterdict.keys()) )
    print( len(melevdict.keys()),min(melevdict.keys()),max(melevdict.keys()) )
    print( len(wetlanddict.keys()),min(wetlanddict.keys()),max(wetlanddict.keys()) )
    print( len(OWseddep_depth_mm_dict.keys()),min(OWseddep_depth_mm_dict.keys()),max(OWseddep_depth_mm_dict.keys()) )
    print( len(stagedict.keys()),min(stagedict.keys()),max(stagedict.keys()) )
    print( len(pctsanddict.keys()),min(pctsanddict.keys()),max(pctsanddict.keys()) )
    print( len(saldict.keys()),min(saldict.keys()),max(saldict.keys()) )
    print( len(tmpdict.keys()),min(tmpdict.keys()),max(tmpdict.keys()) )
    print( len(pctedgedict.keys()),min(pctedgedict.keys()),max(pctedgedict.keys()) )
    print( len(cultchdict.keys()),min(cultchdict.keys()),max(cultchdict.keys()) )


def calc_depdict(HSI_dir,dep_filename,year,gridIDs,file_cols,dep_ints):
    
    # coded based on the depth tables generated by WM.HSIreclass provide depth in centimeters
    DepthsCSV = os.path.normpath("%s/%sDepths_cm_%s.csv" % (HSI_dir,dep_filename,year))

    Depths = np.genfromtxt(DepthsCSV,delimiter = ',',  skip_header = 1)
    Depdict = {}
    Ddict ={}
    # values to assign to grid cells with no GridID key in depth dictionary
    Dmissing = [0]*dep_ints        

    # convert depths array into dictionary, GridID is key. 
    # only grid cells overlaying geospatial extent in WM.CalculateEcohydroAttributes() will have a key and values
    for n in range(0,len(Depths)):
        gridIDinD = Depths[n,0]
        Ddict[gridIDinD] = Depths[n,1:file_cols]

    # generate dictionary of various depths for all gridID values        
    for gridID in gridIDs:
        try:
            Depdict[gridID] = Ddict[gridID]
        except:
            Depdict[gridID] = Dmissing

    return Depdict


def calc_habitat_coverages(gridID,frattdict,frfltdict,interdict,brackdict,salmardict,swfordict,btfordict):
    v1a = frattdict[gridID]
    v1b = frfltdict[gridID]
    v1c = interdict[gridID]
    v1d = brackdict[gridID]
    v1e = salmardict[gridID]
    v1f = swfordict[gridID]
    v1g = btfordict[gridID]

    # percent land as summarized by veg output, exclude v1g b/c it is the same as v1f
    vegland = v1a + v1b + v1c + v1d + v1e + v1f 

    return (v1a,v1b,v1c,v1d,v1e,v1f,v1g,vegland)


def reclassify_water_area(s,w,vegland):
    # Reclassify water area as marsh type based on salinity value
    # initialize additional marsh areas to zero
    w_fresh = 0.0
    w_inter = 0.0
    w_brack = 0.0
    w_saline = 0.0
    
    # classify water areas based on salinity to add to wetland areas in S1 equation
    # vegetation land may not exactly match percent water due to differences in morph and veg output;
    # therefore, check that percent water + percent land from veg output is not greater than 100.0
    if s < 1.5:
        w_fresh = max(0,min(w,100.0-vegland))
    elif s < 4.5:
        w_inter = max(0,min(w,100.0-vegland))
    elif s < 9.5:
        w_brack = max(0,min(w,100.0-vegland))
    else:
        w_saline = max(0,min(w,100.0-vegland))

    return w_fresh,w_inter,w_brack,w_saline


def depth_intervals(Depdict,gridID,dep_ints):
    area = 0.0
    less0 = 0.0
    v3a = 0.0
    v3b = 0.0
    v3c = 0.0
    v3d = 0.0
    v3e = 0.0
    v3f = 0.0
    v3g = 0.0
    v3h = 0.0
    v3i = 0.0
    v3j = 0.0
    v3k = 0.0
    v3l = 0.0
    deepwat = 0.0

    for x in range(1,dep_ints):
        area = area + Depdict[gridID][x]  #determine area of cell (not exactly equal to 500x500 since the 30x30 m grid doesn't fit in the 500x500
        if area < 480*480:
            area = 480*480
        less0 = Depdict[gridID][0]/area             # portion of cell less than 0 cm deep
        v3a = Depdict[gridID][1]/area               # portion of cell 0-4 cm deep
        v3b = Depdict[gridID][2]/area               # portion of cell 4-8 cm deep
        v3c = Depdict[gridID][3]/area               # portion of cell 8-12 cm deep
        v3d = Depdict[gridID][4]/area               # portion of cell 12-18 cm deep
        v3e = Depdict[gridID][5]/area               # portion of cell 18-22 cm deep
        v3f = Depdict[gridID][6]/area               # portion of cell 22-28 cm deep
        v3g = Depdict[gridID][7]/area               # portion of cell 28-32 cm deep
        v3h = Depdict[gridID][8]/area               # portion of cell 32-36 cm deep
        
        if dep_ints == 13:
            v3i = Depdict[gridID][9]/area           # portion of cell 36-40 cm deep
            v3j = Depdict[gridID][10]/area          # portion of cell 40-44 cm deep
            v3k = Depdict[gridID][11]/area          # portion of cell 44-78 cm deep
            v3l = Depdict[gridID][12]/area          # portion of cell 78-150 cm deep

        if dep_ints == 14:
            deepwat = Depdict[gridID][13]/area      # portion of cell greater than 150 cm deep

    return less0,v3a,v3b,v3c,v3d,v3e,v3f,v3g,v3h,v3i,v3j,v3k,v3l,deepwat


def build_gamm_dict(HSI_dir,gamm_filename):
    # read in GAMM lookup table for sal/temp combinations and build dictionary
    gamm_dict = {}
    gamm_filepath = os.path.normpath('%s/%s' % (HSI_dir,gamm_filename))
    gamm_table_delimiter = '\t' #','
    with open(gamm_filepath) as tf:
        nline = 0
        for line in tf: 
            if nline > 0:
                linesplit = line.split(gamm_table_delimiter)
                s = float(linesplit[0])
                t = float(linesplit[1])
                cpue_sc = float(linesplit[6])
                try:
                    gamm_dict[s][t] = cpue_sc    
                except:
                    gamm_dict[s] = {}            
                    gamm_dict[s][t] = cpue_sc    
            nline +=1 

    return gamm_dict
        

def oyster_years_to_use(OYE_cultch_update_years,elapsedyear): 
    # lookup function to go from elapsed year to decadal cultch map
    # find the corresponding oyster cultch map for elapsed year from list of years with cultch maps (ICM_Settings.py)
    # rounding year down to the previous cultch map
    oyr2use = OYE_cultch_update_years[np.searchsorted(OYE_cultch_update_years,elapsedyear,side='right')-1]

    return oyr2use


def build_cultch_map(OYE_cultch_update_years,elapsedyear,gridIDs,HSI_dir,runprefix):                                    
    # if new decade (or end of spin-up period) build new Cultch map from previous oyster HSI outputs
    # this will be mapped to any given model year using oysters_years_to_use and oyster_cultchdict
    ave_cultch = {}
    # during spin up period (e.g. before second year listed in OYE_cultch_update_years), set cultch to optimal value
    if elapsedyear < OYE_cultch_update_years[1]:
        for n in gridIDs:
            ave_cultch[n] = 1.0
    # after spinup, update cultch by setting equal to the average oyster HSI values since last cultch update was made
    else:
        ey_index = OYE_cultch_update_years.index(elapsedyear)
        years4update = OYE_cultch_update_years[ey_index] - OYE_cultch_update_years[ey_index-1]
        for n in gridIDs:
            ave_cultch[n] = 0.0
        for oyr in range(elapsedyear-years4update,elapsedyear):
            OYSE_filepath = os.path.normpath(r'%s/%s_O_%02d_%02d_X_OYSTE.csv'% (HSI_dir,runprefix,oyr,oyr))
            oyr_OYSE = np.genfromtxt(OYSE_filepath,delimiter=',',skip_header=1,dtype='str')
            for row in oyr_OYSE:
                gr = int(row[0])
                oHSI = float(row[1])
                # after looping over all years4update, each grid cell's value will be the average cultch
                ave_cultch[gr] += oHSI/years4update
        
    file2write = os.path.normpath(r'%s/OysterCultch_%02d.csv'% (HSI_dir,elapsedyear))
    
    with open(file2write,mode='w') as fo:
        fo.write('GRID_ID,REEF_PCT,SEED_PCT,CULTCH_PCT,LEASE_PCT,PCT_CULTCH\n')
        for n in gridIDs:
            # cultch file is in integers and we only need the last column populated with the average HSI
            # all other columns are filled with 0
            fo.write('%d,0,0,0,0,%d\n' % (n,100.*ave_cultch[n]) ) 


def oyster_cultchdict(HSI_dir,oyr2use):
    # generate cultch surface from pre-existing Cultch map file written every 10 years
    # cultchdict is written every year
    cultch_file = os.path.normpath(r'%s/OysterCultch_%02d.csv'% (HSI_dir,oyr2use))
    cultchdict = {}
    cnp = np.genfromtxt(cultch_file,skip_header=True,usecols=(0,5),delimiter=',')
    for row in cnp:
        gid = int(row[0])
        # cultch is used as a ratio from 0-1.0 so divide by 100 here to convert from percent to ratio
        cultchdict[gid] = row[1]/100.0      

    return cultchdict


def calc_avg_elev_grid(gridIDs,waterdict,bedelevdict,landdict,melevdict):
    # calculate average elevation for grid cell from values for marsh elev and bed elev imported separately
    grid_elv_ave = {}
    for n in gridIDs:
        use_water = 0
        use_land = 0
        if waterdict[n] > 0:
            if bedelevdict != -9999:
                # have values for both percent water and bed elevation
                use_water = 1
        if landdict[n] > 0:
            if bedelevdict != -9999:
                # have values for both percent land and marsh elevation
                use_land = 1
        if use_water == 1:
            # have both land and water data - calculate weighted mean elevation
            if use_land == 1:
                grid_elv_ave[n] = ( bedelevdict[n]*waterdict[n] + melevdict[n]*landdict[n] ) / ( waterdict[n] + landdict[n] )
            else: 
                # have only water data              
                grid_elv_ave[n] = bedelevdict[n]
        elif use_land == 1:
                # have only land data 
                grid_elv_ave[n] = melevdict[n]
        else:
            # do not have land or water data
            grid_elv_ave[n] = -9999

    return grid_elv_ave


def calc_OWseddep(OWseddep_depth_mm_dict,n500grid):
    ow_seddep_grid = dict((n,OWseddep_depth_mm_dict[n][1]) for n in range(1,n500grid+1))
        
    return ow_seddep_grid

def calc_OWseddep_monthly(OWseddep_depth_mm_dict):
    subset = [1,2,3,4,5,6,7,8,9,10,11,12]
    OWseddep_monthly = monthly_avg_dict(OWseddep_depth_mm_dict,subset)

    return OWseddep_monthly


def prepare_lavegmod_output(n500rows,nvegtype,n500grid,veg_output_filepath):
    # skipvalue is the number of rows contained in the header and the grid array located at the start of the Veg output file
    skipvalue = n500rows + 7
    # veg columns is the number of vegetation types (including flotant/dead flt/bare flt) plus CellID, Water, NotMod, 
    # BareGround (old and new), FFIBS score, and percent vegetation type summary values
    vegcolumns = nvegtype + 12   
    # generate zeros array that will be filled with Veg results
    new_veg = np.zeros((n500grid,vegcolumns))
    veg_missing = 0
    # open Vegetation output file
    with open(veg_output_filepath,'r') as vegfile:
        # skip ASCII header rows and ASCII grid at start of output file
        for n in range(0,skipvalue-1):
            #TODO check, this file dump is never used
            dump=vegfile.readline()
        # read in header of Vegetation output at bottom of ASCII grid    
        vegtypenames = vegfile.readline().split(',')
        # remove any leading or trailing spaces in veg types
        for n in range(0,len(vegtypenames)):
            vegtypenames[n] = vegtypenames[n].lstrip().rstrip()
        # loop through rest of Vegetation file         
        for nn in range(0,n500grid):
            # split each line of file based on comma delimiter (any spaces will be removed with rstrip,lstrip)
            vline = vegfile.readline().split(",")
            # if all columns have data in output file, assign veg output to veg_ratios array
            if (len(vline) == vegcolumns):
                for nnn in range(0,len(vline)):
                    new_veg[nn,nnn]=float(vline[nnn].lstrip().rstrip())
            # if there are missing columns in line, set first column equal to grid cell, and set all other columns equal to 0.
            else:
                for nnn in range(1,vegcolumns):
                    new_veg[nn,0]=nn+1
                    new_veg[nn,nnn] = 0.0
                veg_missing += 1
    if (veg_missing > 0):
        print( ' Some Vegetation output was not written correctly to Veg output file.')
        print('  - %s 500m grid cells did not have complete results in Veg Output file.' % veg_missing)

    return vegtypenames,new_veg


def landwater_calculation(landdict,waterdict,gridID):
    # use landdict to assign portion of cell that is water. this value is the updated land/water ratio AFTER the Morph run
    # the 'WATER' value from Veg output is not needed here
    # landdict is bare land, vegetated land, and upland - it does not include water or floating marsh
    # check that percent land is Data (-9999 if NoData), if NoData, set water area to zero
    try:
        if landdict[gridID] >= 0:
            waterdict[gridID] = 100 - landdict[gridID]
        else:
            waterdict[gridID] = 0
    except:
        waterdict[gridID] = 0

    return waterdict


def reclass_lavegmod(landwater_calc,sav_asc_file,grid_ascii_file,new_veg,vegtypenames,gridIDs,landdict,waterdict):
    # generate some blank dictionaries that will be filled with Veg output
    wetlndict = {}
    frattdict = {}
    frfltdict = {}
    interdict = {}
    brackdict = {}
    salmardict = {}
    swfordict = {}
    btfordict = {}
    baldcypdict = {}
    blackmangrovedict = {}
    marshelderdict = {}
    baredict = {}
    bare_mult = {}
    fresh_for_mult = {}
    land_mult = {}
    uplanddict = {}
    watsavdict = {}

    sav_in = np.genfromtxt(sav_asc_file,skip_header=6,delimiter=' ',dtype='str')
    grid_in = np.genfromtxt(grid_ascii_file,skip_header=6,delimiter=' ',dtype='str')
    
    nl = 0

    for line in grid_in:
        nc = 0
        for nc in range(0,len(grid_in[nl])):
            gridID = int(grid_in[nl][nc])
            watsavdict[gridID] = float(sav_in[nl][nc])
            nc += 1
        nl += 1  
                
    # determine portion of cell that is covered by water, land, and different wetland types
    for n in range(0,len(new_veg)):
        gridID = int(new_veg[n][0])
        
        if landwater_calc:
            waterdict = landwater_calculation(landdict,waterdict,gridID)
            
        pland = landdict[gridID]/100.0
        
        # pland is the percentage of the grid cell that is land (as calculated by ICM-Morph)
        # The pL_XX values included in the ICM-LAVegMod output files are the 'portion of land that is habitat type X'
        # These pL_XX values in ICM-LAVegMod are the respective portion of VEGETATED LAND covered by habitat type 
        # So water, NotMod, and Bareground are excluded from pL_XX calculations
        btfordict[gridID] = pland*new_veg[n][vegtypenames.index('pL_BF')]  # Bottomland Hardwood Forest
        swfordict[gridID] = pland*new_veg[n][vegtypenames.index('pL_SF')]  # Bottomland Hardwood Forest
        frattdict[gridID] = pland*new_veg[n][vegtypenames.index('pL_FM')]  # Fresh Herbaceous Marsh
        interdict[gridID] = pland*new_veg[n][vegtypenames.index('pL_IM')]  # Intermediate Herbaceous marsh
        brackdict[gridID] = pland*new_veg[n][vegtypenames.index('pL_BM')]  # Brackish Herbaceous Marsh
        salmardict[gridID] = pland*new_veg[n][vegtypenames.index('pL_SM')] # Saline Herbaceous Marsh                
        
        # Species-specific outputs from ICM-LAVegMod are reported out as percentage of grid cell that
        # No need to multiply by pland
        baldcypdict[gridID] = new_veg[n][vegtypenames.index('TADI2')] 
        blackmangrovedict[gridID] = new_veg[n][vegtypenames.index('AVGE')]
        marshelderdict[gridID] = new_veg[n][vegtypenames.index('IVFR')]
        # Live floating marsh LULC           
        frfltdict[gridID] = new_veg[n][vegtypenames.index('ELBA2_Flt')] + new_veg[n][vegtypenames.index('PAHE2_Flt')]
        # Bareground (including bare flotant)
        baredict[gridID] = new_veg[n][vegtypenames.index('BAREGRND_Flt')] + new_veg[n][vegtypenames.index('BAREGRND_OLD')] + new_veg[n][vegtypenames.index('BAREGRND_NEW')]
        # Marsh Wetland (all types, including flotant)
        wetlndict[gridID] = 1.0 - ( baredict[gridID] + new_veg[n][vegtypenames.index('WATER')] + new_veg[n][vegtypenames.index('NOTMOD')] )
        # upland/developed (classified as NOTMOD in LAVegMod)
        uplanddict[gridID] = new_veg[n][vegtypenames.index('NOTMOD')]                 
        # set land multiplier to zero for grid cells that are 100% land
        if waterdict[gridID] == 0.0:
            land_mult[gridID] = 0.0
        else:
            land_mult[gridID] = 1.0
        
        # Check for bareground - if there is no wetland or forest type, but there is bareground, set bareground multiplier to zero
        bare_mult[gridID] = 1.0
        if baredict[gridID] > 0.0:
            if wetlndict[gridID] == 0.0:
                if btfordict[gridID] == 0.0:
                    if watsavdict[gridID] == 0.0:
                        bare_mult[gridID] = 0.0
            # if there is wetland area, and it is greater than forested area, add bareground to wetland area
            elif wetlndict[gridID] > btfordict[gridID]:
                wetlndict[gridID] += baredict[gridID]
            # if forest is greater than wetland area, add bareground to foreseted areas (both swamp forest and bottom hardwood - since they are set equal)
            else:
                btfordict[gridID] += baredict[gridID]
                swfordict[gridID] += baredict[gridID]

        # if fresh forest is present and greater than wetland area, set fresh forest multiplier to zero
        fresh_for_mult[gridID] = 1.0
        if btfordict[gridID] > 0.0:
            
            if btfordict[gridID] > wetlndict[gridID]:
                fresh_for_mult[gridID] = 0.0


    # convert marsh/land type dictionaries from portion (0-1) to percentage (0-100)
    for gridID in gridIDs:
        wetlndict[gridID]   =  max(0.0,min(100.0,100.0*wetlndict[gridID]))
        btfordict[gridID]   =  max(0.0,min(100.0,100.0*btfordict[gridID]))
        swfordict[gridID]   =  max(0.0,min(100.0,100.0*swfordict[gridID]))
        frattdict[gridID]   =  max(0.0,min(100.0,100.0*frattdict[gridID]))
        interdict[gridID]   =  max(0.0,min(100.0,100.0*interdict[gridID]))
        brackdict[gridID]   =  max(0.0,min(100.0,100.0*brackdict[gridID]))
        salmardict[gridID]  =  max(0.0,min(100.0,100.0*salmardict[gridID]))
        watsavdict[gridID]  =  max(0.0,min(100.0,100.0*watsavdict[gridID]))
        frfltdict[gridID]   =  max(0.0,min(100.0,100.0*frfltdict[gridID]))
        baldcypdict[gridID] =  max(0.0,min(100.0,100.0*baldcypdict[gridID]))

    return     wetlndict,frattdict,frfltdict,interdict,brackdict,salmardict,swfordict,\
        btfordict,baldcypdict,blackmangrovedict,marshelderdict, \
            baredict,bare_mult,fresh_for_mult,land_mult,uplanddict,watsavdict


#########################################################################################################
####                                                                                                 ####
####                           LEGACY HSI FUNCTIONS FROM 2023                                        ####
####                                                                                                 ####
#########################################################################################################

def build_dictionaries_2023(gridIDs):
    # build empty dictionaries that will be filled with monthly average values
    # key will be grid ID
    # value will be an array of 12 monthly values
    saldict_2023 = {}
    tmpdict_2023 = {}
    stgmndict_2023 = {}
    
    for n in gridIDs:
        saldict_2023[n] = []
        tmpdict_2023[n] = []
        stgmndict_2023[n] = []
    
    return saldict_2023, tmpdict_2023, stgmndict_2023


def monthly_mean_salinity_2023(saldict_2023,ecohydro_dir,runprefix,endyear,startyear,ndays_run, data_start,ave_end,ave_start,grid_comp):
    ##############
    # Salinity   
    ##############
    # read in daily salinity and calculate monthly mean for compartment then map to grid using daily2ave and comp2grid functions
    daily_timeseries_file = os.path.normpath(r'%s/SAL.out' % ecohydro_dir)
    if os.path.exists(daily_timeseries_file) == False:
        daily_timeseries_file = os.path.normpath(r'%s/%s_O_01_%02d_H_SAL.out' % (ecohydro_dir,runprefix,endyear-startyear+1) )
    comp_month_ave_dict = daily2ave(data_start,ave_start,ave_end,daily_timeseries_file,ndays_run)
    mon_ave = comp2grid(comp_month_ave_dict,grid_comp)
    # loop through monthly average and append to array of monthly averages in dictionary to be passed into HSI.py
    for n in grid_comp.keys():
        saldict_2023[n].append(round(mon_ave[n],1)) # this will save monthly mean to the tenths decimal #.# precision

    return saldict_2023


def monthly_mean_temp_2023(tmpdict_2023,ecohydro_dir,runprefix,endyear,startyear,ndays_run, data_start,ave_end,ave_start,grid_comp):
    ##############
    # Temperature 
    ##############
    # read in daily temperature and calculate monthly mean for compartment then map to grid using daily2ave and comp2grid functions
    daily_timeseries_file = os.path.normpath(r'%s/TMP.out' % ecohydro_dir)
    if os.path.exists(daily_timeseries_file) == False:
        daily_timeseries_file = os.path.normpath(r'%s/%s_O_01_%02d_H_TMP.out' % (ecohydro_dir,runprefix,endyear-startyear+1) )
    comp_month_ave_dict = daily2ave(data_start,ave_start,ave_end,daily_timeseries_file,ndays_run)
    mon_ave = comp2grid(comp_month_ave_dict,grid_comp)
    # loop through monthly average and append to array of monthly averages in dictionary to be passed into HSI.py
    for n in grid_comp.keys():
        tmpdict_2023[n].append(round(mon_ave[n],1)) # this will save monthly mean to the tenths decimal #.# precision

    return tmpdict_2023


def monthly_mean_stage_2023(stgmndict_2023,ecohydro_dir,runprefix,endyear,startyear,ndays_run, data_start,ave_end,ave_start,grid_comp):        
    ##############
    # Monthly Stage 
    ##############
    # read in daily temperature and calculate monthly mean for compartment then map to grid using daily2ave and comp2grid functions
    daily_timeseries_file = os.path.normpath(r'%s/STG.out' % ecohydro_dir)
    if os.path.exists(daily_timeseries_file) == False:
        daily_timeseries_file = os.path.normpath(r'%s/%s_O_01_%02d_H_STG.out' % (ecohydro_dir,runprefix,endyear-startyear+1) )
    comp_month_ave_dict = daily2ave(data_start,ave_start,ave_end,daily_timeseries_file,ndays_run)
    mon_ave = comp2grid(comp_month_ave_dict,grid_comp)
    # loop through monthly average and append to array of monthly averages in dictionary to be passed into HSI.py
    for n in grid_comp.keys():
        stgmndict_2023[n].append(mon_ave[n])

    return stgmndict_2023

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




    