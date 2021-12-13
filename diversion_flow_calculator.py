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

TribQ_in_file  = 'S07_G501_TribQ.csv'
TribQ_out_file = 'S07_G600_TribQ.csv'


# Set implementation year (elapsed) for each diversion
#          0 = implemented at the start of the model run (ICM year 0)
#          9 = diversion is implemented in year 9 of ICM run - which is year 7 of FWOA (FWOA year = ICM year + 2 spinup yeard)
#       9999 = diversion is not implemented at all 

implementation = {}
implementation['IAFT'] = 9999		# Increase Atchafalaya Flows to Terrebonne
implementation['AtRD'] = 9999		# Atchafalaya River Diversion
implementation['BLaF'] = 0		# Bayou Lafourche Diversion
implementation['UBaH'] = 9999		# Upper Barataria Hydrologic Restoration
implementation['UFWD'] = 9999		# Union Freshwater Diversion
implementation['WMPD'] = 9999		# West Maurepas Diversion
implementation['MSRM'] = 0		# Mississippi River Reintroduction in Maurepas Swamp
implementation['EdDI'] = 9999		# Edgard Diversion
implementation['Bonn'] = 0		# Bonnet Carre
implementation['MLBD'] = 9999   	# Manchac Landbridge Diversion # IMPLEMENTED VIA LINKS FOR ALTERNATIVE RUNS - DO NOT ACTIVATE IN THIS CODE
implementation['LaBr'] = 9999		# LaBranche Hydrological Restoration (not the same as LaBranche Diversion)
implementation['DavP'] = 0		# Davis Pond
implementation['AmaD'] = 9999		# Ama Sediment Diversion
implementation['IHNC'] = 0		# Inner Harbor Navigational Canal
implementation['CWDI'] = 9999		# Central Wetlands Diversion
implementation['Caer'] = 0		# Caernarvon
implementation['UBrD'] = 9999		# Upper Breton Diversion
implementation['MBrD'] = 0		# Mid-Breton Sound Diversion
implementation['Naom'] = 0		# Naomi
implementation['MBaD'] = 0		# Mid-Barataria Diversion
implementation['WPLH'] = 0		# West Pointe a la Hache
implementation['LPlq'] = 0		# Lower Plaquemines River Sediment Plan
implementation['LBaD'] = 9999		# Lower Barataria Diversion
implementation['LBrD'] = 9999		# Lower Breton Diversion



nTributaries = 35				# number of riverine input timeseries included in TribQ, TribF, TribS, and QMult
nMissRiv_Diversions = 21			# number of Mississippi River diversion timeseries included in TribQ, TribF, TribS, and QMult
nBFD_Passes = 12				# number of distributary passes timeseries in the BFD included in TribQ, TribF, TribS, and QMult
nAtchRiv_Diversions = 2				# number of Atchafalaya River diversion timeseries included in TribQ, TribF, TribS, and QMult

nTribs = nTributaries + nMissRiv_Diversions + nBFD_Passes + nAtchRiv_Diversions	# total number of timeseries read in as tributary boundary conditions in TribQ

trib_cols   = range(0,nTributaries)      	# first 35 columns of TribQ.csv are tributary flows; diversions start in column 36
date_col    = [nTribs]          		# last column of TribQ.csv is the date
MissRiv_col = 10                		# column 11 of TribQ.csv is the Miss. River @ Tarbert Landing data

TribQ_in    = np.genfromtxt(TribQ_in_file,delimiter=',',dtype=str,skip_header=1,usecols=trib_cols)
dates_all   = np.genfromtxt(TribQ_in_file,delimiter=',',dtype=str,skip_header=1,usecols=date_col)


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
IAFT_cfs = np.zeros(ndays)	# Increase Atchafalaya Flows to Terrebonne
IAFT_cms = np.zeros(ndays)
AtRD_cfs = np.zeros(ndays)	# Atchafalaya River Diversion
AtRD_cms = np.zeros(ndays)
BLaF_cfs = np.zeros(ndays)      # Bayou Lafourche Diversion
BLaF_cms = np.zeros(ndays)
#UBaH_cfs = np.zeros(ndays)      # Upper Barataria Hydrologic Restoration (not used - added as additional flow to BLaF timeseries)
#UBaH_cms = np.zeros(ndays)
UFWD_cfs = np.zeros(ndays)      # Union Freshwater Diversion
UFWD_cms = np.zeros(ndays)
WMPD_cfs = np.zeros(ndays)      # West Maurepas Diversion
WMPD_cms = np.zeros(ndays)
MSRM_cfs = np.zeros(ndays)      # Mississippi River Reintroduction in Maurepas Swamp
MSRM_cms = np.zeros(ndays)
EdDI_cfs = np.zeros(ndays)      # Edgard Diversion
EdDI_cms = np.zeros(ndays)
Bonn_cfs = np.zeros(ndays)      # Bonnet Carre
Bonn_cms = np.zeros(ndays)
MLBD_cfs = np.zeros(ndays)      # Manchac Landbridge Diversion
MLBD_cms = np.zeros(ndays)
LaBr_cfs = np.zeros(ndays)      # LaBranche Hydrological Restoration
LaBr_cms = np.zeros(ndays)
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
#LPlq_cfs = np.zeros(ndays)      # Lower Plaquemines River Sediment Plan (not used - added as additional flow to WPLH timeseries)
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
        month = int(date[4:6])                                                  # this will work if date is formatted as YYYYMMDD

