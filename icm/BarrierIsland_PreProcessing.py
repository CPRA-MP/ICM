#ICM imports
import ICM_Settings as icm

#Python imports
import numpy as np
import os


def BIyearlyVars():
    ###########################################################
    ###       Barrier Island Tidal Inlet (BITI) Model       ###
    ###########################################################

    os.chdir(bimode_dir)

    # read in mean water levels for each barrier island model domain
    EH_MHW = dict((EH_comp_out[n][0],EH_comp_out[n][2]) for n in range(0,len(EH_comp_out)))     # create dictionary where key is compartment ID, values is mean water (column 3 of Ecohydro output)
    
    # create liste of ICM compartments that will be used as MHW for each BI group (west-to-east)
    IslandMHWCompLists = [494,482,316,314,306,303]
    
    # read mean water level for each BI region
    BIMODEmhw = np.zeros(shape=len(IslandMHWCompLists))    # Initialize MHW array to zero - will write over previous year's array
    for n in range(0,len(IslandMHWCompLists)):
        comp = IslandMHWCompLists[n]
        BIMODEmhw[n] = EH_MHW[comp]

    # calculate one average water level for all BI regions to be used for BITI depth calculations
    BITI_MWL = BIMODEmhw.mean()

    # create dictionary where key is compartment ID, value is tidal prism (Column 14 of Ecohydro output)
    EH_prisms = dict((EH_comp_out[n][0],EH_comp_out[n][13]) for n in range(0,len(EH_comp_out)))
    
    # no longer need NumPy array of compartment output summary data - delete until next year
    del(EH_comp_out)
    
    
    #Barrier Island Tidal Inlet (BITI) tidal prism values
    #Get the tidal prism values for each compartment from the Hydro output
    BITI_Terrebonne_prism = [EH_prisms.get(comp) for comp in BITI_Terrebonne_comp]
    BITI_Barataria_prism = [EH_prisms.get(comp) for comp in BITI_Barataria_comp]
    BITI_Pontchartrain_prism = [EH_prisms.get(comp) for comp in BITI_Pontchartrain_comp]


    # Calculate the effective tidal prism and cross-sectional area for each link in each basin
    # effective tidal prism = sum(tidal prism * partitioning coefficient) [summed across all compartments in the basin]
    # cross-sectional area = kappa *((effective tidal prism)^alpha)
    BITI_Terrebonne_inlet_area = np.zeros(shape=len(BITI_Terrebonne_link))
    for n in range(0,len(BITI_Terrebonne_link)):
        BITI_Terrebonne_effective_prism = sum((BITI_Terrebonne_partition[:,n])*BITI_Terrebonne_prism)
        BITI_Terrebonne_inlet_area[n] = np.multiply(kappa, np.power(BITI_Terrebonne_effective_prism,alpha))*BITI_Terrebonne_BWF

    BITI_Barataria_inlet_area = np.zeros(shape=len(BITI_Barataria_link))
    for n in range(0,len(BITI_Barataria_link)):
        BITI_Barataria_effective_prism = sum((BITI_Barataria_partition[:,n])*BITI_Barataria_prism)
        BITI_Barataria_inlet_area[n] = np.multiply(kappa, np.power(BITI_Barataria_effective_prism,alpha))*BITI_Barataria_BWF

    BITI_Pontchartrain_inlet_area = np.zeros(shape=len(BITI_Pontchartrain_link))
    for n in range(0,len(BITI_Pontchartrain_link)):
        BITI_Pontchartrain_effective_prism = sum((BITI_Pontchartrain_partition[:,n])*BITI_Pontchartrain_prism)
        BITI_Pontchartrain_inlet_area[n] = np.multiply(kappa, np.power(BITI_Pontchartrain_effective_prism,alpha))*BITI_Pontchartrain_BWF

    BITI_inlet_areas = [BITI_Terrebonne_inlet_area,BITI_Barataria_inlet_area,BITI_Pontchartrain_inlet_area]

    # BITI depth for each link in each basin
    # Depth = sqrt(inlet area*(depth to width ratio))
    BITI_Terrebonne_inlet_depth = np.power(np.multiply(BITI_Terrebonne_inlet_area,BITI_Terrebonne_dwr),0.5)
    BITI_Barataria_inlet_depth = np.power(np.multiply(BITI_Barataria_inlet_area,BITI_Barataria_dwr),0.5)
    BITI_Pontchartrain_inlet_depth = np.power(np.multiply(BITI_Pontchartrain_inlet_area,BITI_Pontchartrain_dwr),0.5)

    BITI_inlet_depth = [BITI_Terrebonne_inlet_depth,BITI_Barataria_inlet_depth,BITI_Pontchartrain_inlet_depth]

    # BITI width for each link in each basin
    # Width = sqrt(inlet area/(depth to width ratio))
    BITI_Terrebonne_inlet_width = np.power(np.divide(BITI_Terrebonne_inlet_area,BITI_Terrebonne_dwr),0.5)
    BITI_Barataria_inlet_width = np.power(np.divide(BITI_Barataria_inlet_area,BITI_Barataria_dwr),0.5)
    BITI_Pontchartrain_inlet_width = np.power(np.divide(BITI_Pontchartrain_inlet_area,BITI_Pontchartrain_dwr),0.5)

    BITI_inlet_width = [BITI_Terrebonne_inlet_width,BITI_Barataria_inlet_width,BITI_Pontchartrain_inlet_width]

    # BITI dimensions
    # Create a dictionary where key is link ID, first value is inlet depth, second value is inlet width
    # This dictionary can be used to update the link attributes. All inlet links are Type 1 links.
    BITI_inlet_dimensions = {}
    for n in range(0,len(BITI_Links)):
        for k in range(0,len(BITI_Links[n])):
            BITI_inlet_dimensions[BITI_Links[n][k]] = ([BITI_inlet_depth[n][k],BITI_inlet_width[n][k]])
    
    # BITI dimensions for inlet links with jetties constraining inlet width
    # do not allow inlets that are currently jettied to change in width dimension - all areal adjustments for these two links must occur in the depth dimension
    CamPassLinkID = 529
    CamPassWidth = 900          # intial Caminada Pass width
    BarPassLinkID = 532
    BarPassWidth = 700          # intial Barataria Pass width    
    
    BITI_inlet_dimensions[CamPassLinkID][0] = (BITI_inlet_dimensions[CamPassLinkID][0] *  BITI_inlet_dimensions[CamPassLinkID][1])/CamPassWidth
    BITI_inlet_dimensions[CamPassLinkID][1] = CamPassWidth 

    BITI_inlet_dimensions[BarPassLinkID][0] = (BITI_inlet_dimensions[BarPassLinkID][0] *  BITI_inlet_dimensions[BarPassLinkID][1])/BarPassWidth
    BITI_inlet_dimensions[BarPassLinkID][1] = BarPassWidth 

        # set upper and lower limits on how much the tidal inlet dimensions can change as a ratio of the initial dimensions
    # currently, the limits are (arbitrarily) set to limit expansion to twice the original width and/or depth and limit the contraction to 1/4th the original width and/or depth
    for BITI_Link_ID in BITI_inlet_dimensions.keys():

        orig_depth = BITI_inlet_dimensions_init[BITI_Link_ID][0]
        BITI_inlet_depth_min = 0.25*orig_depth
        BITI_inlet_depth_max = 1.5*orig_depth           # based on analysis by BITI team, when basin is completely open water, maximum increase in inlet dimensions was 145% increase from initial dimensions
        new_depth = min( max( BITI_inlet_dimensions[BITI_Link_ID][0], BITI_inlet_depth_min ), BITI_inlet_depth_max)

        orig_width = BITI_inlet_dimensions_init[BITI_Link_ID][1]  
        BITI_inlet_width_min = 0.25*orig_width
        BITI_inlet_width_max = 1.5*orig_width           # based on analysis by BITI team, when basin is completely open water, maximum increase in inlet dimensions was 145% increase from initial dimensions
        new_width = min( max( BITI_inlet_dimensions[BITI_Link_ID][1], BITI_inlet_width_min ), BITI_inlet_width_max)


        EHLinks_index = int(BITI_Link_ID) - 1                                # EHLinks is a numpy 0-based index, not dictionary with lookup
        EHLinksArray[EHLinks_index,8] = BITI_MWL - new_depth                ## invert elevation is attribute1 for Type 1 links (column 8 in links array)
        EHLinksArray[EHLinks_index,11] = new_width                          ## channel width is attribute4 for Type 1 links (column 11 in links array)

