import os
import platform
import sys
import exceptions
import shutil
import math
import time
import errno
import numpy as np
import pysftp
import random

## Save Python's console output to a log file
class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

## Activate log text file
logfile ='ICM_%s_ICM_Veg_Morph_HSI.log' % time.strftime('%Y%m%d_%H%M', time.localtime())
hydro_logfile = 'ICM_%s_Hydro.log' % time.strftime('%Y%m%d_%H%M', time.localtime()) 
sys.stdout = Logger(logfile)


## NOTE: all directory paths and filenames (when appended to a directory path) are normalized
##          in this ICM routine using os.path.normpath(). This is likely a bit redundant, but it
##          was instituted so that file path directory formatting in the input parameters is forgiving.
##          If converted to Linux, this should allow for flexibility between the forward-slash vs.
##          back-slash differences between Windows and Linux.

print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
print '~~                                                           ~~'
print '~~      LOUISIANA MASTER PLAN FOR A SUSTAINABLE COAST        ~~' 
print '~~                Integrated Compartment Model               ~~'
print '~~   Louisiana Coastal Restoration and Protection Authority  ~~'
print '~~                                                           ~~'
print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
print '~~                                                           ~~'
print '~~ Developed under Cooperative Endeavor Agreement Number:    ~~'
print '~~      2503-12-58, Task Order No. 03 (subtask 4.8)          ~~'
print '~~                                                           ~~'
print '~~ Development team:                                         ~~'
print '~~   CB&I                                                    ~~'
print '~~   Fenstermaker                                            ~~'
print '~~   Moffatt & Nichol                                        ~~'
print '~~   University of Louisiana at Lafayette                    ~~'
print '~~   University of New Orleans                               ~~'
print '~~   USGS National Wetlands Research Center                  ~~'
print '~~   The Water Institute of the Gulf                         ~~'
print '~~                                                           ~~'
print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
print '~~                                                           ~~'
print '~~            Version 01.01.FWOA - 08/28/2015                  ~~'
print '~~                                                           ~~'
print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
print ''
print ' ICM run started at:       %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
print ' ICM running on computer:  %s' % platform.node()
print ''



#########################################################
##           CHECK PYTHON AND NUMPY VERSIONS           ##
#########################################################
vs=sys.version_info
npvs=np.__version__
npvsarray = np.fromstring(npvs,sep='.',dtype=int)
npver=float(npvsarray[0])+float(npvsarray[1])/10.0
## Check if Python version is 64-bit
if sys.maxsize > 2**32:
        arch = '64-bit'
        print ' This run is utilizing %s Python %s.%s.%s with NumPy %s' %(arch,vs.major,vs.minor,vs.micro,npvs)
## Check that NumPy version is 1.7 or newer
        if npver < 1.7:
                print ' NumPy version is earlier than NumPy 1.7.0 - this version of NumPy is not supported.'
                print ' Install 64-bit NumPy 1.7.0 (or newer) and re-run ICM.'
                print '\n Press <ENTER> to cancel run.'
                raw_input()
                sys.exit()
        else:
                print '\n This Python configuration is supported.'
else:
        arch = '32-bit'
        print ' This run is utilizing %s Python %s.%s.%s with NumPy %s' %(arch,vs.major,vs.minor,vs.micro,npvs)
        print ' Install 64-bit Python with NumPy 1.7.0 (or newer) and re-run ICM.'
        print '\n Press ENTER to cancel run.'
        raw_input()
        sys.exit()

del (vs,arch,npvs, npvsarray,npver)

#########################################################
## INPUT VARIABLES TO BE READ FROM CONFIGURATION FILES ##
#########################################################
print '--------------------------------------------------'
print '\n CONFIGURING ICM MODEL FILES.'
print '--------------------------------------------------'

#Years to implement new files for hydro model
#the hydro filenames are now dictionaries where the key will be the implementation year
hyd_file_new = {}
hyd_file_bk = {}

#original filename (required for hydro input)
hyd_file_orig = []

#years where hydro files need to be switched
hyd_switch_years = []

#files to be used for the first switch
#hyd_file_new[] = []
#hyd_file_bk[] = []

# files to be used for second switch
# hyd_file_new[2025] = ['hydro_03b.DI.04.Link4023_03a.DI.05.Link4031.exe']
# hyd_file_bk[2025] = ['hydro_03b.DI.04_only.exe'] #this can be named anything

# read in links to deactivate for ALL projects



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

# Years to update marsh edge erosion rate for shoreline protection projects
sp_mee_years = []
# Compartments that will have updated marsh edge erosion rates
sp_mee_comps = []
# New marsh edge erosion rate for each compartment
sp_mee_rates = []




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
if len(link_years) <> len(links_to_change):
    InputErrorFlag = 1
    InputErrorMsg = '%sNumber of links to activate/deactivate and implementation years are not equal in length!\n' % InputErrorMsg 
if len(mc_links_years) <> len(mc_links):
    InputErrorFlag = 1
    InputErrorMsg = '%sNumber of links to update for marsh creation projects and implementation years are not equal in length!\n' % InputErrorMsg
if len(mc_years) <> len(mc_shps) <> len(mc_shps_fields):
    InputErrorFlag = 1
    InputErrorMsg = '%sMarsh Creation Project Implementation variables are not of equal length!\n' % InputErrorMsg
if len(sp_years) <> len(sp_shps) <> len(sp_shps_fields):
    InputErrorFlag = 1
    InputErrorMsg = '%sShoreline Protection Project Implementation variables are not of equal length!\n' % InputErrorMsg
if len(levee_years) <> len(levee_shps) <> len(levee_shps_fields1) <> len(levee_shps_fields2) <> len(levee_shps_fields3) <> len(levee_shps_fields4):
    InputErrorFlag = 1
    InputErrorMsg = '%sLevee & Ridge Project Implementation variables are not of equal length!\n' % InputErrorMsg

if InputErrorFlag == 1:
    print ' ***********Error with Project Implementation variables! Fix and re-run!\n'
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

run_ewe = True

sftp_upload = True
host = 'sftp_url'
un = 'username'
pw = #'password' #password goes here in quotes 
pt = 52222


#########################################################
##            SETTING UP ECOHYRO MODEL                 ##
#########################################################

print ' Configuring Hydro Model.'
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
        print '\n**************ERROR**************'
        print '\n Hydro output files already exist in Hydro project directory.'
        print '\n Would you like to:'
        print '\n     1. Exit run and manually delete all *.out files?'
        print '\n     2. Programatically delete all *.out files and continue run?'
        option=raw_input()
        try:
                if int(option) == 1:
                        exitmsg='\n Manually remove *.out files and re-run ICM.'
                        sys.exit(exitmsg)
                elif int(option) == 2:
                        print '\n Attempting to remove *.out files from Hydro directory.'
                        try:
                                ehfiles=os.listdir(ecohydro_dir)
                                for f in ehfiles:
                                        if f.endswith('.out'):
                                                fp = ecohydro_dir+'\\'+f
                                                os.unlink(fp)
                                                print '   - deleted %s' %f
                                print '\n Successfully deleted all *.out files in %s.' % ecohydro_dir
                                print '\n Continuing with ICM run.'
                        except Exception,e:
                                print ' Automatic delete failed.'
                                sys.exit(e)
                else:
                        exitmsg='\n Invalid option - manually remove *.out files and re-run ICM.'
                        sys.exit(exitmsg)
        except Exception,e:
                exitmsg='\n Invalid option - manually remove *.out files and re-run ICM.'
                sys.exit(exitmsg)

## repeat check for output files - but look in Veg folder for files generated by hydro.exe Fortran program
## change working directory to veg folder
os.chdir(vegetation_dir)


## Single slash used here because this is getting written to a file to be read into Fortran in Windows.
#VegWaveAmpFile =     r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),WaveAmplitudeFile)
#VegMeanSalFile =     r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),MeanSalinityFile)
#VegSummerDepthFile = r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),SummerMeanWaterDepthFile)
#VegSummerSalFile =   r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),SummerMeanSalinityFile)
#VegSummerTempFile =  r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),SummerMeanTempFile)
#VegTreeEstCondFile = r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),TreeEstCondFile)
#VegBIHeightFile =    r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),HtAbvWaterFile)
#VegPerLandFile =     r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,(1+elapsed_hotstart),(endyear-startyear+1),PerLandFile)
VegWaveAmpFile =     r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,1,(endyear-startyear+1),WaveAmplitudeFile)
VegMeanSalFile =     r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,1,(endyear-startyear+1),MeanSalinityFile)
VegSummerDepthFile = r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,1,(endyear-startyear+1),SummerMeanWaterDepthFile)
VegSummerSalFile =   r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,1,(endyear-startyear+1),SummerMeanSalinityFile)
VegSummerTempFile =  r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,1,(endyear-startyear+1),SummerMeanTempFile)
VegTreeEstCondFile = r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,1,(endyear-startyear+1),TreeEstCondFile)
VegBIHeightFile =    r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,1,(endyear-startyear+1),HtAbvWaterFile)
VegPerLandFile =     r'%s\%s_N_%02d_%02d_H_%s' % (vegetation_dir,runprefix,1,(endyear-startyear+1),PerLandFile)



vegflag = 0        
ehveg_outfiles = [VegWaveAmpFile,VegMeanSalFile,VegSummerDepthFile,VegSummerSalFile,VegSummerTempFile,VegTreeEstCondFile,VegBIHeightFile,VegPerLandFile]

for veginfile in ehveg_outfiles:
    if os.path.isfile(veginfile) == True:
                vegflag = 1

if elapsed_hotstart > 0:
    vegflag = 0