#        month, yr = int(date.split('/')[0]), int(date.split('/')[2])        # this will work if date is formatted as MM/DD/YYYY
#        year = date.split('-')[2]                                          # this will work if date is formatted as MM-DD-YYYY
        
        Qresidual = MissTarb_cfs[d]
	                
        ##############################
        ###   Atchafalaya River    ###
        ##############################
        # Assume 70/30 flow split at Old River Control Structure (river mile 316)
        # 70% of Mississippi River flow is kept in main channel (this is the observed discharge at Tarbert Landing)
        # 30% of Mississippi River flow is diverted into Atchafalaya River
        
        Qdiv = 0.7/Qresidual*0.3
        Atch_cfs[d] = Qdiv
        Atch_cms[d] = Qdiv*(0.3048**3)
        
	Qresidual_Atch = Atch_cfs[d]
        
	##############################
        ###   Morganza Floodway    ###
        ##############################
        # river mile 280
        # not active, set to zero (this is redundant since Morg_cfs is already set as a zero array above)
        
        Qdiv = 0
        Morg_cfs[d] = Qdiv
        Morg_cms[d] = Qdiv*(0.3048**3)
	
	###################################################
        ###   Increase Atchafalaya Flows to Terrebonne  ###
        ###################################################
	# location at GIWW
	# still need to determine rating curve to use (currently set to 0)
	# rating curve needs to be a function of Atchafalaya River @ Simmesport since it is calculated here from the flows directly downstream of Old River Control Structure

	impl_yr = implementation['IAFT']
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:   
            if Qresidual_Atch >= 0:
                Qdiv = 0
            else:
  		Qdiv = 0
                
        IAFT_cfs[d] = Qdiv
        IAFT_cms[d] = Qdiv*(0.3048**3)
        Qresidual_Atch -= Qdiv
	
	
	########################################
        ###   Atchafalaya River Diversion    ###
        ########################################
	# location south of GIWW 
	# still need to determine rating curve to use (currently set to 0)
	# rating curve needs to be a function of Atchafalaya River @ Simmesport since it is calculated here from the flows directly downstream of Old River Control Structure
	
	impl_yr = implementation['AtRD']
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:   
            if Qresidual_Atch >= 0:
                Qdiv = 0
            else:
  		Qdiv = 0
                
        AtRD_cfs[d] = Qdiv
        AtRD_cms[d] = Qdiv*(0.3048**3)
        Qresidual_Atch -= Qdiv

	
        ######################################
        ###   Bayou Lafourche Diversion    ###
        ######################################
        # river mile 176
        # current condition is 500 cfs but an additional 1000 cfs pump is in the permitting stage as of 4/27/2021
        # Constant diversion flow of 1,500 cfs

        impl_yr = implementation['BLaF']
        
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:   
            if Qresidual >= 1500:
                Qdiv = 1500
            else:
                Qdiv = Qresidual
                
        BLaF_cfs[d] = Qdiv
        BLaF_cms[d] = Qdiv*(0.3048**3)
        Qresidual -= Qdiv
	
	
	###################################################
        ###   Upper Barataria Hydrologic Restoration    ###
        ###################################################
        # river mile 176 
	# additional flow pumped into Bayou Lafourche
	# pump 750 cfs into Bayou Lafourche to be routed down BLaF and eventually eastward into Upper Barataria
	# add this diversion flow to the pre-existing Bayou Lafourche flow calculated above
        impl_yr = implementation['UBaH']
	
	if yr < yr0 + impl_yr:
            Qdiv = 0
        else:   
            if Qresidual >= 750:
                Qdiv = 750
            else:
                Qdiv = Qresidual
                
        BLaF_cfs[d] += Qdiv
        BLaF_cms[d] += Qdiv*(0.3048**3)
        Qresidual -= Qdiv
        
	
	#######################################
        ###   Union Freshwater Diversion    ###
        #######################################
        # river mile 169
        # No diversion flow below 200,000 or above 600,000, Diversion flow of 25,000 between 400,000 and 600,000, Else, diversion flow = 0.125x-2500
        
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
         
		
        ####################################
        ###   West Maurepas Diversion    ###
        ####################################
        # river mile 162
        # Diversion flow of 3,000 cfs
            
        impl_yr = implementation['WMPD']
       
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:
            if Qresidual >= 3000:
                Qdiv = 3000
            else:
                Qdiv = Qresidual
           
        WMPD_cfs[d] = Qdiv
        WMPD_cms[d] = Qdiv*(0.3048**3)
        Qresidual -= Qdiv
            
        
        #################################################################
        ###   Mississippi River Reintroduction into Maurepas Swamp    ###
        #################################################################
        # river mile 144
        # Minimum operation in April and July-December
        # January-March and May-June operation follows the rating curve 2466.1*ln(Qresidual)-21462 with a maximum of 2,000 cfs
            
        impl_yr = implementation['MSRM']
        
        if yr < yr0 + impl_yr:
            Qdiv == 0
        else:
            if month == 4:
                Qdiv == 10
            elif month >= 7:
                Qdiv == 10
            else:
                Qdiv = max(10, (min(2000, 2466.1*np.log(Qresidual))-21462))
            
        MSRM_cfs[d] = Qdiv  
        MSRM_cms[d] = Qdiv*(0.3048**3)
        Qresidual -= Qdiv
       

        #############################
        ###   Edgard Diversion    ###
        #############################
        # river mile 137
        # off below 200,000; rating curve of 0.0625x-12500 between 200,000 and 600,000; constant flow of 25,000 cfs at 600,000; off between 600,000 and 1,250,000; constant flow of 35,000 cfs above 1,250,000
        
        impl_yr = implementation['EdDI']
        
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:
            if Qresidual = 600000
                Qdiv = 25000
            elif Qresidual < 200000 or Qresidual > 600000 and Qresidual < 1250000:
                Qdiv = 0
            elif Qresidual >= 1250000
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
        # IMPLEMENTED VIA LINKS FOR ALTERNATIVE RUNS DO NOT USE THIS
        # from Bonnet Carre, which is at river mile 128
        # Diversion flow of 5,000 cfs at Bonnet Carre flow above 5,000 cfs
            
        impl_yr = implementation['MLBD']
       
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:
            if Bonn_cfs[d] >= 5000:
                Qdiv = 5000
            else:
                Qdiv = Bonn_cfs[d]
               
        MLBD_cfs[d] = Qdiv
        MLBD_cms[d] = Qdiv*(0.3048**3)

	
        ############################################
        ###   Davis Pond Freshwater Diversion    ###
        ############################################
        # river mile 118
        # Diversion flow of rating curve 1269.1454*ln(Qresidual)-9932.94805 with a maximum of 10,594 cfs
              
        impl_yr = implementation['DavP']
        
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:
            Qdiv = min(max(0,1269.1454*np.log(Qresidual) - 9932.94805), 10594.3487)
            
        DavP_cfs[d] = Qdiv  
        DavP_cms[d] = Qdiv*(0.3048**3)
        Qresidual -= Qdiv
        
        #print(DavP_cfs)
        
	
        ###############################################
        ###   LaBranche Hydrologic Restoration    ###
        ###############################################
        # river mile 116
        # Diversion flow of 750 cfs at river flows above 750 cfs
            
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
        # Diversion flow of rating curve 0.0625*Qresidual-12500 at river flows above 200,000 cfs
            
        impl_yr = implementation['AmaD']
        
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:
            if Qresidual < 200000:
                Qdiv = 0
            else:
                Qdiv = 0.0625*Qresidual-12500
            
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
                Qdiv = Qresidual*0.011297797
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
            Qdiv = min(max(0,701.9143*np.log(Qresidual)-5299.908567),8828.66655)
            
        Caer_cfs[d] = Qdiv  
        Caer_cms[d] = Qdiv*(0.3048**3)
        Qresidual -= Qdiv
       

        ###################################
        ###   Upper Breton Diversion    ###
        ###################################
        # river mile 77
        # 250,000 cfs version: Diversion flow following rating curve of 0.3125*Qresidual-62500 at river flows above 200,000 cfs
        # 75,000 cfs version: Diversion flow following rating curve of 0.3048*Qresidual-18750 at river flows above 200,000 cfs

        # 250,000 cfs #
            
        impl_yr = implementation['UBrD']
        
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:
            if Qresidual < 200000:
                Qdiv = 0
            else:
                Qdiv = 0.3125*Qresidual-62500
            
        UBrD_cfs[d] = Qdiv 
        UBrD_cms[d] = Qdiv*(0.3048**3)
        Qresidual -= Qdiv
        
        # 75,000 cfs #
        
