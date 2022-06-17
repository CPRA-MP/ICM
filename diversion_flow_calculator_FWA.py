# -*- coding: utf-8 -*-
#"""
#Created on Thu Jan 28 11:46:45 2021
#@author: madelinel & ewhite12
#"""

# This script is designed to build daily flow timeseries of flow diversions off of the Mississippi River, including the distributary network in the Birdsfoot Delta.
# input/output flowrates are saved in cubic meters per second (cms), but all operational rules are defined in cubic feet per second (cfs)

#import numpy as np

#daily_input_file = r'MP2023_diversion_calculator.csv'
#daily_input_flow_column = [10]       # column number input file that has the data to be used as the upstream timeseries (note that Python uses a 0 index...so a value of 10 here is actually the 11th column in the input data
#daily_input_year_column = [0]

# read in Mississippi River @ Tarbert Landing (input data is in cms)
#MissTarb_cms = np.genfromtxt(daily_input_file,delimiter=',', dtype='float',skip_header=header_rows,usecols=daily_input_flow_column)
#MissTarb_cfs = MissTarb_cms / 0.3048**3      

# read in date timeseries
#dates_all = np.genfromtxt(daily_input_file,delimiter=',', dtype='string',skip_header=header_rows,usecols=daily_input_year_column)
#ndays = len(dates_all)
#yr0 = 2019      # this is the first year that will be used to determine what calendar year diversions are activated

### Using pandas ###

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

TribQ_in_file  = 'S07_G500_TribQ.csv'
TribQ_out_file = 'S07_G600_TribQ.csv'


# Set implementation year (elapsed) for each diversion
#          0 = implemented at the start of the model run (ICM year 0)
#          9 = diversion is implemented in year 9 of ICM run - which is year 7 of FWOA (FWOA year = ICM year + 2 spinup yeard)
#       9999 = diversion is not implemented at all 

implementation = {}
implementation['IAFT'] = 9999       # Increase Atchafalaya Flows to Terrebonne
implementation['AtRD'] = 9999       # Atchafalaya River Diversion
implementation['BLaF'] = 9999       # Bayou Lafourche Diversion (existing pump @ Bayou Lafourche - in FWOA) ASSUMED IN THE MODEL VIA THE OBSERVED FLOWRATES IN TribQ FOR BAYOU LAFOURCHE AT THIBODEAUX
implementation['FDWB'] = 9999       # Freshwater Delivery to Western Barataria (pump capacity increase to BLaF diversion)
implementation['UBaH'] = 9999       # Upper Barataria Hydrologic Restoration
implementation['UFWD'] = 9999       # Union Freshwater Diversion
implementation['WMPD'] = 9999       # West Maurepas Diversion
implementation['MSRM'] = 0          # Mississippi River Reintroduction in Maurepas Swamp
implementation['EdDI'] = 9999       # Edgard Diversion
implementation['Bonn'] = 0          # Bonnet Carre
implementation['MLBD'] = 9999       # Manchac Landbridge Diversion  # IMPLEMENTED VIA LINKS FOR ALTERNATIVE RUNS - DO NOT ACTIVATE IN THIS CODE
implementation['LaBr'] = 9999       # LaBranche Hydrological Restoration (not the same as LaBranche Diversion)
implementation['LaBD'] = 9999       # LaBranche Diversion           # IMPLEMENTED VIA LINKS FOR ALTERNATIVE RUNS - DO NOT ACTIVATE IN THIS CODE
implementation['DavP'] = 0          # Davis Pond
implementation['AmaD'] = 9999       # Ama Sediment Diversion
implementation['IHNC'] = 0          # Inner Harbor Navigational Canal
implementation['CWDI'] = 9999       # Central Wetlands Diversion
implementation['Caer'] = 0          # Caernarvon
implementation['UBrD'] = 9999       # Upper Breton Diversion
implementation['MBrD'] = 0          # Mid-Breton Sound Diversion
implementation['Naom'] = 0          # Naomi
implementation['MBaD'] = 0          # Mid-Barataria Diversion
implementation['WPLH'] = 0          # West Pointe a la Hache
implementation['LPlq'] = 9999       # Lower Plaquemines River Sediment Plan (yr2038)
implementation['LBaD'] = 9999       # Lower Barataria Diversion
implementation['LBrD'] = 9999       # Lower Breton Diversion



nTributaries = 35                   # number of riverine input timeseries included in TribQ, TribF, TribS, and QMult
nMissRiv_Diversions = 21            # number of Mississippi River diversion timeseries included in TribQ, TribF, TribS, and QMult
nBFD_Passes = 12                    # number of distributary passes timeseries in the BFD included in TribQ, TribF, TribS, and QMult
nAtchRiv_Diversions = 2             # number of Atchafalaya River diversion timeseries included in TribQ, TribF, TribS, and QMult

nTribs = nTributaries + nMissRiv_Diversions + nBFD_Passes + nAtchRiv_Diversions # total number of timeseries read in as tributary boundary conditions in TribQ

trib_cols   = range(0,nTributaries) # first 35 columns of TribQ.csv are tributary flows; diversions start in column 36
TribQ_in_date_col    = 67           # last column of input TribQ.csv is the date
MissRiv_col = 10                    # column 11 of TribQ.csv is the Miss. River @ Tarbert Landing data

TribQ_in    = np.genfromtxt(TribQ_in_file,delimiter=',',dtype=str,skip_header=1,usecols=trib_cols)
dates_all   = np.genfromtxt(TribQ_in_file,delimiter=',',dtype=str,skip_header=1,usecols=TribQ_in_date_col)


dates_all = [d.split()[1] for d in dates_all]

# read in Mississippi River @ Tarbert Landing (input data is in cms)
MissTarb_cms = [ float(q) for q in TribQ_in[:,[MissRiv_col]] ]
MissTarb_cfs = [ q/(0.3048**3.0) for q in MissTarb_cms ]

# read in date timeseries
ndays = len(dates_all)
yr0 = 2019
 