if vegflag == 1:
        print '\n**************ERROR**************'
        print '\n Hydro output files formatted for Veg model already exist in Veg project directory.\n Move or delete files and re-run ICM.'
        print '\n Would you like to:'
        print '\n     1. Exit run and manually delete all Hydro output files in Veg directory?'
        print '\n     2. Programatically delete files and continue run?'
        option=raw_input()
        try:
                if int(option) == 1:
                        exitmsg='\n Manually remove Hydro output files from Veg directory and re-run ICM.'
                        sys.exit(exitmsg)
                elif int(option) == 2:
                        print '\n Attempting to remove Hydro output files from Veg directory.'
                        try:
                                vegfiles=os.listdir(vegetation_dir)
                                for vf in ehveg_outfiles:
                                        os.unlink(vf)
                                        print '   - deleted %s' %vf
                                print '\n Successfully deleted all Hydro output files in %s.' % vegetation_dir
                                print '\n Continuing with ICM run.'
                        except Exception,e:
                                print ' Automatic delete failed.'
                                sys.exit(e)
                else:
                        exitmsg='\n Invalid option - manually remove files from Veg directory and re-run ICM.'
                        sys.exit(exitmsg)
        except Exception,e:
                exitmsg='\n Invalid option - manually remove files from Veg directory and re-run ICM.'
                sys.exit(exitmsg)

## change working directory to hydro folder
os.chdir(ecohydro_dir)        
                                           
# create temporary files folder - where ICM files will be saved for examination or debugging
# Temporary file location must not exist  
## errno.EEXIST is a cross-platform 'existing file' error flag
EHtemp_path = os.path.normpath(r'%s\\TempFiles' % ecohydro_dir)

rnflag = 0

if os.path.isdir(EHtemp_path):
        rnflag=1

if elapsed_hotstart > 0:
    rnflag = 0

if rnflag == 1:
        print '\n Temporary folder for Hydro files already exists.'
        print '\n Would you like to:'
        print '\n     1. Exit run and manually move or delete folder?'
        print '\n     2. Programatically rename folder and continue run?'
        option=raw_input()
        try:
                if int(option) == 1:
                        exitmsg='\n Manually rename or delete folder and re-run ICM.'
                        sys.exit(exitmsg)
                elif int(option) == 2:
                        print '\n Attempting to rename folder.'
                        try:
                                print '\n What would you like to rename the folder?'
                                nn = raw_input()
                                newnn = os.path.normpath(r'%s\\%s' % (ecohydro_dir,nn))
                                os.rename(EHtemp_path,newnn)
                                print '\n Successfully renamed Hydro temporary folder.'
                                print '\n Continuing with ICM run.'
                        except Exception,e:
                                print ' Automatic folder rename failed.'
                                sys.exit(e)
                else:
                        exitmsg='\n Invalid option - manually rename or delete folder and re-run ICM.'
                        sys.exit(exitmsg)
        except Exception,e:
                exitmsg='\n Invalid option - manually remove files from Veg directory and re-run ICM.'
                sys.exit(exitmsg)

if elapsed_hotstart == 0:
    try:                                
        os.makedirs(EHtemp_path)
    
    except OSError as Exception:        
        print '******ERROR******'       
        error_msg = ' Error encountered during Hydrology Model configuration.\n'+str(Exception)+'\n Check error and re-run ICM.'
        ## re-write error message if it was explictily an 'existing file' error.
        if Exception.errno == errno.EEXIST:
            error_msg = '\n Temporary folder for Hydro files already exists.\n Rename existing folder if files are needed, otherwise delete and re-run ICM.'
             

del (ehflag,vegflag,rnflag)
print ' Writing file to be passed to Hydro routine containing location of files shared with Vegetation Model.'
                                    

max_string = max(len(VegWaveAmpFile),len(VegMeanSalFile),len(VegSummerDepthFile),len(VegSummerSalFile),len(VegSummerTempFile),len(VegTreeEstCondFile),len(VegPerLandFile))

## Write input file with directories for use in Hydro Fortran module
## This will overwrite any ICM_directories.txt file already saved in the Hydro folder
## length limit of 200 is set due to the character string size declared in the compiled Fortran code
## If the directory location HAS to be longer than 200 characters, this flag will have to be updated
## AND the Fortran Hydro code will have to be updated to allocate a larger variable (in 'params' module)
if max_string > 300:
    error_msg1 = '\n **************ERROR**************'
    error_msg2 = 'The directory location string for the Vegetation files are longer than 300 characters, it will not be correctly passed to the compiled Fortran program. Either rename the directory or edit ICM.py and params.f source code files and recompile.'
    print error_msg1
    sys.exit(error_msg2)
else:   
    file_for_hydro = os.path.normpath(r'%s\\%s' % (ecohydro_dir,EHInterfaceFile))
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
EHCellsArray = np.genfromtxt(EHCellsFile,dtype=float,delimiter=',',skiprows=1)
EHLinksArray = np.genfromtxt(EHLinksFile,dtype=float,delimiter=',',skiprows=1)

## file containing percentage land, and land/water elevations for each 500-m grid cell as it is used by hydro (file is generated by Morph)
EH_grid_file = 'grid_data_500m.csv' # this must match file name used in hydro.exe
EH_grid_filepath = os.path.normpath('%s\\%s' % (ecohydro_dir,EH_grid_file)) # location of grid_data_500m.csv when used by hydro.exe

## Read in file linking Ecohydro links to BIMODE profile IDs
## First column (0) is BIMODE profile ID, second column (1) is Ecohydro link ID
print ' Reading in file matching Hydro link IDs to BIMODE profile IDs'
EHBMfile = os.path.normpath(r'%s\\%s' % (ecohydro_dir,BMInterfaceFile))

linklup=np.genfromtxt(EHBMfile,delimiter=',',skiprows=1)

## Save profile-link lookup as a dictionary, key is EH link ID, value is BIMODE profile
linktoprofile = dict((linklup[n,0],linklup[n,1])for n in range(0,len(linklup)))

## remove temporary variables/arrays that aren't needed
del(linklup,EHBMfile)


#########################################################
##      SETTING UP BARRIER ISLAND MODEL ~ BIMODE       ##
#########################################################
print ' Configuring Barrier Island Model ~ BIMODE.'

#change working directory to wetland morph folder
os.chdir(bimode_dir)

# ICM Compartment IDs for each island's bay areas
BI_Dern=[561,566,575,599,609,649]
BI_Timb=[353,371,373,377,400,414,419,439,445,484]
BI_CamGI=[294,307,313,331,344,366]
BI_Bara=[143,168,176,177,181,183,188,195,200,204,205,217,220,222,231,233,239,244,252,257,266,278,280,284,285,289,291,294,295]
BI_Bret=[29,34,39,40,42,44,47,49,52,54,55,67,68]
BI_Chand=[12,16,19,20,22,24,28,32]

# Create a list of lists - combines the compartment-to-bay lookup lists
# - length of each lookup list can vary, flexible dimensions
IslandCompLists=[BI_Dern,BI_Timb,BI_CamGI,BI_Bara,BI_Bret,BI_Chand]

# create liste of ICM compartments that will be used as MHW for each BI group
IslandMHWCompLists = [598,493,348,281,43,15]

# Create blank dictionary to store lists of breached profile locations
# Each key will be 'YYYY', which is the model year (in integer, NOT string, form)
# Each year's list should only contain profiles breached in that year
breaches = {} 
   

###########################################################
###         SETTING UP MORPH MODEL              ##
##########################################################
print ' Configuring Morphology Model.'
# change working directory to wetland morph folder
os.chdir(wetland_morph_dir)
sys.path.append(wetland_morph_dir)

##import Wetland Morph model
import WM

## read Wetland Morph parameters csv file into array (first column is descriptor, second column is variable)                            
WM_params = np.genfromtxt(WMConfigFile,dtype=str,delimiter=',',usecols=1)                              


#########################################################
##              SETTING UP HSI MODEL                   ##
#########################################################
print ' Configuring HSI Model.'
# change working directory to veg folder
os.chdir(HSI_dir)
sys.path.append(HSI_dir)

import HSI



# check to see if hydro input data start date is different than ICM start year
if inputStartYear > startyear:
    exitmsg='\n Invalid configuration! ICM model set to start before Hydro input data coverage. Check ICM_control.csv file and re-run.'
    sys.exit(exitmsg)

# startrun is row of hydro input data files to import into Hydro.exe
startrun = 0

# update startrun value based on first model year versus beginning of hydro model input data files
## determine the startrun from the input start year - added by zw 2/9/2015
for year in range(inputStartYear,hotstart_year):
    leapfrac4,leapint4 = math.modf(year/4.)     #math.modf splits a number into fractional and integer parts
    leapfrac100,leapint100 = math.modf(year/100.)
    leapfrac400,leapint400 = math.modf(year/400.)
    
    if leapfrac4 == 0:
        yeartype = 'Leap'
    elif leapfrac100 != 0:
        if leapfrac400 == 0:
            yeartype = 'Leap'
        else:
            yeartype = 'Common'
    
    ## Assign number of days in year
    if yeartype == 'Common':
        ndays = 365
    else:
        ndays = 366
    
    startrun = startrun + ndays

#############################################################
## STEP THROUGH YEARS BEFORE HOTSTART TO SPIN VEG MODEL UP ##
#############################################################
if elapsed_hotstart > 0:
    os.chdir(vegetation_dir)
    
    print '\n--------------------------------------------------'
    print '        CONFIGURING VEGETATION MODEL'
    print '      - only during initial year of ICM -'
    print '      THIS IF FOR A HOTSTARTED MODEL RUN '
    print '--------------------------------------------------\n'        

    sys.path.append(vegetation_dir)
        
    import model_v2
        
    LAVegMod = model_v2.Model()
        
    try:
        LAVegMod.config(VegConfigFile)
    except exceptions as error:
        print '******ERROR******'
        print error
        sys.exit('\nFailed to initialize Veg model.')

    #########################################################
    ##      RUN VEGETATION MODEL FOR HOTSTART PERIOD       ##
    #########################################################
    for year in range(startyear,hotstart_year):
        print '\n--------------------------------------------------'
        print '  RUNNING VEGETATION MODEL - Year %s' % year
        print '--------------------------------------------------\n'  
    
        try:
            LAVegMod.step()
        except exceptions.RuntimeError as error:
            print '\n ******ERROR******'
            print error
            sys.exit('Vegetation model run failed - Year %s.' % year)



#########################################################
##              START YEARLY TIMESTEPPING              ##
#########################################################