#       impl_yr = 1
        
#       if yr < yr0 + impl_yr:
#           Qdiv = 0
#       else:
#           if Qresidual < 200000:
#               Qdiv = 0
#           else:
#               Qdiv = 0.3048*Qresidual-18750
            
#       UBrD_cfs[d] = Qdiv  
#       UBrD_cms[d] = Qdiv*(0.3048**3)
#       Qresidual -= Qdiv
       
	
        ##########################################
        ###   Mid Breton Sediment Diversion    ###
        ##########################################
        # river mile 69
        # Diversion flow of rating curve 0.06667*Qresidual-8333 with a minimum of 5,000 cfs
            
        impl_yr = implementation['MBrD']
        
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:
            Qdiv = max(5000,0.06667*Qresidual-8333)
            
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
            Qdiv = min(max(0,281.044708*np.log(Qresidual)-2500.93169),2118.87997)
            
        Naom_cfs[d] = Qdiv  
        Naom_cms[d] = Qdiv*(0.3048**3)
        Qresidual -= Qdiv

	
	#############################################
        ###   Mid-Barataria Sediment Diversion    ###
        #############################################
        # river mile 61
        # 4 different versions:
            # 75k @ 1.0 m : Diversion flow of rating curve 0.09375*residual - 18750 at river flows above 200,000
            # 250k @ 1.0 m : Diversion flow of rating curve 0.3125*residual - 62500 at river flows above 200,000
            # 35k - 75k @ 1.0 m : Diversion flow of rating curve 0.04375*residual - 8750 at river flows above 200,000
            # 75k @ 1.25 m , 5k min : Diversion flow of rating curve 0.06667*residual - 8333 with a minimum of 5,000 cfs
            

        
        impl_yr = implementation['MBaD']

    ###### 75k @ 1.0 m ######

#       if yr <yr0 + impl_yr:
#          Qdiv = 0
#       else:
#           if Qresidual < 200000:
#               Qdiv = 0
#           else:
#               Qdiv = 0.09375*Qresidual - 18750
            
#       MBaD_cfs[d] = Qdiv
#       MBaD_cms[d] = Qdiv*(0.3048**3)
#       Qresidual -= Qdiv
        
    ###### 250k @ 1.0 m ######
        
#       if yr <yr0 + impl_yr:
#           Qdiv = 0
#       else:
#           if Qresidual < 200000:
#               Qdiv = 0
#           else:
#               Qdiv = 0.3125*Qresidual-62500
            
#       MBaD_cfs[d] = Qdiv
#       MBaD_cms[d] = Qdiv*(0.3048**3)
#       Qresidual -= Qdiv
        
   ###### 35k - 75k @ 1.0 m ######
        
#       if yr <yr0 + impl_yr:
#           Qdiv = 0
#       else:
#           if Qresidual < 200000:
#               Qdiv = 0
#           else:
#               Qdiv = 0.04375*Qresidual-8750
            
#       MBaD_cfs[d] = Qdiv
#       MBaD_cms[d] = Qdiv*(0.3048**3)
#       Qresidual -= Qdiv
        
   ###### 75k @ 1.25 m , 5k min ######
        
        if yr <yr0 + impl_yr:
            Qdiv = 0
        else:
            Qdiv = max(5000, 0.06667*Qresidual-8333)
            
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
            Qdiv = min(max(0, 456.35377*np.log(Qresidual)-4049.4586),2118.87997)
            
        WPLH_cfs[d] = Qdiv 
        WPLH_cms[d] = Qdiv*(0.3048**3)
        Qresidual -= Qdiv
        
        
        ################################################
        ###   Lower Plaquemines River Sediment Plan  ###
        ################################################
        # river mile 49 
		# Seven pumps/siphons located throughout the Mississippi River corridor
        # (assume all pumps/siphons are extracted at one location in the river located at West Point a la Hache)
        #
		# Each siphon is operated with the same rating curve ( Qresidual/225 - 1333.3 ):
        #     No flow diverted when river < 300,000 cfs
        #     Maximum flow diverted of 2,000 cfs when river > 750,000 cfs
        #     Linear relationship when river between 300,000 and 750,000 cfs
        # 
        # Since all 7 pump/siphons are being extracted from the Mississippi River flow timeseries at one location (assumed to be at WPLH)
        # this run will also assume that WPLH is operated with this same new operational curve
        # therefore, must add calculated WPLH back into Qresidual before being added and this diversion timeseries overwrites the WPLH timeseries in TribQ.csv
        
        impl_yr = implementation['LPlq']
        
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:
            # add WPLH calculated flow back into residual flow since this diversion will replace that WPLH timeseries
			if yr >= yr0 + implementation['WPLH'] :
            	Qresidual += WPLH_cfs[d]  
            
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
            
        impl_yr = implementation['LBrD']
        
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:
            if Qresidual < 200000:
                Qdiv = 0
            else:
                Qdiv = 0.0625*Qresidual-12500
            
        LBrD_cfs[d] = Qdiv  
        LBrD_cms[d] = Qdiv*(0.3048**3)
        Qresidual -= Qdiv

##############################################################################
###### 		Calculate distributary flow at each BFD pass		######
###### 		Qresidual is no longer updated downstream of here	######
######		All passes will use the same input residual flow	######
######		rating curves come from Mead Allison rating curves	######
##############################################################################
        
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

