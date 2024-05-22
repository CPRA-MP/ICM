#Python imports
import datetime as dt

#ICM imports
import ICM_Settings as icm
import ICM_HelperFunctions as hf


def HydroPostProcess(year, startyear, stg_ts_file, monthly_file_avstg, ncomp,monthly_file_mxstg, sal_ts_file, 
                     monthly_file_avsal, tss_ts_file, monthly_file_avtss, monthly_file_sdowt, monthly_file_sdint, 
                     sed_ow_file, sed_mi_file, sed_me_file, asc_grid_head, old_grid_filepath, pwatr_grid_file, 
                     asc_grid_ids, comp_out_file, monthly_file_sdedg, grid_comp_dict, acute_sal_threshold, 
                     acute_sal_grid_file
                     ):
    
    ########################################################
    ##  Format ICM-Hydro output data for use in ICM-Morph ##
    ########################################################
    
    dom = hf.create_domdict(year)
    
    # Read in monthly water level data
    print(' - calculating mean and max monthly water levels')
    stg_mon = {}
    stg_mon_mx = {}
    for mon in range(1,13):
        print('     - month: %02d' % mon)
        
        # Start date of all data included in the daily timeseries file (YYYY,M,D)
        data_start = dt.date(startyear,1,1)
        # Start date of averaging window, inclusive (YYYY,M,D)             
        ave_start = dt.date(year,mon,1)
        # End date of averaging window, inclusive (YYYY,M,D)                 
        ave_end = dt.date(year,mon,dom[mon])            
        
        stg_mon[mon] = hf.daily2ave(data_start,ave_start,ave_end,stg_ts_file)
        stg_mon_mx[mon] = hf.daily2max(data_start,ave_start,ave_end,stg_ts_file)

    # Write monthly mean water level file for use in ICM-Morph
    with open(monthly_file_avstg,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,stage_m_%02d' % (wrt_hdr,mon)
        
        mon_file.write('%s\n' % wrt_hdr)
        
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                wrt_string = '%s,%s' % (wrt_string,stg_mon[mon][comp])
            
            mon_file.write('%s\n'% wrt_string)

    # Write monthly max water level file for use in ICM-Morph
    with open(monthly_file_mxstg,mode='w') as mon_file:
        wrt_hdr = 'comp'
        
        for mon in range(1,13):
            wrt_hdr = '%s,stage_mx_m_%02d' % (wrt_hdr,mon)
        
        mon_file.write('%s\n' % wrt_hdr)
        
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                wrt_string = '%s,%s' % (wrt_string,stg_mon_mx[mon][comp])
            
            mon_file.write('%s\n'% wrt_string)

    # Read in monthly salinity data
    print(' - calculating mean monthly salinity')
    sal_mon = {}
    for mon in range(1,13):
        print('     - month: %02d' % mon)

        # Start date of all data included in the daily timeseries file (YYYY,M,D)
        data_start = dt.date(startyear,1,1)
        # Start date of averaging window, inclusive (YYYY,M,D)             
        ave_start = dt.date(year,mon,1)
        # End date of averaging window, inclusive (YYYY,M,D)                 
        ave_end = dt.date(year,mon,dom[mon])

        sal_mon[mon] = hf.daily2ave(data_start,ave_start,ave_end,sal_ts_file)

    # Write monthly mean salinity file for use in ICM-Morph
    with open(monthly_file_avsal,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,sal_ave_ppt_%02d' % (wrt_hdr,mon)
        
        mon_file.write('%s\n' % wrt_hdr)
        
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                wrt_string = '%s,%s' % (wrt_string,sal_mon[mon][comp])
            
            mon_file.write('%s\n'% wrt_string)

   # Read in monthly TSS data
    print(' - calculating mean monthly TSS')
    tss_mon = {}
    for mon in range(1,13):
        print('     - month: %02d' % mon)
        
        # Start date of all data included in the daily timeseries file (YYYY,M,D)
        data_start = dt.date(startyear,1,1)
        # Start date of averaging window, inclusive (YYYY,M,D)             
        ave_start = dt.date(year,mon,1)
        # End date of averaging window, inclusive (YYYY,M,D)                 
        ave_end = dt.date(year,mon,dom[mon])            
        
        tss_mon[mon] = hf.daily2ave(data_start,ave_start,ave_end,tss_ts_file)

    # Write monthly mean TSS file for use in ICM-Morph
    with open(monthly_file_avtss,mode='w') as mon_file:
        wrt_hdr = 'comp'
        
        for mon in range(1,13):
            wrt_hdr = '%s,tss_ave_mgL_%02d' % (wrt_hdr,mon)
        
        mon_file.write('%s\n' % wrt_hdr)
        
        for comp in range(1,ncomp+1):
            wrt_string = comp
            for mon in range(1,13):
                wrt_string = '%s,%s' % (wrt_string,tss_mon[mon][comp])
            
            mon_file.write('%s\n'% wrt_string)

    # Read in cumulative sediment deposition data
    print(' - formatting sedimentation output for ICM-Morph')
    sed_ow = {}
    sed_mi = {}
    sed_me = {}
    for mon in range(1,13):
        print('     - month: %02d' % mon)
        
        # Start date of all data included in the daily timeseries file (YYYY,M,D)
        data_start = dt.date(startyear,1,1)
        # End date of averaging window, inclusive (YYYY,M,D)              
        day2get = dt.date(year,mon,dom[mon])            
        
        sed_ow[mon] = hf.daily2day(data_start,day2get,sed_ow_file)
        sed_mi[mon] = hf.daily2day(data_start,day2get,sed_mi_file)
        sed_me[mon] = hf.daily2day(data_start,day2get,sed_me_file)

    # Write monthly sediment deposition in open water file for use in ICM-Morph
    with open(monthly_file_sdowt,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,sed_dp_ow_%02d' % (wrt_hdr,mon)
        
        mon_file.write('%s\n' % wrt_hdr)
        
        for comp in range(1,ncomp+1):
            wrt_string = comp
            
            for mon in range(1,13):
                if mon == 1:
                    val2write = float(sed_ow[mon][comp])
                else:
                    # Convert cumulative sediment deposited during year to amount deposited only during the current month
                    val2write = float(sed_ow[mon][comp]) - float(sed_ow[mon-1][comp])
                
                wrt_string = '%s,%s' % (wrt_string,val2write)
            mon_file.write('%s\n'% wrt_string)

    # Write monthly sediment deposition in marsh interior file for use in ICM-Morph
    with open(monthly_file_sdint,mode='w') as mon_file:
        wrt_hdr = 'comp'
        
        for mon in range(1,13):
            wrt_hdr = '%s,sed_dp_int_%02d' % (wrt_hdr,mon)
        
        mon_file.write('%s\n' % wrt_hdr)
        
        for comp in range(1,ncomp+1):
            wrt_string = comp
            
            for mon in range(1,13):
                if mon == 1:
                    # Marsh deposition can only be positive 
                    #   No erosion - force to zero in case of small negative values due to sigfig
                    val2write = max(0,float(sed_mi[mon][comp]))                                  
                else:
                    # convert cumulative sediment deposited during year to amount deposited only during the current month
                    val2write = max(0,float(sed_mi[mon][comp]) - float(sed_mi[mon-1][comp]))     
                
                wrt_string = '%s,%s' % (wrt_string,val2write)
            mon_file.write('%s\n'% wrt_string)

    # Write monthly sediment deposition in marsh edge zone file for use in ICM-Morph
    with open(monthly_file_sdedg,mode='w') as mon_file:
        wrt_hdr = 'comp'
        for mon in range(1,13):
            wrt_hdr = '%s,sed_dp_edge_%02d' % (wrt_hdr,mon)
        
        mon_file.write('%s\n' % wrt_hdr)
        
        for comp in range(1,ncomp+1):
            wrt_string = comp
            
            for mon in range(1,13):
                if mon == 1:
                    # Marsh deposition can only be positive 
                    #   No erosion - force to zero in case of small negative values due to sigfig
                    val2write = max(0,float(sed_me[mon][comp]))                                  
                else:
                    # Convert cumulative sediment deposited during year to amount deposited only during the current month
                    val2write = max(0,float(sed_me[mon][comp]) - float(sed_me[mon-1][comp]))     

                wrt_string = '%s,%s' % (wrt_string,val2write)
            mon_file.write('%s\n'% wrt_string)


    ###########################################################
    ##  Format ICM-Hydro output data for use in ICM-LAVegMod ##
    ###########################################################

    asc_head = '# Year = %04d\n%s' % (year,asc_grid_head)
    if year == startyear:
        filemode = 'w'
    else:
        filemode = 'a'

    print('   - updating percent water grid file for ICM-LAVegMod')
    pwatr_dict = {}
    with open(old_grid_filepath,mode='r') as grid_data:
        nline = 0
        
        for line in grid_data:
            if nline > 0:
                gr = int(float(line.split(',')[0]))
                # In grid_data: 
                #  5th column is percent_wetland and is defined in morph as: vegetated land + flotant marsh + unvegetated bare ground 
                #  ** it does not include NotMod/Developed or water **
                #  6th column is percent water
                pwatr = line.split(',')[5]          
                pwatr_dict[gr] = pwatr
            nline += 1
    
    print(hf.dict2asc_flt(pwatr_dict,pwatr_grid_file,asc_grid_ids,asc_head,write_mode=filemode) )

    print('   - updating acute salinity stress grid file for ICM-LAVegMod')
    salmx_comp = hf.compout2dict(comp_out_file,7)
    salmx_grid = hf.comp2grid(salmx_comp,grid_comp_dict)
    
    acute_sal_grid = {}
    for gid in salmx_grid.keys():
        val = salmx_grid[gid]
        if val < 0:
            val2write = -9999
        elif val < acute_sal_threshold:
            val2write = 0
        else:
            val2write = 1
        acute_sal_grid[gid] = val2write        
    
    print(hf.dict2asc_int(acute_sal_grid,acute_sal_grid_file,asc_grid_ids,asc_head,write_mode=filemode) )
