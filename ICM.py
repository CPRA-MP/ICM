#########################################################################################################
####                                                                                                 ####   
####                                FUNCTIONS USED BY ICM.PY                                         ####
####                                                                                                 ####   
#########################################################################################################


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


#########################################################################################################
####                                                                                                 ####   
####                                START GENERAL ICM.PY PROGRAM                                     ####
####                                                                                                 ####   
#########################################################################################################

import os
import platform
import sys

import shutil
import math
import time
import errno
import numpy as np
import random
from builtins import Exception as exceptions
#import pysftp


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
hydro_logfile = 'ICM_%s_Hydro.log' % time.strftime('%Y%m%d_%H%M', time.localtime()) 
#HPCmode# sys.stdout = Logger(logfile)


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
print('~~ Development team:                                         ~~')
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

# Years to activate or deactivate Hydro model links
link_years = []
# Link numbers to be activated or deactivated in Hydro model
links_to_change = []


# Years to implement marsh creation projects in Morphology model
mc_years = []
# Years to update 'composite' marsh flow links (type 11) for marsh creation projects - this value should be the year after the project is implemented in the morphology model
mc_links_years = []
# link ID numbers for 'composite' marsh flow links (type 11) that need to be updated due to marsh creation projects
mc_links = []
# Marsh creation projects feature class (optional-enter allcaps NONE if not modeled)
mc_shps = []
# Field with marsh project elevation in NAVD88 m (optional-enter allcaps NONE if not modeled)
mc_shps_fields = []

# Years to implement shoreline protection projects
sp_years = []
# Shoreline protection projects feature class
sp_shps = []
# Field with shoreline protecion project erosion reduction multiplier
sp_shps_fields = []

# Years to implement levee and ridge restoration projects
levee_years = []
# Levee projects feature class
levee_shps = []
# Field with levee project crest width
levee_shps_fields1 = []
# Field with levee project elevation in NAVD88 m
levee_shps_fields2 = []
# Field with levee slope width 
levee_shps_fields3 = []
# Field with levee slope elevation in NAVD88 m
levee_shps_fields4 = []


# check that project implementation variables are of the correct lengths
InputErrorFlag = 0
InputErrorMsg = ''
if len(link_years) != len(links_to_change):
    InputErrorFlag = 1
    InputErrorMsg = '%sNumber of links to activate/deactivate and implementation years are not equal in length!\n' % InputErrorMsg 
if len(mc_links_years) != len(mc_links):
    InputErrorFlag = 1
    InputErrorMsg = '%sNumber of links to update for marsh creation projects and implementation years are not equal in length!\n' % InputErrorMsg
if len(mc_years) != len(mc_shps) != len(mc_shps_fields):
    InputErrorFlag = 1
    InputErrorMsg = '%sMarsh Creation Project Implementation variables are not of equal length!\n' % InputErrorMsg
if len(sp_years) != len(sp_shps) != len(sp_shps_fields):
    InputErrorFlag = 1
    InputErrorMsg = '%sShoreline Protection Project Implementation variables are not of equal length!\n' % InputErrorMsg
if len(levee_years) != len(levee_shps) != len(levee_shps_fields1) != len(levee_shps_fields2) != len(levee_shps_fields3) != len(levee_shps_fields4):
    InputErrorFlag = 1
    InputErrorMsg = '%sLevee & Ridge Project Implementation variables are not of equal length!\n' % InputErrorMsg

if InputErrorFlag == 1:
    print(' ***********Error with Project Implementation variables! Fix and re-run!\n')
    sys.exit(InputErrorMsg)           



inputs = np.genfromtxt('ICM_control.csv',dtype=str,comments='#',delimiter=',')

# Parent directory locations for various ICM components
# These directories must exist in the model folder
# Other directories are created throughout the ICM run - but they are all based on these parent directories
ecohydro_dir = os.path.normpath(inputs[1,1].lstrip().rstrip())
wetland_morph_dir = os.path.normpath(inputs[2,1].lstrip().rstrip())
vegetation_dir = os.path.normpath(inputs[3,1].lstrip().rstrip())
bimode_dir = os.path.normpath(inputs[4,1].lstrip().rstrip())
HSI_dir = os.path.normpath(inputs[5,1].lstrip().rstrip())
ewe_dir = os.path.normpath(inputs[6,1].lstrip().rstrip())
# Configuration files used by various ICM components
VegConfigFile = inputs[7,1].lstrip().rstrip()
WMConfigFile = inputs[8,1].lstrip().rstrip()
EHConfigFile = inputs[9,1].lstrip().rstrip()
EHCellsFile = inputs[10,1].lstrip().rstrip()
EHLinksFile = inputs[11,1].lstrip().rstrip()
BIPrismFile = inputs[12,1].lstrip().rstrip()
BIMHWFile = inputs[13,1].lstrip().rstrip()
EHInterfaceFile = inputs[14,1].lstrip().rstrip()
BMInterfaceFile = inputs[15,1].lstrip().rstrip()
compartment_output_file = 'compartment_out.csv'
grid_output_file = 'grid_500m_out.csv'

# Filenames for Veg model input
WaveAmplitudeFile = inputs[16,1].lstrip().rstrip()
MeanSalinityFile = inputs[17,1].lstrip().rstrip()
SummerMeanWaterDepthFile = inputs[18,1].lstrip().rstrip()
SummerMeanSalinityFile = inputs[19,1].lstrip().rstrip()
SummerMeanTempFile = inputs[20,1].lstrip().rstrip()
TreeEstCondFile = inputs[21,1].lstrip().rstrip()
HtAbvWaterFile = inputs[22,1].lstrip().rstrip()
PerLandFile = inputs[23,1].lstrip().rstrip()

## Simulation Settings
startyear = int(inputs[24,1].lstrip().rstrip())
endyear = int(inputs[25,1].lstrip().rstrip())
nvegtype = int(inputs[26,1].lstrip().rstrip())
inputStartYear = int(inputs[27,1].lstrip().rstrip())
hotstart_year = int(inputs[28,1].lstrip().rstrip())
elapsed_hotstart = hotstart_year - startyear
update_hydro_attr = int(inputs[29,1].lstrip().rstrip())

## grid information for Veg ASCII grid files
n500grid= int(inputs[30,1].lstrip().rstrip())
# n500gridveg = int(inputs[25,1].lstrip().rstrip()) #total number of grid cells in Veg model - including NoData cells
n500rows = int(inputs[31,1].lstrip().rstrip())
n500cols = int(inputs[32,1].lstrip().rstrip())
xll500 = int(inputs[33,1].lstrip().rstrip())
yll500 = int(inputs[34,1].lstrip().rstrip())

## grid information for EwE ASCII grid files
n1000grid = int(inputs[35,1].lstrip().rstrip())
n1000rows = int(inputs[36,1].lstrip().rstrip())
n1000cols = int(inputs[37,1].lstrip().rstrip())
xll1000 = inputs[38,1].lstrip().rstrip()
yll1000 = inputs[39,1].lstrip().rstrip()

# file naming settings
mpterm = inputs[40,1].lstrip().rstrip()
sterm = inputs[41,1].lstrip().rstrip()
gterm = inputs[42,1].lstrip().rstrip()
cterm = inputs[43,1].lstrip().rstrip()
uterm = inputs[44,1].lstrip().rstrip()
vterm = inputs[45,1].lstrip().rstrip()
rterm = inputs[46,1].lstrip().rstrip()
runprefix = '%s_%s_%s_%s_%s_%s_%s' % (mpterm,sterm,gterm,cterm,uterm,vterm,rterm)

## BIMODE sub-directories
n_bimode = int(inputs[47,1].lstrip().rstrip())
bimode_folders=[]
for row in range(48,48+n_bimode):
    bimode_folders.append(inputs[row,1].lstrip().rstrip())
# bimode_folders should be a string array of BIMODE folder names - looks like:
#bimode_folders =['ST73124','ST73126','ST73129','ST73131','ST73139','ST73141']

yearstokeepmorph = [1,2,3,10,20,25,30,40,50]

## Load 1D River Model Configuration file
n_1D = int(inputs[54,1].lstrip().rstrip())

if n_1D > 0:
    RmConfigFile = inputs[55,1].lstrip().rstrip()
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


#########################################################
##            SETTING UP ICM-HYDRO MODEL                 ##
#########################################################

print(' Configuring ICM-Hydro.')
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
#HPCmode#    print('\n Would you like to:')
#HPCmode#    print('\n     1. Exit run and manually delete all *.out files?')
#HPCmode#    print('\n     2. Programatically delete all *.out files and continue run?')
#HPCmode#    option=input()
#HPCmode#    try:
#HPCmode#        if int(option) == 1:
#HPCmode#            exitmsg='\n Manually remove *.out files and re-run ICM.'
#HPCmode#            sys.exit(exitmsg)
#HPCmode#        elif int(option) == 2:
#HPCmode#            print('\n Attempting to remove *.out files from Hydro directory.')
#HPCmode#            try:
#HPCmode#                ehfiles=os.listdir(ecohydro_dir)
#HPCmode#                for f in ehfiles:
#HPCmode#                    if f.endswith('.out'):
#HPCmode#                        fp = ecohydro_dir+'/'+f
#HPCmode#                        os.unlink(fp)
#HPCmode#                        print('   - deleted %s' %f)
#HPCmode#                print('\n Successfully deleted all *.out files in %s.' % ecohydro_dir)
#HPCmode#                print('\n Continuing with ICM run.')
#HPCmode#            except Exception,e:
#HPCmode#                    print(' Automatic delete failed.')
#HPCmode#                    sys.exit(e)
#HPCmode#        else:
#HPCmode#                exitmsg='\n Invalid option - manually remove *.out files and re-run ICM.'
#HPCmode#                sys.exit(exitmsg)
#HPCmode#    except Exception,e:
#HPCmode#            exitmsg='\n Invalid option - manually remove *.out files and re-run ICM.'
#HPCmode#            sys.exit(exitmsg)
    exitmsg='\n Manually remove *.out files and re-run ICM.'
    sys.exit(exitmsg)
    
## repeat check for output files - but look in Veg folder for files generated by hydro.exe Fortran program
## change working directory to veg folder
os.chdir(vegetation_dir)

## Need to select path delimiter since this is getting written to a file to be read into Fortran that is not flexible when running in Windows.
if os.name == 'nt':
    path_del = '\\'
else:
    path_del = '/'
    
VegWaveAmpFile =     r'%s%s%s_N_%02d_%02d_H_%s' % (vegetation_dir,path_del,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),WaveAmplitudeFile)
VegMeanSalFile =     r'%s%s%s_N_%02d_%02d_H_%s' % (vegetation_dir,path_del,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),MeanSalinityFile)
VegSummerDepthFile = r'%s%s%s_N_%02d_%02d_H_%s' % (vegetation_dir,path_del,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),SummerMeanWaterDepthFile)
VegSummerSalFile =   r'%s%s%s_N_%02d_%02d_H_%s' % (vegetation_dir,path_del,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),SummerMeanSalinityFile)
VegSummerTempFile =  r'%s%s%s_N_%02d_%02d_H_%s' % (vegetation_dir,path_del,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),SummerMeanTempFile)
VegTreeEstCondFile = r'%s%s%s_N_%02d_%02d_H_%s' % (vegetation_dir,path_del,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),TreeEstCondFile)
VegBIHeightFile =    r'%s%s%s_N_%02d_%02d_H_%s' % (vegetation_dir,path_del,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),HtAbvWaterFile)
VegPerLandFile =     r'%s%s%s_N_%02d_%02d_H_%s' % (vegetation_dir,path_del,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),PerLandFile)
vegflag = 0        
ehveg_outfiles = [VegWaveAmpFile,VegMeanSalFile,VegSummerDepthFile,VegSummerSalFile,VegSummerTempFile,VegTreeEstCondFile,VegBIHeightFile,VegPerLandFile]

for veginfile in ehveg_outfiles:
    if os.path.isfile(veginfile) == True:
                vegflag = 1

if elapsed_hotstart > 0:
    vegflag = 0


if vegflag == 1:
    print('\n**************ERROR**************')
    print('\n Hydro output files formatted for Veg model already exist in Veg project directory.\n Move or delete files and re-run ICM.')