with open(TribQ_out_file,mode='w') as TribQ_out:
    line = '1'
    for n in range(2,nTribs+1):
        line = '%s,%s' % (line,n)
    
    TribQ_out.write('%s\n' % line)			
	for d in range(0,ndays):
        line = '%s' % TribQ_in[d][0]
		# write tributary flow read in from original TribQ.csv
        for t in range(1,nTributaries+1):
            line = '%s,%s' % (line,TribQ_in[d][t])		# Tributary Name
														# Neches River at Beaumont TX
														# Sabine River at Ruliff TX
														# Vinton Canal
														# Calcasieu River near Kinder LA
														# Bayou Lacassine near Lake Arthur LA
														# Mermentau River at Mermentau LA
														# Vermilion River at Surrey St at Lafayette LA
														# Charenton Drainage Canal at Baldwin LA
														# GIWW at Franklin
														# Atch_cms #Atchafalaya River
														# Mississippi River Upstream (Tarbert Landing)
														# GIWW at Larose
														# Bayou Lafourche at Thibodeaux LA
														# Amite River near Denham Springs LA
														# Natalbany River at Baptist LA
														# Tickfaw River at Holden LA
														# Tangipahoa River at Robert LA
														# Tchefuncte River near Folsom LA
														# Bogue Chitto near Bush LA
														# Pearl River near Bogalusa LA
														# Wolf River near Landon MS
														# Biloxi River at Wortham MS
														# Pascagoula River at Merrill MS
														# Tensaw River near Mount Vernon AL
														# Mobile River at River Mile 31 at Bucks AL
														# Mobile1
														# Mobile 2
														# Jourdan
														# Violet Runoff
														# NE Lake Pontchartrain ungaged drainage (Bayou Bonfouca)
														# SE Lake Pontchartrain ungaged drainage (Orleans Parish)
														# S Lake Pontchartrain ungaged drainage (Jefferson Parish)
														# SW Lake Pontchartrain ungaged drainage
														# S Lake Maurepas ungaged drainage
														# NE Lake Pontchartrain ungaged drainage (Bayou LaCombe)      
        # write calculated diversion/pass flow calculated above
		line = '%s,%s' % (line,Morg_cms[d])            	# Morganza Spillway
        line = '%s,%s' % (line,BLaF_cms[d])            	# Bayou LaFourche Diversion (including additional flow for Upper Barataria Hydrologic Restoration)
        line = '%s,%s' % (line,UFWD_cms[d])            	# Union Freshwater Diversion
        line = '%s,%s' % (line,WMPD_cms[d])            	# West Maurepas Diversion
        line = '%s,%s' % (line,MSRM_cms[d])            	# Mississippi River Reintroduction in Maurepas Swamp (East Maurepas Diversion in 2017 MP)
        line = '%s,%s' % (line,EdDI_cms[d])            	# Edgard Diversion
        line = '%s,%s' % (line,Bonn_cms[d])            	# Bonnet Carre
        line = '%s,%s' % (line,MLBD_cms[d])            	# Manchac Landbridge Diversion
        line = '%s,%s' % (line,LaBr_cms[d])            	# LaBranche Hydrologic Restoration
        line = '%s,%s' % (line,DavP_cms[d])            	# Davis Pond
        line = '%s,%s' % (line,AmaD_cms[d])            	# Ama Sediment Diversion
        line = '%s,%s' % (line,IHNC_cms[d])            	# Inner Harbor Navigational Canal
        line = '%s,%s' % (line,CWDI_cms[d])            	# Central Wetlands Diversion
        line = '%s,%s' % (line,Caer_cms[d])            	# Caernarvon
        line = '%s,%s' % (line,UBrD_cms[d])            	# Upper Breton Diversion
        line = '%s,%s' % (line,MBrD_cms[d])            	# Mid-Breton Sound Diversion
        line = '%s,%s' % (line,MBaD_cms[d])            	# Mid-Barataria Diversion
        line = '%s,%s' % (line,Naom_cms[d])            	# Naomi
        line = '%s,%s' % (line,WPLH_cms[d])            	# West Point a la Hache (including additional flow for Lower Plaquemines River Sediment Plan)
        line = '%s,%s' % (line,LBaD_cms[d])            	# Lower Barataria iversion
        line = '%s,%s' % (line,LBrD_cms[d])            	# Lower Breton Diversion
        line = '%s,%s' % (line,MGPS_cms[d])            	# Mardi Gras Pass
        line = '%s,%s' % (line,Bohe_cms[d])            	# Bohemia
        line = '%s,%s' % (line,Ostr_cms[d])            	# Ostrica
        line = '%s,%s' % (line,FStP_cms[d])            	# Ft St Phillip
        line = '%s,%s' % (line,Bapt_cms[d])            	# Baptiste Collette
        line = '%s,%s' % (line,GrPa_cms[d])             # Grand Pass
        line = '%s,%s' % (line,WBay_cms[d])            	# West Bay Diversion
        line = '%s,%s' % (line,SCut_cms[d])            	# SmallCuts
        line = '%s,%s' % (line,CGap_cms[d])            	# Cubits Gap
        line = '%s,%s' % (line,PLou_cms[d])            	# Pass A Loutre
        line = '%s,%s' % (line,SPas_cms[d])            	# South Pass
        #line = '%s,%s' % (line,SWPS_cms[d])            # South West Pass calculated from curve (not used in model)
        line = '%s,%s' % (line,SWPR_cms[d])            	# South West Pass calculated from residual flow to close mass balance on Miss Riv flow in/out
		line = '%s,%s' % (line,IAFT_cms[d])            	# Increase Atchafalaya Flows to Terrebonne
		line = '%s,%s' % (line,AtRD_cms[d])      	# Atchafalaya River Diversion
        line = '%s,! %s' % (line, dates_all[d])	# Date
        
        TribQ_out.write('%s\n' % line)


###############################################################################

################################
##### Rating Curve Graphs ##### 
################################       
        
exTarb = np.arange(100000, 1510000, 10000)
z = len(exTarb)

##### Zero Arrays for Rating Curves #####

ex = np.zeros(z)
BLaF_RC = np.zeros(z)
UFWD_RC = np.zeros(z)
WMPD_RC = np.zeros(z)
MSRM_RC = np.zeros(z)
EdDI_RC = np.zeros(z)
Bonn_RC = np.zeros(z)
MLBD_RC = np.zeros(z)
LaBr_RC = np.zeros(z)
DavP_RC = np.zeros(z)
AmaD_RC = np.zeros(z)
IHNC_RC = np.zeros(z) 
CWDI_RC = np.zeros(z)
Caer_RC = np.zeros(z)
UBrD_RC = np.zeros(z)  
MBrD_RC = np.zeros(z)
Naom_RC = np.zeros(z)
MBaD_RC = np.zeros(z) 
WPLH_RC = np.zeros(z) 
LBaD_RC = np.zeros(z) 
LBrD_RC = np.zeros(z) 
MGPS_RC = np.zeros(z)  
Bohe_RC = np.zeros(z) 
Ostr_RC = np.zeros(z)  
FStP_RC = np.zeros(z)
Bapt_RC = np.zeros(z) 
GrPa_RC = np.zeros(z) 
WBay_RC = np.zeros(z) 
SCut_RC = np.zeros(z) 
CGap_RC = np.zeros(z) 
SWPS_RC = np.zeros(z) 
SPas_RC = np.zeros(z)  
PLou_RC = np.zeros(z)  
SWPR_RC = np.zeros(z)  

