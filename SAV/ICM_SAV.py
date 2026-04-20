
#########################################################################################################
####                                                                                                 ####
####                            START GENERAL ICM_SAV.PY PROGRAM                                     ####
####                                                                                                 ####
#########################################################################################################

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



#########################################################
## INPUT VARIABLES TO BE READ FROM CONFIGURATION FILES ##
#########################################################
SAVyear = int(sys.argv[1])


print('--------------------------------------------------')
print('\n CONFIGURING ICM-SAV MODEL FILES: %s' % SAVyear)
print('--------------------------------------------------')


par_dir = os.getcwd()

inputs = np.genfromtxt('ICM_SAV_control.csv',dtype=str,comments='#',delimiter=',')

# Parent directory locations for various ICM components
# These directories must exist in the model folder
# Other directories are created throughout the ICM run - but they are all based on these parent directories
ecohydro_dir = os.path.normpath('%s/%s' % (par_dir,inputs[1,1].lstrip().rstrip()))
wetland_morph_dir = os.path.normpath('%s/%s' % (par_dir,inputs[2,1].lstrip().rstrip()))
vegetation_dir = os.path.normpath('%s/%s' % (par_dir,inputs[3,1].lstrip().rstrip()))
bimode_dir = os.path.normpath('%s/%s' % (par_dir,inputs[4,1].lstrip().rstrip()))
HSI_dir = os.path.normpath('%s/%s' % (par_dir,inputs[5,1].lstrip().rstrip()))
ewe_dir = os.path.normpath('%s/%s' % (par_dir,inputs[6,1].lstrip().rstrip()))

#default# hydro_exe_path = './hydro_v23.4.0' 
#default# bidem_exe_path = './bidem_v23.0.0'
#default# morph_exe_path = './morph_v23.1.0' 

hydro_exe_path = inputs[7,1].lstrip().rstrip() # path to hydro executable - ** path is relative to the S##/G###/hydro        ** - use './' if running copy of executable that is saved in /hydro directory 
bidem_exe_path = inputs[8,1].lstrip().rstrip() # path to bidem executable - ** path is relative to the S##/G###/bidem/REGION ** - use './' if running copy of executable that is saved in /bidem/REGION directory
SAV_exe_path = inputs[9,1].lstrip().rstrip() # path to morph executable - ** path is relative to the S##/G###              ** - use './' if running copy of executable that is saved in /G## directory

# Configuration files used by various ICM components
VegConfigFile = inputs[10,1].lstrip().rstrip()
WMConfigFile = inputs[11,1].lstrip().rstrip()
EHConfigFile = inputs[12,1].lstrip().rstrip()
EHCellsFile = inputs[13,1].lstrip().rstrip()
EHLinksFile = inputs[14,1].lstrip().rstrip()
BIMHWFile = inputs[15,1].lstrip().rstrip()
exist_cond_tag = inputs[16,1].lstrip().rstrip()
fwoa_init_cond_tag = inputs[17,1].lstrip().rstrip()
shallow_subsidence_column = int(inputs[18,1].lstrip().rstrip())

compartment_output_file = 'compartment_out.csv'
grid_output_file        = 'grid_500m_out.csv'
EHInterfaceFile         = 'ICM_info_into_EH.txt'


# Filenames for Veg model input
WaveAmplitudeFile = inputs[19,1].lstrip().rstrip()
MeanSalinityFile = inputs[20,1].lstrip().rstrip()
SummerMeanWaterDepthFile = inputs[21,1].lstrip().rstrip()
SummerMeanSalinityFile = inputs[22,1].lstrip().rstrip()
SummerMeanTempFile = inputs[23,1].lstrip().rstrip()
TreeEstCondFile = inputs[24,1].lstrip().rstrip()
HtAbvWaterFile = inputs[25,1].lstrip().rstrip()
PerLandFile = inputs[26,1].lstrip().rstrip()
PerWaterFile = inputs[27,1].lstrip().rstrip()
AcuteSalFile = inputs[28,1].lstrip().rstrip()
acute_sal_threshold = 5.5