#HPCmode#    print('\n Would you like to:' )
#HPCmode#    print('\n     1. Exit run and manually delete all Hydro output files in Veg directory?')
#HPCmode#    print('\n     2. Programatically delete files and continue run?' )
#HPCmode#    option=input()
#HPCmode#    try:
#HPCmode#        if int(option) == 1:
#HPCmode#            exitmsg='\n Manually remove Hydro output files from Veg directory and re-run ICM.'
#HPCmode#            sys.exit(exitmsg)
#HPCmode#        elif int(option) == 2:
#HPCmode#            print('\n Attempting to remove Hydro output files from Veg directory.')
#HPCmode#            try:
#HPCmode#                vegfiles=os.listdir(vegetation_dir)
#HPCmode#                for vf in ehveg_outfiles:
#HPCmode#                    os.unlink(vf)
#HPCmode#                    print('   - deleted %s' %vf)
#HPCmode#                print('\n Successfully deleted all Hydro output files in %s.' % vegetation_dir)
#HPCmode#                print('\n Continuing with ICM run.')
#HPCmode#            except Exception,e:
#HPCmode#                    print(' Automatic delete failed.')
#HPCmode#                    sys.exit(e)
#HPCmode#        else:
#HPCmode#                exitmsg='\n Invalid option - manually remove files from Veg directory and re-run ICM.'
#HPCmode#                sys.exit(exitmsg)
#HPCmode#    except Exception,e:
#HPCmode#            exitmsg='\n Invalid option - manually remove files from Veg directory and re-run ICM.'
#HPCmode#                sys.exit(exitmsg)
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
#HPCmode#    print('\n Would you like to:')
#HPCmode#    print('\n     1. Exit run and manually move or delete folder?')
#HPCmode#    print('\n     2. Programatically rename folder and continue run?')
#HPCmode#    option=input()
#HPCmode#    try:
#HPCmode#        if int(option) == 1:
#HPCmode#            exitmsg='\n Manually rename or delete folder and re-run ICM.'
#HPCmode#            sys.exit(exitmsg)
#HPCmode#        elif int(option) == 2:
#HPCmode#            print('\n Attempting to rename folder.')
#HPCmode#            try:
#HPCmode#                print('\n What would you like to rename the folder?')
#HPCmode#                nn = input()
#HPCmode#                newnn = os.path.normpath(r'%s/%s' % (ecohydro_dir,nn))
#HPCmode#                os.rename(EHtemp_path,newnn)
#HPCmode#                print('\n Successfully renamed Hydro temporary folder.')
#HPCmode#                print('\n Continuing with ICM run.')
#HPCmode#            except Exception,e:
#HPCmode#                print(' Automatic folder rename failed.')
#HPCmode#                sys.exit(e)
#HPCmode#        else:
#HPCmode#            exitmsg='\n Invalid option - manually rename or delete folder and re-run ICM.'
#HPCmode#            sys.exit(exitmsg)
#HPCmode#    except Exception,e:
#HPCmode#        exitmsg='\n Invalid option - manually remove files from Veg directory and re-run ICM.'
#HPCmode#        sys.exit(exitmsg)
#HPCmode#    exitmsg='\n Manually remove files from Veg directory and re-run ICM.'
#HPCmode#    sys.exit(exitmsg)    
    exitmsg='\n Manually remove files from Veg directory and re-run ICM.'
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


## Read Ecohydro's initial configuration file into an array of strings
## first column is configuration value, second column is description of value
EHConfigArray=np.genfromtxt(EHConfigFile,dtype=str,delimiter='!',autostrip=True)

cellsheader='Compartment,TotalArea,AreaWaterPortion,AreaUplandPortion,AreaMarshPortion,MarshEdgeLength,WSEL_init,bed_elev,depth,initial_stage,percentForETcalc,initial_sand,initial_salinity,RainGage,WindGage,ETGage,CurrentsCoeff,bedFricCoeff,NonSandExp,NonSandCoeff,SandCoeff,KadlecKnightA,KadlecKnightDepth,MarshEdgeErosion,initial_stage_marsh,marsh_elev,soil_moisture_depth,initial_salinity_marsh,marh_elev_adjust'
linksheader='ICM_Link_ID,USnode,DSnode,USx,USy,DSx,DSy,Type,attribute1,attribute2,attribute3,attribute4,attribute5,attribute6,attribute7,attribute8,Exy,attribute9,attribute10,fa_mult'

## Read Ecohydro's Compartment Attributes file into an array
EHCellsArray = np.genfromtxt(EHCellsFile,dtype=float,delimiter=',',skip_header=1)
EHLinksArray = np.genfromtxt(EHLinksFile,dtype=float,delimiter=',',skip_header=1)

## file containing percentage land, and land/water elevations for each 500-m grid cell as it is used by hydro (file is generated by Morph)
EH_grid_file = 'grid_data_500m.csv' # this must match file name used in hydro.exe
EH_grid_filepath = os.path.normpath('%s/%s' % (ecohydro_dir,EH_grid_file)) # location of grid_data_500m.csv when used by hydro.exe

## Read in file linking Ecohydro links to BIMODE profile IDs
## First column (0) is BIMODE profile ID, second column (1) is Ecohydro link ID
print(' Reading in file matching Hydro link IDs to BIMODE profile IDs')
EHBMfile = os.path.normpath(r'%s/%s' % (ecohydro_dir,BMInterfaceFile))

linklup=np.genfromtxt(EHBMfile,delimiter=',',skip_header=1)

## Save profile-link lookup as a dictionary, key is EH link ID, value is BIMODE profile
linktoprofile = dict((linklup[n,0],linklup[n,1])for n in range(0,len(linklup)))

## remove temporary variables/arrays that aren't needed
del(linklup,EHBMfile)

#test_hydro_veg##########################################################
#test_hydro_veg###      SETTING UP BARRIER ISLAND MODEL ~ BIMODE       ##
#test_hydro_veg##########################################################
#test_hydro_veg#print(' Configuring Barrier Island Model ~ BIMODE.')
#test_hydro_veg#
#test_hydro_veg##change working directory to wetland morph folder
#test_hydro_veg#os.chdir(bimode_dir)
#test_hydro_veg#
#test_hydro_veg## ICM Compartment IDs for each island's bay areas
#test_hydro_veg##test_hydro_veg#BI_Dern=[561,566,575,599,609,649]
#test_hydro_veg#BI_Timb=[353,371,373,377,400,414,419,439,445,484]
#test_hydro_veg#BI_CamGI=[294,307,313,331,344,366]
#test_hydro_veg#BI_Bara=[143,168,176,177,181,183,188,195,200,204,205,217,220,222,231,233,239,244,252,257,266,278,280,284,285,289,291,294,295]
#test_hydro_veg#BI_Bret=[29,34,39,40,42,44,47,49,52,54,55,67,68]
#test_hydro_veg#BI_Chand=[12,16,19,20,22,24,28,32]
#test_hydro_veg#
#test_hydro_veg## Create a list of lists - combines the compartment-to-bay lookup lists
#test_hydro_veg## - length of each lookup list can vary, flexible dimensions
#test_hydro_veg#IslandCompLists=[BI_Dern,BI_Timb,BI_CamGI,BI_Bara,BI_Bret,BI_Chand]
#test_hydro_veg#
#test_hydro_veg## create liste of ICM compartments that will be used as MHW for each BI group
#test_hydro_veg#IslandMHWCompLists = [598,493,348,281,43,15]
#test_hydro_veg#
#test_hydro_veg## Create blank dictionary to store lists of breached profile locations
#test_hydro_veg## Each key will be 'YYYY', which is the model year (in integer, NOT string, form)
#test_hydro_veg## Each year's list should only contain profiles breached in that year
#test_hydro_veg#breaches = {} 
#test_hydro_veg#   
#test_hydro_veg#
#test_hydro_veg############################################################
#test_hydro_veg####         SETTING UP MORPH MODEL              ##
#test_hydro_veg###########################################################
#test_hydro_veg#print(' Configuring ICM-Morph.')
#test_hydro_veg## change working directory to wetland morph folder
#test_hydro_veg#os.chdir(wetland_morph_dir)
#test_hydro_veg#sys.path.append(wetland_morph_dir)
#test_hydro_veg#
#test_hydro_veg###import Wetland Morph model
#test_hydro_veg##test_hydro_veg#import WM
#test_hydro_veg#
#test_hydro_veg### read Wetland Morph parameters csv file into array (first column is descriptor, second column is variable)                            
#test_hydro_veg#WM_params = np.genfromtxt(WMConfigFile,dtype=str,delimiter=',',usecols=1)                              
#test_hydro_veg#
#test_hydro_veg#
#test_hydro_veg##########################################################
#test_hydro_veg###              SETTING UP HSI MODEL                   ##
#test_hydro_veg##########################################################
#test_hydro_veg#print(' Configuring ICM-HSI.')
#test_hydro_veg## change working directory to veg folder
#test_hydro_veg#os.chdir(HSI_dir)
#test_hydro_veg#sys.path.append(HSI_dir)
#test_hydro_veg#
#test_hydro_veg#import HSI
#test_hydro_veg#


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
##              START YEARLY TIMESTEPPING              ##
#########################################################

for year in range(startyear+elapsed_hotstart,endyear+1):
    print('\n--------------------------------------------------')
    print('  START OF MODEL TIMESTEPPING LOOP - YEAR %s' % year)
    print('--------------------------------------------------\n')
    
    ## Check if current year is a leap year
    if year in range(1984,4000,4):
        ndays = 366
        print(r' Current model year (%s) is a leap year - input timeseries must include leap day' % year)
    else:
        ndays = 365


    #########################################################
    ##     SETTING UP 1D HYDRO MODEL FOR CURRENT YEAR      ##
    #########################################################
    
    for i in range (0,n_1D):
        print(r' Preparing 1D Channel Hydro Input Files for reach %d - Year %s' % (i,year))
        
        Rmfile = os.path.normpath(r'%s/input/hydro.inp' % HydroConfigFile[i])
        f1 = open(Rmfile, "r") 
        templine = f1.readlines() 
        f1.close()
        RmTemp = os.path.normpath(r'%s/input/temp.txt' % HydroConfigFile[i])
        f2 = open(RmTemp, "w")
        idx2 = 1
        for pl in templine:
            if idx2 == 5:
                f2.write('input/Upstream/Discharge_%s.txt =: upstream_path\n' % year)
                idx2 += 1
            elif idx2 == 6:
                f2.write('input/Downstream/WL_%s.txt =: downstream_path\n' % year)
                idx2 += 1
            elif idx2 == 9:
                f2.write('input/Lateral/%s/ =: lateralFlow_path\n' % year)
                idx2 += 1
            else:
                f2.writelines(pl)
                idx2 += 1
        f2.close()        
        if year == startyear:
            os.remove(Rmfile)
            os.rename(RmTemp,Rmfile)
        else:
            RmfileBackup = os.path.normpath(r'%s/input/hydro_%s.inp' % (HydroConfigFile[i],(year-1)))
            os.rename(Rmfile,RmfileBackup)
            os.rename(RmTemp,Rmfile)
        # convert filepath delimiter to backslash if running on Windows (this is for text I/O passed into Fortran executables)
        if os.name == 'nt':
            forward2backslash(Rmfile)
            
        if Sub_Sal[i]=="1":
            Rmfile = os.path.normpath(r'%s/input/sal.inp' % SalConfigFile[i])
            f1 = open(Rmfile, "r") 
            templine = f1.readlines() 
            f1.close()
            RmTemp = os.path.normpath(r'%s/input/temp.txt' % SalConfigFile[i])
            f2 = open(RmTemp, "w")
            idx2 = 1
            for pl in templine:
                if idx2 == 5:
                    f2.write('input/Upstream/upstream_sal_%s.txt            ! File that contains upstream concentration BC for all particle classes consided (1, 2, 3, ...)\n' % year)
                    idx2 += 1
                elif idx2 == 6:
                    f2.write('input/Downstream/downstream_sal_%s.txt        ! File that contains downstream concentration BC for all particle classes consided (1, 2, 3, ...)\n' % year)
                    idx2 += 1
                elif idx2 == 8:
                    f2.write('input/Lateral/lateral_q_con_%s.txt            ! File that contains lateral Q and Con (1, 2, ..., Nlat)\n' % year)
                    idx2 += 1
                else:
                    f2.writelines(pl)
                    idx2 += 1
            f2.close()  
            if year == startyear:
                os.remove(Rmfile)
                os.rename(RmTemp,Rmfile)
            else:
                RmfileBackup = os.path.normpath(r'%s/input/sal_%s.inp' % (SalConfigFile[i],(year-1)))
                os.rename(Rmfile,RmfileBackup)
                os.rename(RmTemp,Rmfile)
            # convert filepath delimiter to backslash if running on Windows (this is for text I/O passed into Fortran executables)
            if os.name == 'nt':
                forward2backslash(Rmfile)
              
        if Sub_Temp[i]=="1":   
            Rmfile = os.path.normpath(r'%s/input/tmp.inp' % TempConfigFile[i])
            f1 = open(Rmfile, "r") 
            templine = f1.readlines() 
            f1.close()
            RmTemp = os.path.normpath(r'%s/input/temp.txt' % TempConfigFile[i])
            f2 = open(RmTemp, "w")
            idx2 = 1
            for pl in templine:
                if idx2 == 5:
                    f2.write('input/Upstream/upstream_temp_%s.txt           ! File that contains upstream concentration BC for all particle classes consided (1, 2, 3, ...)\n' % year)
                    idx2 += 1
                elif idx2 == 6:
                    f2.write('input/Downstream/downstream_temp_%s.txt       ! File that contains upstream concentration BC for all particle classes consided (1, 2, 3, ...)\n' % year)
                    idx2 += 1
                elif idx2 == 8:
                    f2.write('input/Lateral/lateral_q_con_%s.txt            ! File that contains lateral Q and Con (1, 2, ..., Nlat)\n' % year)
                    idx2 += 1
                elif idx2 == 10:
                    f2.write('input/Wind/U10_GI_ncep_%s.txt                 !Wind U10 input\n' % year)
                    idx2 += 1
                elif idx2 == 11:
                    f2.write('input\Tbk\Tback_GI_ncep_%s.txt                !Tback input\n' % year)
                    idx2 += 1     
                else:
                    f2.writelines(pl)
                    idx2 += 1
            f2.close()  
            if year == startyear:
                os.remove(Rmfile)
                os.rename(RmTemp,Rmfile)
            else:
                RmfileBackup = os.path.normpath(r'%s/input/tmp_%s.inp' % (TempConfigFile[i],(year-1)))
                os.rename(Rmfile,RmfileBackup)
                os.rename(RmTemp,Rmfile)
            # convert filepath delimiter to backslash if running on Windows (this is for text I/O passed into Fortran executables)
            if os.name == 'nt':
                forward2backslash(Rmfile)


        if Sub_Fine[i]=="1":
            Rmfile = os.path.normpath(r'%s/input/fine.inp' % FineConfigFile[i])
            f1 = open(Rmfile, "r") 
            templine = f1.readlines() 
            f1.close()
            RmTemp = os.path.normpath(r'%s/input/temp.txt' % FineConfigFile[i])
            f2 = open(RmTemp, "w")
            idx2 = 1
            for pl in templine:
                if idx2 == 12:
                    f2.write('input/Upstream/upstream_fine_%s.txt           ! File that contains upstream concentration BC for all particle classes consided (1, 2, 3, ...)\n' % year)
                    idx2 += 1
                elif idx2 == 13:
                    f2.write('input/Downstream/downstream_fine_%s.txt       ! File that contains downstream concentration BC for all particle classes consided (1, 2, 3, ...)\n' % year)
                    idx2 += 1
                elif idx2 == 16:
                    f2.write('input/Lateral/lateral_q_con_%s.txt            ! File that contains lateral Q and Con (1, 2, ..., Nlat)\n' % year)
                    idx2 += 1
                else:
                    f2.writelines(pl)
                    idx2 += 1
            f2.close()  
            if year == startyear:
                os.remove(Rmfile)
                os.rename(RmTemp,Rmfile)
            else:
                RmfileBackup = os.path.normpath(r'%s/input/fine_%s.inp' % (FineConfigFile[i],(year-1)))
                os.rename(Rmfile,RmfileBackup)
                os.rename(RmTemp,Rmfile)
            # convert filepath delimiter to backslash if running on Windows (this is for text I/O passed into Fortran executables)
            if os.name == 'nt':
                forward2backslash(Rmfile)
        
        if Sub_Sand[i]=="1":     
            Rmfile = os.path.normpath(r'%s/input/sand.inp' % SandConfigFile[i])
            f1 = open(Rmfile, "r") 
            templine = f1.readlines() 
            f1.close()
            RmTemp = os.path.normpath(r'%s/input/temp.txt' % SandConfigFile[i])
            f2 = open(RmTemp, "w")
            idx2 = 1
            for pl in templine:
                if idx2 == 12:
                    f2.write('input/Upstream/upstream_sand_%s.txt           ! File that contains upstream concentration BC for all particle classes consided (1, 2, 3, ...)\n' % year)
                    idx2 += 1
                elif idx2 == 13:
                    f2.write('input/Downstream/downstream_sand_%s.txt       ! File that contains downstream concentration BC for all particle classes consided (1, 2, 3, ...)\n' % year)
                    idx2 += 1
                elif idx2 == 16:
                    f2.write('input/Lateral/lateral_q_con_%s.txt            ! File that contains lateral Q and Con (1, 2, ..., Nlat)\n' % year)
                    idx2 += 1
                else:
                    f2.writelines(pl)
                    idx2 += 1
            f2.close()
            if year == startyear:
                os.remove(Rmfile)
                os.rename(RmTemp,Rmfile)
            else:
                RmfileBackup = os.path.normpath(r'%s/input/sand_%s.inp' % (SandConfigFile[i],(year-1)))
                os.rename(Rmfile,RmfileBackup)
                os.rename(RmTemp,Rmfile)
            # convert filepath delimiter to backslash if running on Windows (this is for text I/O passed into Fortran executables)
            if os.name == 'nt':
                forward2backslash(Rmfile)



    #########################################################
    ##                  RUN HYDRO MODEL                    ##
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
    if year != startyear+elapsed_hotstart:
