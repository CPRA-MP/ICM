#ICM imports
import ICM_HelperFunctions as hf

#Python imports
import os
import numpy as np


HSI_standalone = True # Run HSI in Standalone Mode; must have existing EcoHyd, Veg, and Morph model output

par_dir = os.getcwd()

#TODO this file name for the CSV should be rectified once ICM and HSI models are merged
inputs = np.genfromtxt('ICM_HSI_control.csv',dtype=str,comments='#',delimiter=',')

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
morph_exe_path = inputs[9,1].lstrip().rstrip() # path to morph executable - ** path is relative to the S##/G###              ** - use './' if running copy of executable that is saved in /G## directory
sav_submit_exe_path = '/ocean/projects/bcs200002p/ewhite12/code/git/ICM/submit_SAV.py'
run_sav = 1         # 1 = submit SAV simulations to queue at end of year; 0 = do not run SAV
morph_zonal_stats = 0 # 1 = zonal stats run in ICM-Morph; 0 = zonal stats run here in ICM

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
#cycle_start_elapsed = startyear_cycle - startyear #TODO check, this line differs from the one below
cycle_end_elapsed = endyear_cycle - startyear + 1
cycle_start_elapsed = startyear_cycle - startyear + 1

## grid information for Veg ASCII grid files
n500grid= int(inputs[37,1].lstrip().rstrip())
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

EHtemp_path = os.path.normpath(r'%s/TempFiles' % ecohydro_dir)

# 1D Hydro model information
n_1D = int(inputs[54,1].lstrip().rstrip())
RmConfigFile = inputs[55,1].lstrip().rstrip()

## Barrier Island Model settings
BITIconfig = inputs[56,1].lstrip().rstrip()
n_bimode = int(inputs[57,1].lstrip().rstrip())
bimode_folders=[]
for row in range(58,58+n_bimode):
    bimode_folders.append(inputs[row,1].lstrip().rstrip())
bidem_fixed_grids=[]
for row in range(58+n_bimode,58+2*n_bimode):
    bidem_fixed_grids.append(inputs[row,1].lstrip().rstrip())

# read in asci grid structure
asc_grid_file = os.path.normpath(r'%s/veg_grid.asc' % vegetation_dir)
asc_grid_ids = np.genfromtxt(asc_grid_file,skip_header=6,delimiter=' ',dtype='int')
asc_grid_head = 'ncols 1052\nnrows 365\nxllcorner 404710\nyllcorner 3199480\ncellsize 480\nNODATA_value -9999\n'

# read in grid-to-compartment lookup table into a dictionary
# key is grid ID and value is compartment
grid_lookup_file = r'%s/grid_lookup_500m.csv' % ecohydro_dir
grid_lookup = np.genfromtxt(grid_lookup_file,skip_header=1,delimiter=',',dtype='int',usecols=[0,1])
grid_comp = {row[0]:row[1] for row in grid_lookup}
grid500_res = 480.0

# Save list of GridIDs into an array for use in some loops later # ultimately can replace with grid_comp.keys() in loops
gridIDs=grid_comp.keys()

# run HSIascii_grid for each species
map2grid = False
ascii_grid_lookup,ascii_header,ascii_header_nrows,n500rows,n500cols  = hf.create_ASCII_grid_vals(vegetation_dir,n500rows,n500cols,yll500,xll500)


    