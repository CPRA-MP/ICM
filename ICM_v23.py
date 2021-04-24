import os
import platform
import sys
import shutil
import math
import time
import errno
import random
import subprocess
import datetime as dt
import numpy as np
import xlrd
import pandas
    

def daily2ave(all_sd,ave_sd,ave_ed,input_file):
    # this function reads a portion of the ICM-Hydro daily timeseries file into a numpy array and then computes the average for the time slice read in
    # this function returns a dictionary 'comp_ave' that has ICM-Hydro compartment ID as the key and a temporal average for each compartment as the value
    # the key is of type integer and the values are of type float

    # if looping through the whole file and batch generating averages for a bunch of timeslices it will be faster to read in the whole file to a numpy array and iterating over the whole array rather than iteratively calling this function

    # 'all_sd' is the start date of all data included in the daily timeseries file - all_sd is a datetime.date object
    # 'ave_sd' is the start date of averaging window, inclusive - ave_sd is a datetime.date object
    # 'ave_ed' is the end date of averaging window, inclusive - ave_ed is a datetime.date object

    all_rows = file_len(input_file)
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

def dict2asc_flt(mapping_dict,outfile,asc_grid,asc_header,write_mode):
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

def file_len(fname):
    # this function counts the number of lines in a text file
    # this function returns an integer value that is the number of lines in the file 'fname'

    # 'fname' is a string variable that contains the full path to a text file with an unknown number of lines

    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

proj_dir = os.getcwd()
vegetation_dir = os.path.normpath(r'%s/veg' % proj_dir)
hydro_dir = os.path.normpath(r'%s/hydro' % proj_dir)
morph_dir = os.path.normpath(r'%s/geomorph' % proj_dir)

VegConfigFile = os.path.normpath('%s/lavegmod_proto.config' % vegetation_dir)
asc_grid_file = os.path.normpath(r'%s/veg_grid.asc' % vegetation_dir)
pwatr_grid_file = os.path.normpath(r'%s/MP2023_S06_G501_C000_U00_V00_SLA_N_01_01_H_pwatr.asc' % vegetation_dir)
acute_sal_grid_file = os.path.normpath(r'%s/MP2023_S06_G501_C000_U00_V00_SLA_N_01_01_H_acsal.asc' % vegetation_dir)

startyear = 2019
endyear = 2019
hotstart_year = 2019
elapsed_hotstart = hotstart_year - startyear

ncomp = 1778

# read in asci grid structure
asc_grid_ids = np.genfromtxt(asc_grid_file,skip_header=6,delimiter=' ',dtype='int')

# read in compartment-to-grid structure
grid_lookup_file = '%s/grid_lookup_500m.csv' % hydro_dir
grid_comp_np = np.genfromtxt(grid_lookup_file,delimiter=',',skip_header=1,usecols=[0,1],dtype='int')
grid_comp_dict = {rows[0]:rows[1] for rows in grid_comp_np}
del(grid_comp_np)