#test_hydro_veg#        print(' Importing updated landscape attributes from Morphology output files - Year %s' % year)
#test_hydro_veg#        ## set output hotstart file generated from last model timestep to be new input hotstart file
        os.rename('hotstart_out.dat', 'hotstart_in.dat')
#test_hydro_veg#        ## update LW ratio in Cells.csv (compartment attributes table)
#test_hydro_veg#        # new pct water from WM output saved in temp folder during last model year (year-1)
#test_hydro_veg#        PctWaterFile = os.path.normpath(r'%s/PctWater_%s.csv' % (EHtemp_path,year-1))  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year-1) here instead of CurrentYear
#test_hydro_veg#        new_pctwater = np.genfromtxt(PctWaterFile,delimiter=',')
#test_hydro_veg#        new_pctwater_dict=dict((new_pctwater[n,0],new_pctwater[n,1]) for n in range(0,len(new_pctwater)))
#test_hydro_veg#        
#test_hydro_veg#        # move grid data file from location saved by previous year's Morph run to the Hydro directory (new_grid_filepath not defined until after Morph is run each year)
#test_hydro_veg#        os.rename(new_grid_filepath,EH_grid_filepath)
#test_hydro_veg#                
#test_hydro_veg#        # new pct upland from WM output saved in temp folder during last model year (year-1)
#test_hydro_veg#        PctUplandFile = os.path.normpath(r'%s/PctUpland_%s.csv' % (EHtemp_path,year-1))  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year-1) here instead of CurrentYear
#test_hydro_veg#        new_pctupland = np.genfromtxt(PctUplandFile,delimiter=',')
#test_hydro_veg#        new_pctupland_dict=dict((new_pctupland[n,0],new_pctupland[n,1]) for n in range(0,len(new_pctupland)))
#test_hydro_veg#        
#test_hydro_veg#        ## read in updated bed and land elevation values for compartments - save in dictionaries where compartment ID is the key
#test_hydro_veg#        ## column 1 = compartment ID, column 2 = bed elev, column 3 = land elev, column 4 - marsh edge length
#test_hydro_veg#        # The marsh elevation value is filtered in WM.CalculateEcohydroAttributes() such that the average marsh elevation can be no lower than the average bed elevation
#test_hydro_veg#        CompElevFile = os.path.normpath(r'%s/compelevs_end_%s.csv' % (EHtemp_path,year-1))  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year-1) here instead of CurrentYear
#test_hydro_veg#        new_compelev = np.genfromtxt(CompElevFile,delimiter=',',skip_header=1)
#test_hydro_veg#                
#test_hydro_veg#        new_OWelev_dict = dict((new_compelev[n,0],new_compelev[n,1]) for n in range(0,len(new_compelev)))
#test_hydro_veg#        new_Melev_dict = dict((new_compelev[n,0],new_compelev[n,2]) for n in range(0,len(new_compelev)))
#test_hydro_veg#        new_Medge_dict = dict((new_compelev[n,0],new_compelev[n,3]) for n in range(0,len(new_compelev)))
#test_hydro_veg#
#test_hydro_veg#        ## create blank dictionaries that will save changes in compartment attributes and initialize flags for counting updated compartments
#test_hydro_veg#        bedchange_dict={}
#test_hydro_veg#        marshchange_dict={}
#test_hydro_veg#        new_bed_dict={}
#test_hydro_veg#        new_marsh_dict={}
#test_hydro_veg#        
#test_hydro_veg#        orig_marsh_area = {}
#test_hydro_veg#        new_marsh_area = {}
#test_hydro_veg#        
#test_hydro_veg#        flag_cell_wat = 0
#test_hydro_veg#        flag_cell_upl = 0
#test_hydro_veg#        flag_bed_ch = 0
#test_hydro_veg#        flag_mar_ch = 0
#test_hydro_veg#        flag_edge_ch = 0
#test_hydro_veg#        
#test_hydro_veg### update Hydro compartment water/upland/marsh area attributes
#test_hydro_veg#        print(' Updating land/water ratios and bed/marsh elevation attributes for Hydro compartments - Year %s' % year)   
#test_hydro_veg#        for nn in range(0,len(EHCellsArray)):
#test_hydro_veg#            cellID = EHCellsArray[nn,0]
#test_hydro_veg#            cellarea = EHCellsArray[nn,1]         
#test_hydro_veg#            # update percent water only if new value was calculated in Morph (e.g. dicitionary has a key of cellID and value that is not -9999), otherwise keep last year value
#test_hydro_veg#            try:
#test_hydro_veg#                if new_pctwater_dict[cellID] != -9999:
#test_hydro_veg#                    EHCellsArray[nn,2] = new_pctwater_dict[cellID]
#test_hydro_veg#                else:
#test_hydro_veg#                    flag_cell_wat =+ 1
#test_hydro_veg#            except:
#test_hydro_veg#                flag_cell_wat += 1
#test_hydro_veg#            
#test_hydro_veg#            # update percent upland only if new value was calculated in Morph (e.g. dictionary has a key of cellID and value that is not -9999), otherwise keep last year value
#test_hydro_veg#            try:
#test_hydro_veg#                if new_pctupland_dict[cellID] != -9999:
#test_hydro_veg#                    EHCellsArray[nn,3] = new_pctupland_dict[cellID]
#test_hydro_veg#                else:
#test_hydro_veg#                    flag_cell_upl += 1
#test_hydro_veg#            except:
#test_hydro_veg#                flag_cell_upl += 1
#test_hydro_veg#                
#test_hydro_veg#            
#test_hydro_veg#            # update marsh edge area, in attributes array
#test_hydro_veg#            try:
#test_hydro_veg#                if new_Medge_dict[cellID] != -9999:
#test_hydro_veg#                    EHCellsArray[nn,5] = new_Medge_dict[cellID]
#test_hydro_veg#            except:
#test_hydro_veg#                    flag_edge_ch += 1
#test_hydro_veg#            
#test_hydro_veg#            # update percent marsh - use cell array, rather than new dictionaries to account for compartments that weren't updated by Morph
#test_hydro_veg#            orig_marsh_area[nn] = EHCellsArray[nn,4]*cellarea
#test_hydro_veg#            EHCellsArray[nn,4] = max((1-EHCellsArray[nn,2]-EHCellsArray[nn,3]),0)
#test_hydro_veg#            new_marsh_area[nn] = EHCellsArray[nn,4]*cellarea
#test_hydro_veg#            
#test_hydro_veg#            # update Hydro compartment/link elevation attributes (if turned on as model option)
#test_hydro_veg#        if update_hydro_attr == 0:
#test_hydro_veg#            print(' Hydro link and compartment attributes are not being updated (update_hydro_attr = 0)')
#test_hydro_veg#        
#test_hydro_veg#        else:
#test_hydro_veg#            
#test_hydro_veg#            # calculate change in bed elevation if new value was calculated in Morph (e.g. dictionary has a key of cellID and value that is not -9999)
#test_hydro_veg#            # set change value to zero if value is NoData or if key does not exist
#test_hydro_veg#            try:
#test_hydro_veg#                if new_OWelev_dict[cellID] != -9999:
#test_hydro_veg#                    bedchange_dict[cellID] = new_OWelev_dict[cellID]-EHCellsArray[nn,7]
#test_hydro_veg#                else:
#test_hydro_veg#                    bedchange_dict[cellID] = 0.0
#test_hydro_veg#                    flag_bed_ch += 1
#test_hydro_veg#            except:
#test_hydro_veg#                bedchange_dict[cellID] = 0.0
#test_hydro_veg#                flag_bed_ch += 1
#test_hydro_veg#            
#test_hydro_veg#            # calculate change in marsh elevation if new value was calculated in Morph (e.g. dictionary has a key of cellID and value that is not -9999)
#test_hydro_veg#            # set change value to zero if value is NoData or if key does not exist
#test_hydro_veg#            # as noted above, the new marsh elevation value is filtered in WM.CalculateEcohydroAttributes() such that the average marsh elevation can never be below average bed elevation
#test_hydro_veg#            try:
#test_hydro_veg#                if new_Melev_dict[cellID] != -9999:
#test_hydro_veg#                    marshchange_dict[cellID] = new_Melev_dict[cellID]-EHCellsArray[nn,25]
#test_hydro_veg#                else:
#test_hydro_veg#                    marshchange_dict[cellID] = 0.0
#test_hydro_veg#                    flag_mar_ch += 1
#test_hydro_veg#            except:
#test_hydro_veg#                marshchange_dict[cellID] = 0.0
#test_hydro_veg#                flag_mar_ch += 1
#test_hydro_veg#            
#test_hydro_veg#            # update elevation of marsh area, in attributes array
#test_hydro_veg#            EHCellsArray[nn,25] += marshchange_dict[cellID]
#test_hydro_veg#            # update bed elevation of open water area in attributes array
#test_hydro_veg#            EHCellsArray[nn,7] += bedchange_dict[cellID]
#test_hydro_veg#            
#test_hydro_veg#            # save updated elevations into dictionaries to use for filtering link elevations in next section
#test_hydro_veg#            new_bed_dict[cellID] = EHCellsArray[nn,7]
#test_hydro_veg#            new_marsh_dict[cellID] = EHCellsArray[nn,25]
#test_hydro_veg#                
#test_hydro_veg#            
#test_hydro_veg#
#test_hydro_veg#            ## update Hydro link attributes                                 
#test_hydro_veg#            print(' Updating elevation attributes for Hydro links - Year %s' % year)
#test_hydro_veg#            for mm in range(0,len(EHLinksArray)):
#test_hydro_veg#                linkID = EHLinksArray[mm,0]
#test_hydro_veg#                linktype = EHLinksArray[mm,7]
#test_hydro_veg#                us_comp = EHLinksArray[mm,1]
#test_hydro_veg#                ds_comp = EHLinksArray[mm,2]
#test_hydro_veg#                
#test_hydro_veg#                # determine maximum of updated upstream and downstream bed elevations
#test_hydro_veg#                limiting_bed_elev = max(new_bed_dict[us_comp],new_bed_dict[ds_comp])
#test_hydro_veg#                limiting_marsh_elev = max(new_marsh_dict[us_comp],new_marsh_dict[ds_comp])
#test_hydro_veg#                
#test_hydro_veg#                ## update link invert elevations for channels
#test_hydro_veg#                if linktype == 1:
#test_hydro_veg#                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
#test_hydro_veg#                    ## invert elevation is attribute1 for channels (column 8 in links array)
#test_hydro_veg#                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
#test_hydro_veg#                    EHLinksArray[mm,8] = newelev
#test_hydro_veg#                    
#test_hydro_veg#                    ## only one channel bank elevation, it is equal to the lower of the US or DS marsh elevations
#test_hydro_veg#                    ## channel bank elevation is attribute2 for channels (column 9 in links array)
#test_hydro_veg#                    EHLinksArray[mm,9] = limiting_marsh_elev
#test_hydro_veg#                    
#test_hydro_veg#                ## update bed elevations for weirs
#test_hydro_veg#                elif linktype == 2:
#test_hydro_veg#                    ## upstream elevations are not allowed to be below the US bed elevation
#test_hydro_veg#                    ## upstream elevation is attribute2 for weirs and ridges/levees (column 9 in links array)
#test_hydro_veg#                    newelevus = max((EHLinksArray[mm,9] + bedchange_dict[us_comp]),new_bed_dict[us_comp])
#test_hydro_veg#                    EHLinksArray[mm,9] = newelevus
#test_hydro_veg#                
#test_hydro_veg#                    ## downstream elevations are not allowed to be below the DS bed elevation
#test_hydro_veg#                    ## downstream elevation is attribute3 for weirs (column 10 in links array)
#test_hydro_veg#                    newelevds = max((EHLinksArray[mm,10] + bedchange_dict[ds_comp]),new_bed_dict[ds_comp])
#test_hydro_veg#                    EHLinksArray[mm,10] = newelevds
#test_hydro_veg#                
#test_hydro_veg#                ## update link invert elevations for locks            
#test_hydro_veg#                elif linktype == 3:
#test_hydro_veg#                    ## updated from change in OW bed elevation in upstream compartment
#test_hydro_veg#                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
#test_hydro_veg#                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
#test_hydro_veg#                    EHLinksArray[mm,8] = newelev            
#test_hydro_veg#            
#test_hydro_veg#                ## update elevations for tide gates
#test_hydro_veg#                elif linktype == 4:
#test_hydro_veg#                    ## invert elevation is attribute1 for tide gates (column 8 in links array)
#test_hydro_veg#                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
#test_hydro_veg#                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
#test_hydro_veg#                    EHLinksArray[mm,8] = newelev
#test_hydro_veg#                    
#test_hydro_veg#                    ## invert elevation is attribute3 for tide gates (column 10 in links array)
#test_hydro_veg#                    ## upstream elevation is not allowed to be below either the US bed elevation
#test_hydro_veg#                    newelevus = max((EHLinksArray[mm,10] + bedchange_dict[us_comp]),new_bed_dict[us_comp])
#test_hydro_veg#                    EHLinksArray[mm,10] = newelevus
#test_hydro_veg#                    
#test_hydro_veg#                    ## invert elevation is attribute5 for tide gates (column 12 in links array)
#test_hydro_veg#                    ## downstream elevation is not allowed to be below either the DS bed elevation
#test_hydro_veg#                    newelevds = max((EHLinksArray[mm,12] + bedchange_dict[us_comp]),new_bed_dict[ds_comp])
#test_hydro_veg#                    EHLinksArray[mm,12] = newelevds
#test_hydro_veg#                
#test_hydro_veg#                ## update elevations for orifices
#test_hydro_veg#                elif linktype == 5:
#test_hydro_veg#                    ## invert elevation is attribute1 for orifices (column 8 in links array)
#test_hydro_veg#                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
#test_hydro_veg#                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
#test_hydro_veg#                    EHLinksArray[mm,8] = newelev
#test_hydro_veg#                    
#test_hydro_veg#                    ## invert elevation is attribute3 for orifices (column 10 in links array)
#test_hydro_veg#                    ## upstream elevation is not allowed to be below either the US bed elevation
#test_hydro_veg#                    newelevus = max((EHLinksArray[mm,10] + bedchange_dict[us_comp]),new_bed_dict[us_comp])
#test_hydro_veg#                    EHLinksArray[mm,10] = newelevus
#test_hydro_veg#                    
#test_hydro_veg#                    ## invert elevation is attribute5 for orifices (column 12 in links array)
#test_hydro_veg#                    ## downstream elevation is not allowed to be below either the DS bed elevation
#test_hydro_veg#                    newelevds = max((EHLinksArray[mm,12] + bedchange_dict[us_comp]),new_bed_dict[ds_comp])
#test_hydro_veg#                    EHLinksArray[mm,12] = newelevds
#test_hydro_veg#                                
#test_hydro_veg#                ## update elevations for culverts
#test_hydro_veg#                elif linktype == 6:
#test_hydro_veg#                    ## invert elevation is attribute1 for culverts (column 8 in links array)
#test_hydro_veg#                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
#test_hydro_veg#                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
#test_hydro_veg#                    EHLinksArray[mm,8] = newelev
#test_hydro_veg#                
#test_hydro_veg#                ## don't need to update anything for pumps
#test_hydro_veg#                ##  elif linktype == 7:
#test_hydro_veg#                    
#test_hydro_veg#                ## update marsh elevation for marsh links
#test_hydro_veg#                elif linktype == 8:
#test_hydro_veg#                    ## only one invert elevation, it is not allowed to be below either the US or DS marsh elevation
#test_hydro_veg#                    ## unlike the bank elevation calculation for link type 1 this calculates the change from the original invert elevation (as opposed to just using the new marsh elevation) in case the original elevation defining marsh overland flow is above the average marsh elevation
#test_hydro_veg#                    newelev = max((EHLinksArray[mm,8] + marshchange_dict[us_comp]),(EHLinksArray[mm,8] + marshchange_dict[ds_comp]),limiting_marsh_elev)
#test_hydro_veg#                    EHLinksArray[mm,8] = newelev            
#test_hydro_veg#                
#test_hydro_veg#                ## update bed elevations for ridge/levee link types
#test_hydro_veg#                elif linktype ==9:
#test_hydro_veg#                    ## upstream elevations are not allowed to be below the US bed elevation
#test_hydro_veg#                    ## upstream elevation is attribute2 for ridges/levees (column 9 in links array)
#test_hydro_veg#                    ## unlike the bank elevation calculation for link type 1 this calculates the change from the original invert elevation (as opposed to just using the new marsh elevation) because the original elevation defining ridge overland flow is above the average marsh elevation
#test_hydro_veg#                    newelevus = max((EHLinksArray[mm,9] + bedchange_dict[us_comp]),new_bed_dict[us_comp])
#test_hydro_veg#                    EHLinksArray[mm,9] = newelevus
#test_hydro_veg#                    
#test_hydro_veg#                    ## downstream elevations are not allowed to be below the DS bed elevation
#test_hydro_veg#                    ## downstream elevation is attribute10 for ridges/levees (column 18 in links array)
#test_hydro_veg#                    ## unlike the bank elevation calculation for link type 1 this calculates the change from the original invert elevation (as opposed to just using the new marsh elevation) because the original elevation defining ridge overland flow is above the average marsh elevation
#test_hydro_veg#                    newelevds = max((EHLinksArray[mm,18] + bedchange_dict[ds_comp]),new_bed_dict[ds_comp])
#test_hydro_veg#                    EHLinksArray[mm,18] = newelevds
#test_hydro_veg#                    
#test_hydro_veg#                ## update link invert elevations for regime channels
#test_hydro_veg#                elif linktype == 10:
#test_hydro_veg#                    ## updated from change in OW bed elevation in upstream compartment
#test_hydro_veg#                    ## only one invert elevation, it is not allowed to be below either the US or DS bed elevation
#test_hydro_veg#                    newelev = max((EHLinksArray[mm,8] + bedchange_dict[us_comp]),limiting_bed_elev)
#test_hydro_veg#                    EHLinksArray[mm,8] = newelev
#test_hydro_veg#                
#test_hydro_veg#
#test_hydro_veg#                # update link types for barrier island breaches in BIMODE's previous year run
#test_hydro_veg#                # check if link is representative of a barrier island breach (will be a key in the linktoprofile dict)
#test_hydro_veg#                if linkID in linktoprofile.keys():
#test_hydro_veg#                    # check if barrier island breach link is currently dormant
#test_hydro_veg#                    if linktype < 0:
#test_hydro_veg#                        # check if corresponding BIMMODE profile was breached in previous year
#test_hydro_veg#                        if linktoprofile[linkID] in breaches[year-1]:
#test_hydro_veg#                            newlinktype = -linktype
#test_hydro_veg#                            EHLinksArray[mm,7] = newlinktype 
#test_hydro_veg#    
#test_hydro_veg#    ## end update of Hydro compartment attributes            
#test_hydro_veg#        print(' %s Hydro compartments have updated percent land values for model year %s.' % ((len(EHCellsArray)-flag_cell_upl),year) )
#test_hydro_veg#        print(' %s Hydro compartments have updated percent water values for model year %s.' % ((len(EHCellsArray)-flag_cell_wat),year) )
#test_hydro_veg#        print(' %s Hydro compartments have updated average bed elevations for model year %s.' % ((len(EHCellsArray)-flag_bed_ch),year) )
#test_hydro_veg#        print(' %s Hydro compartments have updated average marsh elevations for model year %s.' % ((len(EHCellsArray)-flag_mar_ch),year) )
#test_hydro_veg#        print(' %s Hydro compartments have updated marsh edge lengths for model year %s.' % ((len(EHCellsArray)-flag_edge_ch),year) )
#test_hydro_veg#        
#test_hydro_veg#        # update links for project implmentation
#test_hydro_veg#        # if project links are to be changed during model year update those links by looping through link attributes array
#test_hydro_veg#        if year in link_years:
#test_hydro_veg#            print('  Some links are set to be activated or deactivated for this model year due to project implementation.')
#test_hydro_veg#            for mm in range(0,len(EHLinksArray)):
#test_hydro_veg#                linkID = EHLinksArray[mm,0]
#test_hydro_veg#                if linkID in links_to_change:
#test_hydro_veg#                    yearindex = links_to_change.index(linkID)    
#test_hydro_veg#                    if year == link_years[yearindex]:
#test_hydro_veg#                        print(' Link type for link %s is being activated (or deactivated if already active).' % linkID)
#test_hydro_veg#                        oldlinktype = EHLinksArray[mm,7]
#test_hydro_veg#                        newlinktype = -1*oldlinktype
#test_hydro_veg#                        EHLinksArray[mm,7] = newlinktype
#test_hydro_veg#                
#test_hydro_veg#        ## update link width for 'composite' marsh links if marsh creation project was implemented in previous year
#test_hydro_veg#        # link length is attribute 3 (column 11 in links array)
#test_hydro_veg#        # link width is attribute 4 (column 12 in links array)   
#test_hydro_veg#        if year in mc_links_years:
#test_hydro_veg#            print('  Some composite marsh flow links are being updated due to marsh creation projects implemented during last year.')
#test_hydro_veg#            for mm in range(0,len(EHLinksArray)):
#test_hydro_veg#                linkID = EHLinksArray[mm,0]
#test_hydro_veg#                linktype = EHLinksArray[mm,7]
#test_hydro_veg#                us_comp = EHLinksArray[mm,1]
#test_hydro_veg#                ds_comp = EHLinksArray[mm,2]    
#test_hydro_veg#                if linktype == 11:
#test_hydro_veg#                    if linkID in mc_links:
#test_hydro_veg#                        linkindex = mc_links.index(linkID)
#test_hydro_veg#                        if year == mc_links_years[linkindex]:
#test_hydro_veg#                            print(' Updating composite marsh flow link (link %s) for marsh creation project implemented in previous year.' % mm)
#test_hydro_veg#                            darea_us = new_marsh_area[us_comp] - orig_marsh_area[us_comp]            
#test_hydro_veg#                            darea_ds = new_marsh_area[ds_comp] - orig_marsh_area[ds_comp]
#test_hydro_veg#                            origwidth = EHLinksArray[mm,12]
#test_hydro_veg#                            length = EHLinksArray[mm,11]
#test_hydro_veg#                            # change in link area is equal to the increase in marsh area between the two compartments
#test_hydro_veg#                            newwidth = origwidth*length - (darea_us + darea_ds)/length
#test_hydro_veg#                            EHLinksArray[mm,12] = max(newwidth,30) # do not let marsh link go to zero - allow some flow, minimum width is one pixel wide
#test_hydro_veg#        
        ## save updated Cell and Link attributes to text files read into Hydro model                      
        np.savetxt(EHCellsFile,EHCellsArray,fmt='%.12f',header=cellsheader,delimiter=',',comments='')
        np.savetxt(EHLinksFile,EHLinksArray,fmt='%.12f',header=linksheader,delimiter=',',comments='')
    
