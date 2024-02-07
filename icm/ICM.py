#########################################################################################################
####                                                                                                 ####
####                                START GENERAL ICM.PY PROGRAM                                     ####
####                                                                                                 ####
#########################################################################################################

#ICM imports
#import HSI_Main as hsi_main
import ICM_HelperFunctions as hf
import ICM_Setup
import ICM_Settings as icm

#Python imports
import time

## NOTE: all directory paths and filenames (when appended to a directory path) are normalized
##          in this ICM routine using os.path.normpath(). This is likely a bit redundant, but it
##          was instituted so that file path directory formatting in the input parameters is forgiving.
##          If converted to Linux, this should allow for flexibility between the forward-slash vs.
##          back-slash differences between Windows and Linux.
##          This approach does not work for filepaths that are written to input text files that are passed
##          into Fortran executables. Python will convert / to \ when run on Windows...so all filepaths
##          now utilize Posix filepath convention with /. There is a function call forward2backslash that
##          can be used to convert to Windows-specific slash characters for specific files for use in Windows Fortran.

#TODO update this when ICM_Settings has been switched to globals format
#Run options flags
morph_zonal_stats = icm.morph_zonal_stats
run_sav = icm.run_sav
HSI_Standalone = icm.HSI_standalone

#TODO update this when ICM_Settings has been switched to globals format
#Run duration parameters
startyear = icm.startyear
elapsed_hotstart = icm.elapsed_hotstart
endyear_cycle = icm.endyear_cycle
endyear = icm.endyear

if not HSI_Standalone:

    #NOTE Removed logger code (2029MP_Task01)

    hydro_logfile = 'ICM_%s_Hydro.log' % time.strftime('%Y%m%d_%H%M', time.localtime())

    hf.print_credits()

    #########################################################
    ## INPUT VARIABLES TO BE READ FROM CONFIGURATION FILES ##
    #########################################################
    print('--------------------------------------------------')
    print('\n CONFIGURING ICM MODEL FILES.')
    print('--------------------------------------------------')

    #TODO check, this may also be a spot that could benefit from globals
    hyd_switch_years, hyd_file_orig, hyd_file_new, hyd_file_bk, links_to_change, link_years, \
        FWA_prj_input_dir_MC, FWA_prj_input_dir_RR, FWA_prj_input_dir_BS, mc_elementIDs, mc_years, \
        mc_eid_with_deep_fill, mc_depth_threshold_def, mc_depth_threshold_deep, mc_links, mc_links_years, \
        sp_projectIDs, sp_years, rr_projectIDs, rr_years, comps_to_change_elev, comp_elevs, comp_years, \
        act_del_files, act_del_years = ICM_Setup.ICMVars()


    #TODO need to determine whether this step is necessary, all of these lists should be empty
    # check that project implementation variables are of the correct lengths
    hf.check_var_lengths(links_to_change, link_years, mc_elementIDs, mc_years, mc_links, mc_links_years, sp_projectIDs, sp_years, rr_projectIDs, rr_years, act_del_files, act_del_years)


    #########################################################
    ##            SETTING UP ICM-HYDRO MODEL               ##
    #########################################################

    print(' Configuring ICM-Hydro.')

    #TODO import Hydro_Setup

    #########################################################
    ##               SETTING UP ICM-LAVegMod               ##
    #########################################################

    print(' Configuring ICM-LAVegMod.')

    #TODO import LAVegMod_Setup

    #########################################################
    ##        SETTING UP ICM-BARRIER ISLAND MODEL          ##
    #########################################################

    print(' Configuring ICM-Barrier Island Model.')

    #TODO import BarrierIsland_Setup

    #########################################################
    ##              START YEARLY TIMESTEPPING              ##
    #########################################################

    for year in range(startyear + elapsed_hotstart, endyear_cycle + 1):
        print('\n--------------------------------------------------')
        print('  START OF MODEL TIMESTEPPING LOOP - YEAR %s' % year)
        print('--------------------------------------------------\n')

        #TODO Run ICM_PreProcessing
        #icm_pp.ICMyearlyVars()

        print('\n--------------------------------------------------')
        print('  RUNNING HYDRO MODEL - Year %s' % year)
        print('--------------------------------------------------\n' )
        print(' See %s for Hydro runtime logs.' % hydro_logfile)
        
        #TODO Run Hydro_PreProcessing
        #hydro_pp.HydroyearlyVars

        #TODO Run Hydro_Main
        #hydro_main.RunHydro

        #TODO Run Hydro_PostProcessing
        #hydro_post.HydroPostProcess

        print('\n-------------------------------------------------------------')
        print('  RUNNING BARRIER ISLAND TIDAL INLET MODEL (ICM-BITI) - Year %s' % year)
        print('-------------------------------------------------------------\n' )

        #TODO Run BarrierIsland_PreProcessing
        #bi_pp.BIyearlyVars

        #TODO Run BarrierIsland_Main
        #bi_main.RunBI

        print('\n--------------------------------------------------')
        print('  RUNNING VEGETATION MODEL - Year %s' % year)
        print('--------------------------------------------------\n')
        
        #TODO Run LAVegmod_Main
        #laveg_main.RunLAVegMod()

        print('\n--------------------------------------------------')
        print('  RUNNING MORPH MODEL - Year %s' % year)
        print('--------------------------------------------------\n')
        
        #TODO Run Morph_PreProcessing
        #morph_pp.MorphyearlyVars()

        #TODO Run Morph_Main
        #morph_main.RunMorph()

        if morph_zonal_stats == 0:
        
            print('\n--------------------------------------------------' )
            print('  RUNNING ZONAL STATS ON ICM-MORPH OUTPUT- year %s' % year)
            print('--------------------------------------------------\n')
            
            #TODO Run Morph_PostProcessing
            #morph_post.MorphPostProcess

        if run_sav == 1:

            print('\n--------------------------------------------------' )
            print('  RUNNING SAV - year %s' % year)
            print('--------------------------------------------------\n')

            #TODO Run SAV_Main
            #sav_main.RunSAV()

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




