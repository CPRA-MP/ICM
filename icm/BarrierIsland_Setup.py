#Python imports
import numpy as np
import os
import pandas

#ICM imports
import ICM_Settings as icm


def icm_barrierisland_setup(
        ecohydro_dir,inputStartYear,endyear,bimode_folders,
        bimode_dir,BITIconfig,EHLinksArrayOrig):
    
    # change back to Hydro directory
    os.chdir(ecohydro_dir)

    print(' Configuring sea level rise rate files for ICM-BIDEM.')

    # 1st column in TideData is YYYYMMDD HH:MM
    # 4th column in TideData is Amerada Pass, LA
    tide_file = os.path.normpath(r'%s/TideData.csv' % ecohydro_dir)
    tide_data = np.genfromtxt(tide_file,skip_header=1,delimiter=',',dtype='str')

    annual_mean_mm = []
    for year in range(inputStartYear,endyear):
        n = 0
        annual_total = 0
        for r in tide_data:
            if int(r[0][0:4]) == year:                  
                annual_total += float(r[3])             
                n+=1                                    
        # 8760 hours or 8784 hours if leap year
        # Take the mean of the hourly data and convert from m to mm
        annual_mean_mm.append((annual_total/n)*1000)    
    yrs4polyfit = range(inputStartYear,endyear)
    
    # Fit a quadratic to the annual mean data
    p = np.polyfit(yrs4polyfit, np.asarray(annual_mean_mm),2) 
    ESLR_rate_mmyr = []
    for year in range(inputStartYear,endyear):

        # Take the first derivative and plug in years to get the rate
        ESLR_rate_mmyr.append((p[0]*2*year)+(p[1]))

    for fol in bimode_folders:
        ESLR_out_file = r'%s/%s/input/SLR_record4modulation.txt' %(bimode_dir,fol)
        with open(ESLR_out_file, mode='w') as outf:
            i = 0
            for year in range(inputStartYear,endyear):
                outf.write("%d %0.2f\n" % (year,ESLR_rate_mmyr[i]))
                i += 1

    print(' Configuring tidal inlet settings for ICM-BITI.')
    # Barrier Island Tidal Inlet (BITI) input file
    # The input file only needs to be read once
    # It contains the comp IDs, link IDs, depth to width ratios, partition coefficients, and basin-wide factors.
    # The Pandas.iloc pointer is used below and must be updated if input file changes structure

    BITI_input_filename = os.path.normpath(r'%s/%s' % (bimode_dir,BITIconfig) )

    BITI_Terrebonne_setup = pandas.read_excel(BITI_input_filename, 'Terrebonne',index_col=None)
    BITI_Barataria_setup = pandas.read_excel(BITI_input_filename, 'Barataria',index_col=None)
    BITI_Pontchartrain_setup = pandas.read_excel(BITI_input_filename, 'Pontchartrain',index_col=None)

    # Barrier Island Tidal Inlet (BITI) compartment IDs
    # These are the compartments that make up each basin
    BITI_Terrebonne_comp = list( BITI_Terrebonne_setup.iloc[3::,0] )
    BITI_Barataria_comp = list( BITI_Barataria_setup.iloc[3::,0] )
    BITI_Pontchartrain_comp = list( BITI_Pontchartrain_setup.iloc[3::,0] )

    # Barrier Island Tidal Inlet (BITI) link IDs
    # These are the links that respresent the tidal inlets in each basin
    BITI_Terrebonne_link = list(BITI_Terrebonne_setup.iloc[0,1:-2])
    BITI_Barataria_link = list(BITI_Barataria_setup.iloc[0,1:-2])
    BITI_Pontchartrain_link = list(BITI_Pontchartrain_setup.iloc[0,1:-2])

    BITI_Links = [BITI_Terrebonne_link,BITI_Barataria_link,BITI_Pontchartrain_link]

    # Barrier Island Tidal Inlet (BITI) partition coefficients
    # Each basin has it's own array of partition coefficients with size m by n,
    # where m = number of compartments in the basin and n = the number of links in the basin
    BITI_Terrebonne_partition = np.asarray(BITI_Terrebonne_setup)[3::,1:-2]
    BITI_Barataria_partition = np.asarray(BITI_Barataria_setup)[3::,1:-2]
    BITI_Pontchartrain_partition = np.asarray(BITI_Pontchartrain_setup)[3::,1:-2]

    # Barrier Island Tidal Inlet (BITI) depth to width ratio (dwr) for each link in each basin (Depth/Width)
    BITI_Terrebonne_dwr = list(BITI_Terrebonne_setup.iloc[1,1:-2])
    BITI_Barataria_dwr = list(BITI_Barataria_setup.iloc[1,1:-2])
    BITI_Pontchartrain_dwr = list(BITI_Pontchartrain_setup.iloc[1,1:-2])

    # Barrier Island Tidal Inlet (BITI) basin-wide factor (BWF) for each basin
    BITI_Terrebonne_BWF = float(BITI_Terrebonne_setup.iloc[1,-1])
    BITI_Barataria_BWF = float(BITI_Barataria_setup.iloc[1,-1])
    BITI_Pontchartrain_BWF = float(BITI_Pontchartrain_setup.iloc[1,-1])

    # BITI effective tidal prism and inlet area
    # kappa and alpha are the Gulf of Mexico constants for unjettied systems (units = metric)
    kappa = 6.99e-4
    alpha = 0.86

    
    # BITI Links - initial channel dimensions
    # Create a dictionary where key is link ID, first value is inlet depth, second value is inlet width
    BITI_inlet_dimensions_init = {}
    for n in range(0,len(BITI_Links)):
        for k in range(0,len(BITI_Links[n])):
            BITI_Link_ID = BITI_Links[n][k]
            
            ## EHLinks is a numpy 0-based index, not dictionary with lookup
            EHLinks_index = int(BITI_Link_ID) - 1
            
            # Invert elevation is attribute1 for Type 1 links (column 8 in links array) 
            # Subtract invert from 0.3 meters to convert from invert to link depth (assuming that initial MWL in GoM is +0.3 m)
            orig_depth = 0.3 - EHLinksArrayOrig[EHLinks_index,8]

            # Channel width is attributed for Type 1 links (column 11 in links array)  
            orig_width = EHLinksArrayOrig[EHLinks_index,11]
            BITI_inlet_dimensions_init[BITI_Link_ID] = (orig_depth,orig_width)
    
    return (BITI_Terrebonne_comp, BITI_Barataria_comp, BITI_Pontchartrain_comp, BITI_Terrebonne_link,
            BITI_Terrebonne_partition, kappa, alpha, BITI_Terrebonne_BWF, BITI_Barataria_link, 
            BITI_Barataria_partition, BITI_Barataria_BWF, BITI_Pontchartrain_link, BITI_Pontchartrain_partition, 
            BITI_Pontchartrain_BWF, BITI_Terrebonne_dwr, BITI_Barataria_dwr, BITI_Pontchartrain_dwr, 
            BITI_Links, BITI_inlet_dimensions_init)