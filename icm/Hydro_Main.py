#ICM imports
import ICM_Settings as icm

#Python imports
import numpy as np
import os
import shutil
import subprocess
import sys

def RunHydro(year):

    ######################################################### 
    ##                  RUN HYDRO MODEL                    ## 
    ######################################################### 


#TODO check if needed
#switch exe code#    if year in hyd_switch_years:
#switch exe code#        for nnn in range(0,len(hyd_file_orig)):
#switch exe code#            oldfile = hyd_file_orig[nnn]
#switch exe code#            newfile = hyd_file_new[nnn]
#switch exe code#            bkfile = hyd_file_bk[nnn]
#switch exe code#            print(' Copying %s to use as the new %s.' % (newfile, oldfile))
#switch exe code#            print(' Saving original %s as %s.' % (oldfile,bkfile))
#switch exe code#            os.rename(oldfile,bkfile)
#switch exe code#            os.rename(newfile,oldfile)

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

    #TODO check if these should be returned 
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
    new_grid_filepath  = os.path.normpath(r'%s/grid_data_500m_end%d.csv'                    % (EHtemp_path,year) )
    comp_elev_file     =  os.path.normpath(r'%s/compelevs_end_%d.csv'                       % (EHtemp_path,year) )
    comp_wat_file      =  os.path.normpath(r'%s/PctWater_%d.csv'                            % (EHtemp_path,year) )
    comp_upl_file      =  os.path.normpath(r'%s/PctUpland_%d.csv'                           % (EHtemp_path,year) )
    grid_pct_edge_file  = 'hsi/%s_W_pedge.csv' % (file_prefix)
    grid_Gdw_dep_file   = 'hsi/GadwallDepths_cm_%d.csv' % (year)
    grid_GwT_dep_file   = 'hsi/GWTealDepths_cm__%d.csv' % (year)
    grid_MtD_dep_file   = 'hsi/MotDuckDepths_cm_%d.csv' % (year)
   
    dem_grid_data_outfile = 'geomorph/output/%s_W_dem_grid_data.csv' % file_prefix
    
    comp_out_file = EH_comp_results_filepath