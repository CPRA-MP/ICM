#ICM imports
import ICM_Settings as icm

#Python imports
import errno
import numpy as np
import os
import shutil
import sys


#########################################################
##              SET UP ICM-HYDRO MODEL                 ##
#########################################################

def icm_hydro_setup(
                    n_1D,RmConfigFile,ecohydro_dir,elapsed_hotstart,vegetation_dir,
                    file_prefix_cycle,WaveAmplitudeFile,MeanSalinityFile,SummerMeanWaterDepthFile,
                    SummerMeanSalinityFile,SummerMeanTempFile,TreeEstCondFile,HtAbvWaterFile,PerLandFile,
                    PerWaterFile,AcuteSalFile,EHInterfaceFile,n500grid,n500rows,n500cols,xll500,yll500,
                    n1000grid,n1000rows,n1000cols,xll1000,yll1000,hydro_logfile,EHConfigFile,EHCellsFile,
                    EHLinksFile,startyear_cycle,startyear,inputStartYear,hotstart_year
                    ):

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

    ## File containing percentage land, and land/water elevations for each 500-m grid cell as it is used by hydro (file is generated by Morph)
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


    # Read Ecohydro's initial configuration, compartmentm and link attributes file into an arrayfile into an array of strings
    cellsheader='Compartment,TotalArea,AreaWaterPortion,AreaUplandPortion,AreaMarshPortion,MarshEdgeLength,WSEL_init,bed_elev,bed_depth,bed_bulk_density,percentForETcalc,initial_sand,initial_salinity,RainGage,WindGage,ETGage,CurrentsCoeff_ka,bedFricCoeff_cf,NonSandExp_sedn,NonSandCoeff_sedcalib,SandCoeff_alphased,Marsh_Flow_roughness_Kka,Minimum_Marsh_Flow_Depth_Kkdepth,MarshEdgeErosionRate_myr,initial_stage_marsh,marsh_elev_mean,marsh_elev_stdv,soil_moisture_depth_Esho,depo_on_off,marh_elev_adjust'
    cells_ncol = range(0,30)

    linksheader='ICM_ID,USnode_ICM,DSnode_ICM,USx,USy,DSx,DSy,Type,attr01,attr02,attr03,attr04,attr05,attr06,attr07,attr08,Exy,attr09,attr10,fa_multi'
    links_ncol = range(0,20)

    EHConfigArray=np.genfromtxt(EHConfigFile,dtype=str,delimiter='!',autostrip=True)
    EHCellsArray = np.genfromtxt(EHCellsFile,dtype=float,delimiter=',',skip_header=1,usecols=cells_ncol)
    EHLinksArray = np.genfromtxt(EHLinksFile,dtype=float,delimiter=',',skip_header=1,usecols=links_ncol)

    # Read in initial Cell/Link settings for first year of entire run, not just current cycle
    if startyear_cycle == startyear: 
        EHCellsArrayOrig = EHCellsArray
        EHLinksArrayOrig = EHLinksArray
    else:
        EHCellsFileOrig  = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EHCellsFile,'.')[0],startyear,str.split(EHCellsFile,'.')[1]))
        EHLinksFileOrig  = os.path.normpath(r"%s/%s_%s.%s" % (EHtemp_path,str.split(EHLinksFile,'.')[0],startyear,str.split(EHLinksFile,'.')[1]))

        EHCellsArrayOrig = np.genfromtxt(EHCellsFileOrig,dtype=float,delimiter=',',skip_header=1,usecols=cells_ncol)
        EHLinksArrayOrig = np.genfromtxt(EHLinksFileOrig,dtype=float,delimiter=',',skip_header=1,usecols=links_ncol)

    ncomp = len(EHCellsArray)

    # Check to see if hydro input data start date is different than ICM start year
    if inputStartYear > startyear:
        exitmsg='\n Invalid configuration! ICM model set to start before Hydro input data coverage. Check ICM_control.csv file and re-run.'
        sys.exit(exitmsg)

    # startrun is row of ICM-Hydro input data files to import into ICM-Hydro.exe
    # used to skip over data in input files for years greater than the initial model year
    # will be 0 if the first year of the simulation matches the first year of the ICM-Hydro input files
    startrun = 0
    
    # If using a hotstart year
    if inputStartYear < hotstart_year:
        for year in range(inputStartYear,hotstart_year):
            if year in range(1984,4000,4):
                ndays = 366
            else:
                ndays = 365
            
            startrun = startrun + ndays
    else:
        ndays = 0

    return (pwatr_grid_file,acute_sal_grid_file,EH_grid_filepath,cellsheader,linksheader,
            EHConfigArray,EHCellsArrayOrig,EHLinksArrayOrig,EHCellsArrayOrig,EHLinksArrayOrig,
            ncomp,HydroConfigFile,SalConfigFile,TempConfigFile,FineConfigFile,SandConfigFile,
            Sub_Sal,Sub_Temp,Sub_Fine,Sub_Sand,n_xs,Hydro_dt,Sal_dt,Tmp_dt,Fine_dt,Sand_dt,
            n_lc,EHCellsArray,lq,ndays,EHLinksArray,startrun,EH_grid_file)