#########################################################################################################
####                                                                                                 ####
####                                START GENERAL ICM.PY PROGRAM                                     ####
####                                                                                                 ####
#########################################################################################################

#Python imports
import time

#ICM imports
#import HSI_Main as hsi_main
import ICM_HelperFunctions as hf
import ICM_Settings as icm
import ICM_Setup as icm_setup
import Hydro_Setup as hydro_setup
import LAVegMod_Setup as laveg_setup
import ICM_PreProcessing as icm_preproc
import Hydro_PreProcessing as hydro_preproc
import Hydro_Main as hydro_main
import Hydro_PostProcessing as hydro_postproc
import BarrierIsland_PreProcessing as bi_preproc
import BarrierIsland_Main as bi_main
import LAVegMod_Main as laveg_main
import Morph_PreProcessing as morph_preproc
import Morph_Main as morph_main
import Morph_PostProcessing as morph_postproc
import SAV_Main as sav_main


## NOTE: all directory paths and filenames (when appended to a directory path) are normalized
##          in this ICM routine using os.path.normpath(). This is likely a bit redundant, but it
##          was instituted so that file path directory formatting in the input parameters is forgiving.
##          If converted to Linux, this should allow for flexibility between the forward-slash vs.
##          back-slash differences between Windows and Linux.
##          This approach does not work for filepaths that are written to input text files that are passed
##          into Fortran executables. Python will convert / to \ when run on Windows...so all filepaths
##          now utilize Posix filepath convention with /. There is a function call forward2backslash that
##          can be used to convert to Windows-specific slash characters for specific files for use in Windows Fortran.

print(' Assigning variables from ICM_Settings.py')

#Run options flags
morph_zonal_stats = icm.morph_zonal_stats
run_sav = icm.run_sav
HSI_Standalone = icm.HSI_standalone

#Duration parameters
startyear = icm.startyear
endyear = icm.endyear
hotstart_year = icm.hotstart_year
elapsed_hotstart = icm.elapsed_hotstart
inputStartYear = icm.inputStartYear
startyear_cycle = icm.startyear_cycle
endyear_cycle = icm.endyear_cycle
cycle_start_elapsed = icm.cycle_start_elapsed
cycle_end_elapsed = icm.cycle_end_elapsed

# Directories
par_dir = icm.par_dir
ecohydro_dir = icm.ecohydro_dir
vegetation_dir = icm.vegetation_dir
wetland_morph_dir = icm.wetland_morph_dir    

# Executables
hydro_exe_path = icm.hydro_exe_path
bidem_exe_path= icm.bidem_exe_path 
morph_exe_path = icm.morph_exe_path
sav_submit_exe_path = icm.sav_submit_exe_path

# Hydro
n_1D = icm.n_1D
RmConfigFile = icm.RmConfigFile
update_hydro_attr = icm.update_hydro_attr

compartment_output_file = icm.compartment_output_file
grid_output_file = icm.grid_output_file
EHConfigFile = icm.EHConfigFile
EHCellsFile = icm.EHCellsFile
EHLinksFile = icm.EHLinksFile
EHInterfaceFile = icm.EHInterfaceFile
EHtemp_path = icm.EHtemp_path

asc_grid_head = icm.asc_grid_head
asc_grid_ids = icm.asc_grid_ids
grid_comp = icm.grid_comp

# Morph
shallow_subsidence_column = icm.shallow_subsidence_column
dem_res = icm.dem_res

# Barrier Island 
bimode_folders = icm.bimode_folders
bimode_dir = icm.bimode_dir
BITIconfig = icm.BITIconfig
BIMHWFile= icm.BIMHWFile 
bidem_fixed_grids= icm.bidem_fixed_grids 
IslandMHWCompLists = icm.IslandMHWCompLists

# Grid information for Veg ASCII grid files
n500grid = icm.n500grid
n500rows = icm.n500rows
n500cols = icm.n500cols
xll500 = icm.xll500
yll500 = icm.yll500

# Grid information for EwE ASCII grid files
n1000grid = icm.n1000grid
n1000rows = icm.n1000rows
n1000cols = icm.n1000cols
xll1000 = icm.xll1000
yll1000 = icm.yll1000

# Veg model input filenames 
WaveAmplitudeFile = icm.WaveAmplitudeFile
MeanSalinityFile = icm.MeanSalinityFile
SummerMeanWaterDepthFile = icm.SummerMeanWaterDepthFile
SummerMeanSalinityFile = icm.SummerMeanSalinityFile
SummerMeanTempFile = icm.SummerMeanTempFile
TreeEstCondFile = icm.TreeEstCondFile
HtAbvWaterFile = icm.HtAbvWaterFile
PerLandFile = icm.PerLandFile
PerWaterFile = icm.PerWaterFile
AcuteSalFile = icm.AcuteSalFile
VegConfigFile = icm.VegConfigFile