# build zero arrays for each diversion timeseries
Atch_cfs = np.zeros(ndays)      # Atchafalaya River
Atch_cms = np.zeros(ndays)      
Morg_cfs = np.zeros(ndays)      # Morganza Floodway
Morg_cms = np.zeros(ndays)
IAFT_cfs = np.zeros(ndays)      # Increase Atchafalaya Flows to Terrebonne
IAFT_cms = np.zeros(ndays)
AtRD_cfs = np.zeros(ndays)      # Atchafalaya River Diversion
AtRD_cms = np.zeros(ndays)
BLaF_cfs = np.zeros(ndays)      # Bayou Lafourche Diversion / Freshwater Delivery to Westeran Barataria / Upper Barataria Hydrologic Restoration
BLaF_cms = np.zeros(ndays)
UFWD_cfs = np.zeros(ndays)      # Union Freshwater Diversion
UFWD_cms = np.zeros(ndays)
WMPD_cfs = np.zeros(ndays)      # West Maurepas Sediment Diversion
WMPD_cms = np.zeros(ndays)
MSRM_cfs = np.zeros(ndays)      # Mississippi River Reintroduction in Maurepas Swamp
MSRM_cms = np.zeros(ndays)
EdDI_cfs = np.zeros(ndays)      # Edgard Diversion
EdDI_cms = np.zeros(ndays)
Bonn_cfs = np.zeros(ndays)      # Bonnet Carre
Bonn_cms = np.zeros(ndays)
MLBD_cfs = np.zeros(ndays)      # Manchac Landbridge Diversion (timeseries not used - implemented via links)
MLBD_cms = np.zeros(ndays)
LaBr_cfs = np.zeros(ndays)      # LaBranche Hydrological Restoration
LaBr_cms = np.zeros(ndays)
LaBD_cfs = np.zeros(ndays)      # LaBranche Diversion (timeseries not used - implemented via links)
LaBD_cms = np.zeros(ndays)
DavP_cfs = np.zeros(ndays)      # Davis Pond
DavP_cms = np.zeros(ndays)
AmaD_cfs = np.zeros(ndays)      # Ama Sediment Diversion
AmaD_cms = np.zeros(ndays)
IHNC_cfs = np.zeros(ndays)      # Inner Harbor Navigational Canal
IHNC_cms = np.zeros(ndays) 
CWDI_cfs = np.zeros(ndays)      # Central Wetlands Diversion
CWDI_cms = np.zeros(ndays)
Caer_cfs = np.zeros(ndays)      # Caernarvon
Caer_cms = np.zeros(ndays)
UBrD_cfs = np.zeros(ndays)      # Upper Breton Diversion
UBrD_cms = np.zeros(ndays)  
MBrD_cfs = np.zeros(ndays)      # Mid-Breton Sound Diversion
MBrD_cms = np.zeros(ndays)
Naom_cfs = np.zeros(ndays)      # Naomi
Naom_cms = np.zeros(ndays)
MBaD_cfs = np.zeros(ndays)      # Mid-Barataria Diversion
MBaD_cms = np.zeros(ndays) 
WPLH_cfs = np.zeros(ndays)      # West Point a la Hache
WPLH_cms = np.zeros(ndays) 
#LPlq_cfs = np.zeros(ndays)      # Lower Plaquemines River Sediment Plan (timeseries not used - added as additional flow to WPLH timeseries)
#LPlq_cms = np.zeros(ndays) 
LBaD_cfs = np.zeros(ndays)      # Lower Barataria Diversion
LBaD_cms = np.zeros(ndays) 
LBrD_cfs = np.zeros(ndays)      # Lower Breton Diversion
LBrD_cms = np.zeros(ndays) 

# build zero arrays for each Mississippi River Distributary Pass
MGPS_cfs = np.zeros(ndays)      # Mardi Gras Pass
MGPS_cms = np.zeros(ndays)  
Bohe_cfs = np.zeros(ndays)      # Bohemia
Bohe_cms = np.zeros(ndays) 
Ostr_cfs = np.zeros(ndays)      # Ostrica
Ostr_cms = np.zeros(ndays)  
FStP_cfs = np.zeros(ndays)      # Ft. St. Philip 
FStP_cms = np.zeros(ndays)
Bapt_cfs = np.zeros(ndays)      # Baptiste Collette
Bapt_cms = np.zeros(ndays) 
GrPa_cfs = np.zeros(ndays)      # Grand Pass
GrPa_cms = np.zeros(ndays) 
WBay_cfs = np.zeros(ndays)      # West Bay
WBay_cms = np.zeros(ndays) 
SCut_cfs = np.zeros(ndays)      # SmallCuts
SCut_cms = np.zeros(ndays) 
CGap_cfs = np.zeros(ndays)      # Cubit's Gap
CGap_cms = np.zeros(ndays) 
SWPS_cfs = np.zeros(ndays)      # SW Pass Ratings Curve
SWPS_cms = np.zeros(ndays) 
SPas_cfs = np.zeros(ndays)      # S Pass
SPas_cms = np.zeros(ndays)  
PLou_cfs = np.zeros(ndays)      # Pass a Loutre
PLou_cms = np.zeros(ndays)  
SWPR_cfs = np.zeros(ndays)      # SW Pass Residual
SWPR_cms = np.zeros(ndays)  