for year in range(startyear+elapsed_hotstart,endyear+1):
    print '\n--------------------------------------------------'
    print '  START OF MODEL TIMESTEPPING LOOP - YEAR %s' % year                  
    print '--------------------------------------------------\n'    
    
    ## Check if current year is a leap year
    leapfrac4,leapint4 = math.modf(year/4.)     #math.modf splits a number into fractional and integer parts
    leapfrac100,leapint100 = math.modf(year/100.)
    leapfrac400,leapint400 = math.modf(year/400.)
    
    if leapfrac4 == 0:
        yeartype = 'Leap'
    elif leapfrac100 != 0:
        if leapfrac400 == 0:
            yeartype = 'Leap'
        else:
            yeartype = 'Common'
    
    ## Assign number of days in year
    if yeartype == 'Common':
        ndays = 365
        print r' Current model year (%s) is not a leap year' % year
    else:
        ndays = 366
        print r' Current model year (%s) is a leap year - input timeseries must include leap day' % year
    
            
    #########################################################
    ##                  RUN HYDRO MODEL                    ##
    #########################################################
    print r' Preparing Hydro Input Files - Year %s' % year

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
        print ' Importing updated landscape attributes from Morphology output files - Year %s' % year
        ## set output hotstart file generated from last model timestep to be new input hotstart file
        os.rename('hotstart_out.dat', 'hotstart_in.dat')
        ## update LW ratio in Cells.csv (compartment attributes table)
        # new pct water from WM output saved in temp folder during last model year (year-1)
        PctWaterFile = os.path.normpath(r'%s\\PctWater_%s.csv' % (EHtemp_path,year-1))  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year-1) here instead of CurrentYear
        new_pctwater = np.genfromtxt(PctWaterFile,delimiter=',')
        new_pctwater_dict=dict((new_pctwater[n,0],new_pctwater[n,1]) for n in range(0,len(new_pctwater)))
        
        # move grid data file from location saved by previous year's Morph run to the Hydro directory (new_grid_filepath not defined until after Morph is run each year)
        os.rename(new_grid_filepath,EH_grid_filepath)
                
        # new pct upland from WM output saved in temp folder during last model year (year-1)
        PctUplandFile = os.path.normpath(r'%s\\PctUpland_%s.csv' % (EHtemp_path,year-1))  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year-1) here instead of CurrentYear
        new_pctupland = np.genfromtxt(PctUplandFile,delimiter=',')
        new_pctupland_dict=dict((new_pctupland[n,0],new_pctupland[n,1]) for n in range(0,len(new_pctupland)))
        
        ## read in updated bed and land elevation values for compartments - save in dictionaries where compartment ID is the key
        ## column 1 = compartment ID, column 2 = bed elev, column 3 = land elev, column 4 - marsh edge length
        # The marsh elevation value is filtered in WM.CalculateEcohydroAttributes() such that the average marsh elevation can be no lower than the average bed elevation
        CompElevFile = os.path.normpath(r'%s\\compelevs_end_%s.csv' % (EHtemp_path,year-1))  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year-1) here instead of CurrentYear
        new_compelev = np.genfromtxt(CompElevFile,delimiter=',',skiprows=1)
                
        new_OWelev_dict = dict((new_compelev[n,0],new_compelev[n,1]) for n in range(0,len(new_compelev)))
        new_Melev_dict = dict((new_compelev[n,0],new_compelev[n,2]) for n in range(0,len(new_compelev)))
        new_Medge_dict = dict((new_compelev[n,0],new_compelev[n,3]) for n in range(0,len(new_compelev)))

        ## create blank dictionaries that will save changes in compartment attributes and initialize flags for counting updated compartments
        bedchange_dict={}
        marshchange_dict={}
        new_bed_dict={}
        new_marsh_dict={}
        
        orig_marsh_area = {}
        new_marsh_area = {}
        
        flag_cell_wat = 0
        flag_cell_upl = 0
        flag_bed_ch = 0
        flag_mar_ch = 0
        flag_edge_ch = 0
        