#test_hydro_veg#    if year in hyd_switch_years:
#test_hydro_veg#        for nnn in range(0,len(hyd_file_orig)):
#test_hydro_veg#            oldfile = hyd_file_orig[nnn]
#test_hydro_veg#            newfile = hyd_file_new[nnn]
#test_hydro_veg#            bkfile = hyd_file_bk[nnn]
#test_hydro_veg#            print(' Copying %s to use as the new %s.' % (newfile, oldfile))
#test_hydro_veg#            print(' Saving original %s as %s.' % (oldfile,bkfile))
#test_hydro_veg#            os.rename(oldfile,bkfile)
#test_hydro_veg#            os.rename(newfile,oldfile)
    
    print('\n--------------------------------------------------')
    print('  RUNNING HYDRO MODEL - Year %s' % year)
    print('--------------------------------------------------\n' )
    print(' See %s for Hydro runtime logs.' % hydro_logfile)
     
    # run compiled Fortran executable - will automatically return to Python window when done running
    hydrorun = os.system('hydro_v23.2.0.exe')
       
    if hydrorun != 0:
        print('******ERROR******')
        error_msg = '\n Hydro model run for year %s was unsuccessful.' % year
        sys.exit(error_msg)    
    
    # Clean up and set Ecohydro up for next year model run
    print(r' Cleaning up after Hydro Model - Year %s' % year)
    ## update startrun value for next model year
    startrun = endrun + 1
    ## calculate elapsed years of model run
    elapsedyear = year - startyear + 1

    ## append year to names and move hotstart,config, cells, links, and grid files to temp folder so new ones can be written for next model year
    print(' Cleaning up Hydro output files.')
    
    move_hs = os.path.normpath(r"%s/hotstart_in_%s.dat" % (EHtemp_path,year))
    os.rename('hotstart_in.dat',move_hs)
    
    move_EHconfig = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EHConfigFile,'.')[0],year,str.split(EHConfigFile,'.')[1]))
    os.rename(EHConfigFile,move_EHconfig)

    move_EHcell = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EHCellsFile,'.')[0],year,str.split(EHCellsFile,'.')[1]))
    os.rename(EHCellsFile,move_EHcell)

    move_EHlink = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EHLinksFile,'.')[0],year,str.split(EHLinksFile,'.')[1]))
    os.rename(EHLinksFile,move_EHlink)