for d in range(0,ndays):
    
    date = dates_all[d]
    yr = int(date[0:4])                                                   # this will work if date is formatted as YYYYMMDD, or YYYY-MM-DD, etc.
    month = int(date[4:6])                                                # this will work if date is formatted as YYYYMMDD

    # month, yr = int(date.split('/')[0]), int(date.split('/')[2])        # this will work if date is formatted as MM/DD/YYYY
    # year = date.split('-')[2]                                          # this will work if date is formatted as MM-DD-YYYY
    
    Qresidual   = MissTarb_cfs[d]       # this residual flow is the flow in the Mississippi River that is continuously updated as flows are diverted out of the river
    
    ##########################################
    ###   Atchafalaya River @ Simmesport   ###
    ##########################################
    # input dataset is Mississippi River flow at Tarbert Landing
    # Tarbert Landing is located downstream of the Old River Control Structure
    # Assume 70/30 flow split at Old River Control Structure (river mile 316)
    # 70% of Mississippi River flow is kept in main channel (this is the observed discharge at Tarbert Landing)
    # 30% of Mississippi River flow is diverted into Atchafalaya River
    
    Q_ORCS = MissTarb_cfs[d]/0.7
    Qdiv = Q_ORCS*0.3
    
    Atch_cfs[d] = Qdiv
    Atch_cms[d] = Qdiv*(0.3048**3)
        
    Q_Atch_Simm = Qdiv
        
    ##############################
    ###   Morganza Floodway    ###
    ##############################
    # river mile 280
    # not active, set to zero (this is redundant since Morg_cfs is already set as a zero array above)
    
    Qdiv = 0
    Morg_cfs[d] = Qdiv
    Morg_cms[d] = Qdiv*(0.3048**3)
    
    #####################################################
    ###   Atchafalaya River at Morgan City (rating)   ###
    #####################################################
    
    Q_Atch_MorganCity = 0.70*Q_Atch_Simm - 42040.0      # rating curve developed from G500 simulation by Moffat & Nichol
    Qresidual_Atch = Q_Atch_MorganCity
    
    ###################################################
    ###   Increase Atchafalaya Flows to Terrebonne  ###
    ###################################################
    # location at GIWW
    # rating curve needs to be a function of Atchafalaya River @ Simmesport since it is calculated here from the flows directly downstream of Old River Control Structure
    # MP2023: project 139
    #    Dredging of the Gulf Intracoastal Waterway (GIWW) and construction of a bypass structure at the Bayou Boeuf Lock from the Atchafalaya River 
    #    to Terrebonne marshes allowing peak flows of approximately 20,000 cfs 
    #
    # Rating curve for TE-110 30% design used a stage rating curve at Morgan City
    # Converting the stage curve to a discharge rating curve resulted in:
    #       diversion (cfs) = 0.14*Q_MorganCity(cfs) - 1,880
    #
    # the diversion is deactivated during the spring flood,
    # which corresponds to a flow threshold of 250,000 cfs at Morgan City (417,000 cfs at Simmesport)

    impl_yr = implementation['IAFT']
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:   
        if Q_Atch_MorganCity >= 250000:
            Qdiv = 0
        else:
            Qdiv = max(0,min(0.14*Q_Atch_MorganCity-1880.0, 30000))
            
    IAFT_cfs[d] = Qdiv
    IAFT_cms[d] = Qdiv*(0.3048**3)
    Qresidual_Atch -= Qdiv
    
    
    ########################################
    ###   Atchafalaya River Diversion    ###
    ########################################
    # location south of GIWW 
    # rating curve needs to be a function of Atchafalaya River @ Simmesport since it is calculated here from the flows directly downstream of Old River Control Structure
    # MP2023: project 108
    #    30,000 cfs capacity (modeled at 26% of the Atchafalaya River flow upstream of the confluence with Bayou Shaffer)
    
    impl_yr = implementation['AtRD']
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:   
        if Qresidual_Atch <= 0:
            Qdiv = 0
        else:
            Qdiv = min(0.26*Qresidual_Atch, 30000)
            
    AtRD_cfs[d] = Qdiv
    AtRD_cms[d] = Qdiv*(0.3048**3)
    Qresidual_Atch -= Qdiv

    
    #####################################################
    ###          Bayou Lafourche Diversion            ###
    ###  & Freshwater Delivery to Western Barataria   ###
    ###  &  Upper Barataria Hydrologic Restoration    ###
    #####################################################
    # river mile 176
    # current condition is 500 cfs but an additional 1000 cfs pump is in the permitting stage as of 4/27/2021
    # Constant diversion flow of 1,500 cfs
    impl_yr  = implementation['BLaF']
    impl_yr2 = implementation['FDWB']
    impl_yr3 = implementation['UBaH']
    
    # Bayou Lafourche Diversion (existing pump station - in FWOA)
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:   
        if Qresidual >= 1500:
            Qdiv = 1500
        else:
            Qdiv = Qresidual
    
    # Freshwater Delivery to Western Barataria
    # MP2023: project 322
    # add additional 500 cfs capacity to Bayou Lafourche pump
    if yr < yr0 + impl_yr2:
        Qdiv += 0
    else:   
        if Qresidual >= 500:
            Qdiv += 500
        else:
            Qdiv += Qresidual

    # Upper Barataria Hydrologic Restoration
    # MP2023: project 324
    #  Construction of a 750 cfs pump/siphon structure along Bayou Lafourche to supply freshwater into the marshes, bayous, and lakes of the Upper Barataria Sub-Basin
    # pump 750 cfs into Bayou Lafourche to be routed down BLaF and eventually eastward into Upper Barataria
    # add this diversion flow to the pre-existing Bayou Lafourche flow calculated above
    if yr < yr0 + impl_yr3:
        Qdiv += 0
    else:   
        if Qresidual >= 750:
            Qdiv += 750
        else:
            Qdiv += Qresidual

    # update Bayou LaFourche array with diverted volumes from all possible projects        
    BLaF_cfs[d] = Qdiv
    BLaF_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv

    
    #######################################
    ###   Union Freshwater Diversion    ###
    #######################################
    # river mile 169
    # No diversion flow below 200,000 or above 600,000, Diversion flow of 25,000 between 400,000 and 600,000, Else, diversion flow = 0.125x-25000
    # MP2023: project 244
    #     modeled at 25,000 cfs when Mississippi River flow equals 400,000 cfs; 
    #     closed when river flow is below 200,000 cfs or above 600,000 cfs; 
    #     a variable flow rate calculated using a linear function from 0 to 25,000 cfs for river flow between 200,000 cfs and 400,000 cfs 
    #     and held constant at 25,000 cfs for river flow between 400,000 cfs and 600,000 cfs
    
    impl_yr = implementation['UFWD']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual < 200000 or Qresidual >= 600000:
            Qdiv = 0
        elif Qresidual > 400000 and Qresidual < 600000:
            Qdiv = 25000
        else:
            Qdiv = 0.125*Qresidual - 25000
        
    UFWD_cfs[d] = Qdiv  
    UFWD_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
     
    
    #############################################
    ###   West Maurepas Sediment Diversion    ###
    #############################################
    # river mile 169
    # Diversion flow of 3,000 cfs
    # MP2023: project 305
    #     modeled at 50,000 cfs when the Mississippi River flow equals 1,000,000 cfs; 
    #     open with a variable flow rate calculated using a linear function from 0 to 50,000 cfs for river flow between 200,000 cfs and 1,000,000 cfs;
    #     constant flow rate of 50,000 cfs for river flow above 1,000,000 cfs. No operation below 200,000 cfs
    # Note that this is different than the West Maurepas Diversion from the 2012 and 2017 Master Plans (see below)

    impl_yr = implementation['WMPD']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual < 200000:
            Qdiv = 0
        else:
            Qdiv = min(0.0625*Qresidual-12500, 50000)
       
    WMPD_cfs[d] = Qdiv
    WMPD_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv


    #####################################
    ###   West Maurepas Diversion     ###
    ###  legacy from 2012 and 2017 MPs ##
    #####################################
    # river mile 162
    # Diversion flow of 3,000 cfs

