#ICM imports
import ICM_Settings as icm
import ICM_HelperFunctions as hf

#Python imports
import numpy as np
import os
import sys
import time

def HydroyearlyVars(year):
    #########################################################
    ##     SETTING UP 1D HYDRO MODEL FOR CURRENT YEAR      ##
    #########################################################
    os.chdir(ecohydro_dir)

    for i in range (0,n_1D):
        print(r' Preparing 1D Channel Hydro Input Files for reach %d - Year %s' % (i,year))

        print(HydroConfigFile[i])

        wr = write_1d_hyd_inp(ecohydro_dir,HydroConfigFile,i,year,lq)
#        try:
#            wr = write_1d_hyd_inp(HydroConfigFile,i,year,lq)
#        except:
#            print('  - failed to write HYDRO input file for %s.   Retrying after 5 seconds.' % HydroConfigFile[i])
#            time.sleep(5)
#            try:
#                wr = write_1d_hyd_inp(HydroConfigFile,i,year,lq)
#            except:
#                print('  - failed on second attempt to write HYDRO input file for %s.   Quitting.' % HydroConfigFile[i])
#                sys.exit()
#

        if Sub_Sal[i]=="1":
            print(SalConfigFile[i])

            try:
                wr = hf.write_1d_sal_inp(SalConfigFile,i,year,lq)
            except:
                print('  - failed to write SAL input file for %s.   Retrying after 5 seconds.' % SalConfigFile[i])
                time.sleep(5)
                try:
                    wr = hf.write_1d_sal_inp(SalConfigFile,i,year,lq)
                except:
                    print('  - failed on second attempt to write SAL input file for %s.   Quitting.' % SalConfigFile[i])
                    sys.exit()



        if Sub_Temp[i]=="1":
            print(TempConfigFile[i])

            try:
                wr = hf.write_1d_tmp_inp(TempConfigFile,i,year,lq)
            except:
                print('  - failed to write TMP input file for %s.   Retrying after 5 seconds.' % TempConfigFile[i])
                time.sleep(5)
                try:
                    wr = hf.write_1d_tmp_inp(TempConfigFile,i,year,lq)
                except:
                    print('  - failed on second attempt to write TMP input file for %s.   Quitting.' % TempConfigFile[i])
                    sys.exit()


        if Sub_Fine[i]=="1":
            print(FineConfigFile[i])

            try:
                wr = hf.write_1d_fine_inp(FineConfigFile,i,year,lq)
            except:
                print('  - failed to write FINES input file for %s.   Retrying after 5 seconds.' % FineConfigFile[i])
                time.sleep(5)
                try:
                    wr = hf.write_1d_fine_inp(FineConfigFile,i,year,lq)
                except:
                    print('  - failed on second attempt to write FINES input file for %s.   Quitting.' % FineConfigFile[i])
                    sys.exit()

        if Sub_Sand[i]=="1":
            print(SandConfigFile[i])

            try:
                wr = hf.write_1d_sand_inp(SandConfigFile,i,year,lq)
            except:
                print('  - failed to write SAND input file for %s.   Retrying after 5 seconds.' % SandConfigFile[i])
                time.sleep(5)
                try:
                    wr = hf.write_1d_sand_inp(SandConfigFile,i,year,lq)
                except:
                    print('  - failed on second attempt to write SAND input file for %s.   Quitting.' % SandConfigFile[i])
                    sys.exit()

    #########################################################
    ##               SET UP HYDRO MODEL                    ##
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
    if year != startyear:#+elapsed_hotstart:
        print(' Importing updated landscape attributes from Morphology output files - Year %s' % year)
        ## set output hotstart file generated from last model timestep to be new input hotstart file
        os.rename('hotstart_out.dat', 'hotstart_in.dat')
        ## update LW ratio in Cells.csv (compartment attributes table)
        # new pct water from WM output saved in temp folder during last model year (year-1)
        PctWaterFile = os.path.normpath(r'%s/PctWater_%s.csv' % (EHtemp_path,year-1))  # this must match filename set as 'comp_wat_file' variable written to ICM-Morph input_params.csv
        new_pctwater = np.genfromtxt(PctWaterFile,delimiter=',')
        new_pctwater_dict=dict((new_pctwater[n,0],new_pctwater[n,1]) for n in range(0,len(new_pctwater)))

        # move grid data file from location saved by previous year's Morph run to the Hydro directory (new_grid_filepath not defined until after Morph is run each year)
        # prev_new_grid_filepath will have the "endYYYY" in filename - EH_grid_filepath will not
        # this is then renamed with calendar year when moved to TempFiles after Hydro run is complete
        prev_new_grid_filepath  = os.path.normpath(r'%s/grid_data_500m_end%d.csv'  % (EHtemp_path,year-1) )  # this is the grid file generated by zonal statistics in the previous model year
        os.rename(prev_new_grid_filepath,EH_grid_filepath)

        # new pct upland from WM output saved in temp folder during last model year (year-1)
        PctUplandFile = os.path.normpath(r'%s/PctUpland_%s.csv' % (EHtemp_path,year-1))  # this must match filename set as 'comp_upl_file' variable written to ICM-Morph input_params.csv
        new_pctupland = np.genfromtxt(PctUplandFile,delimiter=',')
        new_pctupland_dict=dict((new_pctupland[n,0],new_pctupland[n,1]) for n in range(0,len(new_pctupland)))

        ## read in original bed and land elevation values for compartments as calculated from DEM- save in dictionaries where compartment ID is the key
        ## column 1 = compartment ID, column 2 = bed elev, column 3 = land elev, column 4 - marsh edge length
        # this file is used to calcualte elevation change for the year, which is then applied to the values in Cells.csv
        # this will allow for any manual manipulation of landscape elevations to the ICM-Hydro comps made during calibration to remain in place
        OrigCompElevFile = os.path.normpath(r'%s/compelevs_initial_conditions.csv' % ecohydro_dir )
        orig_compelev = np.genfromtxt(OrigCompElevFile,delimiter=',',skip_header=1)
        orig_OWelev_dict = dict((orig_compelev[n,0],orig_compelev[n,1]) for n in range(0,len(orig_compelev)))
        orig_Melev_dict = dict((orig_compelev[n,0],orig_compelev[n,2]) for n in range(0,len(orig_compelev)))

        ## read in updated bed and land elevation values for compartments - save in dictionaries where compartment ID is the key
        ## column 1 = compartment ID, column 2 = bed elev, column 3 = land elev, column 4 - marsh edge length
        # The marsh elevation value is filtered in WM.CalculateEcohydroAttributes() such that the average marsh elevation can be no lower than the average bed elevation
        CompElevFile = os.path.normpath(r'%s/compelevs_end_%s.csv' % (EHtemp_path,year-1))  # this must match filename set as 'comp_elev_file' variable written to ICM-Morph input_params.csv
        new_compelev = np.genfromtxt(CompElevFile,delimiter=',',skip_header=1)

        new_OWelev_dict = dict((new_compelev[n,0],new_compelev[n,1]) for n in range(0,len(new_compelev)))
        new_Melev_dict = dict((new_compelev[n,0],new_compelev[n,2]) for n in range(0,len(new_compelev)))
        new_Medge_dict = dict((new_compelev[n,0],new_compelev[n,3]) for n in range(0,len(new_compelev)))

        ## create blank dictionaries that will save changes in compartment attributes and initialize flags for counting updated compartments
        bedchange_dict={}
        marshchange_dict={}
        new_bed_dict={}
        new_marsh_dict={}

        orig_marsh_area_dict = {}
        new_marsh_area_dict = {}

        flag_cell_wat = 0
        flag_cell_upl = 0
        flag_bed_ch = 0
        flag_mar_ch = 0
        flag_edge_ch = 0

        ## update Hydro compartment water/upland/marsh area attributes
        print(' Updating land/water ratios and bed/marsh elevation attributes for Hydro compartments - Year %s' % year)
        
        # open list of compartments that should not have land attributes updated (e.g. open water Gulf, 1D channels, and upland non-tidal areas)
        LWupdate = {}
        staticLW_file = os.path.normpath('%s/comp_LW_update.csv' % ecohydro_dir)
        with open(staticLW_file,mode='r') as staticLW:
            nl = 0
            for line in staticLW:
                if nl >= 1:
                    cID =float(line.split(',')[0])
                    LWup = int(line.split(',')[2])
                    LWupdate[cID] = LWup
                nl +=1 
        
        for nn in range(0,len(EHCellsArray)):
            cellID = EHCellsArray[nn,0]
            cellarea = EHCellsArray[nn,1]
            orig_marsh_area_dict[cellID] = EHCellsArray[nn,4]*cellarea   # store original marsh area for link adjustment calculations later
            
            # check that Hydro Compartment should have landscape areas updated 
            if LWupdate[cellID] == 1:
                # update land percentages only if new value for percent water was calculated in Morph (e.g. dicitionary has a key of cellID and value that is not -9999), otherwise keep last year value
                try:
                    if new_pctwater_dict[cellID] != -9999:
                        orig_water = EHCellsArrayOrig[nn,2]
                        orig_upland = EHCellsArrayOrig[nn,3]
                        orig_wetland = EHCellsArrayOrig[nn,4]

                        # set minimum percentage of water allowed in Hydro compartment - if comp started with small water, it won't be allowed to get any smaller
                        # if it started with more than 10% water, it won't be allowed to get any smaller than 10% water
                        # this filter is only applied to Cells.csv for stability purposes - the Morph landscape will still be updated
                        
                        min_water = min(orig_water,0.1)
                        
                        new_water = max(min_water, new_pctwater_dict[cellID])
                        new_upland = orig_upland                                                    # don't allow any changes to upland percentage
                        new_marsh = max(0.0, min(1.0, (1.0 - new_water - new_upland) ) )
                        
                        EHCellsArray[nn,2] = new_water
                        EHCellsArray[nn,3] = new_upland
                        EHCellsArray[nn,4] = new_marsh
                    else:
                        flag_cell_wat =+ 1
                except:
                    flag_cell_wat += 1
            
                new_marsh_area_dict[cellID] = EHCellsArray[nn,4]*cellarea  # store updated marsh area for link adjustment calculations later

                # update marsh edge area, in attributes array
                try:
                    if new_Medge_dict[cellID] != -9999:
                        EHCellsArray[nn,5] = new_Medge_dict[cellID]
                except:
                        flag_edge_ch += 1
            
            # if not being updated (LWupdate <> 1) , keep original values
            else:
                new_marsh_area_dict[cellID] = orig_marsh_area_dict[cellID]


        # update Hydro compartment/link elevation attributes (if turned on as model option)
        if update_hydro_attr == 0:
            print(' Hydro link and compartment attributes are not being updated (update_hydro_attr = 0)')

        else:
            # calculate change in bed elevation if new value was calculated in Morph (e.g. dictionary has a key of cellID and value that is not -9999)
            # set change value to zero if value is NoData or if key does not exist
            try:
                if new_OWelev_dict[cellID] != -9999:
                    bedchange_dict[cellID] = new_OWelev_dict[cellID] - orig_OWelev_dict[cellID] # EHCellsArray[nn,7]
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
                    marshchange_dict[cellID] = new_Melev_dict[cellID] - orig_Melev_dict[cellID] # EHCellsArray[nn,25]
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
            print(' Updating elevation attributes for Hydro links - Year %s' % year)
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


        ## end update of Hydro compartment attributes
        print(' %s Hydro compartments have updated percent land values for model year %s.' % ((len(EHCellsArray)-flag_cell_upl),year) )
        print(' %s Hydro compartments have updated percent water values for model year %s.' % ((len(EHCellsArray)-flag_cell_wat),year) )
        print(' %s Hydro compartments have updated average bed elevations for model year %s.' % ((len(EHCellsArray)-flag_bed_ch),year) )
        print(' %s Hydro compartments have updated average marsh elevations for model year %s.' % ((len(EHCellsArray)-flag_mar_ch),year) )
        print(' %s Hydro compartments have updated marsh edge lengths for model year %s.' % ((len(EHCellsArray)-flag_edge_ch),year) )

        # update links for project implmentation
        # if project links are to be changed during model year update those links by looping through link attributes array
        if year in link_years:
            print('  Some links are set to be activated or deactivated for this model year due to project implementation.')
            for mm in range(0,len(EHLinksArray)):
                linkID = EHLinksArray[mm,0]
                if linkID in links_to_change:
                    yearindex = links_to_change.index(linkID)
                    if year == link_years[yearindex]:
                        print(' Link type for link %s is being activated (or deactivated if already active).' % linkID)
                        oldlinktype = EHLinksArray[mm,7]
                        newlinktype = -1*oldlinktype
                        EHLinksArray[mm,7] = newlinktype

        ## update link width for 'composite' marsh links if marsh creation project was implemented in previous year
        # link length is attribute 3 (column 11 in links array)
        # link width is attribute 4 (column 12 in links array)
        if year in mc_links_years:
            print('  Some composite marsh flow links are being updated due to marsh creation projects implemented during last year.')
            for mm in range(0,len(EHLinksArray)):
                linkID   = int(EHLinksArray[mm,0])
                linktype = int(EHLinksArray[mm,7])
                us_comp  = int(EHLinksArray[mm,1])
                ds_comp  = int(EHLinksArray[mm,2])
                if linktype == 11:
                    if linkID in mc_links:
                        linkindex = mc_links.index(linkID)
                        if year == mc_links_years[linkindex]:
                            print(' Updating composite marsh flow link (link %s) for marsh creation project implemented in previous year.' % linkID)
                            darea_us = new_marsh_area_dict[us_comp] - orig_marsh_area_dict[us_comp]
                            darea_ds = new_marsh_area_dict[ds_comp] - orig_marsh_area_dict[ds_comp]
                            origwidth = EHLinksArray[mm,11]
                            length = EHLinksArray[mm,10]
                            # change in link area is equal to the increase in marsh area between the two compartments
                            newwidth = origwidth - (darea_us + darea_ds)/length

                            # set min/max width thresholds on marsh creation link updates
                            # minimum width is currently hard-set to be no smaller than 30-m wide
                            # maximum width is currently set to the square root of the smaller of the two compartments connected by the link
                            # this assumes that the compartment is completely square and the width is not allowed to be wider than one of the four sides of the assumed-square compartment
                            min_allowable_width = 30
                            max_allowable_width = min( EHCellsArray[us_comp,1], EHCellsArray[ds_comp,1] )**0.5
                            EHLinksArray[mm,11] = min(max_allowable_width,max(newwidth,min_allowable_width)) # do not let marsh link go to zero - allow some flow, minimum width is one pixel wide
        
        ## update compartment bed elevation for projects that have dredging and update open water elevation
        # bed elevation is column 8 in cells array
        if year in comp_years:
            print('  Some Hydro comparments have a bed elevation being updated due to dredging projects implemented during year.')
            for nn in range(0,len(EHCellsArray)):
                cellID = EHCellsArray[nn,0]
                if cellID in comps_to_change_elev:
                    cellindex = comps_to_change_elev.index(cellID)
                    if year == comp_years[cellindex]:
                        new_bed_elev = comp_elevs[cellindex]
                        EHCellsArray[nn,7] = new_bed_elev   # update bed elevation of open water area in attributes array
                            
                            
        ## save updated Cell and Link attributes to text files read into Hydro model
        np.savetxt(EHCellsFile,EHCellsArray,fmt='%.12f',header=cellsheader,delimiter=',',comments='')
        np.savetxt(EHLinksFile,EHLinksArray,fmt='%.12f',header=linksheader,delimiter=',',comments='')
