#ICM imports
import ICM_Settings as icm

#Python imports
import os
import subprocess

def MorphyearlyVars(year, par_dir, mc_elementIDs, file_iprefix, file_oprefix, mc_eid_with_deep_fill, 
                    mc_depth_threshold_deep, mc_depth_threshold_def, FWA_prj_input_dir_MC, sterm,
                    runprefix, rr_years, rr_projectIDs, FWA_prj_input_dir_RR, sp_years, sp_projectIDs,
                    FWA_prj_input_dir_BS, startyear, act_del_years, act_del_files
                    
                    ):
    #########################################################
    ##         SETUP MORPH MODEL FOR CURRENT YEAR          ##
    #########################################################
    
    os.chdir(par_dir)

    #########################################################################
    ##    IMPLEMENT MARSH CREATION PROJECTS BY ELEMENT FOR CURRENT YEAR    ##
    #########################################################################
    
    # count number of marsh creation project elements to be built during current year
    n_mc_yr = 0
    mc_eid_yr = []
    mc_project_list_yr = 'na'
    mc_project_list_VolArea_yr = 'na'
    
    mcyi = 0
    for mc_yr in c:
        if year == mc_yr:
            n_mc_yr += 1
            mc_eid_yr.append( mc_elementIDs[mcyi] )
        mcyi += 1

    # unzip each TIF file and convert to XYZ format for each element of marsh creation projects implemented during current year
    if n_mc_yr > 0:
        mc_project_list_yr = 'geomorph/input/%s_MCelements.csv' % file_iprefix
        mc_project_list_VolArea_yr = 'geomorph/output/%s_MC_VolArea.csv' % file_oprefix
        
        with open (mc_project_list_yr,mode='w') as mcpl:
            mcpl.write('ElementID,xyz_file\n')
            
            for eid in mc_eid_yr:
                
                if eid in mc_eid_with_deep_fill:
                    fill_depth =  mc_depth_threshold_deep
                else:
                    fill_depth =  mc_depth_threshold_def
                
                zfile = '%s/%s/MCElementElevation_%s_%s.zip' % (FWA_prj_input_dir_MC,sterm,sterm,eid)
                print ('unzipping %s' % zfile)
                zcmd = ['unzip','-j',zfile]
                zrun = subprocess.check_output(zcmd).decode()
                
                TIFpath = zrun.split('inflating:')[1].strip()
                TIFfile = TIFpath.split('/')[-1]
                
                XYZfile = '%s_00_00_MC_%d.xyz' % (runprefix,eid)
                XYZpath = 'geomorph/input/%s' % XYZfile

                gtcmd = ['gdal_translate',TIFpath,XYZpath]
                gtrun = subprocess.call(gtcmd)
                
                rmcmd = ['rm', TIFpath]
                rmcmd = subprocess.call(rmcmd)
               
                # add element ID and location of XYZ project file to text file passed into Morph
                mcpl.write('%d,%s,%f\n' % (eid,XYZfile,fill_depth) )

    
    ###########################################################
    ##    IMPLEMENT RIDGE/LEVEE PROJECTS FOR CURRENT YEAR    ##
    ###########################################################    
    
    # count number of ridge/levee projects to be built during current year  
    n_rr_yr = 0
    rr_eid_yr = []
    rr_project_list_yr = 'na'
  
    rryi = 0
    for rr_yr in rr_years:
        if year == rr_yr:
            n_rr_yr += 1
            rr_eid_yr.append( rr_projectIDs[rryi] )
        rryi += 1

    # unzip each TIF file and convert to XYZ format for ridge/levee projects implemented during current year
    if n_rr_yr > 0:
        rr_project_list_yr = 'geomorph/input/%s_ridge_levee_projects.csv' % file_iprefix
        
        with open (rr_project_list_yr,mode='w') as rrpl:
            rrpl.write('ProjectID,xyz_file\n')
            
            for eid in rr_eid_yr:
                zfile = '%s/RR_PL_PW_ProjectElevation_%s.zip' % (FWA_prj_input_dir_RR,eid)
                print ('unzipping %s' % zfile)
                zcmd = ['unzip','-j',zfile]
                zrun = subprocess.check_output(zcmd).decode()
                
                TIFpath = zrun.split('inflating:')[1].strip()
                TIFfile = TIFpath.split('/')[-1]
                
                XYZfile = '%s_00_00_RRPL_%d.xyz' % (runprefix,eid)
                XYZpath = 'geomorph/input/%s' % XYZfile

                gtcmd = ['gdal_translate',TIFpath,XYZpath]
                gtrun = subprocess.call(gtcmd)
                
                rmcmd = ['rm', TIFpath]
                rmcmd = subprocess.call(rmcmd)
                
                # add project ID and location of XYZ project file to text file passed into Morph
                rrpl.write('%d,%s\n' % (eid,XYZfile) )
    
    ###################################################################################
    ##    IMPLEMENT SHORELINE PROTECTION PROJECTS FOR CURRENT AND PREVIOUS YEARS     ##
    ################################################################################### 
    
    # count number of shoreline protection projects built during, or prior to, current year
    n_sp_cumul = 0
    sp_eid_cumul = []
    sp_project_list_cumul = 'geomorph/input/%s_shoreline_protection_projects.csv' % file_iprefix
    
    spci = 0
    for sp_yr in sp_years:
        if year >= sp_yr:
            n_sp_cumul += 1
            sp_eid_cumul.append( sp_projectIDs[spci] )
        spci += 1
    
    # add project ID and location of XYZ project files to text file passed into Morph for all shoreline protection projects for current and previous years
    with open (sp_project_list_cumul,mode='w') as sppl:
        sppl.write('ProjectID,xyz_file\n')
        if n_sp_cumul > 0:
            for eid in sp_eid_cumul:
                XYZfile = '%s_00_00_MEEmult_%d.xyz' % (runprefix,eid)
                sppl.write('%d,%s\n' % (eid,XYZfile) )
        else:
            sppl.write('No updates to default marsh edge erosion rates\n')

   
    # count number of shoreline protection projects built during current year only
    n_sp_yr = 0
    spyi = 0
    sp_eid_yr = []
    for sp_yr in sp_years:
        if year == sp_yr:
            n_sp_yr += 1
            sp_eid_yr.append( sp_projectIDs[spyi] )
        spyi += 1

    for eid in sp_eid_yr:
        zfile = '%s/BS_SP_MEEmultiplier_%s.zip' % (FWA_prj_input_dir_BS,eid)
        print ('unzipping %s' % zfile)
        zcmd = ['unzip','-j',zfile]
        zrun = subprocess.check_output(zcmd).decode()
        
        TIFpath = zrun.split('inflating:')[1].strip()
        TIFfile = TIFpath.split('/')[-1]
        
        XYZfile = '%s_00_00_MEEmult_%d.xyz' % (runprefix,eid)
        XYZpath = 'geomorph/input/%s' % XYZfile
        
        gtcmd = ['gdal_translate',TIFpath,XYZpath]
        gtrun = subprocess.call(gtcmd)
        
        rmcmd = ['rm', TIFpath]
        rmcmd = subprocess.call(rmcmd)


    
    ############################################################################
    ##    IMPLEMENT ACTIVE DELTAIC COMPARTMENT FILES FOR DIVERSION PROJECT    ##
    ############################################################################
    
    # set default active deltaic compartment file
    act_del_file_2use = 'compartment_active_delta.csv'
    
    # loop through all past and present model years - look to see if any previous (or current) year had an updated active delta file
    # if so, the year closest (but prior) to the current model year's active deltaic file will be used
    for ady in range(startyear,year+1):
        if ady in act_del_years:
            act_del_file_2use = act_del_files[act_del_years.index(ady)]


    return(act_del_file_2use, n_mc_yr, mc_project_list_yr, mc_project_list_VolArea_yr, 
           rr_project_list_yr, n_sp_cumul, sp_project_list_cumul, n_rr_yr)
   
      