#test_hydro_veg#    move_EH_gridfile = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EH_grid_file,'.')[0],year,str.split(EH_grid_file,'.')[1]))  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year-1) here instead of CurrentYear
#test_hydro_veg#    os.rename(EH_grid_filepath,move_EH_gridfile)

    # read in compartment output from hydro model to generate input file for BIMODE
    EH_comp_results_file = os.path.normpath('%s/%s') % (ecohydro_dir,compartment_output_file)
    EH_comp_out = np.genfromtxt(EH_comp_results_file,dtype='float',delimiter=',',names=True)
    
    #generate single string from names that will be used as header when writing output file
    compnames = EH_comp_out.dtype.names
    compheader = compnames[0]
    
    for n in range(1,len(compnames)):
        compheader +=',%s' % compnames[n]
    
    # re-write compartment output file with year appended to name - file is re-written (as opposed to moved) to ensure floating point format will be correct for import into WM.ImportEcohydroResults - corrects issues with Fortran formatting
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
    
#test_hydro_veg#    # create dictionary where key is compartment ID, value is tidal prism (Column 14 of Ecohydro output)
#test_hydro_veg#    EH_prisms = dict((EH_comp_out[n][0],EH_comp_out[n][13]) for n in range(0,len(EH_comp_out)))
#test_hydro_veg#    
#test_hydro_veg#    # create dictionary where key is compartment ID, values is mean water (column 3 of Ecohydro output)
#test_hydro_veg#    EH_MHW = dict((EH_comp_out[n][0],EH_comp_out[n][2]) for n in range(0,len(EH_comp_out)))
#test_hydro_veg#
#test_hydro_veg#
#test_hydro_veg#    # Initialize tidal prism and MHW arrays to zero - will write over previous year's array
#test_hydro_veg#    BIMODEprisms = np.zeros(shape=len(IslandCompLists))
#test_hydro_veg#    BIMODEmhw = np.zeros(shape=len(IslandMHWCompLists))
#test_hydro_veg#
#test_hydro_veg#    # Loop through each Barrier Islands Ecohydro compartments
#test_hydro_veg#    # Add compartment tidal prism volumes to calculate total bay tidal prism for each island    
#test_hydro_veg#    for n in range(0,len(IslandCompLists)):
#test_hydro_veg#        BI = IslandCompLists[n]
#test_hydro_veg#        for k in range(0,len(BI)):
#test_hydro_veg#            comp=BI[k]
#test_hydro_veg#    # compartment 296 is split between two different sets of Barrier Islands - therefore its volume is cut in half          
#test_hydro_veg#            if comp==296:
#test_hydro_veg#                BIMODEprisms[n] += EH_prisms[comp]/2
#test_hydro_veg#            else:
#test_hydro_veg#                BIMODEprisms[n] += EH_prisms[comp]    
#test_hydro_veg#
#test_hydro_veg#    for n in range(0,len(IslandMHWCompLists)):
#test_hydro_veg#        comp = IslandMHWCompLists[n]
#test_hydro_veg#        BIMODEmhw[n] = EH_MHW[comp]
#test_hydro_veg#
#test_hydro_veg#    del(EH_comp_out,EH_grid_out)
#test_hydro_veg#
#test_hydro_veg#    #########################################################
#test_hydro_veg#    ##              RUN BARRIER ISLAND MODEL               ##
#test_hydro_veg#    #########################################################
#test_hydro_veg#
#test_hydro_veg#    print('\n--------------------------------------------------' )
#test_hydro_veg#    print('  RUNNING BARRIER ISLAND MODEL - Year %s' % year)
#test_hydro_veg#    print('--------------------------------------------------\n')
#test_hydro_veg#    print(' See separate log files generated by each BIMODE run.')
#test_hydro_veg#    
#test_hydro_veg#                   
#test_hydro_veg#    # initialize breach dictionary key for current year to an empty list
#test_hydro_veg#    # this will be appended to with the profile numbers that have been breached
#test_hydro_veg#    breaches[year]=[]
#test_hydro_veg#    
#test_hydro_veg#    # initialize array to pass profile output files into Wetland Morph
#test_hydro_veg#    BMprof_forWM =[]
#test_hydro_veg#    
#test_hydro_veg#
#test_hydro_veg#    
#test_hydro_veg#    # write Tidal Prism file in made BIMODE folder
#test_hydro_veg#    # Generate tab-seperated file of tidal prism volumes    
#test_hydro_veg#    prism_file_for_bimode = os.path.normpath(r'%s/%s' % (bimode_dir,BIPrismFile))
#test_hydro_veg#    with open(prism_file_for_bimode,'w') as f:                        
#test_hydro_veg#        f.write('% Tidal Prism\t%Region')                            
#test_hydro_veg#        f.write('\n')
#test_hydro_veg#        for n in range(0,len(IslandCompLists)):
#test_hydro_veg#            prism = str(BIMODEprisms[n])+'\t'+str(n+1)
#test_hydro_veg#            f.write(prism)
#test_hydro_veg#            f.write('\n')
#test_hydro_veg#    
#test_hydro_veg#    mhw_file_for_bimode = os.path.normpath(r'%s/%s' % (bimode_dir,BIMHWFile))
#test_hydro_veg#    with open(mhw_file_for_bimode,'w') as f:                        
#test_hydro_veg#        f.write('% MHW (m NAVD88)\t%SLR_A\t%SLR_B\t%Region ')                            
#test_hydro_veg#        f.write('\n')
#test_hydro_veg#        for n in range(0,len(IslandMHWCompLists)):
#test_hydro_veg#            bmhw = str(BIMODEmhw[n])+'\t0.000\t0.000\t'+str(n+1)
#test_hydro_veg#            f.write(bmhw)
#test_hydro_veg#            f.write('\n')
#test_hydro_veg#
#test_hydro_veg#
#test_hydro_veg#    # loop BIMODE runs over the different folders - each with individual executables and I/O
#test_hydro_veg#    for fol in bimode_folders:
#test_hydro_veg#        print('\n Modeling %s' % fol)
#test_hydro_veg#        bmdir = os.path.normpath(r'%s/%s' %(bimode_dir,fol))
#test_hydro_veg#        os.chdir(bmdir)
#test_hydro_veg#    
#test_hydro_veg#    # copy tidal prism file into specific BIMODE folder (shutil.copy will overwrite any existing tidal prism file that has the same name)
#test_hydro_veg#        prism_file_for_folder = os.path.normpath('%s/input/%s' %(bmdir,BIPrismFile))
#test_hydro_veg#        shutil.copy(prism_file_for_bimode,prism_file_for_folder)
#test_hydro_veg#    # copy MHW file into specific BIMODE folder (shutil.copy will overwrite any existing tidal prism file that has the same name)
#test_hydro_veg#        mhw_file_for_folder = os.path.normpath('%s/input/%s' %(bmdir,BIMHWFile))
#test_hydro_veg#        shutil.copy(mhw_file_for_bimode,mhw_file_for_folder)
#test_hydro_veg#    
#test_hydro_veg#    
#test_hydro_veg#        
#test_hydro_veg## run compiled Fortran executable - will automatically return to Python window when done running
#test_hydro_veg#        print(' Running BIMODE executable for %s region.' % fol)
#test_hydro_veg#        bimoderun = os.system('bimo.exe')
#test_hydro_veg#        
#test_hydro_veg#        if bimoderun != 0:
#test_hydro_veg#            print('\n\n  BIMODE did not run for year %s.' % year  )
#test_hydro_veg#            waittime = random.random()*60
#test_hydro_veg#            print('\n Retrying BIMODE model run for year %s after waiting %.2f seconds.' % (year,waittime)  )
#test_hydro_veg#            print(' Waiting...')
#test_hydro_veg#            time.sleep(waittime)
#test_hydro_veg#            print(' Done waiting. Retrying BIMODE now.')
#test_hydro_veg#            bimoderun = os.system('bimo.exe')
#test_hydro_veg#
#test_hydro_veg#            if bimoderun != 0:
#test_hydro_veg#                print('\n\n  BIMODE still did not run for year %s.' % year  )
#test_hydro_veg#                waittime = random.random()*60
#test_hydro_veg#                print('\n Retrying BIMODE model run for year %s after waiting %.2f seconds.' % (year,waittime)    )
#test_hydro_veg#                print(' Waiting...')
#test_hydro_veg#                time.sleep(waittime)
#test_hydro_veg#                print(' Done waiting. Retrying BIMODE now.')
#test_hydro_veg#                bimoderun = os.system('bimo.exe')
#test_hydro_veg#
#test_hydro_veg#                if bimoderun != 0:
#test_hydro_veg#                    error_msg = '\n BIMODE model run for year %s was unsuccessful.' % year
#test_hydro_veg#                    sys.exit(error_msg)
#test_hydro_veg#
#test_hydro_veg#    
#test_hydro_veg## rename existing tidal prism files by appending model year to file name
#test_hydro_veg#        print(' Cleaning up BIMODE files for %s region.' % fol)
#test_hydro_veg#        prismfile_noext = BIPrismFile.split('.')
#test_hydro_veg#        rename_BMprism = os.path.normpath(r'%s/input/%s_%04d.%s' % (bmdir,prismfile_noext[0],year-startyear+1,prismfile_noext[1]))
#test_hydro_veg#
#test_hydro_veg## first try rename, so that a warning is given that the existing tidal prism file is being overwritten (only occurs if old model run data exists)    
#test_hydro_veg#        try:
#test_hydro_veg#            os.rename(prism_file_for_folder,rename_BMprism)
#test_hydro_veg#        except OSError as Exception:
#test_hydro_veg#            if Exception.errno == errno.EEXIST:
#test_hydro_veg#                print(' Tidal prism file %s already exists.' % rename_BMprism)
#test_hydro_veg#                print(' The pre-existing file was deleted and overwritten.')
#test_hydro_veg#                shutil.copy(prism_file_for_folder,rename_BMprism)
#test_hydro_veg#
#test_hydro_veg#        # read in profiles that were breached during model year
#test_hydro_veg#        breachfile = os.path.normpath('%s/results/Breaching_%04d' %(bmdir,elapsedyear))   #BIMODE uses output files use elapsed years, BIMODE file at end of startyear = filename1
#test_hydro_veg#        brs = np.genfromtxt(breachfile,skip_header=1)
#test_hydro_veg#        # read through profiles and append to breach dictionary for year if breached
#test_hydro_veg#        for n in range(0,len(brs)):
#test_hydro_veg#            if brs[n,1] == 1.:
#test_hydro_veg#                   breaches[year].append(brs[n,0])
#test_hydro_veg#
#test_hydro_veg#
#test_hydro_veg#        ## append profile files to array that gets passed to WM.py - use np.vstack if profile array has already been started
#test_hydro_veg#        print(' Adding BIMODE output profile data for %s into array with profiles from other regions.' % fol)
#test_hydro_veg#        profilefile = os.path.normpath('%s/results/profile_%04d' %(bmdir,year-startyear+1))
#test_hydro_veg#        if len(BMprof_forWM) == 0:
#test_hydro_veg#            BMprof_forWM=np.genfromtxt(profilefile,usecols=[0,1,2]) #ignore last column of file, which is the profile ID #
#test_hydro_veg#        else:
#test_hydro_veg#            BMprof_forWM=np.vstack((BMprof_forWM,np.genfromtxt(profilefile,usecols=[0,1,2])))
#test_hydro_veg#        # check BIMODE results folder for separate 'window file' which is proflies located in island passes
#test_hydro_veg#        
#test_hydro_veg#        # if this file exists, append those xyz values to BMprof_forWM with np.vstack
#test_hydro_veg#        passprofilefile = os.path.normpath('%s/results/window_file_%04d' %(bmdir,year-startyear+1))
#test_hydro_veg#        if os.path.isfile(passprofilefile) == True:
#test_hydro_veg#            BMprof_forWM=np.vstack((BMprof_forWM,np.genfromtxt(profilefile,usecols=[0,1,2],skip_header = 1)))
#test_hydro_veg#        
#test_hydro_veg#              
#test_hydro_veg#        
#test_hydro_veg#    ## write master file with all profile XYZ info to text file that gets read by WM.py function
#test_hydro_veg#    ## this will overwrite existing file named the same and located here (e.g. the previous year's file)
#test_hydro_veg#    ## this is intentional, since the profile data is all saved individually within BIMODE project folders
#test_hydro_veg#
#test_hydro_veg#    print('\n Writing all BIMODE profiles to single text file to pass to Morphology model.')
#test_hydro_veg#    BMprof_forWMfile = os.path.normpath(r'%s/BIMODEprofiles.xyz' %(bimode_dir))
#test_hydro_veg#    np.savetxt(BMprof_forWMfile,BMprof_forWM,delimiter='   ',comments='',fmt=['%.4f','%.4f','%.4f'])
#test_hydro_veg#    
#test_hydro_veg#    del BMprof_forWM
#test_hydro_veg#
#test_hydro_veg#    
#test_hydro_veg#    #########################################################
#test_hydro_veg#    ##                SETUP VEGETATION MODEL               ##
#test_hydro_veg#    #########################################################
#test_hydro_veg#    os.chdir(vegetation_dir)
#test_hydro_veg#    
#test_hydro_veg#    if year == startyear + elapsed_hotstart:
#test_hydro_veg#        print('\n--------------------------------------------------')
#test_hydro_veg#        print('        CONFIGURING VEGETATION MODEL')
#test_hydro_veg#        print('      - only during initial year of ICM -')
#test_hydro_veg#        print('--------------------------------------------------\n')        
#test_hydro_veg#
#test_hydro_veg#
#test_hydro_veg#
#test_hydro_veg#        sys.path.append(vegetation_dir)
#test_hydro_veg#        
#test_hydro_veg#        import model_v2
#test_hydro_veg#        
#test_hydro_veg#        LAVegMod = model_v2.Model()
#test_hydro_veg#        
#test_hydro_veg#        try:
#test_hydro_veg#            LAVegMod.config(VegConfigFile)
#test_hydro_veg#        except exceptions as error:
#test_hydro_veg#            print('******ERROR******')
#test_hydro_veg#            print(error)
#test_hydro_veg#            sys.exit('\nFailed to initialize Veg model.')
#test_hydro_veg#
#test_hydro_veg#    #########################################################
#test_hydro_veg#    ##                RUN VEGETATION MODEL                 ##
#test_hydro_veg#    #########################################################
#test_hydro_veg#    print('\n--------------------------------------------------')
#test_hydro_veg#    print('  RUNNING VEGETATION MODEL - Year %s' % year)
#test_hydro_veg#    print('--------------------------------------------------\n')
#test_hydro_veg#    
#test_hydro_veg#    
#test_hydro_veg#    try:
#test_hydro_veg#        LAVegMod.step()
#test_hydro_veg#    except exceptions.RuntimeError as error:
#test_hydro_veg#        print('\n ******ERROR******')
#test_hydro_veg#        print(error)
#test_hydro_veg#        sys.exit('Vegetation model run failed - Year %s.' % year)
#test_hydro_veg#    
#test_hydro_veg#    veg_output_file = '%s_O_%02d_%02d_V_vegty.asc+' % (runprefix,elapsedyear,elapsedyear)
#test_hydro_veg#    veg_deadfloat_file = '%s_O_%02d_%02d_V_deadf.asc' % (runprefix,elapsedyear,elapsedyear)
#test_hydro_veg#
#test_hydro_veg#    if os.path.isfile(veg_deadfloat_file) == False:
#test_hydro_veg#        veg_deadfloat_file = 'NONE'
#test_hydro_veg#        
#test_hydro_veg#
#test_hydro_veg#    #########################################################
#test_hydro_veg#    ##                  RUN MORPHOLOGY MODEL               ##
#test_hydro_veg#    #########################################################
#test_hydro_veg#    print('\n--------------------------------------------------')
#test_hydro_veg#    print(r'  RUNNING MORPHOLOGY MODEL - Year %s' % year)
#test_hydro_veg#    print('--------------------------------------------------\n')
#test_hydro_veg#    #change working directory to wetland morph folder
#test_hydro_veg#    os.chdir(wetland_morph_dir)
#test_hydro_veg#   
#test_hydro_veg#    #update WM config file with current model year
#test_hydro_veg#    WM_params[0] = runprefix
#test_hydro_veg#    WM_params[1] = str(year)
#test_hydro_veg#
#test_hydro_veg#    WM_params[54] = EH_grid_out_newfile
#test_hydro_veg#    WM_params[58] = EH_comp_out_newfile
#test_hydro_veg#    
#test_hydro_veg#    if elapsedyear in yearstokeepmorph:
#test_hydro_veg#        WM_params[62] = 'FALSE'
#test_hydro_veg#    else:
#test_hydro_veg#        WM_params[62] = 'TRUE'
#test_hydro_veg#    
#test_hydro_veg#    # Update morphology model input parameters for project implemented during current model year
#test_hydro_veg#    # Implement marsh creation projects
#test_hydro_veg#    if year in mc_years:
#test_hydro_veg#        pjindex = mc_years.index(year)
#test_hydro_veg#        WM_params[6] = mc_shps[pjindex]
#test_hydro_veg#        WM_params[7] = mc_shps_fields[pjindex]
#test_hydro_veg#    else:
#test_hydro_veg#        WM_params[6] = 'NONE'
#test_hydro_veg#        WM_params[7] = 'NONE'
#test_hydro_veg#    
#test_hydro_veg#    # Implement shoreline protetion projects
#test_hydro_veg#    if year in sp_years:
#test_hydro_veg#        pjindex = sp_years.index(year)
#test_hydro_veg#        WM_params[9] = sp_shps[pjindex]
#test_hydro_veg#        WM_params[10] = sp_shps_fields[pjindex]
#test_hydro_veg#    else:
#test_hydro_veg#        WM_params[9] = 'NONE'
#test_hydro_veg#        WM_params[10] = 'NONE'
#test_hydro_veg#        
#test_hydro_veg#    # Implement shoreline protetion projects
#test_hydro_veg#    if year in levee_years:
#test_hydro_veg#        pjindex = levee_years.index(year)
#test_hydro_veg#        WM_params[13] = levee_shps[pjindex]
#test_hydro_veg#        WM_params[14] = levee_shps_fields1[pjindex]
#test_hydro_veg#        WM_params[15] = levee_shps_fields2[pjindex]
#test_hydro_veg#        WM_params[16] = levee_shps_fields3[pjindex]
#test_hydro_veg#        WM_params[17] = levee_shps_fields4[pjindex]
#test_hydro_veg#    else:
#test_hydro_veg#        WM_params[13] = 'NONE'
#test_hydro_veg#        WM_params[14] = 'NONE'
#test_hydro_veg#        WM_params[15] = 'NONE'
#test_hydro_veg#        WM_params[16] = 'NONE'
#test_hydro_veg#        WM_params[17] = 'NONE'    
#test_hydro_veg#        
#test_hydro_veg#    
#test_hydro_veg#    #run Wetland Morph model
#test_hydro_veg#    try:
#test_hydro_veg#        WM.main(WM_params,ecohydro_dir,wetland_morph_dir,EHtemp_path,vegetation_dir,veg_output_file,veg_deadfloat_file,nvegtype,HSI_dir,BMprof_forWMfile,n500grid,n500rows,n500cols,yll500,xll500,n1000grid,elapsedyear)
#test_hydro_veg#    except Exception, error:
#test_hydro_veg#        print('******ERROR******')
#test_hydro_veg#        print(error)
#test_hydro_veg#        sys.exit('\n Morphology model run failed - Year %s.' % year)
#test_hydro_veg#
#test_hydro_veg#    # update name of grid data file generated by Morph to include current year in name
#test_hydro_veg#    new_grid_file = 'grid_data_500m_end%s.csv' % (year)  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year) here instead of CurrentYear
#test_hydro_veg#    new_grid_filepath = os.path.normpath('%s/%s' % (EHtemp_path,new_grid_file)) # location of grid file after it is generated in "WM.CalculateEcohydroAttributes"
#test_hydro_veg#
#test_hydro_veg#    ##############################################
#test_hydro_veg#    ##    HABITAT SUITABILITY INDICES ~ HSIs    ##
#test_hydro_veg#    ##############################################
#test_hydro_veg#    print('\n--------------------------------------------------')
#test_hydro_veg#    print('  RUNNING HABITAT SUITABILITY INDICES - Year %s' % year)
#test_hydro_veg#    print('--------------------------------------------------\n')
#test_hydro_veg#    os.chdir(ecohydro_dir)
#test_hydro_veg#
#test_hydro_veg#    # read in Morph output file
#test_hydro_veg#    print(' Reading in Morphology output files to be used for HSIs.')
#test_hydro_veg#    # import grid summary file (percent land, elevations) generated by Morphology
#test_hydro_veg#    griddata = np.genfromtxt(new_grid_filepath,delimiter=',',skip_header=1)
#test_hydro_veg#    # landdict is a dictionary of percent land (0-100) in each 500-m grid cell, key is gridID
#test_hydro_veg#    landdict = dict((griddata[n][0],griddata[n][3]) for n in range(0,n500grid))
#test_hydro_veg#    waterdict = dict((griddata[n][0],griddata[n][5]) for n in range(0,n500grid))
#test_hydro_veg#    melevdict = dict((griddata[n][0],griddata[n][2]) for n in range(0,n500grid))
#test_hydro_veg#    wetlanddict = dict((griddata[n][0],griddata[n][4]) for n in range(0,n500grid))
#test_hydro_veg#    
#test_hydro_veg#    # Post-process Ecohydro output for HSI calculations
#test_hydro_veg#    print(' Reading in Ecohydro output files to be used for HSIs.'   )
#test_hydro_veg#
#test_hydro_veg#    # import annual Ecohydro output that is summarized by grid ID (Column 0 corresponds to 500m ID#, Column 7 is percent sand, and  Column 17 is average depth)    
#test_hydro_veg#    EH_grid_out = np.genfromtxt(EH_grid_results_filepath,delimiter = ',',skip_header = 1)
#test_hydro_veg#    depthdict = dict((EH_grid_out[n][0],EH_grid_out[n][15:17]) for n in range(0,n500grid)) # column 15 is mean summer depth, column 16 is mean annual depth
#test_hydro_veg#    stagedict = dict((EH_grid_out[n][0],EH_grid_out[n][12]) for n in range(0,n500grid))
#test_hydro_veg#    # Import percent sand in substrate for HSI data
#test_hydro_veg#    pctsanddict = dict((EH_grid_out[n][0],EH_grid_out[n][7]) for n in range(0,n500grid))
#test_hydro_veg#
#test_hydro_veg#    del(EH_grid_out)
#test_hydro_veg#
#test_hydro_veg#    # Import monthly values for HSI data in dictionaries
#test_hydro_veg#    # import ecohydro monthly output that is summarized by 500-m grid ID (Column 0 corresponds to GridID)    
#test_hydro_veg#    EH_sal_file = os.path.normpath(ecohydro_dir + '/sal_monthly_ave_500m.out')
#test_hydro_veg#    sal = np.genfromtxt(EH_sal_file,delimiter = ',',skip_header = 1)
#test_hydro_veg#    saldict = dict((sal[n][0],sal[n][1:14]) for n in range(0,n500grid))
#test_hydro_veg#
#test_hydro_veg#    # Save list of GridIDs from Hydro output file
#test_hydro_veg#    gridIDs=[]
#test_hydro_veg#    for n in range(0,n500grid):
#test_hydro_veg#       gridIDs.append(sal[n][0])
#test_hydro_veg#    del(sal)
#test_hydro_veg#    
#test_hydro_veg#    # Import monthly temperature values for HSI data
#test_hydro_veg#    EH_tmp_file = os.path.normpath(ecohydro_dir + '/tmp_monthly_ave_500m.out')
#test_hydro_veg#    tmp = np.genfromtxt(EH_tmp_file,delimiter = ',',skip_header = 1)
#test_hydro_veg#    tmpdict = dict((tmp[n][0],tmp[n][1:13]) for n in range(0,n500grid))
#test_hydro_veg#    del(tmp)
#test_hydro_veg#    
#test_hydro_veg#    # Import monthly TSS values for HSI data
#test_hydro_veg#    EH_TSS_file = os.path.normpath(ecohydro_dir + '/TSS_monthly_ave_500m.out')
#test_hydro_veg#    TSS = np.genfromtxt(EH_TSS_file,delimiter = ',',skip_header = 1)
#test_hydro_veg#    TSSdict = dict((TSS[n][0],TSS[n][1:13]) for n in range(0,n500grid))
#test_hydro_veg#    del(TSS)
#test_hydro_veg#
#test_hydro_veg#    # Import monthly algae values for HSI data
#test_hydro_veg#    EH_ChlA_file = os.path.normpath(ecohydro_dir + '/tkn_monthly_ave_500m.out')
#test_hydro_veg#    ChlA = np.genfromtxt(EH_ChlA_file,delimiter = ',',skip_header = 1)
#test_hydro_veg#    ChlAdict = dict((ChlA[n][0],ChlA[n][1:13]) for n in range(0,n500grid))
#test_hydro_veg#    del(ChlA)
#test_hydro_veg#
#test_hydro_veg#    veg_output_filepath = os.path.normpath(vegetation_dir + '/' + veg_output_file)
#test_hydro_veg#
#test_hydro_veg#    # run HSI function (run in HSI directory so output files are saved there)
#test_hydro_veg#    os.chdir(HSI_dir)
#test_hydro_veg#
#test_hydro_veg#    # import percent edge output from geomorph routine that is summarized by grid ID
#test_hydro_veg#    pctedge_file = os.path.normpath('%s/%s_N_%02d_%02d_W_pedge.csv'% (HSI_dir,runprefix,elapsedyear,elapsedyear)) # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year) here instead of CurrentYear
#test_hydro_veg#    pedge = np.genfromtxt(pctedge_file,delimiter = ',',skip_header = 1)
#test_hydro_veg#    pctedgedict = dict((pedge[n][0],pedge[n][1]) for n in range(0,n500grid))
#test_hydro_veg#    del(pedge)
#test_hydro_veg#    
#test_hydro_veg#    
#test_hydro_veg#    try:
#test_hydro_veg#        HSI.HSI(gridIDs,stagedict,depthdict,melevdict,saldict,tmpdict,TSSdict,ChlAdict,veg_output_filepath,nvegtype,landdict,waterdict,pctsanddict,pctedgedict,n500grid,n500rows,n500cols,yll500,xll500,year,elapsedyear,HSI_dir,WM_params,vegetation_dir,wetland_morph_dir,runprefix)
#test_hydro_veg#    except Exception,error :
#test_hydro_veg#        print('******ERROR******')
#test_hydro_veg#        print('\n HSI model run failed - Year %s.' % year)
#test_hydro_veg#        print(error)
#test_hydro_veg#        
#test_hydro_veg#
#test_hydro_veg#    ##########################################
#test_hydro_veg#    ##       FORMAT DATA FOR EWE MODEL      ##
#test_hydro_veg#    ##########################################
#test_hydro_veg#    print('\n--------------------------------------------------')
#test_hydro_veg#    print(' FORMATTING DATA FOR EWE - Year %s' % year)
#test_hydro_veg#    print('--------------------------------------------------\n')
#test_hydro_veg#    print(' Reading in ASCII grid template.')                                               
#test_hydro_veg#    os.chdir(ewe_dir)
#test_hydro_veg#    ewe_grid_ascii_file = 'EwE_grid.asc'                                                   
#test_hydro_veg#                                                                                           
#test_hydro_veg#    
#test_hydro_veg#    ascii_grid_lookup = np.genfromtxt(ewe_grid_ascii_file,delimiter=' ',skip_header=6)        
#test_hydro_veg#                                                                                           
#test_hydro_veg#    ascii_header='nrows %s \nncols %s \nyllcorner %s \nxllcorner %s \ncellsize 1000 \nnodata_value -9999' % (n1000rows,n1000cols,yll1000,xll1000)
#test_hydro_veg#
#test_hydro_veg#    nrows = n1000rows                                                                      
#test_hydro_veg#    ncols = n1000cols          
#test_hydro_veg#
#test_hydro_veg#    EwEGridMap = np.genfromtxt('EwE_Veg_grid_lookup.csv',skip_header=1,delimiter=',')         
#test_hydro_veg#    EwEGridMapDict = dict((EwEGridMap[n][0],EwEGridMap[n][1:5])for n in range(0,len(EwEGridMap)))
#test_hydro_veg#    
#test_hydro_veg#    for output in ['depth']:
#test_hydro_veg#        print(' - mapping %s output to EwE grid' % output)                                                 
#test_hydro_veg#        newgrid=np.zeros([nrows,ncols]) 
#test_hydro_veg#        for m in range(0,nrows):                                                           
#test_hydro_veg#            for n in range(0,ncols):                                                       
#test_hydro_veg#                cellID = ascii_grid_lookup[m][n]                                           
#test_hydro_veg#                if cellID == -9999:                                                        
#test_hydro_veg#                    newgrid[m][n] = -9999                                                  
#test_hydro_veg#                else:                                                                      
#test_hydro_veg#                    try:                                                                   
#test_hydro_veg#                        value = 0                                                          
#test_hydro_veg#                        value_n = 0                                                        
#test_hydro_veg#                        for g in range(0,4):                                               
#test_hydro_veg#                            grid = EwEGridMapDict[cellID][g]                               
#test_hydro_veg#                            if grid > 0:                                              
#test_hydro_veg#                                value += depthdict[grid][1] # depthdict[grid][0] is mean summer depth, depthdict[grid][1] is mean annual depth
#test_hydro_veg#                                value_n += 1                                               
#test_hydro_veg#                        newgrid[m][n] = value/value_n                                      
#test_hydro_veg#                    except:   # if cellID is not a key in the newLULCdictionay - assign cell to NoData
#test_hydro_veg#                        newgrid[m][n] = -9999                                              
#test_hydro_veg#
#test_hydro_veg#        print(' - saving new EwE %s ASCII raster file' % output)
#test_hydro_veg#        
#test_hydro_veg#        # save formatted LULC grid to ascii file with appropriate ASCII raster header      
#test_hydro_veg#        EwEasc = '%s/%s/%s_I_%02d-%02d_E_%s.asc' % (ewe_dir,output,runprefix,elapsedyear,elapsedyear,output)
#test_hydro_veg#        np.savetxt(EwEasc,newgrid,fmt='%.4f',delimiter=' ',header=ascii_header,comments='')
#test_hydro_veg#
#test_hydro_veg#    for output in ['uplnd']:
#test_hydro_veg#        print(' - mapping %s output to EwE grid' % output)                                                 
#test_hydro_veg#        newgrid = np.zeros([nrows,ncols]) 
#test_hydro_veg#        for m in range(0,nrows):                                                           
#test_hydro_veg#            for n in range(0,ncols):                                                       
#test_hydro_veg#                cellID = ascii_grid_lookup[m][n]                                           
#test_hydro_veg#                if cellID == -9999:                                                        
#test_hydro_veg#                    newgrid[m][n] = -9999                                                  
#test_hydro_veg#                else:                                                                      
#test_hydro_veg#                    try:                                                                   
#test_hydro_veg#                        value = 0
#test_hydro_veg#                        value_n = 0                                                        
#test_hydro_veg#                        for g in range(0,4):                                               
#test_hydro_veg#                            grid = EwEGridMapDict[cellID][g]                               
#test_hydro_veg#                            if grid > 0:                                              
#test_hydro_veg#                                upvalue = max(landdict[grid] - wetlanddict[grid],0)
#test_hydro_veg#                                value += upvalue
#test_hydro_veg#                                value_n += 1                                               
#test_hydro_veg#                        newgrid[m][n] = value/value_n                                      
#test_hydro_veg#                    except:   # if cellID is not a key in the newLULCdictionay - assign cell to NoData
#test_hydro_veg#                        newgrid[m][n] = -9999                                              
#test_hydro_veg#
#test_hydro_veg#        print(' - saving new EwE %s ASCII raster file' % output)
#test_hydro_veg#        
#test_hydro_veg#        # save formatted LULC grid to ascii file with appropriate ASCII raster header      
#test_hydro_veg#        EwEasc = '%s/%s/%s_I_%02d-%02d_E_%s.asc' % (ewe_dir,output,runprefix,elapsedyear,elapsedyear,output)
#test_hydro_veg#        np.savetxt(EwEasc,newgrid,fmt='%.4f',delimiter=' ',header=ascii_header,comments='')
#test_hydro_veg#
#test_hydro_veg#    for output in ['wtlnd']:
#test_hydro_veg#        print(' - mapping %s output to EwE grid' % output)                                                 
#test_hydro_veg#        newgrid=np.zeros([nrows,ncols]) 
#test_hydro_veg#        for m in range(0,nrows):                                                           
#test_hydro_veg#            for n in range(0,ncols):                                                       
#test_hydro_veg#                cellID = ascii_grid_lookup[m][n]                                           
#test_hydro_veg#                if cellID == -9999:                                                        
#test_hydro_veg#                    newgrid[m][n] = -9999                                                  
#test_hydro_veg#                else:                                                                      
#test_hydro_veg#                    try:                                                                   
#test_hydro_veg#                        value = 0                                                          
#test_hydro_veg#                        value_n = 0                                                        
#test_hydro_veg#                        for g in range(0,4):                                               
#test_hydro_veg#                            grid = EwEGridMapDict[cellID][g]                               
#test_hydro_veg#                            if grid > 0:                                              
#test_hydro_veg#                                value += wetlanddict[grid]
#test_hydro_veg#                                value_n += 1                                               
#test_hydro_veg#                        newgrid[m][n] = value/value_n                                      
#test_hydro_veg#                    except:   # if cellID is not a key in the newLULCdictionay - assign cell to NoData
#test_hydro_veg#                        newgrid[m][n] = -9999                                              
#test_hydro_veg#
#test_hydro_veg#        print(' - saving new EwE %s ASCII raster file' % output)
#test_hydro_veg#        
#test_hydro_veg#        # save formatted LULC grid to ascii file with appropriate ASCII raster header      
#test_hydro_veg#        EwEasc = '%s/%s/%s_I_%02d-%02d_E_%s.asc' % (ewe_dir,output,runprefix,elapsedyear,elapsedyear,output)
#test_hydro_veg#        np.savetxt(EwEasc,newgrid,fmt='%.4f',delimiter=' ',header=ascii_header,comments='')
#test_hydro_veg#
#test_hydro_veg#
#test_hydro_veg#                                                                                               
#test_hydro_veg#    monthcols = [0,1,2,3,4,5,6,7,8,9,10,11]                                                
#test_hydro_veg#    monthtext = ['01','02','03','04','05','06','07','08','09','10','11','12']              
#test_hydro_veg#    
#test_hydro_veg#    for output in ['sal','tkn','tmp','tss']:
#test_hydro_veg#        print(' - mapping %s output to EwE grid' % output)                                                
#test_hydro_veg#        
#test_hydro_veg#        if output == 'sal':
#test_hydro_veg#            monthly_dict = saldict
#test_hydro_veg#        elif output == 'tkn':
#test_hydro_veg#            monthly_dict = ChlAdict # ChlA output is actually TKN (see above HSI.HSI where it is read in to the dictionary)
#test_hydro_veg#        elif output == 'tmp':
#test_hydro_veg#            monthly_dict = tmpdict
#test_hydro_veg#        elif output == 'tss':
#test_hydro_veg#            monthly_dict = TSSdict
#test_hydro_veg#                                                                                             
#test_hydro_veg#        # initialize new array that will save model-wide monthly means for output
#test_hydro_veg#        modelave = np.zeros((1,12))    
#test_hydro_veg#
#test_hydro_veg#        # loop through each month and save an ASCII grid raster file for EwE grid
#test_hydro_veg#        for month in monthcols:                                                                
#test_hydro_veg#            newgrid=np.zeros([nrows,ncols]) 
#test_hydro_veg#            for m in range(0,nrows):                                                           
#test_hydro_veg#                for n in range(0,ncols):                                                       
#test_hydro_veg#                    cellID = ascii_grid_lookup[m][n]                                           
#test_hydro_veg#                    if cellID == -9999:                                                        
#test_hydro_veg#                        newgrid[m][n] = -9999                                                  
#test_hydro_veg#                    else:                                                                      
#test_hydro_veg#                        try:                                                                   
#test_hydro_veg#                            value = 0                                                          
#test_hydro_veg#                           value_n = 0                                                        
#test_hydro_veg#                            for g in range(0,4):                                               
#test_hydro_veg#                                grid = EwEGridMapDict[cellID][g]                               
#test_hydro_veg#                                if grid > 0:                                              
#test_hydro_veg#                                    value += monthly_dict[grid][month]                         
#test_hydro_veg#                                    value_n += 1                                               
#test_hydro_veg#                            newgrid[m][n] = value/value_n                                      
#test_hydro_veg#                        except:   # if cellID is not a key in the newLULCdictionay - assign cell to NoData
#test_hydro_veg#                            newgrid[m][n] = -9999                                              
#test_hydro_veg#                                                                  '
#test_hydro_veg#            print(' - saving new %s ASCII raster file for month %s' % (output,monthtext[month]))
#test_hydro_veg#            
#test_hydro_veg#            # save formatted LULC grid to ascii file with appropriate ASCII raster header      
#test_hydro_veg#            EwEasc = '%s/%s/%s_I_%02d-%02d_E_%s%s.asc' % (ewe_dir,output,runprefix,elapsedyear,elapsedyear,output,monthtext[month])
#test_hydro_veg#            np.savetxt(EwEasc,newgrid,fmt='%.4f',delimiter=' ',header=ascii_header,comments='')
#test_hydro_veg#            
#test_hydro_veg#            # save model-wide monthly average value for output type
#test_hydro_veg#            for row in range(0,len(monthly_dict)):
#test_hydro_veg#                modelave[0][month] += monthly_dict[row+1][month]/len(monthly_dict)
#test_hydro_veg#        
#test_hydro_veg#        print(' - saving model-wide monthly averages for %s' % output)
#test_hydro_veg#        ave_file = '%s/%s/%s_I_%02d-%02d_E_%s00.csv' % (ewe_dir,output,runprefix,elapsedyear,elapsedyear,output)
#test_hydro_veg#        ave_file_h = '1,2,3,4,5,6,7,8,9,10,11,12'
#test_hydro_veg#        np.savetxt(ave_file,modelave,delimiter=',',header=ave_file_h,fmt='%.4f',comments='')
#test_hydro_veg#    
#test_hydro_veg#
#test_hydro_veg#    del (depthdict,saldict,tmpdict,TSSdict,ChlAdict,gridIDs)
#test_hydro_veg#
#test_hydro_veg#
#test_hydro_veg#    print('\n--------------------------------------------------')
#test_hydro_veg#    print('  UPLOADING SELECT OUTPUT TO SFTP SERVER.')
#test_hydro_veg#    print('--------------------------------------------------\n')
#test_hydro_veg#
#test_hydro_veg#    
#test_hydro_veg#    # SFTP settings for data upload
#test_hydro_veg#    host = 'cimsftp.coastal.la.gov'
#test_hydro_veg#    un = 'mp2017models'
#test_hydro_veg#    pw = '0urc0ast1$wa$h1ngAw@y'
#test_hydro_veg#    pt = 52222
#test_hydro_veg#
#test_hydro_veg#    if year == startyear + elapsed_hotstart:
#test_hydro_veg#        uploadfails = []
#test_hydro_veg#
#test_hydro_veg#    
#test_hydro_veg#    dpath = '%s/output_%02d/Deliverables' % (wetland_morph_dir,elapsedyear)
#test_hydro_veg#    upfiles = os.listdir(dpath)
#test_hydro_veg#
#test_hydro_veg#    gpath = os.path.normpath(r'\MP2017\3.8\%s\%s' % (sterm,gterm))
#test_hydro_veg#    up_path = os.path.normpath(r'\MP2017\3.8\%s\%s\output_%02d' % (sterm,gterm,elapsedyear))
#test_hydro_veg#    
#test_hydro_veg#    try:
#test_hydro_veg#        with pysftp.Connection(host,username=un,password=pw,port=pt)as sftp:
#test_hydro_veg#            print('-- SFTP connection successful - uploading files.')
#test_hydro_veg#            
#test_hydro_veg#            if sftp.isdir(gpath) == False:
#test_hydro_veg#                print(' %s is missing on FTP - attempting to make folder.' % gpath)
#test_hydro_veg#                sdir = os.path.normpath('/MP2017/3.8/%s' % sterm)
#test_hydro_veg#                sftp.mkdir(gpath)
#test_hydro_veg#            
#test_hydro_veg#            sftp.mkdir(up_path)
#test_hydro_veg#            sftp.chdir(up_path)
#test_hydro_veg#            for localfile in upfiles:
#test_hydro_veg#                try:
#test_hydro_veg#                    uploadfile = '%s/%s' % (dpath,localfile)
#test_hydro_veg#                    if sftp.isfile(localfile):
#test_hydro_veg#                        print(' %s is already on the SFTP in %s - Not uploaded!' % (outfile,gpath))
#test_hydro_veg#                        uploadfails.append(localfile)
#test_hydro_veg#                    else:
#test_hydro_veg#                        sftp.put(uploadfile)
#test_hydro_veg#                except:
#test_hydro_veg#                    print(' %s failed to upload - trying next file' % outfile)
#test_hydro_veg#                    uploadfails.append(localfile)
#test_hydro_veg#                
#test_hydro_veg#
#test_hydro_veg#    except:
#test_hydro_veg#        print('-- SFTP connection unsuccessful for %s model year.' % elapsedyear)
#test_hydro_veg#        uploadfails.append('All files in year %02d' % elapsedyear)
#test_hydro_veg#        
#test_hydro_veg## End Time-stepping loop
#test_hydro_veg#
#test_hydro_veg#if len(uploadfails) > 0:
#test_hydro_veg#    uploadmessage = ' Some SFTP uploads failed - manually upload data for years: %s' % uploadfails
#test_hydro_veg#else:
#test_hydro_veg#    uploadmessage = ' All SFTP uploads were successful.'
    