## update Hydro compartment water/upland/marsh area attributes
        print ' Updating land/water ratios and bed/marsh elevation attributes for Hydro compartments - Year %s' % year   
        for nn in range(0,len(EHCellsArray)):
            cellID = EHCellsArray[nn,0]
            cellarea = EHCellsArray[nn,1]         
            # update percent water only if new value was calculated in Morph (e.g. dicitionary has a key of cellID and value that is not -9999), otherwise keep last year value
            try:
                if new_pctwater_dict[cellID] != -9999:
                    EHCellsArray[nn,2] = new_pctwater_dict[cellID]
                else:
                    flag_cell_wat =+ 1
            except:
                flag_cell_wat += 1
            
            # update percent upland only if new value was calculated in Morph (e.g. dictionary has a key of cellID and value that is not -9999), otherwise keep last year value
            try:
                if new_pctupland_dict[cellID] != -9999:
                    EHCellsArray[nn,3] = new_pctupland_dict[cellID]
                else:
                    flag_cell_upl += 1
            except:
                flag_cell_upl += 1
                
            
            # update marsh edge area, in attributes array
            try:
                if new_Medge_dict[cellID] != -9999:
                    EHCellsArray[nn,5] = new_Medge_dict[cellID]
            except:
                    flag_edge_ch += 1
            
            # update percent marsh - use cell array, rather than new dictionaries to account for compartments that weren't updated by Morph
            orig_marsh_area[nn] = EHCellsArray[nn,4]*cellarea
            EHCellsArray[nn,4] = max((1-EHCellsArray[nn,2]-EHCellsArray[nn,3]),0)
            new_marsh_area[nn] = EHCellsArray[nn,4]*cellarea
            
            # update Hydro compartment/link elevation attributes (if turned on as model option)
        if update_hydro_attr == 0:
            print ' Hydro link and compartment attributes are not being updated (update_hydro_attr = 0)'
        
        else:
            
            # calculate change in bed elevation if new value was calculated in Morph (e.g. dictionary has a key of cellID and value that is not -9999)
            # set change value to zero if value is NoData or if key does not exist
            try:
                if new_OWelev_dict[cellID] != -9999:
                    bedchange_dict[cellID] = new_OWelev_dict[cellID]-EHCellsArray[nn,7]
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
                    marshchange_dict[cellID] = new_Melev_dict[cellID]-EHCellsArray[nn,25]
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
            print ' Updating elevation attributes for Hydro links - Year %s' % year   
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
                

                # update link types for barrier island breaches in BIMODE's previous year run
                # check if link is representative of a barrier island breach (will be a key in the linktoprofile dict)
                if linkID in linktoprofile.keys():
                    # check if barrier island breach link is currently dormant
                    if linktype < 0:
                        # check if corresponding BIMMODE profile was breached in previous year
                        if linktoprofile[linkID] in breaches[year-1]:
                            newlinktype = -linktype
                            EHLinksArray[mm,7] = newlinktype 
    
    ## end update of Hydro compartment attributes            
        print ' %s Hydro compartments have updated percent land values for model year %s.' % ((len(EHCellsArray)-flag_cell_upl),year)   
        print ' %s Hydro compartments have updated percent water values for model year %s.' % ((len(EHCellsArray)-flag_cell_wat),year)  
        print ' %s Hydro compartments have updated average bed elevations for model year %s.' % ((len(EHCellsArray)-flag_bed_ch),year)  
        print ' %s Hydro compartments have updated average marsh elevations for model year %s.' % ((len(EHCellsArray)-flag_mar_ch),year)
        print ' %s Hydro compartments have updated marsh edge lengths for model year %s.' % ((len(EHCellsArray)-flag_edge_ch),year)     

        # update compartments for project implementation
        # if any compartment are supposed to have a new marsh edge erosion rate due to a shoreline protetion project
        if year in sp_mee_years:
            mee_dict_for_year = {}
            print ' Some compartments are set to have marsh edge erosion rates updated for this model year due to project implementation.'
            for sp_n in range(0,len(sp_mee_years)):
                year_to_change = sp_mee_years[sp_n]
                if year_to_change == year:
                    cell_to_change = sp_mee_comps[sp_n]
                    new_rate = sp_mee_rates[sp_n]
                    if cell_to_change in mee_dict_for_year.keys():
                        print '  Compartment %s has multiple retreat rates implemented in this model year - the minimum will be used.' % cell_to_change
                        orig_change = mee_dict_for_year[cell_to_change]
                        mee_dict_for_year[cell_to_change] = min(orig_change,new_rate)
                    else:
                        mee_dict_for_year[cell_to_change] = new_rate
                        
            for nmn in range(0,len(EHCellsArray)):
                cellID = EHCellsArray[nmn,0]
                if cellID in mee_dict_for_year.keys():
                    old_mee_rate = EHCellsArray[nmn,23]
                    new_mee_rate = mee_dict_for_year[cellID]
                    if old_mee_rate > new_mee_rate:
                        print '   Compartment %s has a new marsh edge erosion rate due to projection implmentation.' % cellID
                        EHCellsArray[nmn,23] = new_mee_rate
                    else:
                        print '   Compartment %s is keeping original marsh edge erosion rate because post-project rate is not reduced' % cellID

        
        # update links for project implmentation
        # if project links are to be changed during model year update those links by looping through link attributes array
        if year in link_years:
            print '  Some links are set to be activated or deactivated for this model year due to project implementation.'
            for mm in range(0,len(EHLinksArray)):
                linkID = EHLinksArray[mm,0]
                if linkID in links_to_change:
                    yearindex = links_to_change.index(linkID)    
                    if year == link_years[yearindex]:
                        print ' Link type for link %s is being activated (or deactivated if already active).' % linkID
                        oldlinktype = EHLinksArray[mm,7]
                        newlinktype = -1*oldlinktype
                        EHLinksArray[mm,7] = newlinktype
                
        ## update link width for 'composite' marsh links if marsh creation project was implemented in previous year
        # link length is attribute 3 (column 11 in links array)
        # link width is attribute 4 (column 12 in links array)   
        if year in mc_links_years:
            print '  Some composite marsh flow links are being updated due to marsh creation projects implemented during last year.'
            for mm in range(0,len(EHLinksArray)):
                linkID = EHLinksArray[mm,0]
                linktype = EHLinksArray[mm,7]
                us_comp = EHLinksArray[mm,1]
                ds_comp = EHLinksArray[mm,2]    
                if linktype == 11:
                    if linkID in mc_links:
                        linkindex = mc_links.index(linkID)
                        if year == mc_links_years[linkindex]:
                            print ' Updating composite marsh flow link (link %s) for marsh creation project implemented in previous year.' % linkID
                            origwidth = EHLinksArray[mm,11]
                            length = EHLinksArray[mm,10]
                            
                            if orig_marsh_area[us_comp] > 0:
                                darea_us_ratio = new_marsh_area[us_comp]/orig_marsh_area[us_comp]            

                                if orig_marsh_area[ds_comp] > 0:
                                    darea_ds_ratio = new_marsh_area[ds_comp]/orig_marsh_area[ds_comp]
                                    
                                    ave_marsh_area_change_ratio = (darea_ds_ratio + darea_us_ratio)/2.0
                                    
                                    # do not let marsh link go to zero - allow some flow, minimum width is one pixel wide - also do not let it be larger than original link
                                    # original marsh link width is reduced by the ratio that the marsh area increased in the project area
                                    newwidth = min(origwidth,max(origwidth*(1.0 - ave_marsh_area_change_ratio),30.0))
                                    
                                else:
                                    newwidth = origwidth
                            else:
                                newwidth = origwidth
                            
                            EHLinksArray[mm,11] = newwidth
        
        
        
        
        
        ## save updated Cell and Link attributes to text files read into Hydro model                      
        np.savetxt(EHCellsFile,EHCellsArray,fmt='%.12f',header=cellsheader,delimiter=',',comments='')
        np.savetxt(EHLinksFile,EHLinksArray,fmt='%.12f',header=linksheader,delimiter=',',comments='')

    if year in hyd_switch_years:
        for nnn in range(0,len(hyd_file_orig)):
            oldfile = hyd_file_orig[nnn]
            newfile = hyd_file_new[year][nnn]
            bkfile = hyd_file_bk[year][nnn]
            print ' Copying %s to use as the new %s.' % (newfile, oldfile)
            print ' Saving original %s as %s.' % (oldfile,bkfile)
            os.rename(oldfile,bkfile)
            os.rename(newfile,oldfile)

    print '\n--------------------------------------------------'
    print '  RUNNING HYDRO MODEL - Year %s' % year
    print '--------------------------------------------------\n' 
    print ' See %s for Hydro runtime logs.' % hydro_logfile  
     
    # run compiled Fortran executable - will automatically return to Python window when done running
    hydrorun = os.system('hydro.exe')
       
    if hydrorun != 0:
        print '******ERROR******'
        error_msg = '\n Hydro model run for year %s was unsuccessful.' % year
        sys.exit(error_msg)    
    
    # Clean up and set Ecohydro up for next year model run
    print r' Cleaning up after Hydro Model - Year %s' % year
    ## update startrun value for next model year
    startrun = endrun + 1
    ## calculate elapsed years of model run
    elapsedyear = year - startyear + 1

    ## append year to names and move hotstart,config, cells, links, and grid files to temp folder so new ones can be written for next model year
    print ' Cleaning up Hydro output files.'
    
    move_hs = os.path.normpath(r"%s\\hotstart_in_%s.dat" % (EHtemp_path,year))
    os.rename('hotstart_in.dat',move_hs)
    
    move_EHconfig = os.path.normpath(r"%s\\%s_%s.%s" % (EHtemp_path,str.split(EHConfigFile,'.')[0],year,str.split(EHConfigFile,'.')[1]))
    os.rename(EHConfigFile,move_EHconfig)

    move_EHcell = os.path.normpath(r"%s\\%s_%s.%s" % (EHtemp_path,str.split(EHCellsFile,'.')[0],year,str.split(EHCellsFile,'.')[1]))
    os.rename(EHCellsFile,move_EHcell)

    move_EHlink = os.path.normpath(r"%s\\%s_%s.%s" % (EHtemp_path,str.split(EHLinksFile,'.')[0],year,str.split(EHLinksFile,'.')[1]))
    os.rename(EHLinksFile,move_EHlink)

    move_EH_gridfile = os.path.normpath(r"%s\\%s_%s.%s" % (EHtemp_path,str.split(EH_grid_file,'.')[0],year,str.split(EH_grid_file,'.')[1]))  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year-1) here instead of CurrentYear
    os.rename(EH_grid_filepath,move_EH_gridfile)

    # read in compartment output from hydro model to generate input file for BIMODE
    EH_comp_results_file = os.path.normpath('%s\\%s') % (ecohydro_dir,compartment_output_file)
    EH_comp_out = np.genfromtxt(EH_comp_results_file,dtype='float',delimiter=',',names=True)
    
    #generate single string from names that will be used as header when writing output file
    compnames = EH_comp_out.dtype.names
    compheader = compnames[0]
    
    for n in range(1,len(compnames)):
        compheader +=',%s' % compnames[n]
    
    # re-write compartment output file with year appended to name - file is re-written (as opposed to moved) to ensure floating point format will be correct for import into WM.ImportEcohydroResults - corrects issues with Fortran formatting
    EH_comp_out_newfile = '%s_%s.%s' % (str.split(compartment_output_file,'.')[0],year,str.split(compartment_output_file,'.')[1])
    EH_comp_results_filepath = os.path.normpath('%s\\%s' % (EHtemp_path,EH_comp_out_newfile))
    np.savetxt(EH_comp_results_filepath,EH_comp_out,delimiter=',',fmt='%.4f',header=compheader,comments='')    
    
    # read in grid output from hydro model
    EH_grid_results_file = os.path.normpath('%s\\%s') % (ecohydro_dir,grid_output_file)
    EH_grid_out = np.genfromtxt(EH_grid_results_file,dtype='float',delimiter=',',names=True)
    
    #generate single string from names that will be used as header when writing output file
    gridnames = EH_grid_out.dtype.names
    gridheader = gridnames[0]
    for n in range(1,len(gridnames)):
        gridheader +=',%s' % gridnames[n]

    # re-write grid output file with year appended to name - file is re-written (as opposed to moved) to ensure floating point format will be correct for import into WM.ImportEcohydroResults - corrects issues with Fortran formatting
    EH_grid_out_newfile = '%s_%s.%s' % (str.split(grid_output_file,'.')[0],year,str.split(grid_output_file,'.')[1])
    EH_grid_results_filepath = os.path.normpath('%s\\%s' % (EHtemp_path,EH_grid_out_newfile))
    np.savetxt(EH_grid_results_filepath,EH_grid_out,delimiter=',',fmt='%.4f',header=gridheader,comments='')

## Copy monthly gridded output used by EwE model to temporary output folder in Hydro directory
    SalMonth = 'sal_monthly_ave_500m'
    SalMonthFile = os.path.normpath(r"%s\\%s.out" % (ecohydro_dir,SalMonth))
    move_salmonth = os.path.normpath(r"%s\\%s_%02d.out" % (EHtemp_path,SalMonth,elapsedyear))
    shutil.copy(SalMonthFile,move_salmonth)

    TmpMonth = 'tmp_monthly_ave_500m'
    TmpMonthFile = os.path.normpath(r"%s\\%s.out" % (ecohydro_dir,TmpMonth))
    move_tmpmonth = os.path.normpath(r"%s\\%s_%02d.out" % (EHtemp_path,TmpMonth,elapsedyear))
    shutil.copy(TmpMonthFile,move_tmpmonth)

    TKNMonth = 'tkn_monthly_ave_500m'
    TKNMonthFile = os.path.normpath(r"%s\\%s.out" % (ecohydro_dir,TKNMonth))
    move_tknmonth = os.path.normpath(r"%s\\%s_%02d.out" % (EHtemp_path,TKNMonth,elapsedyear))
    shutil.copy(TKNMonthFile,move_tknmonth)

    TSSMonth = 'TSS_monthly_ave_500m'
    TSSMonthFile = os.path.normpath(r"%s\\%s.out" % (ecohydro_dir,TSSMonth))
    move_tssmonth = os.path.normpath(r"%s\\%s_%02d.out" % (EHtemp_path,TSSMonth,elapsedyear))
    shutil.copy(TSSMonthFile,move_tssmonth)



    
    # create dictionary where key is compartment ID, value is tidal prism (Column 14 of Ecohydro output)
    EH_prisms = dict((EH_comp_out[n][0],EH_comp_out[n][13]) for n in range(0,len(EH_comp_out)))
    
    # create dictionary where key is compartment ID, values is mean water (column 3 of Ecohydro output)
    EH_MHW = dict((EH_comp_out[n][0],EH_comp_out[n][2]) for n in range(0,len(EH_comp_out)))


    # Initialize tidal prism and MHW arrays to zero - will write over previous year's array
    BIMODEprisms = np.zeros(shape=len(IslandCompLists))
    BIMODEmhw = np.zeros(shape=len(IslandMHWCompLists))

    # Loop through each Barrier Islands Ecohydro compartments
    # Add compartment tidal prism volumes to calculate total bay tidal prism for each island    
    for n in range(0,len(IslandCompLists)):
        BI = IslandCompLists[n]
        for k in range(0,len(BI)):
            comp=BI[k]
    # compartment 296 is split between two different sets of Barrier Islands - therefore its volume is cut in half          
            if comp==296:
                BIMODEprisms[n] += EH_prisms[comp]/2
            else:
                BIMODEprisms[n] += EH_prisms[comp]    

    for n in range(0,len(IslandMHWCompLists)):
        comp = IslandMHWCompLists[n]
        BIMODEmhw[n] = EH_MHW[comp]

    del(EH_comp_out,EH_grid_out)

    #########################################################
    ##              RUN BARRIER ISLAND MODEL               ##
    #########################################################

    print '\n--------------------------------------------------'
    print '  RUNNING BARRIER ISLAND MODEL - Year %s' % year
    print '--------------------------------------------------\n'
    print ' See separate log files generated by each BIMODE run.' 
    
                   
    # initialize breach dictionary key for current year to an empty list
    # this will be appended to with the profile numbers that have been breached
    breaches[year]=[]
    
    # initialize array to pass profile output files into Wetland Morph
    BMprof_forWM =[]
    

    
    # write Tidal Prism file in made BIMODE folder
    # Generate tab-seperated file of tidal prism volumes    
    prism_file_for_bimode = os.path.normpath(r'%s\\%s' % (bimode_dir,BIPrismFile))
    with open(prism_file_for_bimode,'w') as f:                        
        f.write('% Tidal Prism\t%Region')                            
        f.write('\n')
        for n in range(0,len(IslandCompLists)):
            prism = str(BIMODEprisms[n])+'\t'+str(n+1)
            f.write(prism)
            f.write('\n')
    
    mhw_file_for_bimode = os.path.normpath(r'%s\\%s' % (bimode_dir,BIMHWFile))
    with open(mhw_file_for_bimode,'w') as f:                        
        f.write('% MHW (m NAVD88)\t%SLR_A\t%SLR_B\t%Region ')                            
        f.write('\n')
        for n in range(0,len(IslandMHWCompLists)):
            bmhw = str(BIMODEmhw[n])+'\t0.000\t0.000\t'+str(n+1)
            f.write(bmhw)
            f.write('\n')


    # loop BIMODE runs over the different folders - each with individual executables and I/O
    for fol in bimode_folders:
        print '\n Modeling %s' % fol
        bmdir = os.path.normpath(r'%s\\%s' %(bimode_dir,fol))
        os.chdir(bmdir)
    
    # copy tidal prism file into specific BIMODE folder (shutil.copy will overwrite any existing tidal prism file that has the same name)
        prism_file_for_folder = os.path.normpath('%s\\input\\%s' %(bmdir,BIPrismFile))
        shutil.copy(prism_file_for_bimode,prism_file_for_folder)
    # copy MHW file into specific BIMODE folder (shutil.copy will overwrite any existing tidal prism file that has the same name)
        mhw_file_for_folder = os.path.normpath('%s\\input\\%s' %(bmdir,BIMHWFile))
        shutil.copy(mhw_file_for_bimode,mhw_file_for_folder)
    
    
        
