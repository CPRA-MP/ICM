def WVA(gridIDs, links_data, flow_data,grid_comp, 
        comp_volume, annual_salinity, bedelevdict, melevdict, veg_output_filepath, 
        nvegtype,landdict, waterdict,pctedgedict, n500grid, n500rows, 
        n500cols,yll500, xll500, year, elapsedyear, HSI_dir, vegetation_dir, 
        wetland_morph_dir, runprefix,growing_season_salinity, stg_by_days_array, WVA_dir, 
        stand_age_dict, Qmult, tribQ):
    
    import numpy as np
    import os
    import datetime as dt
    import zipfile

    # set some general variables
    print(' Setting up WVA runs.')

    models = ['BF', 'SF', 'FM', 'IM','BM','SM']


    def dict2asc_flt(mapping_dict,outfile,asc_grid,asc_header,write_mode):
        # this function maps a dictionary of floating point data into XY space and saves as a raster file of ASCII grid format
        # this function does not return anything but it will save 'outfile' to disk

        # ASCII grid format description: http://resources.esri.com/help/9.3/arcgisengine/java/GP_ToolRef/spatial_analyst_tools/esri_ascii_raster_format.htm

        # 'mapping_dict' is a dictionary with grid cell ID as the key and some value for each key
        # 'outfile' is the filename (full path) of the output .asc raster text file to be saved
        # 'asc_grid' is a numpy array that is the grid structure of an ASCII text raster
        # 'asc_header' is a string that includes the 6 lines of text required by the ASCII grid format
            msg = '\ndid not save %s' % (outfile)
            with open(outfile, mode=write_mode) as outf:
                outf.write(asc_header)
                for row in asc_grid:
                    nc = 0
                    for col in row:
                        gid_map = row[nc]
                        if gid_map > 0:                     # if the ASC grid has a no data cell (-9999) there will be no dictionary key, the else criterion is met and it keeps the no data value (-9999)
                            gid_val = float(mapping_dict[gid_map] )
                        else:
                            gid_val = float(gid_map)
                        if nc == 0:
                            rowout = '%0.4f'  % gid_val
                        else:
                            rowout = '%s %0.4f' % (rowout,gid_val)
                        nc += 1
                    outf.write('%s\n' % rowout)
                    msg = '\nsuccessfully saved %s' % (outfile)
            return msg
    
    asc_grid_file = os.path.normpath(r'%s/veg_grid.asc' % vegetation_dir)
    asc_grid_ids = np.genfromtxt(asc_grid_file,skip_header=6,delimiter=' ',dtype='int')
    asc_grid_head = 'ncols 1052\nnrows 365\nxllcorner 404710\nyllcorner 3199480\ncellsize 480\nNODATA_value -9999\n'    


    asc_outprefix = '%s/%s_O_%02d_%02d_X_' % (WVA_dir, runprefix, elapsedyear, elapsedyear)
    csv_outprefix = '%s/%s_O_%02d_%02d_X_' % (WVA_dir, runprefix, elapsedyear, elapsedyear)




    #e = 2.718281828
    #jan, feb, mar, apr, may, jun, jul, aug, sep, octb, nov, dec = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11

    grid_ascii_file = os.path.normpath(vegetation_dir + '/veg_grid.asc')
    print(' Reading in ASCII grid template.')

    ascii_grid_lookup = np.genfromtxt(grid_ascii_file, delimiter=' ', skip_header=6)
    ascii_header = 'nrows %s \nncols %s \nyllcorner %s \nxllcorner %s \ncellsize 480.0 \nnodata_value -9999.00' % (
    n500rows, n500cols, yll500, xll500)
    ascii_header_nrows = 6

    # calculate average elevation for grid cell from values for marsh elev and bed elev imported separately
    grid_elv_ave = {}
    for n in gridIDs:
        use_water = 0
        use_land = 0
        if waterdict[n] > 0:
            if bedelevdict != -9999:
                use_water = 1  # have values for both percent water and bed elevation
        if landdict[n] > 0:
            if bedelevdict != -9999:
                use_land = 1  # have values for both percent land and marsh elevation

        if use_water == 1:
            if use_land == 1:  # have both land and water data - calculate weighted mean elevation
                grid_elv_ave[n] = (bedelevdict[n] * waterdict[n] + melevdict[n] * landdict[n]) / (waterdict[n] + landdict[n])
            else:  # have only water data
                grid_elv_ave[n] = bedelevdict[n]
        elif use_land == 1:  # have only land data
            grid_elv_ave[n] = melevdict[n]
        else:  # do not have land or water data
            grid_elv_ave[n] = -9999

    # read in Veg output file - this is the same code that is used in WM.ImportVegResults()
    print(' Reading in LAVegMod output files to be used for HSIs.')
    skipvalue = n500rows + 7
    vegcolumns = nvegtype + 12  # veg columns is the number of vegetation types (including flotant/dead flt/bare flt) plus CellID, Water, NotMod,BareGround (old and new), FFIBS score, and percent vegetation type summary values
    new_veg = np.zeros((n500grid, vegcolumns))
    veg_missing = 0
    
    # open Vegetation output file
    with open(veg_output_filepath, 'r') as vegfile:
        # skip ASCII header rows and ASCII grid at start of output file
        for n in range(0, skipvalue - 1):
            dump = vegfile.readline()
        # read in header of Vegetation output at bottom of ASCII grid
        vegtypenames = vegfile.readline().split(',')
        # remove any leading or trailing spaces in veg types
        for n in range(0, len(vegtypenames)):
            vegtypenames[n] = vegtypenames[n].lstrip().rstrip()
        # loop through rest of Vegetation file
        for nn in range(0, n500grid):
            # split each line of file based on comma delimiter (any spaces will be removed with rstrip,lstrip)
            vline = vegfile.readline().split(",")
            # if all columns have data in output file, assign veg output to veg_ratios array
            if (len(vline) == vegcolumns):
                for nnn in range(0, len(vline)):
                    new_veg[nn, nnn] = float(vline[nnn].lstrip().rstrip())
            # if there are missing columns in line, set first column equal to grid cell, and set all other columns equal to 0.
            else:
                for nnn in range(1, vegcolumns):
                    new_veg[nn, 0] = nn + 1
                    new_veg[nn, nnn] = 0.0
                veg_missing += 1
    if (veg_missing > 0):
        print(' Some Vegetation output was not written correctly to Veg output file.')
        print('  - %s 500m grid cells did not have complete results in Veg Output file.' % veg_missing)



    print(' Reclassifying Veg species output into general LULC types used by HSI equations.')
    # generate some blank dictionaries that will be filled with Veg output
    wetlndict = {}
    btfordict = {}
    baredict = {}
    uplanddict = {}
    watsavdict = {}
    ULAMdict = {}
    NYAQ2dict = {}
    TADI2dict = {}
    SANIdict = {}
    QULEdict = {}
    QUNIdict = {}
    QUVIdict = {}
    QULA3dict = {}
    QUTEdict = {}
    ELBA2dict = {}
    PAHE2dict = {}
    COESdict = {}
    MOCE2dict = {}
    SALA2dict = {}
    ZIMIdict = {}
    CLMA10dict = {}
    ELCEdict = {}
    IVFRdict = {}
    PAVAdict = {}
    PHAU7dict = {}
    POPU5dict = {}
    SALAdict = {}
    SCCA11dict = {}
    TYDOdict = {}
    SCAM6dict = {}
    SCRO5dict = {}
    SPCYdict = {}
    SPPAdict = {}
    AVGEdict = {}
    DISPdict = {}
    JUROdict = {}
    SPALdict = {}
    BAHABIdict = {}
    DISPBIdict = {}
    PAAM2dict = {}
    SOSEdict = {}
    SPPABIdict = {}
    SPVI3dict = {}
    STHE9dict = {}
    UNPAdict = {}
    treecover_dict = {}
    water2dict = {}

    new_files = []
    print('Sub Aquatic Read')
    
    sav_asc_file = '%s/output/%s_O_%02d_%02d_W_SAV.asc' % (wetland_morph_dir, runprefix, elapsedyear, elapsedyear)
    if os.path.isdir(sav_asc_file):
        sav_asc_file = '%s/output/%s_O_%02d_%02d_W_SAV.asc/%s_O_%02d_%02d_W_SAV.asc' % (wetland_morph_dir, runprefix, elapsedyear, elapsedyear,runprefix, elapsedyear, elapsedyear)
    if os.path.exists(sav_asc_file)==False:
        file_name = os.path.basename(sav_asc_file)
        zip_path = os.path.normpath(f'{sav_asc_file}.zip')
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extract(file_name, path=sav_asc_file)
        new_files.append(sav_asc_file)
    
    if os.path.exists(grid_ascii_file)==False:
        file_name = os.path.basename(grid_ascii_file)
        zip_path = os.path.normpath(f'{grid_ascii_file}.zip')
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extract(file_name, path=grid_ascii_file)
        new_files.append(grid_ascii_file)

    sav_in = np.genfromtxt(sav_asc_file, skip_header=6, delimiter=' ', dtype='str')
    grid_in = np.genfromtxt(grid_ascii_file, skip_header=6, delimiter=' ', dtype='str')

    for file in new_files:
        os.remove(file)

    nl = 0
    for line in grid_in:
        nc = 0
        for nc in range(0, len(grid_in[nl])):
            gridID = int(grid_in[nl][nc])
            watsavdict[gridID] = float(sav_in[nl][nc])
            nc += 1
        nl += 1

    print('Generating Additional dictionaries')
    pct_land_cover = {}
    # Veg File to Dictionaries
    for n in range(0, len(new_veg)):
        gridID = int(new_veg[n][0])
        pland = landdict[gridID] / 100.0
        btfordict[gridID] = pland * new_veg[n][vegtypenames.index('pL_BF')]  # % Bottomland Hardwood Forest
        TADI2dict[gridID] = new_veg[n][vegtypenames.index('TADI2')]  # Bald cypress
        NYAQ2dict[gridID] = new_veg[n][vegtypenames.index('NYAQ2')] # Water Tupelo
        SANIdict[gridID] = new_veg[n][vegtypenames.index('SANI')] #Black Willow
        QULEdict[gridID] = new_veg[n][vegtypenames.index('QULE')] #Overcup Oak
        QUNIdict[gridID] = new_veg[n][vegtypenames.index('QUNI')] #Water Oak
        QUVIdict[gridID] = new_veg[n][vegtypenames.index('QUVI')] #Southern Live Oak
        QULA3dict[gridID] = new_veg[n][vegtypenames.index('QULA3')] #Swamp Laurel Oak
        QUTEdict[gridID] = new_veg[n][vegtypenames.index('QUTE')] #Texas Red Oak
        ULAMdict[gridID] = new_veg[n][vegtypenames.index('ULAM')]
        ELBA2dict[gridID] = new_veg[n][vegtypenames.index('ELBA2_Flt')]
        COESdict[gridID] = new_veg[n][vegtypenames.index('COES')]
        MOCE2dict[gridID] = new_veg[n][vegtypenames.index('MOCE2')]
        PAHE2dict[gridID] = new_veg[n][vegtypenames.index('PAHE2')]
        SALA2dict[gridID] = new_veg[n][vegtypenames.index('SALA2')]
        ZIMIdict[gridID] = new_veg[n][vegtypenames.index('ZIMI')]
        CLMA10dict[gridID] = new_veg[n][vegtypenames.index('CLMA10')]
        ELCEdict[gridID] = new_veg[n][vegtypenames.index('ELCE')]
        IVFRdict[gridID] = new_veg[n][vegtypenames.index('IVFR')]
        PAVAdict[gridID] = new_veg[n][vegtypenames.index('PAVA')]
        PHAU7dict[gridID] = new_veg[n][vegtypenames.index('PHAU7')]
        POPU5dict[gridID] = new_veg[n][vegtypenames.index('POPU5')]
        SALAdict[gridID] = new_veg[n][vegtypenames.index('SALA')]
        SCCA11dict[gridID] = new_veg[n][vegtypenames.index('SCCA11')]
        TYDOdict[gridID] = new_veg[n][vegtypenames.index('TYDO')]
        SCAM6dict[gridID] = new_veg[n][vegtypenames.index('SCAM6')]
        SCRO5dict[gridID] = new_veg[n][vegtypenames.index('SCRO5')]
        SPCYdict[gridID] = new_veg[n][vegtypenames.index('SPCY')]
        SPPAdict[gridID] = new_veg[n][vegtypenames.index('SPPA')]
        AVGEdict[gridID] = new_veg[n][vegtypenames.index('AVGE')] #Black Mangrove
        DISPdict[gridID] = new_veg[n][vegtypenames.index('DISP')]
        JUROdict[gridID] = new_veg[n][vegtypenames.index('JURO')]
        SPALdict[gridID] = new_veg[n][vegtypenames.index('SPAL')]
        BAHABIdict[gridID] = new_veg[n][vegtypenames.index('BAHABI')]
        DISPBIdict[gridID] = new_veg[n][vegtypenames.index('DISPBI')]
        PAAM2dict[gridID] = new_veg[n][vegtypenames.index('PAAM2')]
        SOSEdict[gridID] = new_veg[n][vegtypenames.index('SOSE')]
        SPPABIdict[gridID] = new_veg[n][vegtypenames.index('SPPABI')]
        SPVI3dict[gridID] = new_veg[n][vegtypenames.index('SPVI3')]
        STHE9dict[gridID] = new_veg[n][vegtypenames.index('STHE9')]
        UNPAdict[gridID] = new_veg[n][vegtypenames.index('UNPA')]
        water2dict[gridID] = new_veg[n][vegtypenames.index('WATER')]
        treecover_dict[gridID] = new_veg[n][vegtypenames.index('TADI2')] \
                                + new_veg[n][vegtypenames.index('NYAQ2')] \
                                + new_veg[n][vegtypenames.index('SANI')]\
                                + new_veg[n][vegtypenames.index('QULE')]\
                                + new_veg[n][vegtypenames.index('QUNI')]\
                                + new_veg[n][vegtypenames.index('QUVI')]\
                                + new_veg[n][vegtypenames.index('QULA3')]\
                                + new_veg[n][vegtypenames.index('QUTE')]\
                                + new_veg[n][vegtypenames.index('ULAM')]
        baredict[gridID] = new_veg[n][vegtypenames.index('BAREGRND_Flt')] \
                            + new_veg[n][vegtypenames.index('BAREGRND_OLD')] \
                            + new_veg[n][vegtypenames.index('BAREGRND_NEW')]  # % Bareground (including bare flotant)
        wetlndict[gridID] = 1.0 - (baredict[gridID] \
                                    + new_veg[n][vegtypenames.index('WATER')] \
                                    + new_veg[n][vegtypenames.index('NOTMOD')])  # % Marsh Wetland (all types, including flotant)
        uplanddict[gridID] = new_veg[n][vegtypenames.index('NOTMOD')]  # % upland/developed (classified as NOTMOD in LAVegMod)
       
        for model in models:
            if n == 0:
                pct_land_cover[model] = {}
            pct_land_cover[model][gridID] = (new_veg[n][vegtypenames.index(f'pL_{model}')]*(1-water2dict[gridID]))

        # Check for bareground - if there is no wetland or forest type, but there is bareground, set bareground multiplier to zero
        if baredict[gridID] > 0.0:
            if wetlndict[gridID] > btfordict[gridID]:
                wetlndict[gridID] += baredict[gridID]

    for gridID in gridIDs:
        wetlndict[gridID] = max(0.0, min(100.0, 100.0 * wetlndict[gridID]))
        watsavdict[gridID] = max(0.0, min(100.0, 100.0 * watsavdict[gridID]))

    
    variables = {}

    hold_constant = {}
    for gridID in gridIDs:
        hold_constant[gridID]  = 1

    ########################################
    ##    Fresh/Intermediate Marsh WVA    ##
    ########################################
    print('Calculating Fresh Marsh WVA')

    # WVA for Fresh/Intermediate Marsh

    WVAcsv = r'%sFMarsh.csv' % csv_outprefix
    #WVAasc = r'%sFMarsh.asc' % asc_outprefix

    with open(WVAcsv, 'w') as FMarsh:

        headerstring = 'GridID,WVA_FMarsh,WVA_FWater,WVA_IMarsh,WVA_IWater,v1,v2,v3a,v3b,v4,v5,v6,SI1,SI2,SI3,SI4,SI5_Fresh,SI5_Intermediate,S6I\n'
        FMarsh.write(headerstring)
        
        #########################
        #V1: Emergent Vegetation#
        #########################
        print('Calculating Fresh / Intermediate V1: Emergent Vegetation')
        v1 = wetlndict
        S1 = {}
        for gridID in gridIDs:
            S1[gridID] = (0.009 * v1[gridID]) + 0.1

        ###################################
        #V2: Sumbereged Aquatic Vegetation#
        ###################################
        print('Calculating Fresh / Intermediate V2: Submerged Auqatioc Vegetation')
        v2={}
        v2 = watsavdict
        S2 = {}
        for gridID in gridIDs:
            S2[gridID] = (0.009 * v2[gridID]) + 0.1

        
        ###################################
        # V3: Marsh Edge and Interspersion#
        ###################################
        print('Calculating Fresh / Intermediate V3: Marsh Edge and Interspersion')
        S3 = {}
        edgethres = 30
        v3a = landdict #percent land
        v3b = pctedgedict #percent edge
        for gridID in gridIDs:
            if v3a[gridID] > 82:
                if v3b[gridID] < edgethres:
                    S3[gridID] = 1 #Class 1
                else:
                    S3[gridID] = .6 #Class 2
            elif v3a[gridID] > 6:
                if v3b[gridID] <edgethres:
                    S3[gridID] = .6 #Class 2
                else:
                    S3[gridID] = .4 #Class 3
            elif v3a[gridID] > 40:
                if v3b[gridID] <edgethres:
                    S3[gridID] = .4 #Class 3
                else:
                    S3[gridID] = .2 #Class 4
            elif v3a[gridID] > 10:
                if v3b[gridID] <edgethres:
                    S3[gridID] = .2 #Class 4
                else:
                    S3[gridID] = .1 #Class 5
            else: 
                    S3[gridID] = .1 #Class 5

        ########################################
        #Variable 4: Shallow Open Water Habitat#
        ########################################
        print('Calculating Fresh / Intermediate V4: Shallow Open Water Habitat')
        MotDuckCSV = os.path.normpath("%s/MotDuckDepths_cm_%s.csv" % (HSI_dir, year))

        if not os.path.exists(MotDuckCSV):
            file_name = os.path.basename(MotDuckCSV)
            zip_path = os.path.normpath(f'{MotDuckCSV}.zip')
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extract(file_name, path=HSI_dir)
            new_files.append(MotDuckCSV)

        MotDuck = np.genfromtxt(MotDuckCSV, delimiter=',', skip_header=1)
        MotDuckDepdict = {}
        MDDdict = {}
        MDDmissing = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # values to assign to grid cells with no GridID key in depth dictionary
        v4 = {}
        S4a = {}
        # convert MotDuck depths array into dictionary, GridID is key (only grid cells overlaying geospatial extent in WM.CalculateEcohydroAttributes() will have a key and values
        for n in range(0, len(MotDuck)):
            gridIDinD = MotDuck[n, 0]
            MDDdict[gridIDinD] = MotDuck[n, 1:10]

        # generate dictionary of various depths for all gridID values
        for gridID in gridIDs:
            try:
                MotDuckDepdict[gridID] = MDDdict[gridID]
            except:
                MotDuckDepdict[gridID] = MDDmissing
           
            area = 0  # Initialize area variable
            for x in range(0,9):    # x is number of columns in depth dictionary (as summarized in WM.HSIreclass)
                area = area + MotDuckDepdict[gridID][x] #determine area of cell analyzed when developing depth values in morph(not exactly equal to 500x500 since the 30x30 m grid doesn't fit in the 500x500
                #if area < 480*480:
                    #area =480*480
            less0 = MotDuckDepdict[gridID][0] # area of cell less than 0-cm deep    
            v4a = MotDuckDepdict[gridID][1] # area of cell 0-8 cm deep
            v4b = MotDuckDepdict[gridID][2] # area of cell 8-30 cm deep 
            v4c = MotDuckDepdict[gridID][3] # area of cell 30-36 cm deep
            v4d = MotDuckDepdict[gridID][4] # area of cell 36-42 cm deep
            v4e = MotDuckDepdict[gridID][5] # area of cell 42-46 cm deep; 46cm = 1.5ft depth, as per CWPPRA documentation
            
            if area == 0:
                v4[gridID] = 0
            elif area == less0:
                v4[gridID] = 1
            else:
                v4[gridID] = (v4a+v4b+v4c+v4d+v4e) / (area - less0)
            
            #v4[gridID] = (v3f + v3g + v3h)
            if 0 <= v4[gridID] < 0.8:
                S4a[gridID] = (1.125 * v4[gridID]) + 0.1
            elif 0.8 <= v4[gridID] <= 0.9:
                S4a[gridID] = 1.0
            elif v4[gridID] > 0.9:
                S4a[gridID] = (-4 * v4[gridID]) + 4.6

        ###############################################
        # V5: Mean high Salinity During Growing Season#
        ###############################################
        print('Calculating Fresh / Intermediate V5: Mean High Salinity During Growing Season')
        v5 = growing_season_salinity
        S5_Fresh = {}
        S5_Intermediate = {}
        for gridID in gridIDs:
            if 0 <= v5[gridID] <= 0.5:
                S5_Fresh[gridID] = 1.0
            elif 0.5 < v5[gridID] < 5.0:
                S5_Fresh[gridID] = (-0.2 * v5[gridID]) + 1.1
            elif v5[gridID] >= 5.0:
                S5_Fresh[gridID] = 0.1
            
            if 0 <= v5[gridID] <= 2.5:
                S5_Intermediate[gridID] = 1.0
            elif 2.5 < v5[gridID] < 7:
                S5_Intermediate[gridID] = (-.2 * v5[gridID]) + 1.5
            else:
                S5_Intermediate[gridID] = .1
        
        ############################
        #V6 Aquatic organism access# - HOLD CONSTANT
        # ##########################
        v6 = hold_constant
        S6 = hold_constant
    

        print('Printing Fresh / Intermediate Marsh Results')
        variables['FM'] = {'HSI': {},
                           'SI1': {},
                           'SI2': {},
                           'SI3': {},
                           'SI4': {},
                           'SI5': {},
                           'SI6': {},
                           'HSI_W': {}
        }
        
        variables['IM'] = {'HSI': {},
                           'SI1': {},
                           'SI2': {},
                           'SI3': {},
                           'SI4': {},
                           'SI5': {},
                           'SI6': {},
                           'HSI_W': {}
        }
        
        for gridID in gridIDs:
            WVA_FMarsh = ((3.5 * (S1[gridID] ** 5 * S6[gridID]) ** (1 / 6)) + (S3[gridID] + S5_Fresh[gridID]) / 2) / 4.5
            WVA_FWater = ((3.5 * (S2[gridID] ** 3 * S6[gridID]) ** (1 / 4)) + (S3[gridID] + S4a[gridID] + S5_Fresh[gridID]) / 3) / 4.5

            WVA_IMarsh = ((3.5 * (S1[gridID] ** 5 * S6[gridID]) ** (1 / 6)) + (S3[gridID] + S5_Intermediate[gridID]) / 2) / 4.5
            WVA_IWater = ((3.5 * (S2[gridID] ** 3 * S6[gridID]) ** (1 / 4)) + (S3[gridID] + S4a[gridID] + S5_Intermediate[gridID]) / 3) / 4.5

            writestring = '%d,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f\n' % \
            (gridID, WVA_FMarsh, WVA_FWater, WVA_IMarsh, WVA_IWater, v1[gridID], v2[gridID], v3a[gridID], v3b[gridID], v4[gridID], 
            v5[gridID], v6[gridID], S1[gridID], S2[gridID], S3[gridID], S4a[gridID], S5_Fresh[gridID], S5_Intermediate[gridID], S6[gridID])
            FMarsh.write(writestring)



            variables['FM']['HSI'][gridID] = WVA_FMarsh
            variables['FM']['SI1'][gridID] = S1[gridID]
            variables['FM']['SI2'][gridID] = S2[gridID]
            variables['FM']['SI3'][gridID] = S3[gridID]
            variables['FM']['SI4'][gridID] = S4a[gridID]
            variables['FM']['SI5'][gridID] = S5_Fresh[gridID]
            variables['FM']['SI6'][gridID] = S6[gridID]
            variables['FM']['HSI_W'][gridID] = WVA_FWater

            variables['IM']['HSI'][gridID] = WVA_FMarsh
            variables['IM']['SI1'][gridID] = S1[gridID]
            variables['IM']['SI2'][gridID] = S2[gridID]
            variables['IM']['SI3'][gridID] = S3[gridID]
            variables['IM']['SI4'][gridID] = S4a[gridID]
            variables['IM']['SI5'][gridID] = S5_Intermediate[gridID]
            variables['IM']['SI6'][gridID] = S6[gridID]
            variables['IM']['HSI_W'][gridID] = WVA_IWater

        del (v5, S4a, S5_Fresh, S5_Intermediate)

    ########################################
    ##         Brackish Marsh WVA         ##
    ########################################
    print('Calculating Brackish Marsh WVA')

    # WVA for Brackish Marsh

    WVAcsv = r'%sBMarsh.csv' % csv_outprefix
    WVAasc = r'%sBMarsh.asc' % asc_outprefix

    with open(WVAcsv, 'w') as BMarsh:

        headerstring = 'GridID,WVA_BMarsh,WVA_BWater,v1,v2,v3a,v3b,v4,v5,v6,SI1,SI2,SI3,SI4,SI5,SI6\n'
        BMarsh.write(headerstring)

        
        ##############################
        #V4: % Open Water <1.5ft deep#
        ##############################
        print('Calculating Brackish Marsh V4: Percent Open Water <1.5ft')
        S4 = {}
        for gridID in gridIDs:
            if 0 <= v4[gridID] < 0.7:
                S4[gridID] = (1.286 * v4[gridID]) + 0.1
            elif 0.7 <= v4[gridID] <= 0.8:
                S4[gridID] = 1.0
            elif v4[gridID] > 0.8:
                S4[gridID] = (-2 * v4[gridID]) + 2.6

        #############################
        #V5: Average Annual Salinity#
        #############################
        print('Calculating Brackish Marsh V5: Average Annual Salinity')
        v5 = annual_salinity
        S5 = {}
        for gridID in gridIDs:
            if 0 <= v5[gridID] <= 10:
                S5[gridID] = 1.0
            elif 16>= v5[gridID] > 10:
                S5[gridID] = (-0.15 * v5[gridID]) + 2.5
            else:
                S5[gridID] = .1

        ##########################
        # Aquatic organism access# - HOLD CONSTANT
        ##########################
        #v6 = {}
        #S6 = {}
        #for gridID in gridIDs:
        #    v6[gridID] = 1.0
        #    S6[gridID] = 1.0
        print('Printing Brackish Marsh Results')

        variables['BM'] = {'HSI': {},
                           'SI1': {},
                           'SI2': {},
                           'SI3': {},
                           'SI4': {},
                           'SI5': {},
                           'SI6': {},
                           'HSI_W': {}
        }

        for gridID in gridIDs:
            WVA_BMarsh = ((3.5 * (S1[gridID] ** 5 * S6[gridID] ** 1.5) ** (1 / 6.5)) + (S3[gridID] + S5[gridID]) / 2) / 4.5
            WVA_BWater = ((3.5 * (S2[gridID] ** 3 * S6[gridID] ** 2) ** (1 / 5)) + (S3[gridID] + S4[gridID] + S5[gridID]) / 3) / 4.5

            writestring = '%d,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f\n' % \
            (gridID, WVA_BMarsh, WVA_BWater, v1[gridID], v2[gridID], v3a[gridID], v3b[gridID], v4[gridID], 
            v5[gridID], v6[gridID], S1[gridID], S2[gridID], S3[gridID], S4[gridID], S5[gridID], S6[gridID])
            BMarsh.write(writestring)

            variables['BM']['HSI'][gridID] = WVA_BMarsh
            variables['BM']['SI1'][gridID] = S1[gridID]
            variables['BM']['SI2'][gridID] = S2[gridID]
            variables['BM']['SI3'][gridID] = S3[gridID]
            variables['BM']['SI4'][gridID] = S4[gridID]
            variables['BM']['SI5'][gridID] = S5[gridID]
            variables['BM']['SI6'][gridID] = S6[gridID]
            variables['BM']['HSI_W'][gridID] = WVA_BWater

        del (S2, S4, S5)

    ########################################
    ##           Saline Marsh WVA         ##
    ########################################
    print('Calculating Saline Marsh WVA')

    # WVA for Saline Marsh

    WVAcsv = r'%sSMarsh.csv' % csv_outprefix
    WVAasc = r'%sSMarsh.asc' % asc_outprefix

    with open(WVAcsv, 'w') as SMarsh:

        headerstring = 'GridID,WVA_SMarsh,WVA_SWater,v1,v2,v3a,v3b,v4,v5,v6,SI1,SI2,SI3,SI4,SI5,SI6\n'
        SMarsh.write(headerstring)

        ########################################################
        #V2: Percent of wetland covered by submerged vegetation#
        ########################################################
        print('Calculating Saline Marsh V2: Percent Submerged Vegetation')
        #    v2 = watsavdict
        S2 = {}
        for gridID in gridIDs:
            S2[gridID] = (0.007 * v2[gridID]) + 0.3

        ##############################
        #V4: % Open Water <1.5ft deep#
        ##############################
        print('Calculating Saline Marsh V4: Percent Open Water <1.5ft')
        S4 = {}
        for gridID in gridIDs:
            if 0 <= v4[gridID] < 0.7:
                S4[gridID] = (1.286 * v4[gridID]) + 0.1
            elif 0.7 <= v4[gridID] <= 0.8:
                S4[gridID] = 1.0
            elif v4[gridID] > 0.8:
                S4[gridID] = (-2.5 * v4[gridID]) + 3

        ############################
        #V5:Average Annual Salinity#
        ############################
        #v5 = annual_salinity
        print('Calculating Saline Marsh V5: Average Annual Salinity')
        S5 = {}
        for gridID in gridIDs:
            if 9 <= v5[gridID] <= 21:
                S5[gridID] = 1.0
            elif 34.33 >= v5[gridID] > 21: #Added upper limit to prevent negative SI values
                S5[gridID] = (-0.067 * v5[gridID]) + 2.4
            else:
                S5[gridID] = .1 #Added to prevent negative SI values

        print('Printing Saline Marsh Results')

        variables['SM'] = {'HSI': {},
                           'SI1': {},
                           'SI2': {},
                           'SI3': {},
                           'SI4': {},
                           'SI5': {},
                           'SI6': {},
                           'HSI_W': {}
        }

        for gridID in gridIDs:
            WVA_SMarsh = ((3.5 * (S1[gridID] ** 3 * S6[gridID]) ** (1 / 4)) + (S3[gridID] + S5[gridID]) / 2) / 4.5
            WVA_SWater = ((3.5 * (S2[gridID] * S6[gridID] ** 2.5) ** (1 / 3.5)) + (S3[gridID] + S4[gridID] + S5[gridID]) / 3) / 4.5

            writestring = '%d,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f\n' % \
            (gridID, WVA_SMarsh, WVA_SWater, v1[gridID], v2[gridID], v3a[gridID], v3b[gridID], v4[gridID], 
            v5[gridID], v6[gridID], S1[gridID], S2[gridID], S3[gridID], S4[gridID], S5[gridID], S6[gridID])
            
            SMarsh.write(writestring)

            variables['SM']['HSI'][gridID] = WVA_SMarsh
            variables['SM']['SI1'][gridID] = S1[gridID]
            variables['SM']['SI2'][gridID] = S2[gridID]
            variables['SM']['SI3'][gridID] = S3[gridID]
            variables['SM']['SI4'][gridID] = S4[gridID]
            variables['SM']['SI5'][gridID] = S5[gridID]
            variables['SM']['SI6'][gridID] = S6[gridID]
            variables['SM']['HSI_W'][gridID] = WVA_SWater
        # delete temporary variables so they do not accidentally get used in other HSIs
        del (v1, v2, v3a, v3b, v5, S1, S2, S3, S4, S5)


    ########################################
    ##              Swamp WVA             ##
    ########################################
    print('Calculating Swamp WVA')

    # WVA for Swamp

    WVAcsv = r'%sSwamp.csv' % csv_outprefix
    WVAasc = r'%sSwamp.asc' % asc_outprefix

    with open(WVAcsv, 'w') as Swamp:

        headerstring = 'GridID,WVA_Swamp,v1a,v1b,v1c,v2,v3a,v3b,v4,SI1,SI2,SI3,SI4\n'
        Swamp.write(headerstring)

        
        #####################
        #V1: Stand Structure#
        #####################
        print('Calculating Swamp V1: Stand Structure')
        S1 = {}
        v1a = {} # Overstory Closure
        v1b = {} # Midstory Cover
        v1c = {} # Herbaceous Cover
        for gridID in gridIDs:
            denominator = (1-uplanddict[gridID]-water2dict[gridID])
            if denominator != 0:
                v1a[gridID] = treecover_dict[gridID]/(1-uplanddict[gridID]-water2dict[gridID]) #Overtory Closure
            else:
                v1a[gridID] = 0

            if v1a[gridID] <.2:
                midstory_ratio = .8
            elif v1a[gridID] <= .8:
                midstory_ratio = 1 - v1a[gridID]
            else:
                midstory_ratio = .2

            useable_space = 1-uplanddict[gridID] - (treecover_dict[gridID]*(1-midstory_ratio))
            
            v1b[gridID]=(((ULAMdict[gridID]+NYAQ2dict[gridID]+TADI2dict[gridID]+SANIdict[gridID]
                        +QULEdict[gridID]+QUNIdict[gridID]+QUVIdict[gridID]+QULA3dict[gridID]+
                        QUTEdict[gridID])*midstory_ratio)+AVGEdict[gridID]+MOCE2dict[gridID]+PHAU7dict[gridID]
                        +IVFRdict[gridID]+BAHABIdict[gridID])/useable_space
            
            v1c[gridID] = (ELBA2dict[gridID]+PAHE2dict[gridID]+COESdict[gridID]+SALA2dict[gridID]
                        + ZIMIdict[gridID]+CLMA10dict[gridID]+ELCEdict[gridID]+PAVAdict[gridID]
                        +POPU5dict[gridID]+SALAdict[gridID]+SCCA11dict[gridID]+TYDOdict[gridID]+SCAM6dict[gridID]+SPCYdict[gridID]
                        +SCRO5dict[gridID]+SPPAdict[gridID]+DISPdict[gridID]+JUROdict[gridID]+SPALdict[gridID]
                        +DISPBIdict[gridID]+PAAM2dict[gridID]+SOSEdict[gridID]+SPPABIdict[gridID]+SPVI3dict[gridID]+STHE9dict[gridID]
                        +UNPAdict[gridID])/useable_space
            
            if v1a[gridID] < .33:
                S1[gridID] = .1 #Class 1
            elif v1a[gridID] <.5:
                if v1b[gridID] < .33:
                    if v1c[gridID] < .33:
                        S1[gridID] = .2 #Class 2
                    else:
                        S1[gridID] = .4 #Class 3
                else:
                    if v1c[gridID] < .33:
                        S1[gridID] = .4 #Class 3
                    else:
                        S1[gridID] = .8 #Class 5
            elif .75 > v1a[gridID] >= .50:
                if v1b[gridID] > .33:
                    if v1c[gridID] <.33:
                        S1[gridID] = .6 #Class 4
                    else:
                        S1[gridID] = 1.0 #Class 6
                else: 
                    if v1c[gridID] >.33:
                        S1[gridID] = .6 #Class 4
                    else:
                        S1[gridID] = .4 #No Definition to this, went down a class
            else: #if overstory > .75
                if v1b[gridID] >.33:
                    S1[gridID] = 1.0 #Class 6
                else:
                    if v1c[gridID] >.33:
                        S1[gridID] = 1.0 #Class 6
                    else: 
                        S1[gridID] = .6 #No Definition to this, went down to class 4

                

        ####################
        #V2: Stand Maturity#
        ####################
        v2 = stand_age_dict
        S2 = {}
        for gridID in gridIDs: #The age to SI relationship was defined by the work of Atchafalaya Master Plan Team
            if v2[gridID] == 0:
                S2[gridID] = 0
            elif v2[gridID] <= 3:
                S2[gridID] = (.0033*v2[gridID])
            elif v2[gridID] <= 7:
                S2[gridID] = (.01*v2[gridID])-.02
            elif v2[gridID] <= 10:
                S2[gridID] = (0.017 * v2[gridID]) - 0.07
            elif v2[gridID] <= 20:
                S2[gridID] = (0.02 * v2[gridID]) - 0.1
            elif v2[gridID] <= 30:
                S2[gridID] = (0.03 * v2[gridID]) - 0.3
            elif v2[gridID] <= 50:
                S2[gridID] = (0.02 * v2[gridID])
            else:
                S2[gridID] = 1
        
        ##################
        #V3: WATER REGIME#
        ##################
        print('Calculating Swamp V3: Water Regime')
        S3 = {}

        start_date = dt.date(year,1,1)
        growing_start = dt.date(year, 3, 1)
        growing_end = dt.date(year, 10,31)
        end_date = dt.date(year, 12, 31)
        ind_start = (growing_start - start_date).days
        ind_end = (growing_end - start_date).days
        year_end_data = end_date - start_date
        year_end = year_end_data.days
        v3a = {}
        

        depth_by_day = {}
        for gridID in gridIDs: #Find Depth
            depth_by_day= {}
            for day in range(1,year_end+1):
                if grid_elv_ave[gridID] != -9999:
                    if stg_by_days_array[gridID][day] > grid_elv_ave[gridID]:
                        depth_by_day[day] = 1
                    else:
                        depth_by_day[day] = 0
                else:
                    if abs(stg_by_days_array[gridID][day]) > 0:
                        depth_by_day[day] = 1
                    else:
                        depth_by_day[day] = 0
            num_wet_growing = sum(depth_by_day[day] for day in range(ind_start,ind_end+1))
            num_wet_other = sum(depth_by_day[day] for day in range(1,ind_start)) +sum(depth_by_day[day] for day in range(ind_end+1,year_end+1))
            
            if num_wet_growing < 20:
                v3a[gridID] = 0.0 #No Flooding
            elif num_wet_growing < ((ind_end-ind_start)/2): #Half the Growing Season
                v3a[gridID] = 1.0 #Temporarily Flooded
            elif num_wet_growing < (ind_end-ind_start -20): #Almost all of the growing season
                v3a[gridID] = 2.0 #Seasonally Flooded
            elif (num_wet_growing+num_wet_other) < (year_end):
                v3a[gridID] = 3.0 #Semi-permanently Flooded
            else:
               v3a[gridID] = 4.0 # Permanently Flooded

        #Flow Exchange
        #Initialize the US and DS compartemtns of each link
        links_US = {}
        links_DS = {}
        for link in range(0,len(links_data)):
            links_US[link] = links_data[link][0]
            links_DS[link] = links_data[link][1]

        #Create a dictionary of the volume of each compartment
        flow_in = {compartmentID: 0 for compartmentID in range(1,1788)}
        flow_out = {compartmentID: 0 for compartmentID in range(1,1788)}


        scaled_flow = flow_data * 86400  #Unit Conversion (cfs to cfd) 

        for link in range(0,len(links_data)):
            us_comp = int(links_US[link])
            ds_comp = int(links_DS[link])
            for day in range(1, year_end+1):
                flow = scaled_flow[day][link]
                if flow > 0: #Flowing from US to DS
                    flow_in[ds_comp] += flow
                    flow_out[us_comp] += flow
                else: #Flowing from DS to US
                    flow_in[us_comp] += abs(flow)
                    flow_out[ds_comp] += abs(flow)
        
        for comp in range(1, 1788):
            qmultline = Qmult[comp - 1, 1:]
            if np.nansum(qmultline) != 0:
                for div, col in enumerate(qmultline):
                    if not np.isnan(col) and col > 0:
                        flow =  col * 86400 * np.nansum(tribQ[:, div])
                        flow_in[comp] += flow

        flow_balance = {}
        flow_ratio = {}
        for compartmentID in range(1,1788):
            if comp_volume[compartmentID] != 0:
                if flow_in[compartmentID] + flow_out[compartmentID] == 0:
                    flow_balance[compartmentID] = 0
                else:
                    flow_balance[compartmentID] = flow_in[compartmentID]/(flow_in[compartmentID] + flow_out[compartmentID])
                flow_ratio[compartmentID] = (flow_in[compartmentID]+flow_out[compartmentID])/comp_volume[compartmentID]
            else:
                flow_balance[compartmentID] = 0
                flow_ratio[compartmentID] = 0

        flow_balance_threshold = .25 # This is the threshold + or - from .5
        flow_ratio_threshold = 2 # Threshold from 0 
        v3b = {}
        for gridID in gridIDs:
            compartmentID = grid_comp[gridID]
            if (.5-flow_balance_threshold) < flow_balance[compartmentID] < (.5+flow_balance_threshold) and flow_ratio[compartmentID] > flow_ratio_threshold:
                v3b[gridID] = 0 #High
            else: 
                v3b[gridID] = 1 #None


        #Lookup table for swamp SI3, columns are High Flow Exchange vs Low Flow Exchange
        swamp_SI3_lookup = [[.65,.1], #No Flooding
                            [.9,.4], #Temp
                            [1,.5], #Seasonal
                            [.75,.25], #Semi-perm
                            [.65,.1]] # Perm
                        

        for gridID in gridIDs:
            S3[gridID] = swamp_SI3_lookup[int(v3a[gridID])][int(v3b[gridID])]
            

        ##############################################
        #V4: Mean high salinity during growing season#
        ##############################################
        print('Calculating Swamp V4: Mean high salinity during growing season')
        v4 = growing_season_salinity
        S4 = {}
        for gridID in gridIDs:
            if 0 <= v4[gridID] <= 1.5:
                S4[gridID] = 1.0
            elif 1.5 < v4[gridID] < 3.5:
                S4[gridID] = (-0.45 * v4[gridID]) + 1.675
            elif v4[gridID] >= 3.5:
                S4[gridID] = 0.1

        print('Outputting Swamp WVA')
        variables['SF'] = {'HSI': {},
                    'SI1': {},
                    'SI2': {},
                    'SI3': {},
                    'SI4': {},
        }

        for gridID in gridIDs:
            
            WVA_Swamp = (S1[gridID] ** 3 * S2[gridID] ** 2.5 * S3[gridID] ** 3 * S4[gridID] ** 1.5) ** (1 / 10)

            writestring = '%d,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f\n' % \
            (gridID, WVA_Swamp, v1a[gridID],v1b[gridID],v1c[gridID],v2[gridID], v3a[gridID], v3b[gridID], v4[gridID], 
            S1[gridID], S2[gridID], S3[gridID], S4[gridID])
            Swamp.write(writestring)

            variables['SF']['HSI'][gridID] = WVA_Swamp
            variables['SF']['SI1'][gridID] = S1[gridID]
            variables['SF']['SI2'][gridID] = S2[gridID]
            variables['SF']['SI3'][gridID] = S3[gridID]
            variables['SF']['SI4'][gridID] = S4[gridID]


        #change this for use in BLH Calculation
        v4a = v3a
        v4b = v3b

        # delete temporary variables so they do not accidentally get used in other HSIs
        del (v1a, v1b, v1c, v4, S1, S3, S4,v3a,v3b)

    ########################################
    ##      Bottomland Hardwoods WVA      ##
    ########################################
    print('Calculating Bottomland Hardwoods WVA')

    # WVA for Bottomland Hardwoods

    WVAcsv = r'%sBLH.csv' % csv_outprefix
    WVAasc = r'%sBLH.asc' % asc_outprefix

    with open(WVAcsv, 'w') as BLH:

        headerstring = 'GridID,WVA_BLH,v1a,v1b,v2,v3a,v3b,v4a,v4b,v5,v6,v7,SI1,SI2,SI3,SI4,SI5,SI6,SI7\n'
        BLH.write(headerstring)

        ##############################
        #V1: Tree Species Association#
        ##############################
        print('Calculating BLH V1: Tree Species Association')
        S1 = {}
        v1a = {} #% of mast trees
        v1b = {} #% hard mast
        for gridID in gridIDs:
            
            pct_softmast = ULAMdict[gridID]+NYAQ2dict[gridID]+TADI2dict[gridID]
            pct_nonmast = SANIdict[gridID]
            pct_hardmast = QULEdict[gridID]+QUNIdict[gridID]+QUVIdict[gridID]+QULA3dict[gridID]+QUTEdict[gridID]
            pct_trees = pct_softmast+pct_hardmast+pct_nonmast
            if pct_trees == 0:
                pct_softmast = 0
                v1b[gridID]=0
            else:
                pct_softmast = pct_softmast/pct_trees
                v1b[gridID] = pct_hardmast/pct_trees
            v1a[gridID] = pct_hardmast + pct_softmast
            
            if v1a[gridID] <= .25:
                S1[gridID] = .2 #class 1
            if .25 < v1a[gridID] <= .50:
                if v1b[gridID] < .10:
                    S1[gridID] = .4 #class 2
                else:
                    S1[gridID] = .6 #class 3
            if v1a[gridID] > .50:
                if v1b[gridID] < .20:
                    S1[gridID] = .8 #class 4
                else:
                    S1[gridID] = 1 #class 5


        ####################
        #V2: Stand Maturity#
        ####################
        #v2 = v2 #Value is defined in Swamp SI caclulations
        #S2 = S2


        ###########################
        #V3: Understory / Midstory#
        ###########################
        print('Calculating BLH V3: Understory / Midstory')
        S3 = {}
        v3a = {}
        v3b = {}
        for gridID in gridIDs:
            overstory_cover = treecover_dict[gridID]/(1-uplanddict[gridID]-water2dict[gridID])
            if overstory_cover <.2:
                midstory_ratio = .8
            elif overstory_cover <= .8:
                midstory_ratio = 1 - overstory_cover
            else:
                midstory_ratio = .2

            v3a[gridID]=(ELBA2dict[gridID]+PAHE2dict[gridID]+COESdict[gridID]+MOCE2dict[gridID]+SALA2dict[gridID]
                            + ZIMIdict[gridID]+CLMA10dict[gridID]+ELCEdict[gridID]+IVFRdict[gridID]+PAVAdict[gridID]+PHAU7dict[gridID]
                            +POPU5dict[gridID]+SALAdict[gridID]+SCCA11dict[gridID]+TYDOdict[gridID]+SCAM6dict[gridID]+SPCYdict[gridID]
                            +SCRO5dict[gridID]+SPPAdict[gridID]+DISPdict[gridID]+JUROdict[gridID]+SPALdict[gridID]+BAHABIdict[gridID]
                            +DISPBIdict[gridID]+PAAM2dict[gridID]+SOSEdict[gridID]+SPPABIdict[gridID]+SPVI3dict[gridID]+STHE9dict[gridID]
                            +UNPAdict[gridID])
            v3b[gridID]=(((ULAMdict[gridID]+NYAQ2dict[gridID]+TADI2dict[gridID]+SANIdict[gridID]
                        +QULEdict[gridID]+QUNIdict[gridID]+QUVIdict[gridID]+QULA3dict[gridID]+
                        QUTEdict[gridID])*midstory_ratio)+AVGEdict[gridID])
            #Understory
            if v3a[gridID] == 0:
                understory_SI = .1 #trying to save on memory by not keeping a dictionary of all these intermediate steps
            elif v3a[gridID] <= .3:
                understory_SI = (.03*100*v3a[gridID])+.1
            elif v3a[gridID] <= .6:
                understory_SI = 1
            else:
                understory_SI = (-.01*100*v3a[gridID])+1.6
            #Midstory
            if v3b[gridID] == 0:
                midstory_SI = .1
            elif v3b[gridID] <= .2:
                midstory_SI = (.045*100*v3b[gridID])+.1
            elif v3b[gridID] <= .5:
                midstory_SI = 1
            else:
                midstory_SI = (-.01*100*v3b[gridID])+1.5  
            S3[gridID] = (understory_SI + midstory_SI)/2

        ###############
        #V4: Hydrology#
        ###############
        print('Calculating BLH V4: Hydrology')
        
        blh_SI4_lookup =[[.65,.1], #No Flooding
                        [1,.5], #Temp
                        [.85,.4], #Seasonal
                        [.75,.25], #Semi-perm
                        [.65,.1]] # Perm

        S4 = {}
        for gridID in gridIDs:
            S4[gridID] = blh_SI4_lookup[int(v4a[gridID])][int(v4b[gridID])]


        ######################################
        #v5: Size of Contiguous Forested Area# - HOLD CONSTANT
        ######################################
        v5 = hold_constant
        S5 = hold_constant

        ############################################################
        #V6: Suitability and Traversability of Surrounding Land Use# - HOLD CONSTANT
        ############################################################
        v6 = hold_constant
        S6 = hold_constant

        #################
        #V7: Disturbance# - Hold Constant
        #################
        v7 = hold_constant
        S7 = hold_constant

        print('Outputting BLH Results')

        variables['BF'] = {'HSI': {},
                            'SI1': {},
                            'SI2': {},
                            'SI3': {},
                            'SI4': {},
                            'SI5': {},
                            'SI6': {},
                            'SI7': {},
        }

        for gridID in gridIDs:
            
            WVA_BLH = (((S1[gridID]**4)*(S2[gridID]**4)*(S3[gridID]**2)*(S4[gridID]**2)*S5[gridID]*S6[gridID]*S7[gridID])**(1/15))

            writestring = '%d,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f,%.8f\n' % ( gridID,WVA_BLH,v1a[gridID],v1b[gridID],v2[gridID],v3a[gridID],v3b[gridID],v4a[gridID],v4b[gridID],v5[gridID],v6[gridID],v7[gridID],S1[gridID],
            S2[gridID],S3[gridID],S4[gridID],S5[gridID],S6[gridID],S7[gridID])
            BLH.write(writestring)



            variables['BF']['HSI'][gridID] = WVA_Swamp
            variables['BF']['SI1'][gridID] = S1[gridID]
            variables['BF']['SI2'][gridID] = S2[gridID]
            variables['BF']['SI3'][gridID] = S3[gridID]
            variables['BF']['SI4'][gridID] = S4[gridID]
            variables['BF']['SI5'][gridID] = S5[gridID]
            variables['BF']['SI6'][gridID] = S6[gridID]
            variables['BF']['SI7'][gridID] = S7[gridID]
        
        # delete temporary variables so they do not accidentally get used in other HSIs
        del (v1a, v1b, v2, v3a, v3b, v4a,v4b, v5, v6, v7, S1, S2, S3, S4, S5, S6, S7)


    #This output is meant to be used for the HSI and SI sums to be used on line or difference plots.
    table = ["GridID"]
    all_vars = []
    weighted_score = {}
    for model in models:
        weighted_score[model] = {}
        table.append(f"pL_{model}")
        all_vars.append(pct_land_cover[model])
        for var in variables[model].keys():
            table.append(f"{model}_{var}")
            weighted_score[model][var] = {key: value * pct_land_cover[model][key] for key, value in variables[model][var].items()}
            all_vars.append(weighted_score[model][var])

    headerstring = ",".join(table)+"\n"
    array  = [[key]+[d[key] for d in all_vars] for key in gridIDs]
    
    WVA_combined_csv = '%sScaled_Output.csv' % csv_outprefix
    with open(WVA_combined_csv, 'w') as Combinedcsv:
        Combinedcsv.write(headerstring)
        for row in array:
            Combinedcsv.write(",".join(map(str,row)) + "\n")

    # This is the output that is meant to be used for mapping and box plots, as the values in the cells is representative of the actual SI or HSI scores calaculated
    
    threshold = 0.1  # Defined threshold, if the pct cover of a given vairable is above this threshold present here, it is included int he count
    table = ["GridID"]
    all_vars = []
    filtered_values = {}

    for model in models:
        filtered_values[model] = {}
        for var in variables[model].keys():
            table.append(f"{model}_{var}")
            filtered_values[model][var] = {
                key: value if pct_land_cover[model][key] >= threshold else 0
                for key, value in variables[model][var].items()
            }
            all_vars.append(filtered_values[model][var])

    headerstring = ",".join(table) + "\n"
    array = [[key] + [d[key] for d in all_vars] for key in gridIDs]

    WVA_combined_csv = f"{csv_outprefix}Filtered_Output.csv"
    with open(WVA_combined_csv, 'w') as Combinedcsv:
        Combinedcsv.write(headerstring)
        for row in array:
            Combinedcsv.write(",".join(map(str, row)) + "\n")

    #Water Outputs Scaled by Near Coverage:
    dominant_coverage = {}
    scaled_hsi = {}
    for gridID in gridIDs:
        if all(pct_land_cover[model][gridID] == 0 for model in models):
            dominant_coverage[gridID] = "No Near Coverage"
            scaled_hsi[gridID] = 0
        else:
            max_model = max(pct_land_cover, key=lambda model: pct_land_cover[model][gridID])
            dominant_coverage[gridID] = max_model
            if dominant_coverage[gridID] in ['SF','BF']:
                hsi = 0
            else:
                hsi = variables[dominant_coverage[gridID]]["HSI_W"][gridID]
            scaled_hsi[gridID] = water2dict[gridID] * hsi
    
    water1_csv = f"{csv_outprefix}Scaled_Water_by_Coverage.csv"
    with open(water1_csv, "w") as water1:
        water1.write("GridID,Dominant_Coverage,Water_Area,Scaled_HSI\n")
        for gridID in gridIDs:
            water1.write(f"{gridID},{dominant_coverage[gridID]},{water2dict[gridID]},{scaled_hsi[gridID]}\n")


    #HUS

    veg_area_acres = (480*480/4046.856422) #480 m x 480m / (m/acre)
    hu = {}
    for model in models:
        hu[model] = {}
    for gridID in gridIDs:
        for model in models:
            if model == "BF" or model == "SF":
                hu[model][gridID] = weighted_score[model]['HSI'][gridID]*veg_area_acres
            if model == "FM" or model == "IM":
                if dominant_coverage[gridID] == model:
                    water_hsi = scaled_hsi[gridID]
                else:
                    water_hsi = 0
                hu[model][gridID] = (((weighted_score[model]['HSI'][gridID]*2.1)+water_hsi)/3.1)*veg_area_acres
            if model == "BM":
                if dominant_coverage[gridID] == model:
                    water_hsi = scaled_hsi[gridID]
                else:
                    water_hsi = 0
                hu[model][gridID] = (((weighted_score[model]['HSI'][gridID]*2.6)+water_hsi)/3.6)*veg_area_acres
            if model == "SM":
                if dominant_coverage[gridID] == model:
                    water_hsi = scaled_hsi[gridID]
                else:
                    water_hsi = 0
                hu[model][gridID] = (((weighted_score[model]['HSI'][gridID]*3.5)+water_hsi)/4.5)*veg_area_acres

    aahu_csv = f"{csv_outprefix}HUS.csv"
    
    table = ["GridID"] + models
    array = [[gridID] + [hu[model].get(gridID, 0) for model in models] for gridID in gridIDs]

    with open(aahu_csv, "w") as f:
        f.write(",".join(table) + "\n")
        for row in array:
            f.write(",".join(map(str, row)) + "\n")
            