# Veg model params
acute_sal_threshold = icm.acute_sal_threshold

# File naming convention settings
sterm = icm.sterm
gterm = icm.gterm

# Tags
fwoa_init_cond_tag = icm.fwoa_init_cond_tag
exist_cond_tag = icm.exist_cond_tag
file_o_01_end_prefix = icm.file_o_01_end_prefix
runprefix = icm.runprefix
file_prefix_cycle = icm.file_prefix_cycle


if not HSI_Standalone:

    hydro_logfile = 'ICM_%s_Hydro.log' % time.strftime('%Y%m%d_%H%M', time.localtime())

    hf.print_credits()

    #########################################################
    ## INPUT VARIABLES TO BE READ FROM CONFIGURATION FILES ##
    #########################################################
    print('--------------------------------------------------')
    print('\n CONFIGURING ICM MODEL FILES.')
    print('--------------------------------------------------')

    (hyd_switch_years, hyd_file_orig, hyd_file_new, hyd_file_bk, links_to_change, 
     link_years, FWA_prj_input_dir_MC, FWA_prj_input_dir_RR, FWA_prj_input_dir_BS, 
     mc_elementIDs, mc_years, mc_eid_with_deep_fill, mc_depth_threshold_def, 
     mc_depth_threshold_deep, mc_links, mc_links_years, sp_projectIDs, sp_years, 
     rr_projectIDs, rr_years, comps_to_change_elev, comp_elevs, comp_years, 
     act_del_files, act_del_years
     ) = icm_setup.ICMVars()

    # check that project implementation variables are of the correct lengths
    hf.check_var_lengths(
        links_to_change, link_years, mc_elementIDs, mc_years, mc_links, 
        mc_links_years, sp_projectIDs, sp_years, rr_projectIDs, rr_years, 
        act_del_files, act_del_years)

    #########################################################
    ##            SETTING UP ICM-HYDRO MODEL               ##
    #########################################################

    print(' Configuring ICM-Hydro.')

    (pwatr_grid_file, acute_sal_grid_file, EH_grid_filepath, cellsheader, linksheader,
     EHConfigArray, EHCellsArrayOrig, EHLinksArrayOrig, EHCellsArrayOrig, EHLinksArrayOrig,
     ncomp, HydroConfigFile, SalConfigFile, TempConfigFile, FineConfigFile, SandConfigFile,
     Sub_Sal, Sub_Temp, Sub_Fine, Sub_Sand, n_xs, Hydro_dt, Sal_dt, Tmp_dt, Fine_dt,
     Sand_dt, n_lc, EHCellsArray, lq, ndays, EHLinksArray, startrun, EH_grid_file
     ) = hydro_setup.icm_hydro_setup(
         n_1D, RmConfigFile, ecohydro_dir, elapsed_hotstart, vegetation_dir, file_prefix_cycle,
         WaveAmplitudeFile, MeanSalinityFile, SummerMeanWaterDepthFile, SummerMeanSalinityFile,
         SummerMeanTempFile, TreeEstCondFile, HtAbvWaterFile, PerLandFile, PerWaterFile,
         AcuteSalFile, EHInterfaceFile, n500grid, n500rows, n500cols, xll500, yll500,
         n1000grid, n1000rows, n1000cols, xll1000, yll1000, hydro_logfile, EHConfigFile,
         EHCellsFile, EHLinksFile, startyear_cycle, startyear, inputStartYear, hotstart_year)

    #########################################################
    ##               SETTING UP ICM-LAVegMod               ##
    #########################################################

    print(' Configuring ICM-LAVegMod.')

    laveg_setup.icm_LAVegMod_setup(
        vegetation_dir, cycle_start_elapsed, cycle_end_elapsed, startyear_cycle,
        startyear, runprefix, file_prefix_cycle, PerWaterFile, WaveAmplitudeFile,
        MeanSalinityFile, SummerMeanWaterDepthFile, SummerMeanSalinityFile,
        SummerMeanTempFile, TreeEstCondFile, AcuteSalFile, HtAbvWaterFile)

    #########################################################
    ##        SETTING UP ICM-BARRIER ISLAND MODEL          ##
    #########################################################

    print(' Configuring ICM-Barrier Island Model.')

    import BarrierIsland_Setup as bi_setup


    (BITI_Terrebonne_comp, BITI_Barataria_comp, BITI_Pontchartrain_comp, BITI_Terrebonne_link,
     BITI_Terrebonne_partition, kappa, alpha, BITI_Terrebonne_BWF, BITI_Barataria_link, 
     BITI_Barataria_partition, BITI_Barataria_BWF, BITI_Pontchartrain_link, BITI_Pontchartrain_partition, 
     BITI_Pontchartrain_BWF, BITI_Terrebonne_dwr, BITI_Barataria_dwr, BITI_Pontchartrain_dwr, 
     BITI_Links, BITI_inlet_dimensions_init
     ) = bi_setup.icm_barrierisland_setup(
         ecohydro_dir, inputStartYear, endyear, bimode_folders,
         bimode_dir, BITIconfig, EHLinksArrayOrig)

    #########################################################
    ##              START YEARLY TIMESTEPPING              ##
    #########################################################
    
    for year in range(startyear + elapsed_hotstart, endyear_cycle + 1):
        print('\n--------------------------------------------------')
        print('  START OF MODEL TIMESTEPPING LOOP - YEAR %s' % year)
        print('--------------------------------------------------\n')

        # Run ICM_PreProcessing

        (elapsedyear, ndays, file_prefix, file_iprefix, 
         file_oprefix, file_prefix_prv
         ) = icm_preproc.ICMyearlyVars (
             year, startyear, runprefix)

        print('\n--------------------------------------------------')
        print('  RUNNING HYDRO MODEL - Year %s' % year)
        print('--------------------------------------------------\n' )
        print(' See %s for Hydro runtime logs.' % hydro_logfile)

        # Run Pre-Processing for Hydro

        endrun = hydro_preproc.HydroyearlyVars(
            year, ecohydro_dir, n_1D, HydroConfigFile, lq, Sub_Sal, SalConfigFile,
            Sub_Temp, TempConfigFile, Sub_Fine, FineConfigFile, Sub_Sand, SandConfigFile,
            startrun, ndays, EHConfigFile, EHConfigArray, startyear, EHtemp_path,
            EH_grid_filepath, EHCellsArray, EHCellsArrayOrig, update_hydro_attr,
            EHLinksArray, link_years, links_to_change, mc_links_years,  mc_links,
            comp_years, comps_to_change_elev, comp_elevs, EHCellsFile, cellsheader,
            EHLinksFile, linksheader)

        # Begin Hydro Run

        (stg_ts_file, sal_ts_file, tss_ts_file, sed_ow_file, sed_mi_file, sed_me_file, monthly_file_avstg, 
         monthly_file_mxstg, monthly_file_avsal, monthly_file_avtss, monthly_file_sdowt, monthly_file_sdint, 
         monthly_file_sdedg, bidem_xyz_file, new_grid_filepath, comp_elev_file, comp_wat_file, comp_upl_file, 
         grid_pct_edge_file, grid_Gdw_dep_file, grid_GwT_dep_file, grid_MtD_dep_file, dem_grid_data_outfile, 
         comp_out_file, old_grid_filepath
         ) = hydro_main.RunHydro(
             year, hydro_exe_path, endrun, EHtemp_path, EHConfigFile, EHCellsFile, EHLinksFile,
             EH_grid_file, EH_grid_filepath, ecohydro_dir, compartment_output_file, grid_output_file,
             HydroConfigFile, elapsedyear, n_1D, Sub_Sal, Sub_Temp, Sub_Fine, Sub_Sand,SalConfigFile, 
             TempConfigFile, FineConfigFile, SandConfigFile, bimode_dir, file_prefix)

        hydro_postproc.HydroPostProcess(year, startyear, stg_ts_file, monthly_file_avstg, ncomp,monthly_file_mxstg, sal_ts_file, 
                                        monthly_file_avsal, tss_ts_file, monthly_file_avtss, monthly_file_sdowt, monthly_file_sdint, 
                                        sed_ow_file, sed_mi_file, sed_me_file, asc_grid_head, old_grid_filepath, pwatr_grid_file, 
                                        asc_grid_ids, comp_out_file, monthly_file_sdedg, grid_comp, acute_sal_threshold, 
                                        acute_sal_grid_file)
        
        print('\n-------------------------------------------------------------')
        print('  RUNNING BARRIER ISLAND TIDAL INLET MODEL (ICM-BITI) - Year %s' % year)
        print('-------------------------------------------------------------\n' )


        (IslandMHWCompLists, BIMODEmhw) = bi_preproc.BIyearlyVars(
            bimode_dir, BITI_Terrebonne_comp, BITI_Barataria_comp, BITI_Pontchartrain_comp, 
            BITI_Terrebonne_link, BITI_Terrebonne_partition, kappa, alpha, BITI_Terrebonne_BWF, 
            BITI_Barataria_link, BITI_Barataria_partition, BITI_Barataria_BWF, BITI_Pontchartrain_link, 
            BITI_Pontchartrain_partition, BITI_Pontchartrain_BWF, BITI_Terrebonne_dwr, BITI_Barataria_dwr, 
            BITI_Pontchartrain_dwr, BITI_Links, BITI_inlet_dimensions_init, EHLinksArray)


        bi_main.RunBI(year, bimode_folders, bimode_dir, BIMHWFile, IslandMHWCompLists, BIMODEmhw, 
                      bidem_exe_path, elapsedyear, bidem_fixed_grids, bidem_xyz_file)

        print('\n--------------------------------------------------')
        print('  RUNNING VEGETATION MODEL - Year %s' % year)
        print('--------------------------------------------------\n')
        
        laveg_main.RunLAVegMod(year, vegetation_dir, startyear, elapsed_hotstart, 
                VegConfigFile)

        print('\n--------------------------------------------------')
        print('  RUNNING MORPH MODEL - Year %s' % year)
        print('--------------------------------------------------\n')
        
        (act_del_file_2use, n_mc_yr, mc_project_list_yr, mc_project_list_VolArea_yr, 
         rr_project_list_yr, n_sp_cumul, sp_project_list_cumul, n_rr_yr
         ) = morph_preproc.MorphyearlyVars(
             year, par_dir, mc_elementIDs, file_iprefix, file_oprefix, mc_eid_with_deep_fill, 
             mc_depth_threshold_deep, mc_depth_threshold_def, FWA_prj_input_dir_MC, sterm,
             runprefix, rr_years, rr_projectIDs, FWA_prj_input_dir_RR, sp_years, sp_projectIDs,
             FWA_prj_input_dir_BS, startyear, act_del_years, act_del_files)

        morph_main.RunMorph(wetland_morph_dir, startyear, elapsedyear, ncomp, year, fwoa_init_cond_tag, 
                            file_prefix_prv,exist_cond_tag, shallow_subsidence_column, file_oprefix, 
                            monthly_file_avstg, monthly_file_mxstg, monthly_file_sdowt, act_del_file_2use, 
                            monthly_file_sdint, monthly_file_sdedg, monthly_file_avsal, monthly_file_avtss, 
                            bidem_xyz_file, file_prefix, new_grid_filepath, grid_Gdw_dep_file, grid_GwT_dep_file, 
                            grid_MtD_dep_file, grid_pct_edge_file, comp_elev_file, comp_wat_file, comp_upl_file, 
                            dem_grid_data_outfile, file_o_01_end_prefix, n_mc_yr, mc_project_list_yr, 
                            mc_project_list_VolArea_yr, n_rr_yr, rr_project_list_yr, n_sp_cumul, 
                            sp_project_list_cumul, morph_exe_path, mc_depth_threshold_def, dem_res)

        if morph_zonal_stats == 0:
        
            print('\n--------------------------------------------------' )
            print('  RUNNING ZONAL STATS ON ICM-MORPH OUTPUT- year %s' % year)
            print('--------------------------------------------------\n')
            
            morph_postproc.MorphPostProcess(monthly_file_avstg, n500grid, dem_grid_data_outfile, ncomp, dem_res, 
                                            new_grid_filepath, grid_pct_edge_file, comp_elev_file, comp_wat_file, 
                                            comp_upl_file, grid_Gdw_dep_file, grid_GwT_dep_file, grid_MtD_dep_file)

        if run_sav == 1:

            print('\n--------------------------------------------------' )
            print('  RUNNING SAV - year %s' % year)
            print('--------------------------------------------------\n')

            sav_main.RunSAV(year, sterm, gterm, sav_submit_exe_path)

    print('\n--------------------------------------------------')
    print('  BEGIN ICM HSI RUN ')
    print('--------------------------------------------------\n')

    #Run HSI_Main
    #hsi_main.RunHSI(startyear, endyear)
          
    print('\n\n\n')
    print('-----------------------------------------' )
    print(' ICM Model run complete!')
    print('-----------------------------------------\n')

else: 

    print('\n\n\n')
    print('-----------------------------------------' )
    print('    RUNNING HSI STANDALONE   ' )
    print('-----------------------------------------\n')
    
    #Run HSI_Main
    #hsi_main.RunHSI(startyear, endyear)
    
    print('\n\n\n')
    print('-----------------------------------------' )
    print('    HSI STANDALONE RUN COMPLETE!   ' )
    print('-----------------------------------------\n')