# run compiled Fortran executable - will automatically return to Python window when done running
        print ' Running BIMODE executable for %s region.' % fol
        bimoderun = os.system('bimo.exe')

        if bimoderun != 0:
            print '\n\n  BIMODE did not run for year %s.' % year
            waittime = random.random()*60
            print '\n Retrying BIMODE model run for year %s after waiting %.2f seconds.' % (year,waittime)
            print ' Waiting...'
            time.sleep(waittime)
            print ' Done waiting. Retrying BIMODE now.'
            bimoderun = os.system('bimo.exe')

            if bimoderun != 0:
                print '\n\n  BIMODE still did not run for year %s.' % year
                waittime = random.random()*60
                print '\n Retrying BIMODE model run for year %s after waiting %.2f seconds.' % (year,waittime)
                print ' Waiting...'
                time.sleep(waittime)
                print ' Done waiting. Retrying BIMODE now.'
                bimoderun = os.system('bimo.exe')

                if bimoderun != 0:
                    error_msg = '\n BIMODE model run for year %s was unsuccessful.' % year
                    sys.exit(error_msg)

    
# rename existing tidal prism files by appending model year to file name
        print ' Cleaning up BIMODE files for %s region.' % fol
        prismfile_noext = BIPrismFile.split('.')
        rename_BMprism = os.path.normpath(r'%s\\input\\%s_%04d.%s' % (bmdir,prismfile_noext[0],year-startyear+1,prismfile_noext[1]))

