#Python imports
import os

#ICM imports




def MorphPostProcess(monthly_file_avstg, n500grid, dem_grid_data_outfile, ncomp, dem_res, new_grid_filepath, grid_pct_edge_file, 
                     comp_elev_file, comp_wat_file, comp_upl_file, grid_Gdw_dep_file, grid_GwT_dep_file, grid_MtD_dep_file):
    
    ##############################################################
    ##          RUN ZONAL STATISTICS ON MORPH OUTPUTS           ##
    ##############################################################
    
    # Water depth bins HSI
    Gdw_bin_n = 14 # Gadwall
    GwT_bin_n = 9 # Greenwing Teal
    MtD_bin_n = 9 # Mottled Duck
    
    print(' Reading in monthly stage data.')
    comp_mon_stg = {}   
    with open(monthly_file_avstg,mode='r') as comp_stg_data:
        nline = 0
        for line in comp_stg_data:  # comp,stage_m_01,stage_m_02,stage_m_03,stage_m_04,stage_m_05,stage_m_06,stage_m_07,stage_m_08,stage_m_09,stage_m_10,stage_m_11,stage_m_12
            if nline > 0:
                c = int(line.split(',')[0])
                comp_mon_stg[c] = {}
                for n_mon in range(1,13):
                    comp_mon_stg[c][n_mon] = float(line.split(',')[n_mon])
            nline += 1

    # Set up empty dictionaries and arrays that will hold zonal statistic values
    grid_bed_z_all = {}
    grid_bed_z = {} 
    
    grid_land_z_all = {}
    grid_land_z = {}
        
    grid_pct_land_all = {}
    grid_pct_land = {}
    
    grid_pct_land_wetl_all = {} 
    grid_pct_land_wetl = {} 
    
    grid_pct_water_all = {} 
    grid_pct_water = {} 
    
    grid_pct_edge_all = {}
    grid_pct_edge = {}
    
    grid_Gdw_depths = {}
    grid_GwT_depths = {}
    grid_MtD_depths = {}
    
    comp_water_z_all = {}
    comp_water_z = {}
    
    comp_wetland_z_all = {}
    comp_wetland_z = {}
    
    comp_edge_area_all = {}
    comp_edge_area = {}
    
    comp_pct_water_all = {}
    comp_pct_water = {}
    
    comp_pct_upland_all = {}
    comp_pct_upland = {}
    
    for g in range(1,n500grid+1):
        grid_bed_z_all[g] = []         
        grid_bed_z[g] = 0.0         
        
        grid_land_z_all[g] = []      
        grid_land_z[g] = 0.0
    
        grid_pct_land_all[g] = []    
        grid_pct_land[g] = 0.0
        
        grid_pct_land_wetl_all[g] = [] 
        grid_pct_land_wetl[g] = 0.0
        
        grid_pct_water_all[g] = []
        grid_pct_water[g] = 0.0     
        
        grid_pct_edge_all[g] = []      
        grid_pct_edge[g] = 0.0
    
        grid_Gdw_depths[g] = {}
        for Gdw_bin in range(1,Gdw_bin_n + 1):
            grid_Gdw_depths[g][Gdw_bin] = 0.0
            
        grid_GwT_depths[g] = {}
        for GwT_bin in range(1,GwT_bin_n + 1):
            grid_GwT_depths[g][GwT_bin] = 0.0
            
        grid_MtD_depths[g] = {}   
        for MtD_bin in range(1,MtD_bin_n + 1):
            grid_MtD_depths[g][MtD_bin] = 0.0
        
    for c in range(1,ncomp+1):                           
        comp_water_z_all[c] = []       
        comp_water_z[c] = 0.0
                
        comp_wetland_z_all[c] = [] 
        comp_wetland_z[c] = 0.0    
        
        comp_edge_area_all[c] = []    
        comp_edge_area[c] = 0.0    
        
        comp_pct_water_all[c] = []    
        comp_pct_water[c] = 0.0    
        
        comp_pct_upland_all[c] = []   
        comp_pct_upland[c] = 0.0   
    
    print(' Reading in ICM-Morph output data at DEM resolution from %s' % dem_grid_data_outfile)
    with open(dem_grid_data_outfile,mode='r') as grid_data:
        nline = 0
        for line in grid_data:
            if nline > 0:   # header: ndem,ICM_LAVegMod_GridCell,ICM_Hydro_Compartment,landtype,edge,z_NAVD88_m
                g      = int(float(line.split(',')[1]))
                c      = int(float(line.split(',')[2]))
                lndtyp = int(float(line.split(',')[3]))
                edge   = int(float(line.split(',')[4]))
                elev   = float(line.split(',')[5])
                
                if c > 0:
                    comp_edge_area_all[c].append(edge*dem_res*dem_res)
                    if lndtyp == 2:
                        comp_water_z_all[c].append(elev)
                        comp_pct_water_all[c].append(1)
                    else:
                        if lndtyp != 4:     # check if upland/developed
                            comp_wetland_z_all[c].append(elev)
                        else:
                            comp_pct_upland_all[c].append(1)
                
                if g > 0:
                    grid_pct_edge_all[g].append(edge)
                    if lndtyp == 2:
                        grid_bed_z_all[g].append(elev)
                        grid_pct_water_all[g].append(1)
                    else:
                        grid_land_z_all[g].append(elev)
                        grid_pct_land_all[g].append(1)
                        if lndtyp != 4:     # check if upland/developed
                            grid_pct_land_wetl_all[g].append(1)
                    
                    
                    if c > 0:
                        if elev > -9999:
                            dep_oct_apr = (comp_mon_stg[c][1]+comp_mon_stg[c][2]+comp_mon_stg[c][3]+comp_mon_stg[c][4]+comp_mon_stg[c][10]+comp_mon_stg[c][11]+comp_mon_stg[c][12])/7.0 - elev
                            dep_sep_mar = (comp_mon_stg[c][1]+comp_mon_stg[c][2]+comp_mon_stg[c][3]+comp_mon_stg[c][9]+comp_mon_stg[c][10]+comp_mon_stg[c][11]+comp_mon_stg[c][12])/7.0 - elev 
                            dep_ann     = (comp_mon_stg[c][1]+comp_mon_stg[c][2]+comp_mon_stg[c][3]+comp_mon_stg[c][4]+comp_mon_stg[c][5]+comp_mon_stg[c][6]+comp_mon_stg[c][7]+comp_mon_stg[c][8]+comp_mon_stg[c][9]+comp_mon_stg[c][10]+comp_mon_stg[c][11]+comp_mon_stg[c][12])/12.0 - elev
                            
                            # tabulate area of grid cell within each Gadwall depth bin; depth thresholds (in m) are: [0,0.04,0.08,0.12,0.18,0.22,0.28,0.32,0.36,0.40,0.44,0.78,1.50]     
                            if dep_oct_apr <= 0.0:
                                grid_Gdw_depths[g][1]  = grid_Gdw_depths[g][1] + dem_res**2
                            elif dep_oct_apr <= 0.04:
                                grid_Gdw_depths[g][2]  = grid_Gdw_depths[g][2] + dem_res**2
                            elif dep_oct_apr <= 0.08:
                                grid_Gdw_depths[g][3]  = grid_Gdw_depths[g][3] + dem_res**2
                            elif dep_oct_apr <= 0.12:
                                grid_Gdw_depths[g][4]  = grid_Gdw_depths[g][4] + dem_res**2
                            elif dep_oct_apr <= 0.18:
                                grid_Gdw_depths[g][5]  = grid_Gdw_depths[g][5] + dem_res**2
                            elif dep_oct_apr <= 0.22:
                                grid_Gdw_depths[g][6]  = grid_Gdw_depths[g][6] + dem_res**2
                            elif dep_oct_apr <= 0.28:
                                grid_Gdw_depths[g][7]  = grid_Gdw_depths[g][7] + dem_res**2
                            elif dep_oct_apr <= 0.32:
                                grid_Gdw_depths[g][8]  = grid_Gdw_depths[g][8] + dem_res**2
                            elif dep_oct_apr <= 0.36:
                                grid_Gdw_depths[g][9]  = grid_Gdw_depths[g][9] + dem_res**2
                            elif dep_oct_apr <= 0.40:
                                grid_Gdw_depths[g][10] = grid_Gdw_depths[g][10] + dem_res**2
                            elif dep_oct_apr <= 0.44:
                                grid_Gdw_depths[g][11] = grid_Gdw_depths[g][11] + dem_res**2
                            elif dep_oct_apr <= 0.78:
                                grid_Gdw_depths[g][12] = grid_Gdw_depths[g][12] + dem_res**2
                            elif dep_oct_apr <= 1.50:
                                grid_Gdw_depths[g][13] = grid_Gdw_depths[g][13] + dem_res**2
                            else:
                                grid_Gdw_depths[g][14] = grid_Gdw_depths[g][14] + dem_res**2
                            
                            # tabulate area of grid cell within each Greenwing Teal depth bin; depth thresholds (in m) are: [0,0.06,0.18,0.22,0.26,0.30,0.34,1.0]
                            if dep_sep_mar <= 0.0:
                                grid_GwT_depths[g][1] = grid_GwT_depths[g][1] + dem_res**2
                            elif dep_sep_mar <= 0.06:
                                grid_GwT_depths[g][2] = grid_GwT_depths[g][2] + dem_res**2
                            elif dep_sep_mar <= 0.18:
                                grid_GwT_depths[g][3] = grid_GwT_depths[g][3] + dem_res**2
                            elif dep_sep_mar <= 0.22:
                                grid_GwT_depths[g][4] = grid_GwT_depths[g][4] + dem_res**2
                            elif dep_sep_mar <= 0.26:
                                grid_GwT_depths[g][5] = grid_GwT_depths[g][5] + dem_res**2
                            elif dep_sep_mar <= 0.30:
                                grid_GwT_depths[g][6] = grid_GwT_depths[g][6] + dem_res**2
                            elif dep_sep_mar <= 0.34:
                                grid_GwT_depths[g][7] = grid_GwT_depths[g][7] + dem_res**2
                            elif dep_sep_mar <= 1.0:
                                grid_GwT_depths[g][8] = grid_GwT_depths[g][8] + dem_res**2
                            else:
                                grid_GwT_depths[g][9] = grid_GwT_depths[g][9] + dem_res**2
                            
                            # tabulate area of grid cell within each Mottled Duck depth bin; depth thresholds (in m) are: [0,0.08,0.30,0.36,0.42,0.46,0.50,0.56]
                            if dep_ann <= 0.0:        
                                grid_MtD_depths[g][1] = grid_MtD_depths[g][1] + dem_res**2
                            elif dep_ann <= 0.08:            
                                grid_MtD_depths[g][2] = grid_MtD_depths[g][2] + dem_res**2
                            elif dep_ann <= 0.30:            
                                grid_MtD_depths[g][3] = grid_MtD_depths[g][3] + dem_res**2
                            elif dep_ann <= 0.36:            
                                grid_MtD_depths[g][4] = grid_MtD_depths[g][4] + dem_res**2
                            elif dep_ann <= 0.42:            
                                grid_MtD_depths[g][5] = grid_MtD_depths[g][5] + dem_res**2
                            elif dep_ann <= 0.46:            
                                grid_MtD_depths[g][6] = grid_MtD_depths[g][6] + dem_res**2
                            elif dep_ann <= 0.50:            
                                grid_MtD_depths[g][7] = grid_MtD_depths[g][7] + dem_res**2
                            elif dep_ann <= 0.56:            
                                grid_MtD_depths[g][8] = grid_MtD_depths[g][8] + dem_res**2
                            else:
                                grid_MtD_depths[g][9] = grid_MtD_depths[g][9] + dem_res**2
    
            nline += 1
    
    # determine zonal averages over each ICM-LAVegMod grid cell
    for g in range(1,n500grid+1):
        ng = len(grid_bed_z_all[g]) + len(grid_land_z_all[g])
        
        if ng > 0:
            grid_bed_z[g]          = sum(grid_bed_z_all[g]) / ng
            grid_land_z[g]         = sum(grid_land_z_all[g]) / ng
            grid_pct_land[g]       = 100.0*sum(grid_pct_land_all[g]) / ng
            grid_pct_land_wetl[g]  = 100.0*sum(grid_pct_land_wetl_all[g]) / ng
            grid_pct_water[g]      = 100.0*sum(grid_pct_water_all[g]) / ng
            grid_pct_edge[g]       = 100.0*sum(grid_pct_edge_all[g]) / ng
        else:
            grid_bed_z[g]          = 0.0
            grid_land_z[g]         = 0.0
            grid_pct_land[g]       = 0.0
            grid_pct_land_wetl[g]  = 0.0
            grid_pct_water[g]      = 0.0
            grid_pct_edge[g]       = 0.0
            
    
    # determine zonal averages over each ICM-Hydro compartment
    for c in range(1,ncomp+1):    
        nc = len(comp_water_z_all[c]) + len(comp_wetland_z_all[c]) + len(comp_pct_upland_all[c])
    
        if nc > 0:
            comp_pct_upland[c] = sum(comp_pct_upland_all[c]) / nc
            comp_water_z[c]    = sum(comp_water_z_all[c]   ) / nc
            comp_wetland_z[c]  = sum(comp_wetland_z_all[c] ) / nc
            comp_pct_water[c]  = sum(comp_pct_water_all[c] ) / nc
            comp_edge_area[c]  = sum(comp_edge_area_all[c] )
        else:
            comp_pct_upland[c] = 0.0
            comp_water_z[c]    = 0.0
            comp_wetland_z[c]  = 0.0
            comp_pct_water[c]  = 0.0
            comp_edge_area[c]  = 0.0        
    
    print(' Writing zonal statistics output files:')
    with open(new_grid_filepath,mode='w') as gdaf:  
        print('     - %s' % new_grid_filepath)
        gdaf.write('GRID,MEAN_BED_ELEV,MEAN_LAND_ELEV,PERCENT_LAND_0-100,PERCENT_WETLAND_0-100,PERCENT_WATER_0-100\n')
        for g in grid_bed_z.keys():
            gdaf.write('%d,%0.4f,%0.4f,%0.2f,%0.2f,%0.2f\n' % (g,grid_bed_z[g],grid_land_z[g],grid_pct_land[g],grid_pct_land_wetl[g],grid_pct_water[g]) )
        
    with open(grid_pct_edge_file,mode='w') as gdef:  
        print('     - %s' % grid_pct_edge_file)
        gdef.write('GRID,PERCENT_EDGE_0-100\n')
        for g in grid_pct_edge.keys():
            gdef.write('%d,%0.4f\n' % (g,grid_pct_edge[g]) )
            
    with open(comp_elev_file,mode='w') as cef:
        print('     - %s' % comp_elev_file)
        cef.write('ICM_ID,MEAN_BED_ELEV,MEAN_MARSH_ELEV,MARSH_EDGE_AREA\n')
        for c in comp_water_z.keys():
            cef.write('%d,%0.4f,%0.4f,%d\n' % (c,comp_water_z[c],comp_wetland_z[c],comp_edge_area[c]) )
    
    with open(comp_wat_file, mode='w') as cwf:
        print('     - %s' % comp_wat_file)
        for c in comp_pct_water.keys():
            cwf.write( '%d,%0.4f\n' % (c,comp_pct_water[c]) )
    
    with open(comp_upl_file, mode='w') as cuf:
        print('     - %s' % comp_upl_file)
        for c in comp_pct_upland.keys():
            cuf.write( '%d,%0.4f\n' % (c,comp_pct_upland[c]) )
    
    with open(grid_Gdw_dep_file, mode='w') as Gdw:    
        print('     - %s' % grid_Gdw_dep_file)
        Gdw.write('GRID_ID,VALUE_0,VALUE_4,VALUE_8,VALUE_12,VALUE_18,VALUE_22,VALUE_28,VALUE_32,VALUE_36,VALUE_40,VALUE_44,VALUE_78,VALUE_150,VALUE_151\n')
        for g in grid_Gdw_depths.keys():
            linewrite = '%d' % g
            for Gdw_bin in range(1,Gdw_bin_n + 1):
                linewrite = '%s,%d' % (linewrite,grid_Gdw_depths[g][Gdw_bin])
            Gdw.write('%s\n' % linewrite)
    
    with open(grid_GwT_dep_file, mode='w') as GwT:
        print('     - %s' % grid_GwT_dep_file)
        GwT.write('GRID_ID,VALUE_0,VALUE_6,VALUE_18,VALUE_22,VALUE_26,VALUE_30,VALUE_34,VALUE_100,VALUE_101\n')
        for g in grid_GwT_depths.keys():
            linewrite = '%d' % g
            for GwT_bin in range(1,GwT_bin_n + 1):
                linewrite = '%s,%d' % (linewrite,grid_GwT_depths[g][GwT_bin])
            GwT.write('%s\n' % linewrite)
    
    with open(grid_MtD_dep_file, mode='w') as MtD:
        print('     - %s' % grid_MtD_dep_file)
        MtD.write('GRID_ID,VALUE_0,VALUE_8,VALUE_30,VALUE_36,VALUE_42,VALUE_46,VALUE_50,VALUE_56,VALUE_57\n')
        for g in grid_MtD_depths.keys():
            linewrite = '%d' % g
            for MtD_bin in range(1,MtD_bin_n + 1):
                linewrite = '%s,%d' % (linewrite,grid_MtD_depths[g][MtD_bin])
            MtD.write('%s\n' % linewrite)
    
            
    print(' Deleting output file: %s' % dem_grid_data_outfile)
    os.remove(dem_grid_data_outfile)