for year in range(startyear+elapsed_hotstart,endyear+1):
    print ('\n--------------------------------------------------')
    print ('  START OF MODEL TIMESTEPPING LOOP - YEAR %s' % year)
    print ('--------------------------------------------------\n')

    elapsedyear = year - startyear + 1
    runprefix = r'MP2023_S06_G501_C000_U00_V00_SLA'
    file_prefix = r'%s_N_%02d_%02d' % (runprefix,elapsedyear,elapsedyear)
    file_oprefix = r'%s_O_%02d_%02d' % (runprefix,elapsedyear,elapsedyear)
    file_o_01_50_prefix = r'%s_O_01_01' % (runprefix)
    file_prefix_prv = r'%s_N_%02d_%02d' % (runprefix,elapsedyear-1,elapsedyear-1)

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



    ########################################################
    ##  Format ICM-Hydro output data for use in ICM-Morph ##
    ########################################################
    
    # read in monthly water level data
    print(' - calculating mean and max monthly water levels')
    stg_mon = {}
    stg_mon_mx = {}
    stg_ts_file = r'%s/STG.out' % hydro_dir
    for mon in range(1,13):
        print('     - month: %02d' % mon)
        data_start = dt.date(startyear,1,1)             # start date of all data included in the daily timeseries file (YYYY,M,D)
        ave_start = dt.date(year,mon,1)                 # start date of averaging window, inclusive (YYYY,M,D)
        ave_end = dt.date(year,mon,dom[mon])            # end date of averaging window, inclusive (YYYY,M,D)
        stg_mon[mon] = daily2ave(data_start,ave_start,ave_end,stg_ts_file)
        stg_mon_mx[mon] = daily2max(data_start,ave_start,ave_end,stg_ts_file)

    # write monthly mean water level file for use in ICM-Morph
    monthly_file_avstg = r'hydro/TempFiles/compartment_monthly_mean_stage_%4d.csv' % year
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
    monthly_file_mxstg = r'hydro/TempFiles/compartment_monthly_max_stage_%4d.csv' % year
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
    sal_ts_file = r'%s/SAL.out' % hydro_dir
    for mon in range(1,13):
        print('     - month: %02d' % mon)
        data_start = dt.date(startyear,1,1)             # start date of all data included in the daily timeseries file (YYYY,M,D)
        ave_start = dt.date(year,mon,1)                 # start date of averaging window, inclusive (YYYY,M,D)
        ave_end = dt.date(year,mon,dom[mon])            # end date of averaging window, inclusive (YYYY,M,D)
        sal_mon[mon] = daily2ave(data_start,ave_start,ave_end,sal_ts_file)
    
    # write monthly mean salinity file for use in ICM-Morph
    monthly_file_avsal = r'hydro/TempFiles/compartment_monthly_mean_salinity_%4d.csv' % year
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
    tss_ts_file = r'%s/TSS.out' % hydro_dir
    for mon in range(1,13):
        print('     - month: %02d' % mon)
        data_start = dt.date(startyear,1,1)             # start date of all data included in the daily timeseries file (YYYY,M,D)
        ave_start = dt.date(year,mon,1)                 # start date of averaging window, inclusive (YYYY,M,D)
        ave_end = dt.date(year,mon,dom[mon])            # end date of averaging window, inclusive (YYYY,M,D)
        tss_mon[mon] = daily2ave(data_start,ave_start,ave_end,tss_ts_file)

    # write monthly mean TSS file for use in ICM-Morph
    monthly_file_avtss = r'hydro/TempFiles/compartment_monthly_mean_tss_%4d.csv' % year
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

    # read in average sediment deposition data
    print(' - formatting sedimentation output for ICM-Morph')
    sed_ow = {}
    sed_mi = {}
    sed_me = {}
    comp_out_file = r'%s/TempFiles/compartment_out_%4d.csv' % (hydro_dir,year)
    comp_out = np.genfromtxt(comp_out_file,delimiter=',',dtype='str',skip_header=1)
    for mon in range(1,13):
        sed_ow[mon] = {}
        sed_mi[mon] = {}
        sed_me[mon] = {}
        for row in comp_out:
            comp = int(float(row[0]))
            sed_ow[mon][comp] = float(row[10])/12.         # reading in annual sediment loading - divide by twelve to convert to average monthly for now
            sed_mi[mon][comp] = float(row[11])/12.         # reading in annual sediment loading - divide by twelve to convert to average monthly for now
            sed_me[mon][comp] = float(row[12])/12.         # reading in annual sediment loading - divide by twelve to convert to average monthly for now

    # write monthly sediment deposition in open water file for use in ICM-Morph
    monthly_file_sdowt = r'hydro/TempFiles/compartment_monthly_sed_dep_wat_%4d.csv' % year
    with open(monthly_file_sdowt,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,sed_dp_ow_%02d' % (wrt_hdr,mon)
        mon_file.write('%s\n' % wrt_hdr)
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                wrt_string = '%s,%s' % (wrt_string,sed_ow[mon][comp])
            mon_file.write('%s\n'% wrt_string)

    # write monthly sediment deposition in marsh interior file for use in ICM-Morph
    monthly_file_sdint = r'hydro/TempFiles/compartment_monthly_sed_dep_interior_%4d.csv' % year
    with open(monthly_file_sdint,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,sed_dp_int_%02d' % (wrt_hdr,mon)
        mon_file.write('%s\n' % wrt_hdr)
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                wrt_string = '%s,%s' % (wrt_string,sed_mi[mon][comp])
            mon_file.write('%s\n'% wrt_string)

    # write monthly sediment deposition in marsh edge zone file for use in ICM-Morph
    monthly_file_sdedg = r'hydro/TempFiles/compartment_monthly_sed_dep_edge_%4d.csv' % year
    with open(monthly_file_sdedg,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,sed_dp_edge_%02d' % (wrt_hdr,mon)
        mon_file.write('%s\n' % wrt_hdr)
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                wrt_string = '%s,%s' % (wrt_string,sed_me[mon][comp])
            mon_file.write('%s\n'% wrt_string)


    ###########################################################
    ##  Format ICM-Hydro output data for use in ICM-LAVegMod ##
    ###########################################################

    asc_grid_head = 'ncols 1052\nnrows 365\nxllcorner 404710\nyllcorner 3199480\ncellsize 480\nNODATA_value -9999\n'
    asc_head = '# Year = %04d\n%s' % (year,asc_grid_head)
    if year == startyear:
        filemode = 'w'
    else:
        filemode = 'a'

    print('   - updating percent water grid file for ICM-LAVegMod')
    pwatr_dict = {}
    gd_file = os.path.normpath(r'%s/TempFiles/grid_data_500m_%04d.csv' % (hydro_dir,year-1))
    with open(gd_file,mode='r') as grid_data:
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
    print(dict2asc_flt(salmx_grid,acute_sal_grid_file,asc_grid_ids,asc_head,write_mode=filemode) )



    bidem_xyz_file = r'bidem/MP2023_S04_G031_C000_U00_V00_SLA_I_00_00_W_2017dem30_bi.xyz'







    
    
    
    
    #Barrier Island Tidal Inlet (BITI) Model (to be added to the ICM py code)

    # FROM 2017 ICM-Py:
    # create dictionary where key is compartment ID, value is tidal prism (Column 14 of Ecohydro output)
    # EH_prisms = dict((EH_comp_out[n][0],EH_comp_out[n][13]) for n in range(0,len(EH_comp_out)))
    ########### EH_comp_out is a numpy array #############
    
    #Barrier Island Tidal Inlet (BITI) input file
    #The input file only needs to be read once
    #It contains the comp IDs, link IDs, depth to width ratios, partition coefficients, and basin-wide factors.
    BITI_input_filename = r'[Add path here]\BITI_setup_input.xlsx'
    BITI_Terrebonne_setup = pandas.read_excel(BITI_input_filename, 'Terrebonne',index_col=None)
    BITI_Barataria_setup = pandas.read_excel(BITI_input_filename, 'Barataria',index_col=None)
    BITI_Pontchartrain_setup = pandas.read_excel(BITI_input_filename, 'Pontchartrain',index_col=None)
    
    #Barrier Island Tidal Inlet (BITI) compartment IDs
    #These are the compartments that make up each basin
    BITI_Terrebonne_comp = list( BITI_Terrebonne_setup.iloc[3::,0] )
    BITI_Barataria_comp = list( BITI_Barataria_setup.iloc[3::,0] )
    BITI_Pontchartrain_comp = list( BITI_Pontchartrain_setup.iloc[3::,0] )
    
    #Barrier Island Tidal Inlet (BITI) link IDs
    #These are the links that respresent the tidal inlets in each basin
    BITI_Terrebonne_link = list(BITI_Terrebonne_setup.iloc[0,1:-2])
    BITI_Barataria_link = list(BITI_Barataria_setup.iloc[0,1:-2])
    BITI_Pontchartrain_link = list(BITI_Pontchartrain_setup.iloc[0,1:-2])
    
    BITI_Links = [BITI_Terrebonne_link,BITI_Barataria_link,BITI_Pontchartrain_link]
    
    #Barrier Island Tidal Inlet (BITI) partition coefficients
    #Each basin has it's own array of partition coefficients with size m by n,
    #where m = number of compartments in the basin and n = the number of links in the basin
    BITI_Terrebonne_partition = np.asarray(BITI_Terrebonne_setup)[3::,1:-2]
    BITI_Barataria_partition = np.asarray(BITI_Barataria_setup)[3::,1:-2]
    BITI_Pontchartrain_partition = np.asarray(BITI_Pontchartrain_setup)[3::,1:-2]
    
    #Barrier Island Tidal Inlet (BITI) depth to width ratio (dwr) for each link in each basin (Depth/Width)
    BITI_Terrebonne_dwr = list(BITI_Terrebonne_setup.iloc[1,1:-2])
    BITI_Barataria_dwr = list(BITI_Barataria_setup.iloc[1,1:-2])
    BITI_Pontchartrain_dwr = list(BITI_Pontchartrain_setup.iloc[1,1:-2])
    
    #Barrier Island Tidal Inlet (BITI) basin-wide factor (BWF) for each basin
    BITI_Terrebonne_BWF = float(BITI_Terrebonne_setup.iloc[1,-1])
    BITI_Barataria_BWF = float(BITI_Barataria_setup.iloc[1,-1])
    BITI_Pontchartrain_BWF = float(BITI_Pontchartrain_setup.iloc[1,-1])
    
    #Barrier Island Tidal Inlet (BITI) tidal prism values
    #Get the tidal prism values for each compartment from the Hydro output
    BITI_Terrebonne_prism = [EH_prisms.get(comp) for comp in BITI_Terrebonne_comp]
    BITI_Barataria_prism = [EH_prisms.get(comp) for comp in BITI_Barataria_comp]
    BITI_Pontchartrain_prism = [EH_prisms.get(comp) for comp in BITI_Pontchartrain_comp]
    
    #BITI effective tidal prism and inlet area
    #kappa and alpha are the Gulf of Mexico constants for unjettied systems (units = metric)
    kappa = 6.99e-4
    alpha = 0.86
    
    #Calculate the effective tidal prism and cross-sectional area for each link in each basin
    #effective tidal prism = sum(tidal prism * partitioning coefficient) [summed across all compartments in the basin]
    #cross-sectional area = kappa *((effective tidal prism)^alpha)
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
    
    #BITI depth for each link in each basin
    #Depth = sqrt(inlet area*(depth to width ratio))
    BITI_Terrebonne_inlet_depth = np.power(np.multiply(BITI_Terrebonne_inlet_area,BITI_Terrebonne_dwr),0.5)
    BITI_Barataria_inlet_depth = np.power(np.multiply(BITI_Barataria_inlet_area,BITI_Barataria_dwr),0.5)
    BITI_Pontchartrain_inlet_depth = np.power(np.multiply(BITI_Pontchartrain_inlet_area,BITI_Pontchartrain_dwr),0.5)
    
    BITI_inlet_depth = [BITI_Terrebonne_inlet_depth,BITI_Barataria_inlet_depth,BITI_Pontchartrain_inlet_depth]
    
    #BITI width for each link in each basin
    #Width = sqrt(inlet area/(depth to width ratio))
    BITI_Terrebonne_inlet_width = np.power(np.divide(BITI_Terrebonne_inlet_area,BITI_Terrebonne_dwr),0.5)
    BITI_Barataria_inlet_width = np.power(np.divide(BITI_Barataria_inlet_area,BITI_Barataria_dwr),0.5)
    BITI_Pontchartrain_inlet_width = np.power(np.divide(BITI_Pontchartrain_inlet_area,BITI_Pontchartrain_dwr),0.5)
    
    BITI_inlet_width = [BITI_Terrebonne_inlet_width,BITI_Barataria_inlet_width,BITI_Pontchartrain_inlet_width]
    
    #BITI dimensions
    #Create a dictionary where key is link ID, first value is inlet depth, second value is inlet width
    #This dictionary can be used to update the link attributes. All inlet links are Type 1 links.
    BITI_inlet_dimensions = {}
    for n in range(0,len(BITI_Links)):
        for k in range(0,len(BITI_Links[n])):
            BITI_inlet_dimensions[BITI_Links[n][k]] = ([BITI_inlet_depth[n][k],BITI_inlet_width[n][k]])
    





    #########################################################
    ##                RUN VEGETATION MODEL                 ##
    #########################################################

    os.chdir(vegetation_dir)

    if elapsed_hotstart == 0:
        if year == startyear + elapsed_hotstart:
            print ('\n--------------------------------------------------')
            print ('        CONFIGURING VEGETATION MODEL')
            print ('      - only during initial year of ICM -')
            print ('----------------------------------------------------')

            sys.path.append(vegetation_dir)

            import model_v3
#
            LAVegMod = model_v3.Model()
#
#            try:
            veg_config = LAVegMod.config(VegConfigFile)
#            except Exception as err:
#                print('******ERROR******' )
#                print(err)
#                sys.exit('\nFailed to initialize Veg model.')

    print('\n--------------------------------------------------')
    print('  RUNNING VEGETATION MODEL - Year %s' % year)
    print('--------------------------------------------------\n')


    #try:
    veg_run = LAVegMod.step()
    #except Exception as err:
    #    print ('\n ******ERROR******')
    #    print(err)
    #    sys.exit('Vegetation model run failed - Year %s.' % year)



    #########################################################
    ##                   RUN MORPH MODEL                   ##
    #########################################################
    os.chdir(proj_dir)

    # read in Wetland Morph input file and update variables for year of simulation
    wm_param_file = r'%s/input_params.csv' % morph_dir

    with open (wm_param_file, mode='w') as ip_csv:
        ip_csv.write("%d, start_year -  first year of model run\n" % startyear)
        ip_csv.write("%d, elapsed_year -  elapsed year of model run\n" % elapsedyear)
        ip_csv.write("30, dem_res -  XY resolution of DEM (meters)\n")
        ip_csv.write("-9999, dem_NoDataVal -  value representing nodata in input rasters and XYZ files\n")
        ip_csv.write("170852857, ndem -  number of DEM pixels - will be an array dimension for all DEM-level data\n")
        ip_csv.write("1142332, ndem_bi -  number of pixels in interpolated ICM-BI-DEM XYZ that overlap primary DEM\n")
        ip_csv.write("946, ncomp -  number of ICM-Hydro compartments - will be an array dimension for all compartment-level data\n")
        ip_csv.write("187553, ngrid -  number of ICM-LAVegMod grid cells - will be an array dimension for all gridd-level data\n")
        ip_csv.write("32, neco -  number of ecoregions\n")
        ip_csv.write("5, nlt -  number of landtype classifications\n")
        ip_csv.write("0.10, ht_above_mwl_est -  elevation (meters) relative to annual mean water level at which point vegetation can establish\n")
        ip_csv.write("2.57, ptile_Z -  Z-value for quantile definining inundation curve\n")
        ip_csv.write("0.0058, B0 -  beta-0 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
        ip_csv.write("-0.00207, B1 -  beta-1 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
        ip_csv.write("0.0809, B2 -  beta-2 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
        ip_csv.write("0.0892, B3 -  beta-3 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
        ip_csv.write("-0.19, B4 -  beta-4 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
        ip_csv.write("0.835, ow_bd -  bulk density of water bottoms (g/cm3)\n")
        ip_csv.write("0.076, om_k1  -  organic matter self-packing density (g/cm3) from CRMS soil data (see 2023 Wetlands Model Improvement report)\n")
        ip_csv.write("2.106, mn_k2 -  mineral soil self-packing density (g/cm3) from CRMS soil data (see 2023 Wetlands Model Improvement report)\n")
        ip_csv.write("0, FIBS_intvals(1)  -  FFIBS score that will serve as lower end for Fresh forested\n")
        ip_csv.write("0.15, FIBS_intvals(2)  -  FFIBS score that will serve as lower end for Fresh marsh\n")
        ip_csv.write("1.5, FIBS_intvals(3)  -  FFIBS score that will serve as lower end for Intermediate marsh\n")
        ip_csv.write("5, FIBS_intvals(4)  -  FFIBS score that will serve as lower end for Brackish marsh\n")
        ip_csv.write("18, FIBS_intvals(5)  -  FFIBS score that will serve as lower end for Saline marsh\n")
        ip_csv.write("24, FIBS_intvals(6)  -  FFIBS score that will serve as upper end for Saline marsh\n")
        ip_csv.write("10, min_accretion_limit_cm -  upper limit to allowable mineral accretion on the marsh surface during any given year [cm]\n")
        ip_csv.write("50, ow_accretion_limit_cm -  upper limit to allowable accretion on the water bottom during any given year [cm]\n")
        ip_csv.write("-50, ow_erosion_limit_cm -  upper limit to allowable erosion of the water bottom during any given year [cm]\n")
        ip_csv.write("0.05, bg_lowerZ_m -  height that bareground is lowered [m]\n")
        ip_csv.write("0.25, me_lowerDepth_m -  depth to which eroded marsh edge is lowered to [m]\n")
        ip_csv.write("1.0, flt_lowerDepth_m -  depth to which dead floating marsh is lowered to [m]\n")
        ip_csv.write("-0.762, mc_depth_threshold - water depth threshold (meters) defining deep water area to be excluded from marsh creation projects footprint\n")
        ip_csv.write("1.1211425, spsal_params[1], SAV parameter - spring salinity parameter 1\n")
        ip_csv.write("-0.7870841, spsal_params[2], SAV parameter - spring salinity parameter 2\n")
        ip_csv.write("1.5059876, spsal_params[3], SAV parameter - spring salinity parameter 3\n")
        ip_csv.write("3.4309696, sptss_params_params[1], SAV parameter - spring TSS parameter 1\n")
        ip_csv.write("-0.8343315, sptss_params_params_params[2], SAV parameter - TSS salinity parameter 2\n")
        ip_csv.write("0.9781167, sptss_params[3], SAV parameter - spring TSS parameter 3\n")
        ip_csv.write("5.934377, dfl_params[1], SAV parameter - distance from land parameter 1\n")
        ip_csv.write("-1.957326, dfl_params[2], SAV parameter - distance from land parameter 2\n")
        ip_csv.write("1.258214, dfl_params[3], SAV parameter - distance from land parameter 3\n")

        if year == startyear:
            ip_csv.write("0,binary_in - read input raster datas from binary files (1) or from ASCI XYZ files (0)\n")
        else:
            ip_csv.write("1,binary_in - read input raster datas from binary files (1) or from ASCI XYZ files (0)\n")

        ip_csv.write("1,binary_out - write raster datas to binary format only (1) or to ASCI XYZ files (0)\n")

        if year == startyear:
            ip_csv.write("'geomorph/input/MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_W_2017dem30.xyz', dem_file -  file name with relative path to DEM XYZ file\n")
            ip_csv.write("'geomorph/input/MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_W_2023lndtyp30.xyz', lwf_file -  file name with relative path to land/water file that is same resolution and structure as DEM XYZ\n")
        else:
            ip_csv.write("'geomorph/output/%s_W_dem30.xyz', dem_file -  file name with relative path to DEM XYZ file\n" % file_prefix_prv)
            ip_csv.write("'geomorph/output/%s_W_lndtyp30.xyz', lwf_file -  file name with relative path to land/water file that is same resolution and structure as DEM XYZ\n" % file_prefix_prv)

        ip_csv.write("'geomorph/input/MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_W_2017meer30.xyz', meer_file -  file name with relative path to marsh edge erosion rate file that is same resolution and structure as DEM XYZ\n")
        ip_csv.write("'geomorph/input/MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_W_polder30.xyz', pldr_file -  file name with relative path to polder file that is same resolution and structure as DEM XYZ\n")
        ip_csv.write("'geomorph/input/MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_W_2017comp30.xyz', comp_file -  file name with relative path to ICM-Hydro compartment map file that is same resolution and structure as DEM XYZ\n")
        ip_csv.write("'geomorph/input/MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_W_2017grid30.xyz', grid_file -  file name with relative path to ICM-LAVegMod grid map file that is same resolution and structure as DEM XYZ\n")
        ip_csv.write("'geomorph/input/MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_W_2023dpsub30.xyz', dsub_file -  file name with relative path to deep subsidence rate map file that is same resolution and structure as DEM XYZ (mm/yr; positive value\n")
        ip_csv.write("'geomorph/input/ecoregion_shallow_subsidence_mm.csv', ssub_file -  file name with relative path to shallow subsidence table with statistics by ecoregion (mm/yr; positive values are for downward VLM)\n")
        ip_csv.write("'geomorph/input/compartment_active_delta.csv', act_del_file -  file name with relative path to lookup table that identifies whether an ICM-Hydro compartment is assigned as an active delta site\n")
        ip_csv.write("'geomorph/input/ecoregion_organic_matter_accum.csv', eco_omar_file -  file name with relative path to lookup table of organic accumulation rates by marsh type/ecoregion\n")
        ip_csv.write("'geomorph/input/compartment_ecoregion.csv', comp_eco_file -  file name with relative path to lookup table that assigns an ecoregion to each ICM-Hydro compartment\n")
        ip_csv.write("'geomorph/input/ecoregion_sav_priors.csv', sav_priors_file - file name, with relative path, to CSV containing parameters defining the periors (per basin) for the SAV statistical model\n'")

        ip_csv.write("'hydro/TempFiles/compartment_out_%4d.csv', hydro_comp_out_file -  file name with relative path to compartment_out.csv file saved by ICM-Hydro\n" % year)
        ip_csv.write("'hydro/TempFiles/compartment_out_%4d.csv', prv_hydro_comp_out_file -  file name with relative path to compartment_out.csv file saved by ICM-Hydro for previous year\n" % (year-1))
        ip_csv.write("'veg/%s_V_vegty.asc+', veg_out_file -  file name with relative path to *vegty.asc+ file saved by ICM-LAVegMod\n" % file_oprefix)
        ip_csv.write("'%s', monthly_mean_stage_file -  file name with relative path to compartment summary file with monthly mean water levels\n" % monthly_file_avstg)
        ip_csv.write("'%s', monthly_max_stage_file -  file name with relative path to compartment summary file with monthly maximum water levels\n" % monthly_file_mxstg)
        ip_csv.write("'%s', monthly_ow_sed_dep_file -  file name with relative path to compartment summary file with monthly sediment deposition in open water\n" % monthly_file_sdowt)
        ip_csv.write("'%s', monthly_mi_sed_dep_file -  file name with relative path to compartment summary file with monthly sediment deposition on interior marsh\n" % monthly_file_sdint)
        ip_csv.write("'%s', monthly_me_sed_dep_file -  file name with relative path to compartment summary file with monthly sediment deposition on marsh edge\n" % monthly_file_sdedg)
        ip_csv.write("'%s', monthly_mean_sal_file -  file name with relative path to compartment summary file with monthly mean salinity values\n" % monthly_file_avsal)
        ip_csv.write("'%s', monthly_mean_tss_file -  file name with relative path to compartment summary file with monthly mean suspended sediment concentrations\n" % monthly_file_avtss)
        ip_csv.write("'%s', bi_dem_xyz_file -  file name with relative path to XYZ DEM file for ICM-BI-DEM model domain - XY resolution must be snapped to XY resolution of main DEM\n" % bidem_xyz_file)
        ip_csv.write("'geomorph/output/%s_W_edge30.xyz', edge_eoy_xyz_file -  file name with relative path to XYZ raster output file for edge pixels\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_dem30.xyz', dem_eoy_xyz_file -  file name with relative path to XYZ raster output file for topobathy DEM\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_dz30.xyz', dz_eoy_xyz_file -  file name with relative path to XYZ raster output file for elevation change raster\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_lndtyp30.xyz', lndtyp_eoy_xyz_file -  file name with relative path to XYZ raster output file for land type\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_lndchg30.xyz', lndchng_eoy_xyz_file -  file name with relative path to XYZ raster output file for land change flag\n" % file_prefix)
        ip_csv.write("'geomorph/output/grid_summary_eoy_%d.csv', grid_summary_eoy_file -  file name with relative path to summary grid file for end-of-year landscape\n" % year)
        ip_csv.write("'hydro/TempFiles/grid_data_500m_%d.csv', grid_data_file -  file name with relative path to summary grid data file used internally by ICM\n" % year)
        ip_csv.write("'hsi/GadwallDepths_cm_%d.csv', grid_depth_file_Gdw -  file name with relative path to Gadwall depth grid data file used internally by ICM and HSI\n" % year)
        ip_csv.write("'hsi/GWTealDepths_cm_%d.csv', grid_depth_file_GwT -  file name with relative path to Greenwing Teal depth grid data file used internally by ICM and HSI\n" % year)
        ip_csv.write("'hsi/MotDuckDepths_cm_%d.csv', grid_depth_file_MtD -  file name with relative path to Mottled Duck depth grid data file used internally by ICM and HSI\n" % year)
        ip_csv.write("'hsi/%s_W_pedge.csv', grid_pct_edge_file -  file name with relative path to percent edge grid data file used internally by ICM and HSI\n" % file_prefix)
        ip_csv.write("'geomorph/output/%s_W_SAV.csv', grid_sav_file -  file name with relative path to csv output file for SAV presence\n" % file_oprefix)
        ip_csv.write("'hydro/TempFiles/compelevs_end_%d.csv', comp_elev_file -  file name with relative path to elevation summary compartment file used internally by ICM\n" % year)
        ip_csv.write("'hydro/TempFiles/PctWater_%d.csv', comp_wat_file -  file name with relative path to percent water summary compartment file used internally by ICM\n" % year)
        ip_csv.write("'hydro/TempFiles/PctUpland_%d.csv', comp_upl_file -  file name with relative path to percent upland summary compartment file used internally by ICM\n" % year)
        ip_csv.write("2941, nqaqc - number of QAQC points for reporting - as listed in qaqc_site_list_file\n")
        ip_csv.write("'geomorph/output_qaqc/qaqc_site_list.csv', qaqc_site_list_file - file name, with relative path, to percent upland summary compartment file used internally by ICM\n")
        ip_csv.write(" %s - file naming convention prefix\n" % file_o_01_50_prefix)


#    try:
#    morph_run = subprocess.call('./morph_v23.G031.1')

#    except Exception as err:
#        print ('\n ******ERROR******')
#        print(err)
#        sys.exit('Morph model run failed - Year %s.' % year)