# first try rename, so that a warning is given that the existing tidal prism file is being overwritten (only occurs if old model run data exists)    
        try:
            os.rename(prism_file_for_folder,rename_BMprism)
        except OSError as Exception:
            if Exception.errno == errno.EEXIST:
                print ' Tidal prism file %s already exists.' % rename_BMprism
                print ' The pre-existing file was deleted and overwritten.'
                shutil.copy(prism_file_for_folder,rename_BMprism)

        # read in profiles that were breached during model year
        breachfile = os.path.normpath('%s\\results\\Breaching_%04d' %(bmdir,elapsedyear))   #BIMODE uses output files use elapsed years, BIMODE file at end of startyear = filename1
        brs = np.genfromtxt(breachfile,skiprows=1)
        # read through profiles and append to breach dictionary for year if breached
        for n in range(0,len(brs)):
            if brs[n,1] == 1.:
                   breaches[year].append(brs[n,0])


        ## append profile files to array that gets passed to WM.py - use np.vstack if profile array has already been started
        print ' Adding BIMODE output profile data for %s into array with profiles from other regions.' % fol
        profilefile = os.path.normpath('%s\\results\\profile_%04d' %(bmdir,year-startyear+1))
        if len(BMprof_forWM) == 0:
            BMprof_forWM=np.genfromtxt(profilefile,usecols=[0,1,2]) #ignore last column of file, which is the profile ID #
        else:
            BMprof_forWM=np.vstack((BMprof_forWM,np.genfromtxt(profilefile,usecols=[0,1,2])))
        # check BIMODE results folder for separate 'window file' which is proflies located in island passes
        
        # if this file exists, append those xyz values to BMprof_forWM with np.vstack
        passprofilefile = os.path.normpath('%s\\results\\window_file_%04d' %(bmdir,year-startyear+1))
        if os.path.isfile(passprofilefile) == True:
            BMprof_forWM=np.vstack((BMprof_forWM,np.genfromtxt(profilefile,usecols=[0,1,2],skiprows = 1)))
        
              
        
    ## write master file with all profile XYZ info to text file that gets read by WM.py function
    ## this will overwrite existing file named the same and located here (e.g. the previous year's file)
    ## this is intentional, since the profile data is all saved individually within BIMODE project folders

    print '\n Writing all BIMODE profiles to single text file to pass to Morphology model.'
    BMprof_forWMfile = os.path.normpath(r'%s\\BIMODEprofiles.xyz' %(bimode_dir))
    np.savetxt(BMprof_forWMfile,BMprof_forWM,delimiter='   ',comments='',fmt=['%.4f','%.4f','%.4f'])
    
    del BMprof_forWM

    
    #########################################################
    ##                SETUP VEGETATION MODEL               ##
    #########################################################
    os.chdir(vegetation_dir)
    if elapsed_hotstart == 0:
        if year == startyear + elapsed_hotstart:
            print '\n--------------------------------------------------'
            print '        CONFIGURING VEGETATION MODEL'
            print '      - only during initial year of ICM -'
            print '--------------------------------------------------\n'        



            sys.path.append(vegetation_dir)
        
            import model_v2
            
            LAVegMod = model_v2.Model()
        
            try:
                LAVegMod.config(VegConfigFile)
            except exceptions as error:
                print '******ERROR******'
                print error
                sys.exit('\nFailed to initialize Veg model.')

    #########################################################
    ##                RUN VEGETATION MODEL                 ##
    #########################################################
    print '\n--------------------------------------------------'
    print '  RUNNING VEGETATION MODEL - Year %s' % year
    print '--------------------------------------------------\n'  
    
    
    try:
        LAVegMod.step()
    except exceptions.RuntimeError as error:
        print '\n ******ERROR******'
        print error
        sys.exit('Vegetation model run failed - Year %s.' % year)
    
    veg_output_file = '%s_O_%02d_%02d_V_vegty.asc+' % (runprefix,elapsedyear,elapsedyear)
    veg_deadfloat_file = '%s_O_%02d_%02d_V_deadf.asc' % (runprefix,elapsedyear,elapsedyear)

    if os.path.isfile(veg_deadfloat_file) == False:
        veg_deadfloat_file = 'NONE'
        

    #########################################################
    ##                  RUN MORPHOLOGY MODEL               ##
    #########################################################
    print '\n--------------------------------------------------'
    print r'  RUNNING MORPHOLOGY MODEL - Year %s' % year
    print '--------------------------------------------------\n'   
    #change working directory to wetland morph folder
    os.chdir(wetland_morph_dir)
   
    #update WM config file with current model year
    WM_params[0] = runprefix
    WM_params[1] = str(year)

    WM_params[54] = EH_grid_out_newfile
    WM_params[58] = EH_comp_out_newfile
    
    if elapsedyear in yearstokeepmorph:
        WM_params[62] = 'FALSE'
    else:
        WM_params[62] = 'TRUE'
    
    # Update morphology model input parameters for project implemented during current model year
    # Implement marsh creation projects
    if year in mc_years:
        pjindex = mc_years.index(year)
        WM_params[6] = mc_shps[pjindex]
        WM_params[7] = mc_shps_fields[pjindex]
    else:
        WM_params[6] = 'NONE'
        WM_params[7] = 'NONE'
    
    # Implement shoreline protetion projects
    if year in sp_years:
        pjindex = sp_years.index(year)
        WM_params[9] = sp_shps[pjindex]
        WM_params[10] = sp_shps_fields[pjindex]
    else:
        WM_params[9] = 'NONE'
        WM_params[10] = 'NONE'
        
    # Implement shoreline protetion projects
    if year in levee_years:
        pjindex = levee_years.index(year)
        WM_params[13] = levee_shps[pjindex]
        WM_params[14] = levee_shps_fields1[pjindex]
        WM_params[15] = levee_shps_fields2[pjindex]
        WM_params[16] = levee_shps_fields3[pjindex]
        WM_params[17] = levee_shps_fields4[pjindex]
    else:
        WM_params[13] = 'NONE'
        WM_params[14] = 'NONE'
        WM_params[15] = 'NONE'
        WM_params[16] = 'NONE'
        WM_params[17] = 'NONE'    
        
    
    #run Wetland Morph model
    try:
        WM.main(WM_params,ecohydro_dir,wetland_morph_dir,EHtemp_path,vegetation_dir,veg_output_file,veg_deadfloat_file,nvegtype,HSI_dir,BMprof_forWMfile,n500grid,n500rows,n500cols,yll500,xll500,n1000grid,elapsedyear)
    except Exception, error:
        print '******ERROR******'
        print error
        sys.exit('\n Morphology model run failed - Year %s.' % year)

    # update name of grid data file generated by Morph to include current year in name
    new_grid_file = 'grid_data_500m_end%s.csv' % (year)  # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year) here instead of CurrentYear
    new_grid_filepath = os.path.normpath('%s\\%s' % (EHtemp_path,new_grid_file)) # location of grid file after it is generated in "WM.CalculateEcohydroAttributes"

    ##############################################
    ##    HABITAT SUITABILITY INDICES ~ HSIs    ##
    ##############################################
    print '\n--------------------------------------------------'
    print '  RUNNING HABITAT SUITABILITY INDICES - Year %s' % year
    print '--------------------------------------------------\n'
    os.chdir(ecohydro_dir)

    # read in Morph output file
    print ' Reading in Morphology output files to be used for HSIs.'
    # import grid summary file (percent land, elevations) generated by Morphology
    griddata = np.genfromtxt(new_grid_filepath,delimiter=',',skiprows=1)
    # landdict is a dictionary of percent land (0-100) in each 500-m grid cell, key is gridID
    landdict = dict((griddata[n][0],griddata[n][3]) for n in range(0,n500grid))
    waterdict = dict((griddata[n][0],griddata[n][5]) for n in range(0,n500grid))
    melevdict = dict((griddata[n][0],griddata[n][2]) for n in range(0,n500grid))
    wetlanddict = dict((griddata[n][0],griddata[n][4]) for n in range(0,n500grid))
    
    # Post-process Ecohydro output for HSI calculations
    print ' Reading in Ecohydro output files to be used for HSIs.'

    # import annual Ecohydro output that is summarized by grid ID (Column 0 corresponds to 500m ID#, Column 7 is percent sand, and  Column 17 is average depth)    
    EH_grid_out = np.genfromtxt(EH_grid_results_filepath,delimiter = ',',skiprows = 1)
    depthdict = dict((EH_grid_out[n][0],EH_grid_out[n][15:17]) for n in range(0,n500grid)) # column 15 is mean summer depth, column 16 is mean annual depth
    stagedict = dict((EH_grid_out[n][0],EH_grid_out[n][12]) for n in range(0,n500grid))
    # Import percent sand in substrate for HSI data
    pctsanddict = dict((EH_grid_out[n][0],EH_grid_out[n][7]) for n in range(0,n500grid))

    del(EH_grid_out)

    # Import monthly values for HSI data in dictionaries
    # import ecohydro monthly output that is summarized by 500-m grid ID (Column 0 corresponds to GridID)    
    EH_sal_file = os.path.normpath(ecohydro_dir + '\\sal_monthly_ave_500m.out')
    sal = np.genfromtxt(EH_sal_file,delimiter = ',',skiprows = 1)
    saldict = dict((sal[n][0],sal[n][1:14]) for n in range(0,n500grid))

    # Save list of GridIDs from Hydro output file
    gridIDs=[]
    for n in range(0,n500grid):
       gridIDs.append(sal[n][0])
    del(sal)
    
    # Import monthly temperature values for HSI data
    EH_tmp_file = os.path.normpath(ecohydro_dir + '\\tmp_monthly_ave_500m.out')
    tmp = np.genfromtxt(EH_tmp_file,delimiter = ',',skiprows = 1)
    tmpdict = dict((tmp[n][0],tmp[n][1:13]) for n in range(0,n500grid))
    del(tmp)
    
    # Import monthly TSS values for HSI data
    EH_TSS_file = os.path.normpath(ecohydro_dir + '\\TSS_monthly_ave_500m.out')
    TSS = np.genfromtxt(EH_TSS_file,delimiter = ',',skiprows = 1)
    TSSdict = dict((TSS[n][0],TSS[n][1:13]) for n in range(0,n500grid))
    del(TSS)

    # Import monthly algae values for HSI data
    EH_ChlA_file = os.path.normpath(ecohydro_dir + '\\tkn_monthly_ave_500m.out')
    ChlA = np.genfromtxt(EH_ChlA_file,delimiter = ',',skiprows = 1)
    ChlAdict = dict((ChlA[n][0],ChlA[n][1:13]) for n in range(0,n500grid))
    del(ChlA)

    veg_output_filepath = os.path.normpath(vegetation_dir + '\\' + veg_output_file)

    # run HSI function (run in HSI directory so output files are saved there)
    os.chdir(HSI_dir)

    # import percent edge output from geomorph routine that is summarized by grid ID
    pctedge_file = os.path.normpath('%s\\%s_N_%02d_%02d_W_pedge.csv'% (HSI_dir,runprefix,elapsedyear,elapsedyear)) # this must match name set in "WM.CalculateEcohydroAttributes" with the exception of (year) here instead of CurrentYear
    pedge = np.genfromtxt(pctedge_file,delimiter = ',',skiprows = 1)
    pctedgedict = dict((pedge[n][0],pedge[n][1]) for n in range(0,n500grid))
    del(pedge)
    
    
    try:
        HSI.HSI(gridIDs,stagedict,depthdict,melevdict,saldict,tmpdict,TSSdict,ChlAdict,veg_output_filepath,nvegtype,landdict,waterdict,pctsanddict,pctedgedict,n500grid,n500rows,n500cols,yll500,xll500,year,elapsedyear,HSI_dir,WM_params,vegetation_dir,wetland_morph_dir,runprefix)
    except Exception,error :
        print '******ERROR******'
        print '\n HSI model run failed - Year %s.' % year
        print error
        

    ##########################################
    ##       FORMAT DATA FOR EWE MODEL      ##
    ##########################################
    print '\n--------------------------------------------------'
    print ' FORMATTING DATA FOR EWE - Year %s' % year
    print '--------------------------------------------------\n'
    print ' Reading in ASCII grid template.'                                               
    os.chdir(ewe_dir)
    ewe_grid_ascii_file = 'EwE_grid.asc'                                                   
                                                                                           
    
    ascii_grid_lookup = np.genfromtxt(ewe_grid_ascii_file,skiprows=6)        
                                                                                           
    ascii_header='nrows %s \nncols %s \nyllcorner %s \nxllcorner %s \ncellsize 1000 \nnodata_value -9999' % (n1000rows,n1000cols,yll1000,xll1000)

    nrows = n1000rows                                                                      
    ncols = n1000cols          

    EwEGridMap = np.genfromtxt('EwE_Veg_grid_lookup.csv',skiprows=1,delimiter=',')         
    EwEGridMapDict = dict((EwEGridMap[n][0],EwEGridMap[n][1:5])for n in range(0,len(EwEGridMap)))
    
    for output in ['depth']:
        print ' - mapping %s output to EwE grid' % output                                                 
        newgrid=np.zeros([nrows,ncols]) 
        for m in range(0,nrows):                                                           
            for n in range(0,ncols):                                                       
                cellID = ascii_grid_lookup[m][n]                                           
                if cellID == -9999:                                                        
                    newgrid[m][n] = -9999                                                  
                else:                                                                      
                    try:                                                                   
                        value = 0                                                          
                        value_n = 0                                                        
                        for g in range(0,4):                                               
                            grid = EwEGridMapDict[cellID][g]                               
                            if grid > 0:                                              
                                value += depthdict[grid][1] # depthdict[grid][0] is mean summer depth, depthdict[grid][1] is mean annual depth
                                value_n += 1                                               
                        newgrid[m][n] = value/value_n                                      
                    except:   # if cellID is not a key in the newLULCdictionay - assign cell to NoData
                        newgrid[m][n] = -9999                                              

        print " - saving new EwE %s ASCII raster file" % output
        
        # save formatted LULC grid to ascii file with appropriate ASCII raster header      
        EwEasc = '%s\\%s\\%s_I_%02d-%02d_E_%s.asc' % (ewe_dir,output,runprefix,elapsedyear,elapsedyear,output)
        np.savetxt(EwEasc,newgrid,fmt='%.4f',delimiter=' ',header=ascii_header,comments='')

    for output in ['uplnd']:
        print ' - mapping %s output to EwE grid' % output                                                 
        newgrid = np.zeros([nrows,ncols]) 
        for m in range(0,nrows):                                                           
            for n in range(0,ncols):                                                       
                cellID = ascii_grid_lookup[m][n]                                           
                if cellID == -9999:                                                        
                    newgrid[m][n] = -9999                                                  
                else:                                                                      
                    try:                                                                   
                        value = 0
                        value_n = 0                                                        
                        for g in range(0,4):                                               
                            grid = EwEGridMapDict[cellID][g]                               
                            if grid > 0:                                              
                                upvalue = max(landdict[grid] - wetlanddict[grid],0)
                                value += upvalue
                                value_n += 1                                               
                        newgrid[m][n] = value/value_n                                      
                    except:   # if cellID is not a key in the newLULCdictionay - assign cell to NoData
                        newgrid[m][n] = -9999                                              

        print " - saving new EwE %s ASCII raster file" % output
        
        # save formatted LULC grid to ascii file with appropriate ASCII raster header      
        EwEasc = '%s\\%s\\%s_I_%02d-%02d_E_%s.asc' % (ewe_dir,output,runprefix,elapsedyear,elapsedyear,output)
        np.savetxt(EwEasc,newgrid,fmt='%.4f',delimiter=' ',header=ascii_header,comments='')

    for output in ['wtlnd']:
        print ' - mapping %s output to EwE grid' % output                                                 
        newgrid=np.zeros([nrows,ncols]) 
        for m in range(0,nrows):                                                           
            for n in range(0,ncols):                                                       
                cellID = ascii_grid_lookup[m][n]                                           
                if cellID == -9999:                                                        
                    newgrid[m][n] = -9999                                                  
                else:                                                                      
                    try:                                                                   
                        value = 0                                                          
                        value_n = 0                                                        
                        for g in range(0,4):                                               
                            grid = EwEGridMapDict[cellID][g]                               
                            if grid > 0:                                              
                                value += wetlanddict[grid]
                                value_n += 1                                               
                        newgrid[m][n] = value/value_n                                      
                    except:   # if cellID is not a key in the newLULCdictionay - assign cell to NoData
                        newgrid[m][n] = -9999                                              

        print " - saving new EwE %s ASCII raster file" % output
        
        # save formatted LULC grid to ascii file with appropriate ASCII raster header      
        EwEasc = '%s\\%s\\%s_I_%02d-%02d_E_%s.asc' % (ewe_dir,output,runprefix,elapsedyear,elapsedyear,output)
        np.savetxt(EwEasc,newgrid,fmt='%.4f',delimiter=' ',header=ascii_header,comments='')


                                                                                               
    monthcols = [0,1,2,3,4,5,6,7,8,9,10,11]                                                
    monthtext = ['01','02','03','04','05','06','07','08','09','10','11','12']              
    
    for output in ['sal','tkn','tmp','tss']:
        print ' - mapping %s output to EwE grid' % output                                                 
        
        if output == 'sal':
            monthly_dict = saldict
        elif output == 'tkn':
            monthly_dict = ChlAdict # ChlA output is actually TKN (see above HSI.HSI where it is read in to the dictionary)
        elif output == 'tmp':
            monthly_dict = tmpdict
        elif output == 'tss':
            monthly_dict = TSSdict
                                                                                             
        # initialize new array that will save model-wide monthly means for output
        modelave = np.zeros((1,12))    

        # loop through each month and save an ASCII grid raster file for EwE grid
        for month in monthcols:                                                                
            newgrid=np.zeros([nrows,ncols]) 
            for m in range(0,nrows):                                                           
                for n in range(0,ncols):                                                       
                    cellID = ascii_grid_lookup[m][n]                                           
                    if cellID == -9999:                                                        
                        newgrid[m][n] = -9999                                                  
                    else:                                                                      
                        try:                                                                   
                            value = 0                                                          
                            value_n = 0                                                        
                            for g in range(0,4):                                               
                                grid = EwEGridMapDict[cellID][g]                               
                                if grid > 0:                                              
                                    value += monthly_dict[grid][month]                         
                                    value_n += 1                                               
                            newgrid[m][n] = value/value_n                                      
                        except:   # if cellID is not a key in the newLULCdictionay - assign cell to NoData
                            newgrid[m][n] = -9999                                              
            
            print " - saving new %s ASCII raster file for month %s" % (output,monthtext[month])
            
            # save formatted LULC grid to ascii file with appropriate ASCII raster header      
            EwEasc = '%s\\%s\\%s_I_%02d-%02d_E_%s%s.asc' % (ewe_dir,output,runprefix,elapsedyear,elapsedyear,output,monthtext[month])
            np.savetxt(EwEasc,newgrid,fmt='%.4f',delimiter=' ',header=ascii_header,comments='')
            
                       
            # save model-wide monthly average value for output type
            for row in range(0,len(monthly_dict)):
                modelave[0][month] += monthly_dict[row+1][month]/len(monthly_dict)
        
        print " - saving model-wide monthly averages for %s" % output
        ave_file = '%s\\%s\\%s_I_%02d-%02d_E_%s00.csv' % (ewe_dir,output,runprefix,elapsedyear,elapsedyear,output)
        ave_file_h = '1,2,3,4,5,6,7,8,9,10,11,12'
        np.savetxt(ave_file,modelave,delimiter=',',header=ave_file_h,fmt='%.4f',comments='')
    

    del (depthdict,saldict,tmpdict,TSSdict,ChlAdict,gridIDs,newgrid,modelave,monthly_dict,ascii_grid_lookup,EwEGridMap,EwEGridMapDict)
        # SFTP settings for data upload
        
    if sftp_upload == True:
        print '\n--------------------------------------------------'
        print '  UPLOADING SELECT OUTPUT TO SFTP SERVER.'
        print '--------------------------------------------------\n'
    
        if year == startyear + elapsed_hotstart:
            uploadfails = []
        
        
        dpath = '%s\\output_%02d\\Deliverables' % (wetland_morph_dir,elapsedyear)
        upfiles = os.listdir(dpath)
        
        gpath = os.path.normpath(r'\MP2017\3.8\%s\%s' % (sterm,gterm))
        geopath = os.path.normpath(r'%s\geomorph' % gpath)
        outputpath = os.path.normpath(r'%s\output_%02d' % (geopath,elapsedyear))
        up_path = os.path.normpath(r'%s\Deliverables' % outputpath)
        
        try:
            with pysftp.Connection(host,username=un,password=pw,port=pt)as sftp:
                print '-- SFTP connection successful - uploading files.'
                
                if sftp.isdir(gpath) == False:
                    print ' %s is missing on FTP - attempting to make folder.' % gpath
                    sdir = os.path.normpath('/MP2017/3.8/%s' % sterm)
                    sftp.mkdir(gpath)
                
                if sftp.isdir(geopath) == False:
                    print ' %s is missing on FTP - attempting to make folder.' % geopath
                    sftp.mkdir(geopath)
                
                print ' - building Deliverables folder for output on SFTP'
                sftp.mkdir(outputpath)
                sftp.mkdir(up_path)
                
                sftp.chdir(up_path)
                
                for localfile in upfiles:
                    try:
                        uploadfile = '%s\\%s' % (dpath,localfile)
                        if sftp.isfile(localfile):
                            print ' %s is already on the SFTP in %s - Not uploaded!' % (outfile,gpath)
                            uploadfails.append(localfile)
                        else:
                            sftp.put(uploadfile)
                    except:
                        print ' %s failed to upload - trying next file' % outfile
                        uploadfails.append(localfile)
                    
        except:
            print '-- SFTP connection unsuccessful for %s model year.' % elapsedyear
            uploadfails.append('All files in year %02d' % elapsedyear)
    else:
        uploadmessage_not_on = ' SFTP uploading was not activated for this run.'