## Simulation Settings
startyear = int(inputs[29,1].lstrip().rstrip())
endyear = int(inputs[30,1].lstrip().rstrip())
ncycle = int(inputs[31,1].lstrip().rstrip())
startyear_cycle = int(inputs[32,1].lstrip().rstrip())
endyear_cycle = int(inputs[33,1].lstrip().rstrip())
inputStartYear = int(inputs[34,1].lstrip().rstrip())
nvegtype = int(inputs[35,1].lstrip().rstrip())
update_hydro_attr = int(inputs[36,1].lstrip().rstrip())

# convert calendar years to elapsed years
hotstart_year = startyear_cycle
elapsed_hotstart = hotstart_year - startyear
cycle_start_elapsed = startyear_cycle - startyear
cycle_end_elapsed = endyear_cycle - startyear + 1

hotstart_year = startyear_cycle
cycle_start_elapsed = startyear_cycle - startyear + 1
cycle_end_elapsed = endyear_cycle - startyear + 1


## grid information for Veg ASCII grid files
n500grid = int(inputs[37,1].lstrip().rstrip())
# n500gridveg = int(inputs[25,1].lstrip().rstrip()) #total number of grid cells in Veg model - including NoData cells
n500rows = int(inputs[38,1].lstrip().rstrip())
n500cols = int(inputs[39,1].lstrip().rstrip())
xll500 = int(inputs[40,1].lstrip().rstrip())
yll500 = int(inputs[41,1].lstrip().rstrip())

## grid information for EwE ASCII grid files
n1000grid = int(inputs[42,1].lstrip().rstrip())
n1000rows = int(inputs[43,1].lstrip().rstrip())
n1000cols = int(inputs[44,1].lstrip().rstrip())
xll1000 = inputs[45,1].lstrip().rstrip()
yll1000 = inputs[46,1].lstrip().rstrip()

# file naming convention settings
mpterm = inputs[47,1].lstrip().rstrip()
sterm = inputs[48,1].lstrip().rstrip()
gterm = inputs[49,1].lstrip().rstrip()
cterm = inputs[50,1].lstrip().rstrip()
uterm = inputs[51,1].lstrip().rstrip()
vterm = inputs[52,1].lstrip().rstrip()
rterm = inputs[53,1].lstrip().rstrip()


# build some file naming convention tags
runprefix = '%s_%s_%s_%s_%s_%s_%s' % (mpterm,sterm,gterm,cterm,uterm,vterm,rterm)
file_prefix_cycle = r'%s_N_%02d_%02d' % (runprefix,cycle_start_elapsed,cycle_end_elapsed)
file_o_01_end_prefix = r'%s_O_01_%02d' % (runprefix,endyear-startyear+1)


# read in asci grid structure
asc_grid_file = os.path.normpath(r'%s/veg_grid.asc' % vegetation_dir)
asc_grid_ids = np.genfromtxt(asc_grid_file,skip_header=6,delimiter=' ',dtype='int')
asc_grid_head = 'ncols 1052\nnrows 365\nxllcorner 404710\nyllcorner 3199480\ncellsize 480\nNODATA_value -9999\n'






#########################################################
##              START YEARLY TIMESTEPPING              ##
#########################################################

#for year in range(startyear+elapsed_hotstart,endyear_cycle+1):
year = SAVyear
print('\n--------------------------------------------------')
print('  MODELING SAV - YEAR %s' % year)
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
#asc_head = '# Year = %04d\n%s' % (year,asc_grid_head)
asc_head = asc_grid_head
file_prefix     = r'%s_N_%02d_%02d' % (runprefix,elapsedyear,elapsedyear)
file_oprefix    = r'%s_O_%02d_%02d' % (runprefix,elapsedyear,elapsedyear)
file_prefix_prv = r'%s_N_%02d_%02d' % (runprefix,elapsedyear-1,elapsedyear-1)