# not used #    impl_yr = implementation['WMPD']
# not used #    
# not used #    if yr < yr0 + impl_yr:
# not used #        Qdiv = 0
# not used #    else:
# not used #        if Qresidual >= 3000:
# not used #            Qdiv = 3000
# not used #        else:
# not used #            Qdiv = Qresidual
# not used #      
# not used #    WMPD_cfs[d] = Qdiv
# not used #    WMPD_cms[d] = Qdiv*(0.3048**3)
# not used #    Qresidual -= Qdiv

    #################################################################
    ###   Mississippi River Reintroduction into Maurepas Swamp    ###
    #################################################################
    # river mile 144
    # Minimum operation in April and July-December
    # January-March and May-June operation follows the rating curve 2466.1*ln(Qresidual)-21462 with a maximum of 2,000 cfs
        
    impl_yr = implementation['MSRM']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if month == 4:
            Qdiv = 10
        elif month >= 7:
            Qdiv = 10
        else:
            Qdiv = max(10, (min(2000, 2466.1*np.log(Qresidual)-21462)))
        
    MSRM_cfs[d] = Qdiv  
    MSRM_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
    

    #############################
    ###   Edgard Diversion    ###
    #############################
    # river mile 137
    # off below 200,000; rating curve of 0.0625x-12500 between 200,000 and 600,000; constant flow of 25,000 cfs at 600,000; off between 600,000 and 1,250,000; constant flow of 35,000 cfs above 1,250,000
    # MP2023: project 323
    #    modeled at 25,000 cfs when Mississippi River flow equals 600,000 cfs; 
    #    open with a variable flow rate calculated using a linear function from 0 to 25,000 cfs for river flow between 200,000 cfs and 600,000 cfs; 
    #    no flow between 600,000 cfs and 1,250,000 cfs; constand flow rate of 35,000 cfs when river is above 1,250,000 cfs
    
    impl_yr = implementation['EdDI']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual == 600000:
            Qdiv = 25000
        elif Qresidual < 200000 or Qresidual > 600000 and Qresidual < 1250000:
            Qdiv = 0
        elif Qresidual >= 1250000:
            Qdiv = 35000
        else:
            Qdiv = 0.0625*Qresidual - 12500
        
    EdDI_cfs[d] = Qdiv  
    EdDI_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv        
        
    
    ##################################
    ###   Bonnet Carre Spillway    ###
    ##################################
    # river mile 128
    # River flow in excess of 1,250,000 cfs is diverted
         
    impl_yr = implementation['Bonn']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual >= 1250000:
            Qdiv = Qresidual - 1250000
        else:
            Qdiv = 0
        
    Bonn_cfs[d] = Qdiv 
    Bonn_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
    
    
    #########################################
    ###   Manchac Landbridge Diversion    ###
    #########################################
    # IMPLEMENTED VIA LINKS FOR  RUNS DO NOT USE THIS RATING CURVE
    # INSTEAD IMPLEMENT A NEW STATIC LINK WITH CAPACITY APPROXIMATELY EQUAL TO PEAK DIVERTED DISCHARGE
    #
    # from Bonnet Carre, which is at river mile 128
    # Diversion flow of 2,000 cfs at Bonnet Carre flow above 2,000 cfs *2017 MP had a diverted rate of 5,000 cfs*
    # MP2023: project 242
    #    A structure in the existing western spillway guide levee with a capacity of 2,000 cfs to increase freshwater exchange with adjacent wetlands 
        
    impl_yr = implementation['MLBD']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Bonn_cfs[d] >= 2000:
            Qdiv = 2000
        else:
            Qdiv = Bonn_cfs[d]
           
    MLBD_cfs[d] = Qdiv
    MLBD_cms[d] = Qdiv*(0.3048**3)

    
    #########################################
    ###   LaBranche Diversion             ###
    #########################################
    # IMPLEMENTED VIA LINKS FOR  RUNS DO NOT USE THIS RATING CURVE
    # INSTEAD IMPLEMENT A NEW STATIC LINK WITH CAPACITY APPROXIMATELY EQUAL TO PEAK DIVERTED DISCHARGE
    #
    # from Bonnet Carre, which is at river mile 128
    # MP2023: project 304
    #    Modeled at 850 cfs when Bonnet Carre is at 10,000 cfs increasing linearly to 17,500 cfs 
    #    when Bonnet Carre is at 250,000 cfs
        
    impl_yr = implementation['LaBD']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Bonn_cfs[d] < 10000:
            Qdiv = 0
        else:
            Qdiv = min(0.069375*Bonn_cfs[d]+156.25, 175000)
           
    LaBD_cfs[d] = Qdiv
    LaBD_cms[d] = Qdiv*(0.3048**3)

    
    ############################################
    ###   Davis Pond Freshwater Diversion    ###
    ############################################
    # river mile 118
    # Diversion flow of rating curve 1269.1454*ln(Qresidual)-9932.94805 with a maximum of 10,594 cfs
          
    impl_yr = implementation['DavP']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        Qdiv = min(max(0,1269.1454*np.log(Qresidual*0.3048**3) - 9932.94805), 10594.3487)
        
    DavP_cfs[d] = Qdiv  
    DavP_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
    

    ###############################################
    ###   LaBranche Hydrologic Restoration    ###
    ###############################################
    # river mile 116
    # Diversion flow of 750 cfs at river flows above 750 cfs
    # MP2023: project 245
    #     Construction of a pump/siphon with a constant flow of 750 cfs into the LaBranche wetlands via the Mississippi River to restore the historically fresh to intermediate marshes
        
    impl_yr = implementation['LaBr']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual >= 750:
            Qdiv = 750
        else:
            Qdiv = Qresidual
        
    LaBr_cfs[d] = Qdiv  
    LaBr_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
        
        
    ###################################
    ###   Ama Sediment Diversion    ###
    ###################################
    # river mile 115
    # Diversion flow of rating curve 0.0625*Qresidual-12500 at river flows above 200,000 cfs, max flow 50,000cfs
    # MP2023: project 243
    #     modeled at 50,000 cfs when the Mississippi River flow equals 1,000,000 cfs; 
    #     open with a variable flow rate calculated using a linear function from 0 to 50,000 cfs for river flow between 200,000 cfs and 1,000,000 cfs; 
    #     constant flow rate of 50,000 cfs for river flow above 1,000,000 cfs. No operation below 200,000 cfs
        
    impl_yr = implementation['AmaD']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual < 200000:
            Qdiv = 0
        else:
            Qdiv = min(0.0625*Qresidual-12500, 50000)
        
    AmaD_cfs[d] = Qdiv  
    AmaD_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
    
    
    ############################################
    ###   Inner Harbor Navigational Canal    ###
    ############################################
    # river mile 93
    # Diversion flow of rating curve 0.011297797*Qresidual
        
    impl_yr = implementation['IHNC']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual >= 0:
            Qdiv = (Qresidual*0.3048**3)*0.011297797
        else:
            Qdiv = Qresidual
        
    IHNC_cfs[d] = Qdiv  
    IHNC_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
     
    
    #######################################
    ###   Central Wetlands Diversion    ###
    #######################################
    # river mile 86
    # Diversion flow of rating curve 5,000 cfs at river flows above 5,000 cfs
    # MP2023: project 014a
    #     modeled at a constant flow of 5,000 cfs, independent of the Mississippi River flow
        
    impl_yr = implementation['CWDI']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual >= 5000:
            Qdiv = 5000
        else:
            Qdiv = Qresidual
        
    CWDI_cfs[d] = Qdiv  
    CWDI_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
    
    
    ############################################
    ###   Caernarvon Freshwater Diversion    ###
    ############################################
    # river mile 82
    # Diversion flow of rating curve 701.9143*ln(Qresidual)-5299.908567 with a maximum of 8828.66655 cfs
        
    impl_yr = implementation['Caer']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        Qdiv = min(max(0,701.9143*np.log(Qresidual*0.3048**3)-5299.908567),8828.66655)
        
    Caer_cfs[d] = Qdiv  
    Caer_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
    

    ###################################
    ###   Upper Breton Diversion    ###
    ###################################
    # river mile 77
    # 250,000 cfs version: Diversion flow following rating curve of 0.3125*Qresidual-62500 at river flows above 200,000 cfs
    # 75,000 cfs version: Diversion flow following rating curve of 0.3048*Qresidual-18750 at river flows above 200,000 cfs
    # MP2023:  project 013b
    #     modeled at 75,000 cfs when the Mississippi River flow equals 1,000,000 cfs; 
    #     open with a variable flow rate calculated using a linear function from 0 to 75,000 cfs for river flow between 200,000 cfs and 1,000,000 cfs; 
    #     constant flow rate of 75,000 cfs for river flow above 1,000,000 cfs. No operation below 200,000 cfs
        
    impl_yr = implementation['UBrD']

    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual < 200000:
            Qdiv = 0
        else:
            Qdiv = 0.09375*Qresidual-18750      # 75,000 cfs Operations - opening threshold @ 250k
            #Qdiv = 0.3125*Qresidual-62500      # 250,000 cfs Operations - opening threshold @ 250k

    UBrD_cfs[d] = Qdiv  
    UBrD_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv

        
    
    ##########################################
    ###   Mid Breton Sediment Diversion    ###
    ##########################################
    # river mile 69
    # 75k diversion: Diversion flow of rating curve 0.06667*Qresidual-8333 with a minimum of 5,000 cfs
    # MP2023 FWOA using 55k diversion scenario: rating curve 0.04762*Qresidual-4524 with a minimum of 5,000 cfs, opens at 250,000 cfs
        
    impl_yr = implementation['MBrD']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        #Qdiv = max(5000,0.04762*Qresidual-4524)     # 55,000 cfs Operations - opening threshold @ 250k
        #Qdiv = max(5000,0.06667*Qresidual-8333)     # 75,000 cfs Operations - opening threshold @ 250k
        Qdiv = max(5000,0.0625*Qresidual-23125)     # 55,000 cfs Operations - opening threshold @ 450k
    MBrD_cfs[d] = Qdiv
    MBrD_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
    

    ###################################
    ###   Naomi Siphon Diversion    ###
    ###################################
    # river mile 64
    # Diversion flow of rating curve 281.044708*ln(Qresidual)-2500.93169 with a maximum of 2118.87997 cfs

    impl_yr = implementation['Naom']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        Qdiv = min(max(0,281.044708*np.log(Qresidual*0.3048**3)-2500.93169),2118.87997)
        
    Naom_cfs[d] = Qdiv  
    Naom_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv

    
    #############################################
    ###   Mid-Barataria Sediment Diversion    ###
    #############################################
    # river mile 61
    # 5 different versions:
        # 75k @ 1.0 m : Diversion flow of rating curve 0.09375*residual - 18750 at river flows above 200,000
        # 250k @ 1.0 m : Diversion flow of rating curve 0.3125*residual - 62500 at river flows above 200,000
        # 35k - 75k @ 1.0 m : Diversion flow of rating curve 0.04375*residual - 8750 at river flows above 200,000
        # 75k @ 1.25 m , 5k min : Diversion flow of rating curve 0.06667*residual - 8333 with a minimum of 5,000 cfs, opens at 250,000 cfs
        # 75k @ 1.25 m , 5k min : Diversion flow of rating curve 0.08757*residual - 34375 with a minimum of 5,000 cfs, opens at 450,000 cfs
    impl_yr = implementation['MBaD']

    if yr <yr0 + impl_yr:
        Qdiv = 0
    else:
#        if Qresidual < 200000:
#            Qdiv = 0
#        else::
#            Qdiv = 0.09375*Qresidual - 18750       # 75k @ 1.0 m 
#            Qdiv = 0.3125*Qresidual-62500          # 250k @ 1.0 m 
#            Qdiv = 0.04375*Qresidual-8750          # 35k - 75k @ 1.0 m 
#        Qdiv = max(5000, 0.06667*Qresidual-8333)   # 75k @ 1.25 m , 5k min, opening threshold @ 250k
        Qdiv = max(5000, 0.0875*Qresidual-34375)    # 75k @ 1.25 m , 5k min, opening threshold @ 450k
        
    MBaD_cfs[d] = Qdiv
    MBaD_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
    

    ###################################
    ###   West Pointe a la Hache    ###
    ###################################
    # river mile 49
    # Diversion flow of rating curve 456.35377*ln(Qresidual)-4049.4586 with a maximum of 2118.87997 cfs
        
    impl_yr = implementation['WPLH']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        Qdiv = min(max(0, 456.35377*np.log(Qresidual*0.3048**3)-4049.4586),2118.87997)
        
    WPLH_cfs[d] = Qdiv 
    WPLH_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
    
    
    ################################################
    ###   Lower Plaquemines River Sediment Plan  ###
    ################################################
    # river mile 49 
    # MP2023: project 327
    # Seven pumps/siphons located throughout the Mississippi River corridor
    # (assume all pumps/siphons are extracted at one location in the river located at West Point a la Hache)
    #
    # Each siphon is operated with the same rating curve ( Qresidual/225 - 1333.3 ):
    #     No flow diverted when river < 300,000 cfs
    #     Maximum flow diverted of 2,000 cfs when river > 750,000 cfs
    #     Linear relationship when river between 300,000 and 750,000 cfs
    #     Operated December 1 through April 30
    # 
    # Since all 7 pump/siphons are being extracted from the Mississippi River flow timeseries at one location (assumed to be at WPLH)
    # this run will also assume that WPLH is operated with this same new operational curve
    # therefore, must add calculated WPLH back into Qresidual before being added and this diversion timeseries overwrites the WPLH timeseries in TribQ.csv
    
    impl_yr = implementation['LPlq']
    
    if impl_yr < 9999: 
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:
            # add WPLH calculated flow back into residual flow since this diversion will replace that WPLH timeseries
            if yr >= yr0 + implementation['WPLH'] :
                Qresidual += WPLH_cfs[d]  
        
            if month > 4 and month < 12:
                Qdiv = 0
            else:
                # diversion flowrate is 8x for (1) WPLH and (7) pumps as part of LPlq
                Qdiv = 8.0*min(max(0, Qresidual/225.0 - 1333.333 ), 2000.0)
    
        WPLH_cfs[d] = Qdiv
        WPLH_cms[d] = Qdiv*(0.3048**3)
        Qresidual  -= Qdiv    
    
    
    ######################################
    ###   Lower Barataria Diversion    ###
    ######################################
    # river mile 40
    # Diversion flow at rating curve of 0.0625*residual-12500 at river flows above 200,000 cfs
        
    impl_yr = implementation['LBaD']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual < 200000:
            Qdiv = 0
        else:
            Qdiv = 0.0625*Qresidual-12500
        
    LBaD_cfs[d] = Qdiv 
    LBaD_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv
        
        
    ###################################
    ###   Lower Breton Diversion    ###
    ###################################
    # river mile 37
    # Diversion flow of rating curve 0.0625*residual-12500 at river flows above 200,000 cfs
    # MP2023: project 006
    #    modeled at 50,000 cfs when the Mississippi River flow equals 1,000,000 cfs; 
    #    open with a variable flow rate calculated using a linear function from 0 to 50,000 cfs for river flow between 200,000 cfs and 1,000,000 cfs; 
    #    constant flow rate of 50,000 cfs for river flow above 1,000,000 cfs. No operation below 200,000 cfs	
        
    impl_yr = implementation['LBrD']
    
    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual < 200000:
            Qdiv = 0
        else:
            Qdiv = min(0.0625*Qresidual-12500, 50000)
        
    LBrD_cfs[d] = Qdiv  
    LBrD_cms[d] = Qdiv*(0.3048**3)
    Qresidual -= Qdiv

    ######################################################################
    ######      Calculate distributary flow at each BFD pass        ######
    ######      Qresidual is no longer updated downstream of here   ######
    ######      All passes will use the same input residual flow    ######
    ######      rating curves come from Mead Allison rating curves  ######
    ######################################################################
        
    ############################
    ###   Mardi Gras Pass    ###
    ############################
    # river mile 44
    # Diversion flow of rating curve 0.0153*Qresidual+276.2369
        
    Qdiv = 0.0153*Qresidual+276.2369
        
    MGPS_cfs[d] = Qdiv
    MGPS_cms[d] = Qdiv*(0.3048**3)
        
    #############################
    ###   Bohemia Spillway    ###
    #############################
    # river mile 44 to 34
    # Diversion flow of rating curve 1.4/100*Qresidual at river flows above 930,000 cfs
        
    if Qresidual < 930000:
        Qdiv = 0
    else:
        Qdiv = 1.4/100*Qresidual
    
    Bohe_cfs[d] = Qdiv  
    Bohe_cms[d] = Qdiv*(0.3048**3)
        
    #########################
    ###   Ostrica Lock    ###
    #########################
    # river mile 25
    # if input is less than 800,000 cfs, then 0 is diverted
    # Diversion flow of rating curve 5.2/100*Qresidual at river flows above 800,000 cfs
    
    if Qresidual < 800000:
        Qdiv = 0
    else:
        Qdiv = 5.2/100*Qresidual
        
    Ostr_cfs[d] = Qdiv  
    Ostr_cms[d] = Qdiv*(0.3048**3)

    ############################
    ###   Fort St. Philip    ###
    ############################
    # river mile 20
    # Diversion flow of rating curve 0.1011*Qresidual-25159
        
    Qdiv = 0.1011*Qresidual-25159
        
    FStP_cfs[d] = Qdiv  
    FStP_cms[d] = Qdiv*(0.3048**3)

    ##############################
    ###   Baptiste Collette    ###
    ##############################
    # river mile 11
    # Diversion flow of rating curve 0.1031*Qresidual-5631
        
    Qdiv = 0.1031*Qresidual-5631
        
    Bapt_cfs[d] = Qdiv  
    Bapt_cms[d] = Qdiv*(0.3048**3)

    #######################
    ###   Grand Pass    ###
    #######################
    # river mile 11
    # Diversion flow of rating curve 0.0915*Qresidual+4288
        
    Qdiv = 0.0915*Qresidual+4288
        
    GrPa_cfs[d] = Qdiv  
    GrPa_cms[d] = Qdiv*(0.3048**3)

    #####################
    ###   West Bay    ###
    #####################
    # river mile 5
    # Diversion flow of rating curve 0.0653*Qresidual-2075
        
    Qdiv = 0.0653*Qresidual-2075
        
    WBay_cfs[d] = Qdiv  
    WBay_cms[d] = Qdiv*(0.3048**3)

    #######################
    ###   Small Cuts    ###
    #######################
    # This is the amount diverted through all of the small outlets throughout the delta that aren't accounted for by the outlets here
    # the total amount diverted through all of these is 0.0025*Qresidual+10196
        
    Qdiv = 0.0025*Qresidual+10196
        
    SCut_cfs[d] = Qdiv  
    SCut_cms[d] = Qdiv*(0.3048**3)

    ########################
    ###   Cubit's Gap    ###
    ########################
    # river mile 3
    # Diversion flow of rating curve 0.1319*Qresidual-19939
        
    Qdiv = 0.1319*Qresidual-19939
        
    CGap_cfs[d] = Qdiv  
    CGap_cms[d] = Qdiv*(0.3048**3)

    #######################
    ###   South Pass    ###
    #######################
    # river mile 0
    # Diversion flow of rating curve 0.0858*Qresidual+2332
        
    Qdiv = 0.0858*Qresidual+2332
        
    SPas_cfs[d] = Qdiv 
    SPas_cms[d] = Qdiv*(0.3048**3)
 
    ##########################
    ###   Pass a Loutre    ###
    ##########################
    # river mile 0
    # Diversion flow of rating curve 0.0543*Qresidual+15700
        
    Qdiv = 0.0543*Qresidual+15700
        
    PLou_cfs[d] = Qdiv  
    PLou_cms[d] = Qdiv*(0.3048**3)
 
    #########################################
    ###   Southwest Pass Ratings Curve    ###
    #########################################
    # river mile 0
    # this is the ratings curve for SW pass, there is also a SW Pass Residual calculation below
    # Diversion flow of rating curve 0.4189*Qresidual-64787
        
    Qdiv = 0.4189*Qresidual-64787
        
    SWPS_cfs[d] = Qdiv 
    SWPS_cms[d] = Qdiv*(0.3048**3)
    
    ####################################
    ###   Southwest Pass Residual    ###
    ####################################
    # river mile 0
    # the amount diverted here is calculated by finding the residual output after all other distributaries are diverted
        
    Qdiv = Qresidual - (MGPS_cfs[d] + Bohe_cfs[d] + Ostr_cfs[d] + FStP_cfs[d] + Bapt_cfs[d] + GrPa_cfs[d] + WBay_cfs[d] + SCut_cfs[d] + CGap_cfs[d] + SPas_cfs[d] + PLou_cfs[d])
        
    SWPR_cfs[d] = Qdiv
    SWPR_cms[d] = Qdiv*(0.3048**3)