print('\n\n\n')
print('-----------------------------------------' )
print(' ICM Model run complete!')
print('-----------------------------------------\n')
#print(uploadmessage )


# this should eventually be removed.
## Pause to indicate model run is complete.
input(' ICM Model run complete. Press <ENTER> to exit simulation.')  


##################################
## WINDOWS ENVIRONMENT SETTINGS ##
##################################
##
## Be sure the 64-bit versions of Python are correctly set in Windows PATH environment variables,
## and that .py and .exe extensions are added to either a local or system PATHEXT variable
##
## 1. Access Windows Environment Variables (Control Panel > System > Advanced System Settings> Environment Variables)
## 2. The location of the 64-bit Python executable (python.exe) should be the first Python location in the PATH variable
##      Multiple Python installations can be listed here, but only the first one will be used by Windows (Python278 in the sample below)
##          Variable name: PATH
##          Variable value: C:\Python278\;C:\Python276\;C:\SomeOther\InstalledProgramLocation
## 3. Update the PATHEXT variable to include both .EXE and .PY files (this will keep the model operating within the same shell window)
##          Variable name: PATHEXT
##          Variable value: .COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC;.PY
##
## If other versions of Python were installed or updated after the installation of the version used by the ICM,
## the Windows registry may be pointing to a different verion of Python than the PATH variable. This may result in
## different versions of Python being used, depending upon how the ICM.py executable is invoked.
##  
##      Different ways to run .py files, which will open different versions of Python installed:
##          1) .py files will be run with python.exe defined in the registry key if:
##              a. double-clicked, or 
##              b. called within command prompt as:  C:/Working/Directory> ICM.py
##          2) .py files will be run with python.exe defined in Windows PATH variable if:
##              a. Python is directly called before running the file within a console as >python ICM.py
##
##      It is recommended that Windows PowerShell be used to run the ICM.
##      This will keep the model window open after a run is complete (or fails) and output messages will be visible in the console window.
##
##          1.) Running the model with the 64-bit python.exe associated with the Windows registry key:
##                  C:\project\folder> .\ICM.py
##          2.) Running the model with the 64-bit python.exe defined with the PATH variable:
##                  C:\project\folder> python .\ICM.py
##
##  To ensure that the 64-bit version of Python is called every time the ICM is run (regardless of the registry key):
##      1.)  be sure to update the PATH variable (see above) to include the correct directory location of the 64-bit python.exe
##      2.)  run ICM.py with method two above
##
## OPTIONAL, ADVANCED SETTINGS: Windows Registry Edits to Python location
##      (to be done in addition to PATH variable edits above)
## If you would like to update the registry key setting the python.exe location:
##      1) open Registry Editor (REGEDIT)
##      2) the appropriate key to edit is located @ HKEY_CLASSES_ROOT\Python.File\shell\open\command
##      3) set the key value to: "C:\64bit\Python\install\location\python.exe" "%1" %* 
##              be sure to include the quotation marks
##              also be sure to set the location to the correct installation folder
##   As always, be very careful when editing registry keys. Making mistakes here can break your Windows installation and make things very messy.
##   It is good practice to export (File>Export) the registry prior to making edits so you have a backup in case you break anything?
##
## 
#################################
## PYTHON ENVIRONMENT SETTINGS ##
#################################
##
## non-standard modules needed (must be downloaded separately):
##
## arcpy
## numpy
## scipy
## lxml
## pyparsing
## pytz
## setuptools
## shapely
## six
## xlrd
## dateutil     (requires: six)
## matplotlib (requires: numpy, dateutil, pytz, pyparsing, six)
## pandas       (requires: numpy, dateutil, pytz, scipy, matplotlib, lxml)
## dbfpy
##
## Windows installer files for all above modules (except dbfpy) can be found @ http://www.lfd.uci.edu/~gohlke/pythonlibs/
## xlrd not available as Windows binary installer - download tar.gz @ https://pypi.python.org/pypi/xlrd
## install xlrd via cmd:  C:\folder\where\xlrd\download\was\unzipped> setup.py install
## 
##
############################################################
## GETTING ARCPY TO WORK IN STANDALONE VERSIONS OF PYTHON ##
############################################################
##
## these instructions can be ignored if all modules are installed into the Python version installed with Arc
## 
## In PythonXXX\Lib\site-packages folder, add a .pth file 'Desktop10.2.pth' 
## **If Python is 64-bit, the file name should be DTBGGP64.pth instead of Desktop10.2.pth
## 
## 32-bit Python:
## On Eric's machine, this 'Desktop10.2.pth' file was saved @ C:\Python276\Lib\site-packages\Desktop10.2.pth
## 
## 64-bit Python:
## On Eric's machine this 'DTBGGP64.pth' was saved @ C:/Python278\Lib\site-packages\Desktop10.2.pth
## 
## The .pth files contains three lines of text that correspond to the default location of the arcpy files installed by Arc:
##          C:\Program Files (x86)\ArcGIS\Desktop10.2\arcpy
##          C:\Program Files (x86)\ArcGIS\Desktop10.2\bin
##          C:\Program Files (x86)\ArcGIS\Desktop10.2\ArcToolbox\Scripts
## 
## 
## Alternatively, copy and paste the existing Desktop10.2.pth file from the default Arc Python 
## installation folder and save it to the site-packages folder of the Python version to be used
## 
## In cmd for 32-bit Python:
## copy C:\Python27\ArcGIS10.2\Lib\site-packages\Desktop10.2.pth C:\Python276\Lib\site-packages\Desktop10.2.pth 
## 
## In cmd for 64-bit Python:
## copy C:\Python27\ArcGISx6410.2\Lib\site-packages\DTBGGP64.pth C:\Python278\Lib\site-packages\DTBGGP64.pth
## 
##