# set file names for files passed from Hydro into Veg and Morph
EHtemp_path = os.path.normpath(r'%s/TempFiles' % ecohydro_dir)
EH_grid_file = 'grid_data_500m.csv' # this must match file name used in hydro.exe
EH_grid_filepath = os.path.normpath('%s/%s' % (ecohydro_dir,EH_grid_file)) # location of grid_data_500m.csv when used by hydro.exe
move_EH_gridfile = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EH_grid_file,'.')[0],year,str.split(EH_grid_file,'.')[1]))
EH_comp_out_newfile = '%s_%s.%s' % (str.split(compartment_output_file,'.')[0],year,str.split(compartment_output_file,'.')[1])
EH_comp_results_filepath = os.path.normpath('%s/%s' % (EHtemp_path,EH_comp_out_newfile))

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
comp_out_file = EH_comp_results_filepath
griddata_file = move_EH_gridfile                                                                                                                #os.path.normpath(r'%s/grid_data_500m_%04d.csv' % (EHtemp_path,year) )
new_grid_filepath =  os.path.normpath(r"%s/%s_end%s.%s" % (EHtemp_path,str.split(EH_grid_file,'.')[0],year,str.split(EH_grid_file,'.')[1]))     #os.path.normpath(r'%s/grid_data_500m_end%s.csv' % (EHtemp_path,year) )
bidem_xyz_file = os.path.normpath(r'%s/%s_W_dem30_bi.xyz' % (bimode_dir,file_prefix) )
sav_file_no_ext = 'geomorph/output/%s_W_SAV' % file_oprefix


#########################################################
##                   RUN MORPH MODEL                   ##
#########################################################
os.chdir(par_dir)

# read in Wetland Morph input file and update variables for year of simulation
wm_param_file = r'%s/SAV_input_params_%04d.csv' % (wetland_morph_dir,year)

