# This script is designed to build daily flow timeseries of flow diversions off of the Mississippi River, including the distributary network in the Birdsfoot Delta.
# input/output flowrates are saved in cubic meters per second (cms), but all operational rules are defined in cubic feet per second (cfs)


import numpy as np

daily_input_file = r'D:/Data/ICM/MissRiver_Tarbert_daily_flow_cms_2019-2070.csv'
daily_input_flow_column = [10]       # column number input file that has the data to be used as the upstream timeseries (note that Python uses a 0 index...so a value of 10 here is actually the 11th column in the input data

daily_input_year_column = [0]

# read in Mississippi River @ Tarbert Landing (input data is in cms)
MissTarb_cms = np.genfromtxt(daily_input_file,delimiter=',', dtype='float',skip_header=header_rows,usecols=daily_input_flow_column)
MissTarb_cfs = MissTarb_cms / 0.3048**3

# read in date timeseries
dates_all = np.genfromtxt(daily_input_file,delimiter=',', dtype='string',skip_header=header_rows,usecols=daily_input_year_column)
ndays = len(dates_all)
yr0 = 2019      # this is the first year that will be used to determine what calendar year diversions are activated

# build zero arrays for each diversion timeseries
Atch_cfs = np.zeros(ndays)      # Atchafalaya River
Morg_cfs = np.zeros(ndays)      # Morganza Floodway
MBSD_cfs = np.zeros(ndays)      # Mid-Barataria Sediment Diversion


for d in range(0,ndays):
        
        date = dates_all[d]
        year = date[0:4]                    # this will work if date is formatted as YYYYMMDD, or YYYY-MM-DD, etc.
#        year = date.split('-')[2]           # this will work if date is formatted as MM-DD-YYYY
                
        Qresidual = MissTarb_cfs[d]
        
        ##############################
        ###   Atchafalaya River    ###
        ##############################
        # Assume 70/30 flow split at Old River Control Structure
        # 70% of Mississippi River flow is kept in main channel (this is the observed discharge at Tarbert Landing)
        # 30% of Mississippi River flow is diverted into Atchafalaya River

        Qdiv = 0.7*Qres_cfs/0.3
        Atch_cfs[d] = Qdiv
        Qresidual -= Qdiv
        
        ##############################
        ###   Morganza Floodway    ###
        ##############################
        # not active, set to zero (this is redundant since Morg_cfs is already set as a zero array above)
        
        Qdiv = 0
        Morg_cfs[d] = Qdiv
        Qresidual -= Qdiv
        
        
        Work downstream from here updating each diversion with the operations rule


        #############################################
        ###   Mid-Barataria Sediment Diversion    ###
        #############################################
        impl_yr = 0
        
        if yr < yr0 + impl_yr:
            Qdiv = 0
        else:
            if Qresidual <= 100000 :
                Qdiv = 5000
            elif Qresidual > 1000000:
                Qdiv = 75000
            else:
                Qdiv = rating curve calculation
            
        
        MBSD_cfs[d] = Qdiv
        Qresidual -= Qdiv
        
        
        
        