##### Bayou Lafourche Diversion #####

n = 0
for q in range(z):

    if exTarb[n] >= 1500:
        Qdiv = 1500
    else:
        Qdiv = exTarb[n]
    n+=1
        
    BLaF_RC[q] = Qdiv

fig, ax = plt.subplots()
ax.plot(exTarb,BLaF_RC)
ax.set(title = 'Bayou Lafourche Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.4, 0.36, 'Constant diversion flow of 1,500 cfs',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Bayou Lafourche Diversion Rating Curve')    
plt.close()

##### Union Freshwater Diversion #####

n = 0
for q in range(z):

    if exTarb[n] < 200000 or exTarb[n] >= 600000:
        Qdiv = 0
    elif exTarb[n] > 400000 and exTarb[n] < 600000:
        Qdiv = 25000
    else:
        Qdiv = 0.125*exTarb[n] - 25000
    n+=1
            
    UFWD_RC[q] = Qdiv    

fig, ax = plt.subplots()
ax.plot(exTarb,UFWD_RC)
ax.set(title = 'Union Freshwater Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.7, 0.2, 'No flow below 200,000 or above 600,000\nFlow of 25,000 between 400,000 and 600,000\nElse, flow = 0.125x-2500',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Union Freshwater Diversion Rating Curve')          
plt.close()
        
##### West Maurepas Diversion #####

#n = 0
#for q in range(z):
            
#    if exTarb[n] >= 3000:
#        Qdiv = 3000
#    else:
#        Qdiv = exTarb[n]
#    n+=1
    
#    WMPD_RC[q] = Qdiv   

#fig, ax = plt.subplots()
#ax.plot(exTarb,WMPD_RC)
#ax.set(title = 'West Maurepas Diversion Rating Curve',
#       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
#       ylabel = 'Flow Diverted (cfs)')
#plt.rc('xtick', labelsize=8)
#plt.rc('ytick', labelsize=8)
#ax.spines['right'].set_visible(False)
#ax.spines['top'].set_visible(False)
#plt.ticklabel_format(style='plain')
#ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
#plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
#ax.grid(True, which='both')
#ax.text(0.5, 0.6, 'Constant flow of 3,000 cfs',
#        fontsize = 'smaller',
#        horizontalalignment = 'center',
#        backgroundcolor = 'white',
#        transform=ax.transAxes)

#plt.savefig('West Maurepas Diversion Rating Curve')      
#plt.close()
        
##### Mississippi River Reintroduction into Maurepas Swamp #####
# cannot do the month operations with the example hydrograph of tarbert landing 

n = 0
for q in range(z):

#    if month == 4:
#        Qdiv == 10
#    elif month >= 7:
#        Qdiv == 10
#    else:
    Qdiv = max(10, (min(2000, 2466.1*np.log(exTarb[n])-21462)))
    n+=1

    MSRM_RC[q] = Qdiv  