# End Time-stepping loop


if sftp_upload == True:
    if len(uploadfails) > 0:
        uploadmessage = ' Some SFTP uploads failed - manually upload data for years: %s' % uploadfails
    else:
        uploadmessage = ' All SFTP uploads were successful.'
else:
    uploadmessage = uploadmessage_not_on
    



######




print '\n\n\n'
print ' Copying hydro output files with naming convention names...'



print '\n\n\n'
print '--------------------------------------------------'
print ' ICM Model run complete!'
print ' Renaming hydro output files.'
print '--------------------------------------------------\n'

output_dir = os.path.normpath(r'%s\\output_timeseries' % ecohydro_dir)
files_to_rename = ['ALG','DET','DIN','DO','DON','fflood','FLO','NH4','NO3','NRM','OrgN','SAL','SPH','STG','STGm','TKN','TMP','TOC','TPH','TRG','TSS']
os.mkdir(output_dir)

runprefix = '%s_%s_%s_%s_%s_%s_%s' % (mpterm,sterm,gterm,cterm,uterm,vterm,rterm)

eh_outfiles = os.listdir(ecohydro_dir)

oprefix = r'%s_O_%02d_%02d_H_' % (runprefix,1,(endyear-startyear+1))

for outfile in eh_outfiles:
    if outfile.endswith('.out'):
        outfilepath = os.path.normpath(r'%s\\%s' % (ecohydro_dir,outfile))
        splitcode = outfile.split('.')
        startcode = splitcode[0]
        endcode = splitcode[1]
        
        if startcode in files_to_rename:
            print ' Renaming %s' % outfile
            if len(startcode) == 2:
                blanks = "xxx"
            elif len(startcode) == 3:
                blanks = "xx"
            elif len(startcode) == 4:
                blanks = "x"
            else:
                blanks =""
        
            named = os.path.normpath(r'%s\\%s%s%s.%s' % (output_dir,oprefix,startcode,blanks,endcode))
            shutil.copy(outfilepath,named)
        
            if os.path.getsize(outfilepath) != os.path.getsize(named):
                print '********ERROR********'
                print '   Files are not same size - check that file copied to output_timeseries folder correctly.'

print '--------------------------------------------------'
print ' Done renaming hydro output files.'
print '--------------------------------------------------\n'