with open (wm_param_file, mode='w') as ip_csv:
    ip_csv.write("%d, start_year - first year of model run\n" % startyear)
    ip_csv.write("%d, elapsed_year - elapsed year of model run\n" % elapsedyear)
    ip_csv.write("30, dem_res - XY resolution of DEM (meters)\n")
    ip_csv.write("-9999, dem_NoDataVal - value representing nodata in input rasters and XYZ files\n")
    ip_csv.write("171284090, ndem - number of DEM pixels - will be an array dimension for all DEM-level data\n")
    ip_csv.write("2904131, ndem_bi - number of pixels in interpolated ICM-BI-DEM XYZ that overlap primary DEM\n")
    ip_csv.write("1778, ncomp - number of ICM-Hydro compartments - will be an array dimension for all compartment-level data\n")
    ip_csv.write("%d, ngrid - number of ICM-LAVegMod grid cells - will be an array dimension for all gridd-level data\n" % n500grid)
    ip_csv.write("32, neco - number of ecoregions\n")
    ip_csv.write("5, nlt - number of landtype classifications\n")
    ip_csv.write("0.10, ht_above_mwl_est - elevation (meters) relative to annual mean water level at which point vegetation can establish\n")
    ip_csv.write("2.57, ptile_Z - Z-value for quantile definining inundation curve\n")
    ip_csv.write("0.0058, B0 - beta-0 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
    ip_csv.write("-0.00207, B1 - beta-1 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
    ip_csv.write("0.0809, B2 - beta-2 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
    ip_csv.write("0.0892, B3 - beta-3 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
    ip_csv.write("-0.19, B4 - beta-4 coefficient from quantile regression on CRMS annual inundation-salinity data (see App. A of MP2023 Wetland Vegetation Model Improvement report)\n")
    ip_csv.write("0.835, ow_bd - bulk density of water bottoms (g/cm3)\n")
    ip_csv.write("0.076, om_k1 - organic matter self-packing density (g/cm3) from CRMS soil data (see 2023 Wetlands Model Improvement report)\n")
    ip_csv.write("2.106, mn_k2- mineral soil self-packing density (g/cm3) from CRMS soil data (see 2023 Wetlands Model Improvement report)\n")
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
    ip_csv.write("-0.762, mc_depth_threshold - water depth threshold (meters) defining deep water area to be excluded from marsh creation projects footprint\n")
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
    ip_csv.write("'geomorph/input/%s_W_dpsub30.xyz', dsub_file - file name with relative path to deep subsidence rate map file that is same resolution and structure as DEM XYZ (mm/yr; positive value\n" % exist_cond_tag)
    ip_csv.write("'geomorph/input/ecoregion_shallow_subsidence_mm.csv', ssub_file - file name with relative path to shallow subsidence table with statistics by ecoregion (mm/yr; positive values are for downward VLM)\n")
    ip_csv.write(" %d,ssub_col - column of shallow subsidence rates to use for current scenario (1=25th percentile; 2=50th percentile; 3=75th percentile)\n" % shallow_subsidence_column)
    ip_csv.write("'geomorph/input/compartment_active_delta.csv', act_del_file - file name with relative path to lookup table that identifies whether an ICM-Hydro compartment is assigned as an active delta site\n")
    ip_csv.write("'geomorph/input/ecoregion_organic_matter_accum.csv', eco_omar_file - file name with relative path to lookup table of organic accumulation rates by marsh type/ecoregion\n")
    ip_csv.write("'geomorph/input/compartment_ecoregion.csv', comp_eco_file - file name with relative path to lookup table that assigns an ecoregion to each ICM-Hydro compartment\n")
    ip_csv.write("'geomorph/input/ecoregion_sav_priors.csv', sav_priors_file - file name with relative path to CSV containing parameters defining the periors (per basin) for the SAV statistical model\n")

    ip_csv.write("'hydro/TempFiles/compartment_out_%4d.csv', hydro_comp_out_file - file name with relative path to compartment_out.csv file saved by ICM-Hydro\n" % year)

    if year == startyear:
        ip_csv.write("'hydro/TempFiles/compartment_out_%4d.csv', prv_hydro_comp_out_file - file name with relative path to compartment_out.csv file saved by ICM-Hydro for previous year\n" % (year))
    else:
        ip_csv.write("'hydro/TempFiles/compartment_out_%4d.csv', prv_hydro_comp_out_file - file name with relative path to compartment_out.csv file saved by ICM-Hydro for previous year\n" % (year-1))

    ip_csv.write("'veg/%s_V_vegty.asc+', veg_out_file - file name with relative path to *vegty.asc+ file saved by ICM-LAVegMod\n" % file_oprefix)
    ip_csv.write("'%s', monthly_mean_stage_file - file name with relative path to compartment summary file with monthly mean water levels\n" % monthly_file_avstg)
    ip_csv.write("'%s', monthly_max_stage_file - file name with relative path to compartment summary file with monthly maximum water levels\n" % monthly_file_mxstg)
    ip_csv.write("'%s', monthly_ow_sed_dep_file - file name with relative path to compartment summary file with monthly sediment deposition in open water\n" % monthly_file_sdowt)
    ip_csv.write("'%s', monthly_mi_sed_dep_file - file name with relative path to compartment summary file with monthly sediment deposition on interior marsh\n" % monthly_file_sdint)
    ip_csv.write("'%s', monthly_me_sed_dep_file - file name with relative path to compartment summary file with monthly sediment deposition on marsh edge\n" % monthly_file_sdedg)
    ip_csv.write("'%s', monthly_mean_sal_file - file name with relative path to compartment summary file with monthly mean salinity values\n" % monthly_file_avsal)
    ip_csv.write("'%s', monthly_mean_tss_file - file name with relative path to compartment summary file with monthly mean suspended sediment concentrations\n" % monthly_file_avtss)
    ip_csv.write("'%s', bi_dem_xyz_file - file name with relative path to XYZ DEM file for ICM-BI-DEM model domain - XY resolution must be snapped to XY resolution of main DEM\n" % bidem_xyz_file)
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
    ip_csv.write("'hsi/GadwallDepths_cm_%d.csv', grid_depth_file_Gdw - file name with relative path to Gadwall depth grid data file used internally by ICM and HSI\n" % year)
    ip_csv.write("'hsi/GWTealDepths_cm_%d.csv', grid_depth_file_GwT - file name with relative path to Greenwing Teal depth grid data file used internally by ICM and HSI\n" % year)
    ip_csv.write("'hsi/MotDuckDepths_cm_%d.csv', grid_depth_file_MtD - file name with relative path to Mottled Duck depth grid data file used internally by ICM and HSI\n" % year)
    ip_csv.write("'hsi/%s_W_pedge.csv', grid_pct_edge_file - file name with relative path to percent edge grid data file used internally by ICM and HSI\n" % file_prefix)
    ip_csv.write("'%s', grid_sav_file - file name with relative path to output file - file extension will be added in MorphSAV\n" % sav_file_no_ext)
    ip_csv.write("'hydro/TempFiles/compelevs_end_%d.csv', comp_elev_file - file name with relative path to elevation summary compartment file used internally by ICM\n" % year)
    ip_csv.write("'hydro/TempFiles/PctWater_%d.csv', comp_wat_file - file name with relative path to percent water summary compartment file used internally by ICM\n" % year)
    ip_csv.write("'hydro/TempFiles/PctUpland_%d.csv', comp_upl_file - file name with relative path to percent upland summary compartment file used internally by ICM\n" % year)
    ip_csv.write("2941, nqaqc - number of QAQC points for reporting - as listed in qaqc_site_list_file\n")
    ip_csv.write("'geomorph/output_qaqc/qaqc_site_list.csv', qaqc_site_list_file - file name, with relative path, to percent upland summary compartment file used internally by ICM\n")
    ip_csv.write(" %s - file naming convention prefix\n" % file_o_01_end_prefix)

morph_run = subprocess.call([SAV_exe_path, wm_param_file])

print('\nMapping SAV outputs to ASC raster.')

sav_ave_dict = {}   # dictionary where key will be ICM-LAVegMod GridID - value will be average probablity of SAV occurrence within the grid cell
sav_all_dict = {}   # dictionary where key will be ICM-LAVegMod GridID - value will be a list of all SAV probability values from the 30-m SAV raster within each respective grid cell
for g in range(1,n500grid+1):
    sav_ave_dict[g] = 0.0
    sav_all_dict[g] = []
    
SAVcsv = '%s.csv' % sav_file_no_ext 
SAVasc = '%s.asc' % sav_file_no_ext
SAVxyz = '%s_prob.xyz' % sav_file_no_ext

with open(SAVcsv,mode='r') as sav_data:
    nline = 0
    for line in sav_data:
        if nline > 0:   # header: dem_x,dem_y,gridID,compID,spsal,sptss,dfl,ffibs,prob
            gr    = int(float(line.split(',')[2]))
            prsav = float(line.split(',')[8])
            
            sav_all_dict[gr].append(max(prsav,0.0)) # if probability of SAV is -9999 it is no data, reset to zero so that areas further than 2 km from land are included in data for HSIs
        nline += 1
        
for g in sav_ave_dict.keys():
    ng = len(sav_all_dict[g])
    if ng > 0:
        sav_ave_dict[g] = sum(sav_all_dict[g]) / ng
    else:
        sav_ave_dict[g] = 0.0

# build ASC raster of percent SAV 
print(dict2asc_flt(sav_ave_dict,SAVasc,asc_grid_ids,asc_head,write_mode='w') )

# zip up CSV and XYZ outputs - remove original (option -m) after testing for errors (option -T
SAVxyz_zip = '%s.zip' % SAVxyz
zipSAVxyz = subprocess.call(['zip','-mT', SAVxyz_zip,SAVxyz])

SAVcsv_zip = '%s.zip' % SAVcsv
zipSAVcsv = subprocess.call(['zip','-mT', SAVcsv_zip,SAVcsv])


print('\n\n\n')
print('-----------------------------------------' )
print(' ICM SAV Model run complete!')
print('-----------------------------------------\n')