fig, ax = plt.subplots()
ax.plot(exTarb,MSRM_RC)
ax.set(title = 'MS River Reintroduction into Maurepas Swamp Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.7, 0.6, 'Minimum operation in April and July-December\nJanuary-March and May-June operation follows the rating curve\n 2466.1*ln(Qresidual)-21462 with a maximum of 2,000 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('MS River Reintroduction in Maurepas Swamp Rating Curve')      
plt.close()

##### Edgard Diversion #####

n = 0
for q in range(z):

    if yr < yr0 + impl_yr:
        Qdiv = 0
    else:
        if Qresidual = 600000
            Qdiv = 25000
        elif Qresidual < 200000 or Qresidual > 600000 and Qresidual < 1250000:
            Qdiv = 0
        elif Qresidual >= 1250000
            Qdiv = 35000
        else:
            Qdiv = 0.0625*Qresidual - 12500
    
    EdDI_RC[q] = Qdiv

fig, ax = plt.subplots()
ax.plot(exTarb,EdDI_RC)
ax.set(title = 'Edgard Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.35, 0.77, 'Off below river flow of 200,000 cfs and between 600,000 and 1,250,000 cfs\nFlow of 25,000 cfs at river flow of 600,000 cfs\nFlow of 35,000 cfs above river flow of 1,250,000 cfs\nElse, flow = 0.125x-2500',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Edgard Diversion Rating Curve')      
plt.close()

##### Bonnet Carre Spillway #####

n = 0
for q in range(z):

    if exTarb[n] >= 1250000:
        Qdiv = exTarb[n] - 1250000
    else:
        Qdiv = 0
    n+=1
    
    Bonn_RC[q] = Qdiv

fig, ax = plt.subplots()
ax.plot(exTarb,Bonn_RC)
ax.set(title = 'Bonnet Carre Spillway Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.35, 0.77, 'River flow in excess of 1,250,000 cfs is diverted',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Bonnet Carre Spillway Rating Curve')      
plt.close()
        
##### Manchac Landbridge Diversion #####

#n = 0
#for q in range(z):
            
#    if Bonn_RC[q] >= 5000:
#        Qdiv = 5000
#    else:
#        Qdiv = Bonn_RC[q]
#    n+=1
    
#    MLBD_RC[q] = Qdiv

#fig, ax = plt.subplots()
#ax.plot(exTarb,MLBD_RC)
#ax.set(title = 'Manchac Landbridge Rating Curve',
#       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
#       ylabel = 'Flow Diverted (cfs)')
#plt.rc('xtick', labelsize=8)
#plt.rc('ytick', labelsize=8)
#ax.spines['right'].set_visible(False)
#ax.spines['top'].set_visible(False)
#plt.ticklabel_format(style='plain')
#ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
#plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
#ax.grid(True, which='both')
#ax.text(0.7, 0.6, 'Diversion flow of 5,000 cfs at Bonnet Carre flow above 5,000 cfs',
#        fontsize = 'smaller',
#        horizontalalignment = 'center',
#        backgroundcolor = 'white',
#        transform=ax.transAxes)

#plt.savefig('Manchac Landbridge Rating Curve')   
#plt.close()

##### Davis Pond Freshwater Diversion #####

n = 0
for q in range(z):

    Qdiv = min(max(0,1269.1454*np.log(exTarb[n]) - 9932.94805), 10594.3487)
    n+=1
    
    DavP_RC[q] = Qdiv

fig, ax = plt.subplots()
ax.plot(exTarb,DavP_RC)
ax.set(title = 'Davis Pond Freshwater Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.7, 0.55, 'Diversion flow of rating curve\n1269.1454*ln(Qresidual)-9932.94805\nwith a maximum of 10,594 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Davis Pond Freshwater Diversion Rating Curve') 
plt.close()
       
##### LaBranche Hydrologic Restoration #####

n = 0
for q in range(z):

    if exTarb[n] >= 750:
        Qdiv = 750
    else:
        Qdiv = exTarb[n]
    n+=1
    
    LaBr_RC[q] = Qdiv  
    
fig, ax = plt.subplots()
ax.plot(exTarb,LaBr_RC)
ax.set(title = 'LaBranche Hydrologic Restoration Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.7, 0.6, 'Constant diversion flow of 750 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('LaBranche Hydrologic Restoration Rating Curve')  
plt.close()
            
##### Ama Sediment Diversion #####

n = 0
for q in range(z):
        
    if exTarb[n] < 200000:
        Qdiv = 0
    else:
        Qdiv = 0.0625*exTarb[n]-12500
    n+=1
    
    AmaD_RC[q] = Qdiv  
    
fig, ax = plt.subplots()
ax.plot(exTarb,AmaD_RC)
ax.set(title = 'Ama Sediment Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.65, 0.1, 'Diversion flow of rating curve 0.0625*Qresidual-12500\nat river flows above 200,000 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Ama Sediment Diversion Rating Curve')     
plt.close()
            
##### Inner Harbor Navigational Canal #####

n = 0
for q in range(z):

    if exTarb[n] >= 0:
        Qdiv = exTarb[n]*0.011297797
    else:
        Qdiv = exTarb[n]
    n+=1
    
    IHNC_RC[q] = Qdiv  

fig, ax = plt.subplots()
ax.plot(exTarb,IHNC_RC)
ax.set(title = 'Inner Harbor Navigational Canal Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.6, 0.1, 'Diversion flow of rating curve 0.011297797*Qresidual',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Inner Harbor Navigational Canal Rating Curve')  
plt.close()
            
##### Central Wetlands Diversion #####

n = 0
for q in range(z):

    if exTarb[n] >= 5000:
        Qdiv = 5000
    else:
        Qdiv = exTarb[n]
    n+=1
    
    CWDI_RC[q] = Qdiv  

fig, ax = plt.subplots()
ax.plot(exTarb,CWDI_RC)
ax.set(title = 'Central Wetlands Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.7, 0.6, 'Constant diversion flow of 5,000 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Central Wetlands Diversion Rating Curve')   
plt.close()
            
##### Caernarvon Freshwater Diversion #####

n = 0
for q in range(z):

    Qdiv = min(max(0,701.9143*np.log(exTarb[n])-5299.908567),8828.66655)
    n+=1
    
    Caer_RC[q] = Qdiv  

fig, ax = plt.subplots()
ax.plot(exTarb,Caer_RC)
ax.set(title = 'Caernarvon Freshwater Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.55, 0.1, 'Diversion flow of rating curve 701.9143*ln(Qresidual)-5299.90856\nwith a maximum of 8828.66655 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Caernarvon Freshwater Diversion Rating Curve')    
plt.close()

##### Upper Breton Diversion #####

    # 250,000 cfs #
    
n = 0
for q in range(z):
    
    if exTarb[n] < 200000:
        Qdiv = 0
    else:
        Qdiv = 0.3125*exTarb[n]-62500
    n+=1
    
    UBrD_RC[q] = Qdiv 

fig, ax = plt.subplots()
ax.plot(exTarb,UBrD_RC)
ax.set(title = 'Upper Breton Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.65, 0.1, 'Diversion flow with rating curve\n0.3125*Qresidual-62500 at river flows above 200,000 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Upper Breton Diversion Rating Curve')   
plt.close()
        
    # 75,000 cfs #
        
#n = 0
#for q in range(z):
        
#    if exTarb[n] < 200000:
#        Qdiv = 0
#    else:
#        Qdiv = 0.3048*exTarb[n]-18750
#    n+=1
     
#    UBrD_RC[q] = Qdiv  

#fig, ax = plt.subplots()
#ax.plot(exTarb,UBrD_RC)
#ax.set(title = 'Upper Breton Diversion Rating Curve',
#       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
#       ylabel = 'Flow Diverted (cfs)')
#plt.rc('xtick', labelsize=8)
#plt.rc('ytick', labelsize=8)
#ax.spines['right'].set_visible(False)
#ax.spines['top'].set_visible(False)
#plt.ticklabel_format(style='plain')
#ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
#plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
#ax.grid(True, which='both')
#ax.text(0.65, 0.1, 'Diversion flow of rating curve\n0.3048*Qresidual-18750 at river flows above 200,000 cfs',
#        fontsize = 'smaller',
#        horizontalalignment = 'center',
#        backgroundcolor = 'white',
#        transform=ax.transAxes)

#plt.savefig('Upper Breton Diversion Rating Curve')     
#plt.close()
            
##### Mid Breton Sediment Diversion #####

n = 0
for q in range(z):

    Qdiv = max(5000,0.06667*exTarb[n]-8333)
    n+=1
    
    MBrD_RC[q] = Qdiv

fig, ax = plt.subplots()
ax.plot(exTarb,MBrD_RC)
ax.set(title = 'Mid Breton Sediment Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.65, 0.15, 'Diversion flow of rating curve\n0.06667*Qresidual-8333 with a minimum of 5,000 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Mid Breton Sediment Diversion Rating Curve')      
plt.close()
            
##### Naomi Siphon Diversion #####

n = 0
for q in range(z):

    Qdiv = min(max(0,281.044708*np.log(exTarb[n])-2500.93169),2118.87997)
    n+=1
    
    Naom_RC[q] = Qdiv 

fig, ax = plt.subplots()
ax.plot(exTarb,Naom_RC)
ax.set(title = 'Naomi Siphon Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.7, 0.1, 'Diversion flow of rating curve\n281.044708*ln(Qresidual)-2500.93169\nwith a maximum of 2118.87997 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Naomi Siphon Diversion Rating Curve')   
plt.close()

###   Mid-Barataria Sediment Diversion    ###
            
   ###### 75k @ 1.0 m ######
   
#n = 0
#for q in range(z):
        
#    if exTarb[n] < 200000:
#        Qdiv = 0
#    else:
#        Qdiv = 0.09375*exTarb[n] - 18750
#    n+=1
     
#    MBaD_RC[q] = Qdiv

#fig, ax = plt.subplots()
#ax.plot(exTarb,MBaD_RC)
#ax.set(title = 'Mid-Barataria Sediment Diversion Rating Curve',
#       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
#       ylabel = 'Flow Diverted (cfs)')
#plt.rc('xtick', labelsize=8)
#plt.rc('ytick', labelsize=8)
#ax.spines['right'].set_visible(False)
#ax.spines['top'].set_visible(False)
#plt.ticklabel_format(style='plain')
#ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
#plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
#ax.grid(True, which='both')
#ax.text(0.65, 0.1, 'Diversion flow of rating curve\n0.09375*residual - 18750 at river flows above 200,000',
#        fontsize = 'smaller',
#        horizontalalignment = 'center',
#        backgroundcolor = 'white',
#        transform=ax.transAxes)

#plt.savefig('Mid-Barataria Sediment Diversion Rating Curve')    
#plt.close()
        
    ###### 250k @ 1.0 m ######
    
#n = 0
#for q in range(z):
        
#    if exTarb[n] < 200000:
#        Qdiv = 0
#    else:
#        Qdiv = 0.3125*exTarb[n]-62500
#    n+=1
     
#    MBaD_RC[q] = Qdiv

#fig, ax = plt.subplots()
#ax.plot(exTarb,MBaD_RC)
#ax.set(title = 'Mid-Barataria Sediment Diversion Rating Curve',
#       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
#       ylabel = 'Flow Diverted (cfs)')
#plt.rc('xtick', labelsize=8)
#plt.rc('ytick', labelsize=8)
#ax.spines['right'].set_visible(False)
#ax.spines['top'].set_visible(False)
#plt.ticklabel_format(style='plain')
#ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
#plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
#ax.grid(True, which='both')
#ax.text(0.65, 0.1, 'Diversion flow of rating curve\n0.3125*residual - 62500 at river flows above 200,000',
#        fontsize = 'smaller',
#        horizontalalignment = 'center',
#        backgroundcolor = 'white',
#        transform=ax.transAxes)

#plt.savefig('Mid-Barataria Sediment Diversion Rating Curve')    
#plt.close()
        
   ###### 35k - 75k @ 1.0 m ######
   
#n = 0
#for q in range(z):
        
#    if exTarb[n] < 200000:
#        Qdiv = 0
#    else:
#        Qdiv = 0.04375*exTarb[n]-8750
#    n+=1
     
#    MBaD_RC[q] = Qdiv

#fig, ax = plt.subplots()
#ax.plot(exTarb,MBaD_RC)
#ax.set(title = 'Mid-Barataria Sediment Diversion Rating Curve',
#       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
#       ylabel = 'Flow Diverted (cfs)')
#plt.rc('xtick', labelsize=8)
#plt.rc('ytick', labelsize=8)
#ax.spines['right'].set_visible(False)
#ax.spines['top'].set_visible(False)
#plt.ticklabel_format(style='plain')
#ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
#plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
#ax.grid(True, which='both')
#ax.text(0.65, 0.1, 'Diversion flow of rating curve\n0.04375*residual - 8750 at river flows above 200,000',
#        fontsize = 'smaller',
#        horizontalalignment = 'center',
#        backgroundcolor = 'white',
#        transform=ax.transAxes)

#plt.savefig('Mid-Barataria Sediment Diversion Rating Curve')  
#plt.close()
        
   ###### 75k @ 1.25 m , 5k min ######
   
n = 0
for q in range(z):
        
    Qdiv = max(5000, 0.06667*exTarb[n]-8333)
    n+=1
    
    MBaD_RC[q] = Qdiv

fig, ax = plt.subplots()
ax.plot(exTarb,MBaD_RC)
ax.set(title = 'Mid-Barataria Sediment Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both')
ax.text(0.65, 0.1, 'Diversion flow of rating curve\n0.06667*residual - 8333 with a minimum of 5,000 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Mid-Barataria Sediment Diversion Rating Curve')  
plt.close()
        
##### West Pointe a la Hache #####

n = 0
for q in range(z):
        
    Qdiv = min(max(0, 456.35377*np.log(exTarb[n])-4049.4586),2118.87997)
    n+=1
    
    WPLH_RC[q] = Qdiv 

fig, ax = plt.subplots()
ax.plot(exTarb,WPLH_RC)
ax.set(title = 'West Pointe a la Hache Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.7, 0.1, 'Diversion flow of rating curve\n456.35377*ln(Qresidual)-4049.4586\nwith a maximum of 2118.87997 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('West Pointe a la Hache Rating Curve') 
plt.close()
            
##### Lower Barataria Diversion #####

n = 0
for q in range(z):

    if exTarb[n] < 200000:
        Qdiv = 0
    else:
        Qdiv = 0.0625*exTarb[n]-12500
    n+=1
    
    LBaD_RC[q] = Qdiv 

fig, ax = plt.subplots()
ax.plot(exTarb,LBaD_RC)
ax.set(title = 'Lower Barataria Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.65, 0.1, 'Diversion flow at rating curve of\n0.0625*residual-12500 at river flows above 200,000 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Lower Barataria Diversion Rating Curve')  
plt.close()
            
##### Lower Breton Diversion #####

n = 0
for q in range(z):
            
    if exTarb[n] < 200000:
        Qdiv = 0
    else:
        Qdiv = 0.0625*exTarb[n]-12500
    n+=1
    
    LBrD_RC[q] = Qdiv 

fig, ax = plt.subplots()
ax.plot(exTarb,LBrD_RC)
ax.set(title = 'Lower Breton Diversion Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.63, 0.1, 'Diversion flow of rating curve\n0.0625*residual-12500 at river flows above 200,000 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Lower Breton Diversion Rating Curve')   
plt.close()
        
##### Mardi Gras Pass #####

n = 0
for q in range(z):
            
    Qdiv = 0.0153*exTarb[n]+276.2369
    n+=1
    
    MGPS_RC[q] = Qdiv

fig, ax = plt.subplots()
ax.plot(exTarb,MGPS_RC)
ax.set(title = 'Mardi Gras Pass Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.7, 0.4, 'Qdiv = 0.0153x+276.2369',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Mardi Gras Pass Rating Curve')    
plt.close()
            
##### Bohemia Spillway #####

n = 0
for q in range(z):
            
    if exTarb[n] < 930000:
        Qdiv = 0
    else:
        Qdiv = 1.4/100*exTarb[n]
    n+=1
    
    Bohe_RC[q] = Qdiv 

fig, ax = plt.subplots()
ax.plot(exTarb,Bohe_RC)
ax.set(title = 'Bohemia Spillway Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.4, 0.8, 'Diversion flow of rating curve\n1.4/100*Qresidual at river flows above 930,000 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Bohemia Spillway Rating Curve')  
plt.close()
            
##### Ostrica Lock #####

n = 0
for q in range(z):
        
    if exTarb[n] < 800000:
        Qdiv = 0
    else:
        Qdiv = 5.2/100*exTarb[n]
    n+=1
        
    Ostr_RC[q] = Qdiv  

fig, ax = plt.subplots()
ax.plot(exTarb,Ostr_RC)
ax.set(title = 'Ostrica Lock Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.4, 0.8, 'Diversion flow of rating curve 5.2/100*Qresidual\nat river flows above 800,000 cfs',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Ostrica Lock Rating Curve')  
plt.close()

##### Fort St. Philip #####

n = 0
for q in range(z):
            
    Qdiv = 0.1011*exTarb[n]-25159
    n+=1
        
    FStP_RC[q] = Qdiv 

fig, ax = plt.subplots()
ax.plot(exTarb,FStP_RC)
ax.set(title = 'Fort St. Philip Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.7, 0.45, 'Qdiv = 0.1011x-25159',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Fort St Philip Rating Curve')    
plt.close()

##### Baptiste Collette #####

n = 0
for q in range(z):
            
    Qdiv = 0.1031*exTarb[n]-5631
    n+=1
        
    Bapt_RC[q] = Qdiv  

fig, ax = plt.subplots()
ax.plot(exTarb,Bapt_RC)
ax.set(title = 'Baptiste Collette Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.7, 0.45, 'Qdiv = 0.1031x-5631',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Baptiste Collette Rating Curve')  
plt.close()

##### Grand Pass #####

n = 0
for q in range(z):
            
    Qdiv = 0.0915*exTarb[n]+4288
    n+=1
        
    GrPa_RC[q] = Qdiv  

fig, ax = plt.subplots()
ax.plot(exTarb,GrPa_RC)
ax.set(title = 'Grand Pass Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.7, 0.45, 'Qdiv = 0.0915x+4288',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Grand Pass Rating Curve')  
plt.close()

##### West Bay #####

n = 0
for q in range(z):
            
    Qdiv = 0.0653*exTarb[n]-2075
    n+=1
        
    WBay_RC[q] = Qdiv  

fig, ax = plt.subplots()
ax.plot(exTarb,WBay_RC)
ax.set(title = 'West Bay Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.7, 0.45, 'Qdiv = 0.0653x-2075',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('West Bay Rating Curve') 
plt.close()

##### Small Cuts #####

n = 0
for q in range(z):
            
    Qdiv = 0.0025*exTarb[n]+10196
    n+=1
        
    SCut_RC[q] = Qdiv  

fig, ax = plt.subplots()
ax.plot(exTarb,SCut_RC)
ax.set(title = 'Small Cuts Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.7, 0.45, 'Qdiv = 0.0025x+10196',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Small Cuts Rating Curve')   
plt.close()

##### Cubit's Gap #####

n = 0
for q in range(z):
            
    Qdiv = 0.1319*exTarb[n]-19939
    n+=1
        
    CGap_RC[q] = Qdiv  

fig, ax = plt.subplots()
ax.plot(exTarb,CGap_RC)
ax.set(title = "Cubit's Gap Rating Curve",
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.7, 0.45, 'Qdiv = 0.1319x-19939',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig("Cubit's Gap Rating Curve")    
plt.close()

##### Southwest Pass Ratings Curve #####

n = 0
for q in range(z):
            
    Qdiv = 0.4189*exTarb[n]-64787
    n+=1
        
    SWPS_RC[q] = Qdiv 

fig, ax = plt.subplots()
ax.plot(exTarb,SWPS_RC)
ax.set(title = 'Southwest Pass Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.7, 0.45, 'Qdiv = 0.4189x-64787',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Southwest Pass Rating Curve')   
plt.close()
 
##### South Pass #####

n = 0
for q in range(z):
            
    Qdiv = 0.0858*exTarb[n]+2332
    n+=1
        
    SPas_RC[q] = Qdiv 

fig, ax = plt.subplots()
ax.plot(exTarb,SPas_RC)
ax.set(title = 'South Pass Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.7, 0.475, 'Qdiv = 0.0858x+2332',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('South Pass Rating Curve')    
plt.close()

##### Pass a Loutre #####

n = 0
for q in range(z):
            
    Qdiv = 0.0543*exTarb[n]+15700
    n+=1
        
    PLou_RC[q] = Qdiv 

fig, ax = plt.subplots()
ax.plot(exTarb,PLou_RC)
ax.set(title = 'Pass a Loutre Rating Curve',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
ax.text(0.7, 0.435, 'Qdiv = 0.0543x+15700',
        fontsize = 'smaller',
        horizontalalignment = 'center',
        backgroundcolor = 'white',
        transform=ax.transAxes)

plt.savefig('Pass a Loutre Rating Curve')  
plt.close()
    
##### Southwest Pass Residual #####

n = 0
for q in range(z):
           
    Qdiv = exTarb[n] - (MGPS_RC[q] + Bohe_RC[q] + Ostr_RC[q] + FStP_RC[q] + Bapt_RC[q] + GrPa_RC[q] + WBay_RC[q] + SCut_RC[q] + CGap_RC[q] + SPas_RC[q] + PLou_RC[q])
    n+=1  
    
    SWPR_RC[q] = Qdiv 

fig, ax = plt.subplots()
ax.plot(exTarb,SWPR_RC)
ax.set(title = 'Southwest Pass Residual',
       xlabel = 'Mississippi River Flow at Baton Rouge (cfs)',
       ylabel = 'Flow Diverted (cfs)')
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.ticklabel_format(style='plain')
ax.xaxis.set_major_locator(plt.MultipleLocator(200000))
plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
#plt.setp(ax.get_xticklabels(), rotation = 25)
ax.grid(True, which='both') 
#ax.text(0.7, 0.5, 'flow',
#        fontsize = 'smaller',
#        horizontalalignment = 'center',
#        backgroundcolor = 'white',
#        transform=ax.transAxes)

plt.savefig('Southwest Pass Residual')
plt.close()