if run_ewe == True:
        
    print '--------------------------------------------------'
    print ' Running EwE Model.'
    print '--------------------------------------------------\n'
    
    hydlocation = ecohydro_dir
    
    
    years = range(2015,2065) 
    months = range(1,13)
    
    ncols = n1000cols
    nrows = n1000rows
    
    ascii_header='nrows %s \nncols %s \nyllcorner %s \nxllcorner %s \ncellsize 1000 \nnodata_value -9999' % (nrows,ncols,yll1000,xll1000)
    
    
    hyddir = ecohydro_dir
    ewedir = ewe_dir
    origewedir = ewe_dir
    S = sterm
    G = gterm
    
    ewedir_split = ewedir.split('\\')
    ewedirwin = 1
    for term in ewedir_split:
        if ewedirwin == 1:
            ewedirwin = r'%s' % term
        else:
            ewedirwin = r'%s\%s' % (ewedirwin,term)
         
    ewe_spatial_file_template = '%s\\EwESpatialConfigTEMPLATE_CALIB_SPINUP.xml' % ewedir 
    
    
    tssfile = '%s\\output_timeseries\\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_50_H_TSSxx.out' % (hyddir,S,G)
    tknfile = '%s\\output_timeseries\\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_50_H_TKNxx.out' % (hyddir,S,G)
    salfile = '%s\\output_timeseries\\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_50_H_SALxx.out' % (hyddir,S,G)
    tmpfile = '%s\\output_timeseries\\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_50_H_TMPxx.out' % (hyddir,S,G)
    
    #set some paths with single slash for use when writing to EwE configuration text file
    tssfilewin = '%s\output_timeseries\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_50_H_TSSxx.out' % (hyddir,S,G)
    tknfilewin = '%s\output_timeseries\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_50_H_TKNxx.out' % (hyddir,S,G)
    salfilewin = '%s\output_timeseries\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_50_H_SALxx.out' % (hyddir,S,G)
    tmpfilewin = '%s\output_timeseries\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_50_H_TMPxx.out' % (hyddir,S,G)
    ewe_command_file = '%s\\%s_%s_EwECommand.txt' % (ewedir,S,G)            
    ewe_spatial_file = '%s\\%s_%s_EwESpatialConfig.xml' % (ewedir,S,G)      
    ewe_spatial_file_win = '%s\%s_%s_EwESpatialConfig.xml' % (ewedirwin,S,G)
    
    
      
    print ' Reading in dates and grid structure'
    
    datesfile =   r'%s\\dates.csv' % ewedir
    ewegridfile = r'%s\\EwE_grid.asc' % ewedir
    ewecompfile = r'%s\\EwEgrid_ICMID.csv' % ewedir
    
    
    dates = np.genfromtxt(datesfile,delimiter=',',skiprows=1)
    ewegrid=np.genfromtxt(ewegridfile,skiprows=6)
    ewelookup = np.genfromtxt(ewecompfile,delimiter=',',skiprows=1)
                                         
    for data in ['tss','tkn','sal','tmp']:                                     
        if data == 'tss':        
            hyddata = tssfile    
        elif data == 'tkn':
            hyddata = tknfile    
        elif data == 'tmp':
            hyddata = tmpfile
        else:
            hyddata = salfile
        
        
        ewedatadir = '%s\\%s' % (ewedir,data)
        originputdir = '%s\\%s' % (origewedir,data)
        inputgriddata = '%s\\%s_without_offshore_data' % (origewedir,data)
        
        os.rename(originputdir,inputgriddata)
        os.mkdir(ewedatadir)
        
        print ' Reading in data from %s' % hyddata
        compdata = np.genfromtxt(hyddata,delimiter=',')
    
        outfile = '%s\\%s_monthly_compartment.csv' % (ewedir,data)
    
        print ' Updating EwE grid for offshore %s data.' % data
    
        gridcomp = {}
        for pair in ewelookup:
            gridID = pair[0]
            compID = pair[1]
            gridcomp[gridID] = compID
            
        outhead = 'Year,Month'
        for comp in range(1,947):
            outhead = '%s,%s' %(outhead,comp)
    
        out = np.zeros((len(years)*len(months),946+2))
    
        os.chdir(ewedatadir)
    
        outrow = 0
        for year in years:
            for month in months:
                print ' Month %s, Year %s' % (month,year)
                out[outrow][0] = year
                out[outrow][1] = month
                ave = np.zeros(946)
                aven = np.zeros(946)
                for date in range(0,len(dates)):
                    if dates[date][2] == year:
                        if dates[date][1] == month:
                            for comp in range(0,946):
                                ave[comp] += compdata[date][comp]
                                aven[comp] +=1
    
                for comp in range(0,946):
                    outcol = comp +2
                    out[outrow][outcol] = ave[comp]/aven[comp]
                            
                outrow += 1
    
        np.savetxt(outfile,out,delimiter=',',comments='',fmt='%.2f',header=outhead)
    
        for year in years:
            elapsedyear = year-years[0]+1
            for month in months:
                print ' Updating EwE %s ASCII file for %s_%s Month %s, Year %s' % (data,S,G,month,year)
                compave_row = years.index(year) + months.index(month)
                ingridfile = '%s\\MPM2017_%s_%s_C000_U00_V00_SLA_I_%02d-%02d_E_%s%02d.asc' % (inputgriddata,S,G,elapsedyear,elapsedyear,data,month)
                outgridfile = '%s\\MPM2017_%s_%s_C000_U00_V00_SLA_I_%02d-%02d_E_%s%02d.asc' % (ewedatadir,S,G,elapsedyear,elapsedyear,data,month)
                
                ingrid=np.genfromtxt(ingridfile,skiprows=6)
                new = np.zeros((nrows,ncols))
    
                for r in range(0,nrows):
                    for c in range(0,ncols):
                        grid = ewegrid[r][c]
                        if grid > 0:
                            orig = ingrid[r][c]
                            if orig > -9999:
                                new[r][c] = orig
                            else:
                                compave_col = gridcomp[grid]+1
                                if compave_col == 1:
                                    new[r][c] = -9999
                                else:
                                    new[r][c] = out[compave_row][compave_col]
                        else:
                            new[r][c] = -9999
                np.savetxt(outgridfile,new,delimiter=' ',comments='',fmt='%.2f',header=ascii_header)
    
    
        del ingridfile,ingrid
        del compdata, out
    
       
    for data in ['wtlnd','uplnd']:
        ewedatadir = '%s\\%s' % (ewedir,data)
        inputgriddata = '%s\\%s_without_offshore_data' % (origewedir,data)
        
        os.rename(ewedatadir,inputgriddata)
        os.mkdir(ewedatadir)
     
        
        for year in years:
            elapsedyear = year-years[0]+1
            
            print ' Updating EwE %s ASCII file for %s_%s Year %s' % (data,S,G,year)
            infile = '%s\\MPM2017_%s_%s_C000_U00_V00_SLA_I_%02d-%02d_E_%s.asc' % (inputgriddata,S,G,elapsedyear,elapsedyear,data)
            outgridfile = '%s\\MPM2017_%s_%s_C000_U00_V00_SLA_I_%02d-%02d_E_%s.asc' % (ewedatadir,S,G,elapsedyear,elapsedyear,data)
            ingrid=np.genfromtxt(infile,skiprows=6)
            new = np.zeros((nrows,ncols))
            for r in range(0,nrows):
                for c in range(0,ncols):
                    grid = ewegrid[r][c]
                    if grid > 0:
                        orig = ingrid[r][c]
                        if orig > -9999:
                            new[r][c] = orig
                        else:
                            new[r][c] = 0.0
                    else:
                        new[r][c] = -9999
            np.savetxt(outgridfile,new,delimiter=' ',comments='',fmt='%.2f',header=ascii_header)
    
    print '\n Finished writing EwE input data files.'
    
    os.chdir(ewedir)
    
    print ' Opening Spatial File template and writing spatial config file: %s' %ewe_command_file
    with open(ewe_spatial_file_template,'r') as stfile:
        with open(ewe_spatial_file,'w') as scfile:
            for line in stfile:
                split_s = line.split('Sxx_Gxxx')
                if len(split_s) > 1:
                    pre_s = split_s[0]
                    post_g = split_s[1]
                    writeline = '%s%s_%s%s' % (pre_s,S,G,post_g)
                else:
                    writeline = line
                
                scfile.write(writeline)
                
    
    print ' Writing EwE Command file: %s' %ewe_command_file
    with open(ewe_command_file,'w') as cfile:
        cfile.write('\n')
        cfile.write('TAG,DATA,COMMENTS\n')
        cfile.write('<N_BIOMASS_THREADS>, 2\n')
        cfile.write('<N_GRID_THREADS>,2\n')
        cfile.write('<N_EFFORT_DIST_THREADS>,2\n')
        cfile.write('\n')
        cfile.write('Input data base and scenarios\n')
        cfile.write('<EWE_MODEL_FILE>,%s\CMP2017_22Nov_Ecopath.eiixml\n' % ewedirwin)
        cfile.write('<ECOSIM_SCENARIO_INDEX>, 1, Coast wide\n')
        cfile.write('<ECOSPACE_SCENARIO_INDEX>, 1, Coast wide\n')
        cfile.write('\n')
        cfile.write('Run length\n')
        cfile.write('<N_ECOSPACE_YEARS>, 64, 14 year for the spinup period then 50 years for the forecast run\n')
        cfile.write('<N_ECOSPACE_TIMESTEP_YEAR>, 12\n')
        cfile.write('<FIRST_OUTPUT_TIMESTEP>, 169, Start writing results after the spinup period, 14 years of spinup data\n')
        cfile.write('\n')
        cfile.write('Outputs files\n')
        cfile.write('<SAVE_MAP_OUTPUT>, True\n')
        cfile.write('<SAVE_ANNUAL_OUTPUT>, False, Monthly output\n')
        cfile.write('<ECOSPACE_OUTPUT_DIR>, %s\EwEOutput\n' %ewedirwin)
        cfile.write('<ECOSPACE_MAP_OUTPUT_DIR>,Maps\n')
        cfile.write('<ECOSPACE_AREA_OUTPUT_DIR>,AreaAveraged\n')
        cfile.write('\n')
        cfile.write('<SPATIAL_ENABLED>, True\n')
        cfile.write('<SPATIAL_CONFIG_FILE>,%s\n' % ewe_spatial_file_win)
        cfile.write('\n')
        cfile.write('Oyster Layer\n')
        cfile.write('<OYSTER_LAYER_EXE>,%s\OECL.exe\n' % ewedirwin)
        cfile.write('<OYSTER_LAYER_OUTPUT_DIRECTORY>,%s\n'% ewedirwin)
        cfile.write('\n')
        cfile.write('Inputs for the OECL executable\n')
        cfile.write('<OYSTER_LAYER_INPUT_SAL>,%s\n' % salfilewin)
        cfile.write('<OYSTER_LAYER_INPUT_TMP>,%s\n' % tmpfilewin)
        cfile.write('<OYSTER_LAYER_INPUT_TSS>,%s\n' % tssfilewin)
        cfile.write('\n')
        cfile.write('\n')
        cfile.write('\n')
        cfile.write('ICM model run identifier\n')
        cfile.write('<ICM_FILENAME_PREFIX>,%s_%s_C000_U00_V00_SLA\n' % (S,G))
        
    print ' Running EwE for %s_%s' % (S,G)
    
    ewe_call = 'EcospaceConsole.exe .\%s_%s_EwECommand.txt' % (S,G)
    ewerun = os.system(ewe_call)

    print '--------------------------------------------------'
    print ' Finished running EwE'
    print '\n\n ICM Model and EwE runs are both complete.'
    print '--------------------------------------------------\n'

else:
    print '--------------------------------------------------'
    print ' Not running EwE Model - flag set to false.'
    print '\n\n ICM Model Run is complete.'
    print '--------------------------------------------------\n'



print uploadmessage 



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
##              b. called within command prompt as:  C:\\Working\\Directory> ICM.py
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
## On Eric's machine this 'DTBGGP64.pth' was saved @ C:\\Python278\Lib\site-packages\Desktop10.2.pth
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