####################################
###   write new TribQ.csv file   ###
####################################

with open(TribQ_out_file,mode='w') as TribQ_out:
    # write header line to TribQ.csv
    line = '1'
    for n in range(2,nTribs+1):
        line = '%s,%s' % (line,n)
    
    TribQ_out.write('%s\n' % line)          
    for d in range(0,ndays):
        # write tributary flow read in from original TribQ.csv
        line = '%s' % TribQ_in[d][0]                    # ncol 01 # Neches River at Beaumont TX
        for t in range(1,nTributaries):
            line = '%s,%s' % (line,TribQ_in[d][t])      # ncol 02 # Sabine River at Ruliff TX
                                                        # ncol 03 # Vinton Canal
                                                        # ncol 04 # Calcasieu River near Kinder LA
                                                        # ncol 05 # Bayou Lacassine near Lake Arthur LA
                                                        # ncol 06 # Mermentau River at Mermentau LA
                                                        # ncol 07 # Vermilion River at Surrey St at Lafayette LA
                                                        # ncol 08 # Charenton Drainage Canal at Baldwin LA
                                                        # ncol 09 # GIWW at Franklin
                                                        # ncol 10 # Atch_cms #Atchafalaya River
                                                        # ncol 11 # Mississippi River Upstream (Tarbert Landing)
                                                        # ncol 12 # GIWW at Larose
                                                        # ncol 13 # Bayou Lafourche at Thibodeaux LA
                                                        # ncol 14 # Amite River near Denham Springs LA
                                                        # ncol 15 # Natalbany River at Baptist LA
                                                        # ncol 16 # Tickfaw River at Holden LA
                                                        # ncol 17 # Tangipahoa River at Robert LA
                                                        # ncol 18 # Tchefuncte River near Folsom LA
                                                        # ncol 19 # Bogue Chitto near Bush LA
                                                        # ncol 20 # Pearl River near Bogalusa LA
                                                        # ncol 21 # Wolf River near Landon MS
                                                        # ncol 22 # Biloxi River at Wortham MS
                                                        # ncol 23 # Pascagoula River at Merrill MS
                                                        # ncol 24 # Tensaw River near Mount Vernon AL
                                                        # ncol 25 # Mobile River at River Mile 31 at Bucks AL
                                                        # ncol 26 # Mobile1
                                                        # ncol 27 # Mobile 2
                                                        # ncol 28 # Jourdan
                                                        # ncol 29 # Violet Runoff
                                                        # ncol 30 # NE Lake Pontchartrain ungaged drainage (Bayou Bonfouca)
                                                        # ncol 31 # SE Lake Pontchartrain ungaged drainage (Orleans Parish)
                                                        # ncol 32 # S Lake Pontchartrain ungaged drainage (Jefferson Parish)
                                                        # ncol 33 # SW Lake Pontchartrain ungaged drainage
                                                        # ncol 34 # S Lake Maurepas ungaged drainage
                                                        # ncol 35 # NE Lake Pontchartrain ungaged drainage (Bayou LaCombe)      

        # write calculated diversion/pass flow calculated above
        line = '%s,%s' % (line,Morg_cms[d])             # ncol 36 # Morganza Spillway
        line = '%s,%s' % (line,BLaF_cms[d])             # ncol 37 # Bayou LaFourche Diversion (including additional flow for Upper Barataria Hydrologic Restoration)
        line = '%s,%s' % (line,UFWD_cms[d])             # ncol 38 # Union Freshwater Diversion
        line = '%s,%s' % (line,WMPD_cms[d])             # ncol 39 # West Maurepas Diversion
        line = '%s,%s' % (line,MSRM_cms[d])             # ncol 40 # Mississippi River Reintroduction in Maurepas Swamp (East Maurepas Diversion in 2017 MP)
        line = '%s,%s' % (line,EdDI_cms[d])             # ncol 41 # Edgard Diversion
        line = '%s,%s' % (line,Bonn_cms[d])             # ncol 42 # Bonnet Carre
        line = '%s,%s' % (line,MLBD_cms[d])             # ncol 43 # Manchac Landbridge Diversion
        line = '%s,%s' % (line,LaBr_cms[d])             # ncol 44 # LaBranche Hydrologic Restoration
        line = '%s,%s' % (line,DavP_cms[d])             # ncol 45 # Davis Pond
        line = '%s,%s' % (line,AmaD_cms[d])             # ncol 46 # Ama Sediment Diversion
        line = '%s,%s' % (line,IHNC_cms[d])             # ncol 47 # Inner Harbor Navigational Canal
        line = '%s,%s' % (line,CWDI_cms[d])             # ncol 48 # Central Wetlands Diversion
        line = '%s,%s' % (line,Caer_cms[d])             # ncol 49 # Caernarvon
        line = '%s,%s' % (line,UBrD_cms[d])             # ncol 50 # Upper Breton Diversion
        line = '%s,%s' % (line,MBrD_cms[d])             # ncol 51 # Mid-Breton Sound Diversion
        line = '%s,%s' % (line,MBaD_cms[d])             # ncol 52 # Mid-Barataria Diversion
        line = '%s,%s' % (line,Naom_cms[d])             # ncol 53 # Naomi
        line = '%s,%s' % (line,WPLH_cms[d])             # ncol 54 # West Point a la Hache (including additional flow for Lower Plaquemines River Sediment Plan)
        line = '%s,%s' % (line,LBaD_cms[d])             # ncol 55 # Lower Barataria iversion
        line = '%s,%s' % (line,LBrD_cms[d])             # ncol 56 # Lower Breton Diversion
        line = '%s,%s' % (line,MGPS_cms[d])             # ncol 57 # Mardi Gras Pass
        line = '%s,%s' % (line,Bohe_cms[d])             # ncol 58 # Bohemia
        line = '%s,%s' % (line,Ostr_cms[d])             # ncol 59 # Ostrica
        line = '%s,%s' % (line,FStP_cms[d])             # ncol 60 # Ft St Phillip
        line = '%s,%s' % (line,Bapt_cms[d])             # ncol 61 # Baptiste Collette
        line = '%s,%s' % (line,GrPa_cms[d])             # ncol 62 # Grand Pass
        line = '%s,%s' % (line,WBay_cms[d])             # ncol 63 # West Bay Diversion
        line = '%s,%s' % (line,SCut_cms[d])             # ncol 64 # SmallCuts
        line = '%s,%s' % (line,CGap_cms[d])             # ncol 65 # Cubits Gap
        line = '%s,%s' % (line,PLou_cms[d])             # ncol 66 # Pass A Loutre
        line = '%s,%s' % (line,SPas_cms[d])             # ncol 67 # South Pass
        line = '%s,%s' % (line,SWPS_cms[d])             # ncol 68 # South West Pass calculated from curve (not used in model)
        #line = '%s,%s' % (line,SWPR_cms[d])                       # South West Pass calculated from residual flow to close mass balance on Miss Riv flow in/out
        line = '%s,%s' % (line,IAFT_cms[d])             # ncol 69 # Increase Atchafalaya Flows to Terrebonne
        line = '%s,%s' % (line,AtRD_cms[d])             # ncol 70 # Atchafalaya River Diversion
        #line = '%s,%s' % (line,LaBD_cms[d])                       # LaBranche Diversion
        line = '%s,! %s' % (line, dates_all[d])         # ncol 71 # Date
        
        TribQ_out.write('%s\n' % line)
