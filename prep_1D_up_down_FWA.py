import numpy as np
import shutil
import os
import sys

s = sys.argv[1]      #'S06'
g = sys.argv[2]      #'G501'

os.chdir('%s/%s/hydro' % (s,g) )
infol = '../../../FWOA_boundary_conditions' # relative path to FWOA BC from S##/G###/hydro directory

print( 'Setting up files for %s %s' % (s,g) )

print( 'copying group-specific tributary file for %s %s' % (s,g) )
shutil.copyfile('%s/%s_%s_TribQ.csv' % (infol,s,g),'TribQ.csv' )
# do not need to worry about copying over TribF and TribS since the sediment concentrations do not change since they are multiplied by the TribQ

#'%s/%s_Meteorology.csv' % (infol,s),    '%s/%s_MissRToC.csv' % (infol,s),   '%s/%s_PET' % (infol,s),    '%s/%s_Precip_With_Storms.csv' % (infol,s),'%s/%s_BCToC2.dat' % (infol,s),'%s/%s_TideData.csv' % (infol,s)
infiles = ['Meteorology.csv','MissRToC.csv','PET.csv','Precip.csv','BCToC2.dat','TideData.csv']

print( 'copying scenario-specific environmental forcing files for %s %s' % (s,g) )

for newf in infiles:
    origf = '%s/%s_%s' % (infol,s,newf)
    shutil.copyfile( origf, newf )


print( 'prepping 1D input files for %s %s' % (s,g) )
tribQ_file = 'TribQ.csv'
tribF_file = 'TribF.csv'
tribS_file = 'TribS.csv'
temp_file  = 'Meteorology.csv'

# 1D channel reaches
rch_trib = {}
rch_trib['ATCH']                = 10
rch_trib['WLO']                 = 10 # WLO does not need an upstream flow since it is connected to a 2D compartment at upstream end - still reading in data, but will write zero values to input file below
rch_trib['lower_Mississippi']   = 11 # need to update so that lowerMiss used flow at Belle Chasse (residual after Caernarvon)
rch_trib['CSC']                 = 4

# 1D nodes that have lateral flow links
# this section needs to match (or can be read from) region_input.txt
rch_lat = {}
rch_lat['ATCH']                = [126,130,256,274,284,351,379,468,509,528,575,611,615,634,645,667,694,719,737,741,753,823,824,954,1022,1026,1085,1088,1114,1142,1178,1204,1206,1260,1305,1337,1346,1385,1393,1398,1400,1405,1410,1436,1437,1445,1449,1479,1483,1490,1505,1518,1519,1525,1534,1571,1592,1597,1599,1600,1605,1614,1618,1626,1646,1655,1660,1664,1670,1676,1680,1695,1702,1718,1725,1742,1757,1760]
rch_lat['WLO']                 = [17,19,23,36,37,42,43,49,50,60,62,67,68,73,75,76,77,78,83,84,86,89,91]
rch_lat['lower_Mississippi']   = [32,55,74,124,145,148,159,177,233,258,260,274,297,302,318,320,327,333,334,345,349,362,368,392,413]
rch_lat['CSC']                 = [187,210,223,239,243,245,248,249,255,256,264,265,270,286,296,298,302,308,310,317,318,319] #322 #230

MRdiversions_upstream_of_BelleChasse_TribQcols = [37,38,39,40,41,42,43,44,45,46,47,48,49,50]  
# TribQ.csv column #37 Bayou LaFourche Diversion
# TribQ.csv column #38 Union Freshwater Diversion
# TribQ.csv column #39 West Maurepas Diversion
# TribQ.csv column #40 Mississippi River Reintroduction in Maurepas Swamp (East Maurepas Diversion in 2017 MP)
# TribQ.csv column #41 Edgard Diversion
# TribQ.csv column #42 Bonnet Carre
# TribQ.csv column #43 Manchac Landbridge Diversion
# TribQ.csv column #44 LaBranche Hydrologic Restoration
# TribQ.csv column #45 Davis Pond
# TribQ.csv column #46 Ama Sediment Diversion
# TribQ.csv column #47 Inner Harbor Navigational Canal
# TribQ.csv column #48 Central Wetlands Diversion
# TribQ.csv column #49 Caernarvon
# TribQ.csv column #50 Upper Breton Diversion


MRdiversions_downstream_of_BelleChasse_1Dnodes = {}
MRdiversions_downstream_of_BelleChasse_1Dnodes[32]  = 51 # lateral flow at node 32 is Mid-Breton             (TribQ.csv column # = 51)
MRdiversions_downstream_of_BelleChasse_1Dnodes[55]  = 53 # lateral flow at node 55 is Naomi siphon           (TribQ.csv column # = 53)
MRdiversions_downstream_of_BelleChasse_1Dnodes[74]  = 52 # lateral flow at node 74 is Mid-Barataria          (TribQ.csv column # = 52)
MRdiversions_downstream_of_BelleChasse_1Dnodes[124] = 54 # lateral flow at node 124 is West Point a la Hache (TribQ.csv column # = 54)
MRdiversions_downstream_of_BelleChasse_1Dnodes[177] = 56 # lateral flow at node 177 is lower-Breton           (TribQ.csv column # = 56)

n_1D_div = len( MRdiversions_downstream_of_BelleChasse_1Dnodes.keys() )
print(' FWA has 12 diversions downstream of Belle Chasse that are lateral flow in the 1D model:')
print('      - Mid-Breton Diversion       is lateral flow at 1D node 32')
print('      - Naomi Siphon               is lateral flow at 1D node 55')
print('      - Mid-Barataria Diversion    is lateral flow at 1D node 74')
print('      - W. Point a la Hache Siphon is lateral flow at 1D node 124')
print('      - Lower-Breton Diversion     is lateral flow at 1D node 177')

Atchdiversions_downstream_of_MorganCity_1Dnodes = {}
Atchdiversions_downstream_of_MorganCity_1Dnodes[1436]  = 69 # lateral flow at node 1436 is Increase Atch Flow Terrebonne     (TribQ.csv column # = 69)
Atchdiversions_downstream_of_MorganCity_1Dnodes[1600]  = 70 # lateral flow at node 1600 is Atch River Diversion              (TribQ.csv column # = 70)

# 1D lateral links that have timeseries boundaries instead of coupling to 2D model
# the links below will have boundary condition timeseries - if not listed, the remaining lateral links from above will have a timeseries with values of 0.0

lat_ts_trib = {}
lat_ts_trib['ATCH'] = Atchdiversions_downstream_of_MorganCity_1Dnodes
lat_ts_trib['WLO'] = {}
lat_ts_trib['lower_Mississippi'] = MRdiversions_downstream_of_BelleChasse_1Dnodes
lat_ts_trib['CSC'] = {}

#moveon = 'n'
#moveon = input('This run (%s %s) has %02d Mississippi River diversions downstream of Belle Chasse. Is this correct? [y]es or [n]o?' % (s,g,n_1D_div) )
#if moveon == 'n':
#    sys.exit('Double check diversion settings and re-run this script. Exiting now.')
#else:
#    print('OK. Moving forward with setting up 1D channel models with %02d Mississippi River diversions downstream of Belle Chasse.' % n_1D_div )


for rch in rch_trib.keys():
    print(' Building 1D upstream/downstream input files for reach: %s' % rch)
    
    trib_number = rch_trib[rch]
    latlinks = rch_lat[rch]
    
    upQfile =      '%s/HYDRO/input/Upstream/Discharge' % rch
    downWLfile =   '%s/HYDRO/input/Downstream/WL' % rch

    upSalfile =    '%s/SAL/input/Upstream/upstream_sal' % rch
    downSalfile =  '%s/SAL/input/Downstream/downstream_sal' % rch
    
    upFinefile =   '%s/FINE/input/Upstream/upstream_fine' % rch
    downFinefile = '%s/FINE/input/Downstream/downstream_fine' % rch

    upSandfile =   '%s/SAND/input/Upstream/upstream_sand' % rch
    downSandfile = '%s/SAND/input/Downstream/downstream_sand' % rch
    
    Tairfile =     '%s/TMP/input/Tbk/Tback' % rch
    Twfile =       '%s/TMP/input/Upstream/upstream_temp' % rch
    downTmpfile =  '%s/TMP/input/Downstream/downstream_temp' % rch
   
    pad_days = [1,2]    # the number of extra days that will be padded to the end of each input file to account for interpolation in time on last days
    default_val = 0.0
    trib_col = trib_number - 1
    date_col = 71
    
    # read in daily timeseries as strings so that the datestring is maintained
    Q_in    = np.genfromtxt(tribQ_file,usecols=[trib_col,date_col],delimiter=',',dtype=str,skip_header=1)
    Fine_in = np.genfromtxt(tribF_file,usecols=[trib_col,date_col],delimiter=',',dtype=str,skip_header=1)
    Sand_in = np.genfromtxt(tribS_file,usecols=[trib_col,date_col],delimiter=',',dtype=str,skip_header=1)
    Temp_in = np.genfromtxt(temp_file,usecols=[0,1],delimiter=',',dtype=str,skip_header=1)
    
    # read in daily timeseries flows for all diversions upstream of Belle Chasse to build residual flow at Belle Chasse
    # can read as float since date value is not needed
    if rch == 'lower_Mississippi' :
        us_dv = MRdiversions_upstream_of_BelleChasse_TribQcols
        us_dv_cols = np.subtract(us_dv,1)                       # convert column number to zero-based-index for np.genfromtxt
        Q_in_us_dv = np.genfromtxt(tribQ_file,usecols=us_dv_cols,delimiter=',',dtype=float,skip_header=1)
    
    
    Qdays = len(Q_in[:])
    Finedays = len(Fine_in[:])
    Sanddays = len(Sand_in[:])
    
    if Qdays != Finedays:
        print('\n  %s and %s are not the same length. Check files.' % (tribQ_file,tribF_file))
        quit()
    elif Qdays != Sanddays:
        print('\n  %s and %s are not the same length. Check files.' % (tribQ_file,tribS_file))
        quit()
    elif Finedays != Sanddays:
        print('\n  %s and %s are not the same length. Check files.' % (tribF_file,tribS_file))
        quit()
    elif Qdays != len(Temp_in[:]):
        print('\n  %s and %s are not the same length. Check files.' % (tribQ_file,temp_file))
        quit()

    for d in range(0,Qdays):
        date = Q_in[d][1]             # date format = '!   YYYYMMDD'
        yr = date[-8:-4]
        mn = date[-4:-2]
        day = date[-2:]
        # write number of days that are included in the file - varies based on leap year - needs to be longer than one year to account for interpolation on last day 
        if int(yr) in range(2000,4001,4):
            dtall = 365 + pad_days[-1]      # the last day of the year is 365 for leap years if starting with day 0
        else:
            dtall = 364 + pad_days[-1]
        
        # if building Wax Lake Outlet timeseries, set to zero since this reach is connected to a 2D compartment upstream and does not need this input data
        if rch == 'WLO' :
            Qval = 0.0
        # if building Miss. Riv. timeseries, need the residual flow at Belle Chasse, so subtract all upstream diversion flows
        elif rch == 'lower_Mississippi' :
            Qval = float(Q_in[d][0]) - sum(Q_in_us_dv[d])
        else:
            Qval = Q_in[d][0] 
        Fval = Fine_in[d][0]
        Fval = Fine_in[d][0]
        Sval = Sand_in[d][0]
        Tairval = Temp_in[d][0]
        Twval = Temp_in[d][1]

        ###########################################################################
        ###   build files that have timeseries data at upstream or downstream   ###
        ###########################################################################    
        if mn == '01':
            if day == '01':
                dt = 0
    
                upQoutfile = '%s_%s.txt' % (upQfile,yr)
                upQout = open(upQoutfile,mode='w')
                
                downWLoutfile = '%s_%s.txt' % (downWLfile,yr)
                downWLout = open(downWLoutfile,mode='w')
    
                upFineoutfile = '%s_%s.txt' % (upFinefile,yr)
                upFineout = open(upFineoutfile,mode='w')
                upFineout.write('time(m)    Conc_group1(mg/l) Conc_group2(mg/l)\n%d 1\n' % dtall)
                
                upSandoutfile = '%s_%s.txt' % (upSandfile,yr)
                upSandout = open(upSandoutfile,mode='w')
                upSandout.write('time(m)    Conc_group1(mg/l) Conc_group2(mg/l)\n%d 1\n' % dtall)
                
                Tairoutfile = '%s_%s.txt' % (Tairfile,yr)
                Tairout = open(Tairoutfile,mode='w')
                Tairout.write('time(m)    Tbk (oC)\n%d\n' % dtall)
    
                Twoutfile = '%s_%s.txt' % (Twfile,yr)
                Twout = open(Twoutfile,mode='w')
                Twout.write('time(m)    Conc_group1(mg/l) Conc_group2(mg/l)\n%d 1\n' % dtall)
    
        upQout.write('%s\t%s\n' % (dt, Qval))
        downWLout.write('%s\t%s\n' % (dt, default_val))
        upFineout.write('%s\t%s\n' % (dt, Fval))
        upSandout.write('%s\t%s\n' % (dt, Sval))
        Tairout.write('%s\t%s\n' % (dt, Tairval))
        Twout.write('%s\t%s\n' % (dt, Twval))
        
        dt += 1440
        
        # on last day of year pad end of file with additional daily values as an extra timestep for iteration functions. then close file.
        if mn == '12':
            if day == '31':
                for pad in pad_days:  # this will pad the bottom of the daily record based on a set  number of days set above
                    upQout.write('%s\t%s\n' % (dt,Qval))
                    downWLout.write('%s\t%s\n' % (dt, default_val))
                    upFineout.write('%s\t%s\n' % (dt, Fval))
                    upSandout.write('%s\t%s\n' % (dt, Sval))
                    Tairout.write('%s\t%s\n' % (dt, Tairval))
                    Twout.write('%s\t%s\n' % (dt, Twval))
                
                    dt += 1440
                
                # close timeseries files
                upQout.close()
                downWLout.close()
                upFineout.close()
                upSandout.close()
                Tairout.close()
                Twout.close()
                
                ##################################################################
                ###   build files that have constant value for all timesteps   ###
                ##################################################################

                upSaloutfile = '%s_%s.txt' % (upSalfile,yr)
                upSalout = open(upSaloutfile,mode='w')
                upSalout.write('time(m)	Conc_group1(mg/l) Conc_group2(mg/l) ..,\n2 1\n0.00         0. \n528480.      0.')
                upSalout.close()

                downSaloutfile = '%s_%s.txt' % (downSalfile,yr)
                downSalout = open(downSaloutfile,mode='w')
                downSalout.write('time(m)	Conc_group1(mg/l) Conc_group2(mg/l) ..,\n2 1\n0.00         25. \n528480.      25.')
                downSalout.close()    

                downFineoutfile = '%s_%s.txt' % (downFinefile,yr)
                downFineout = open(downFineoutfile,mode='w')
                downFineout.write('time(m)	Conc_group1(mg/l) Conc_group2(mg/l) ..,\n2 1\n0.00         0. \n528480.      0.')
                downFineout.close()    
    
                downSandoutfile = '%s_%s.txt' % (downSandfile,yr)
                downSandout = open(downSandoutfile,mode='w')
                downSandout.write('time(m)	Conc_group1(mg/l) Conc_group2(mg/l) ..,\n2 1\n0.00         0. \n528480.      0.')
                downSandout.close()
                            
                downTmpoutfile = '%s_%s.txt' % (downTmpfile,yr)
                downTmpout = open(downTmpoutfile,mode='w')
                downTmpout.write('time(m)	Conc_group1(mg/l) Conc_group2(mg/l) ..,\n2 1\n0.00        10. \n528480.     10.')
                downTmpout.close()
                
                #######################################################################
                ###  copy files that uses the same timeseries for every model year  ###
                #######################################################################
                
                refWindfile_orig = '%s/TMP/input/Wind/U10_2010.txt' % rch   
                refWindfile = '%s/TMP/input/Wind/U10_%s.txt' % (rch,yr)
                shutil.copy(refWindfile_orig,refWindfile)
                
    
    ##########################
    ###   Lateral Links    ###
    ##########################
    print(' Building 1D lateral input files for reach: %s' % rch)
    
    # read in timeseries for lateral links that have timeseries data
    # these will be dictionaries, not lists
    latQ_in = {}
    latFine_in = {}
    latSand_in = {}
    
    for lat in lat_ts_trib[rch].keys():    
        lat_trib_col = lat_ts_trib[rch][lat] - 1
        latQ_in[lat] = np.genfromtxt(tribQ_file,usecols=[lat_trib_col],delimiter=',',dtype=str,skip_header=1)
        latFine_in[lat] = np.genfromtxt(tribF_file,usecols=[lat_trib_col],delimiter=',',dtype=str,skip_header=1)
        latSand_in[lat] = np.genfromtxt(tribS_file,usecols=[lat_trib_col],delimiter=',',dtype=str,skip_header=1)
    
    #############################
    ###   Lateral Link Flow   ###
    #############################
    # flow timeseries in lateral links is a different structure than all other data

    for lat in rch_lat[rch]:
        use_latQ = 0
            
        if lat in lat_ts_trib[rch].keys():
            use_latQ = 1
        
        # loop through lateral links and build individual timeseries flow file for each lateral link - with a folder for each year    
        for d in range(0,Qdays):
            date = Q_in[d][1]             # date format = '!   YYYYMMDD'
            yr = date[-8:-4]
            mn = date[-4:-2]
            day = date[-2:]
            # write number of days that are included in the file - varies based on leap year - needs to be longer than one year to account for interpolation on last day 
            if int(yr) in range(2000,4001,4):
                dtall = 365 + pad_days[-1]      # the last day of the year is 365 for leap years if starting with day 0
            else:
                dtall = 364 + pad_days[-1]

            latfolder =  '%s/HYDRO/input/Lateral/%s' % (rch,yr)
            
            if use_latQ == 1:
                latQval = -1.0*float(latQ_in[lat][d])   # lateral flow from a diversion is negative to leave 1D channel at lateral connection
            else:    
                latQval = 0.0
            
            if mn == '01':
                if day == '01':
                    dt = 0
                    
                    if os.path.exists(latfolder) == False:
                        os.mkdir(latfolder)
                    
                    
                    latQoutfile = '%s/lateral_%04d.txt' % (latfolder,lat)
                    latQout = open(latQoutfile,mode='w')
            
            latQout.write('%s\t%s\n' % (dt, latQval))
        
            dt += 1440
            
            # on last day of year pad end of file with additional daily values as an extra timestep for iteration functions. then close file.
            if mn == '12':
                if day == '31':
                    for pad in pad_days:  # this will pad the bottom of the daily record based on a set  number of days set above
                        latQout.write('%s\t%s\n' % (dt, latQval))
                        
                        dt += 1440
                    
                    latQout.close()
    ##########################################################
    ###   Lateral Sediment, Salinity and Temp Timeseries   ###
    ##########################################################
    
    for d in range(0,Qdays):
        date = Q_in[d][1]             # date format = '!   YYYYMMDD'
        yr = date[-8:-4]
        mn = date[-4:-2]
        day = date[-2:]
        # write number of days that are included in the file - varies based on leap year - needs to be longer than one year to account for interpolation on last day 
        if int(yr) in range(2000,4001,4):
            dtall = 365 + pad_days[-1]      # the last day of the year is 365 for leap years if starting with day 0
        else:
            dtall = 364 + pad_days[-1]

        if mn == '01':
            if day == '01':
                dt = 0
                
                latSalout = open('%s/SAL/input/Lateral/lateral_q_con_%s.txt' % (rch,yr),mode='w')
                latFineout = open('%s/FINE/input/Lateral/lateral_q_con_%s.txt' % (rch,yr),mode='w')
                latSandout = open('%s/SAND/input/Lateral/lateral_q_con_%s.txt' % (rch,yr),mode='w')
                latTwout = open('%s/TMP/input/Lateral/lateral_q_con_%s.txt' % (rch,yr),mode='w')

                nlat = len(rch_lat[rch])
                
                latSalout.write('time(s)    Q1, Sal1, Q2, Sal2,...,for lateral flow / sal input\n %d %d\n' % (dtall,nlat))
                latFineout.write('time(s)   Q1, Fine1, Q2, Fine2,...,for lateral flow / sal input\n %d %d\n' % (dtall,nlat))
                latSandout.write('time(s)   Q1, Sand1, Q2, Sand2,...,for lateral flow / sal input\n %d %d\n' % (dtall,nlat))
                latTwout.write('time(s) Q1, Temp1, Q2, Temp2,...,for lateral flow / sal input\n %d %d\n' % (dtall,nlat))
        
        
        salrow = '%s' % dt
        finerow = '%s' % dt
        sandrow = '%s' % dt
        twrow = '%s' % dt
    
        for lat in rch_lat[rch]:
            if lat in lat_ts_trib[rch].keys():
                q = -1.0*float(latQ_in[lat][d]) # lateral flow from a diversion is negative to leave 1D channel at lateral connection
                sal = 0
                fine = latFine_in[lat][d]
                sand = latSand_in[lat][d]
                tw = Temp_in[d][1]
            else:
                q = 0
                sal = 0
                fine = 0
                sand = 0
                tw = 0
            
            salrow =  '%s\t%s\t%s' % (salrow,  q, sal)
            finerow = '%s\t%s\t%s' % (finerow, q, fine)
            sandrow = '%s\t%s\t%s' % (sandrow, q, sand)
            twrow =   '%s\t%s\t%s' % (twrow,   q, tw)
        
        latSalout.write('%s\n' % salrow) 
        latFineout.write('%s\n' % finerow)
        latSandout.write('%s\n' % sandrow)
        latTwout.write('%s\n' % twrow)
    
        dt += 1440                           
    
        # on last day of year pad end of file with additional daily values as an extra timestep for iteration functions. then close file.
        if mn == '12':
            if day == '31':
                for pad in pad_days:  # this will pad the bottom of the daily record based on a set  number of days set above
                   salrow = '%s' % dt
                   finerow = '%s' % dt
                   sandrow = '%s' % dt
                   twrow = '%s' % dt
                
                   for lat in rch_lat[rch]:
                       if lat in lat_ts_trib[rch].keys():
                           # in this loop section, the index d has not been updated since 12/31 so each loop during pad_days will just repeat the value q,fine,sand,tw for the last day of the year
                           q = -1.0*float(latQ_in[lat][d]) # lateral flow from a diversion is negative to leave 1D channel at lateral connection
                           sal = 0
                           fine = latFine_in[lat][d]
                           sand = latSand_in[lat][d]
                           tw = Temp_in[d][1]
                       else:
                           q = 0
                           sal = 0
                           fine = 0
                           sand = 0
                           tw = 0
                       
                       salrow =  '%s\t%s\t%s' % (salrow,  q, sal)
                       finerow = '%s\t%s\t%s' % (finerow, q, fine)
                       sandrow = '%s\t%s\t%s' % (sandrow, q, sand)
                       twrow =   '%s\t%s\t%s' % (twrow,   q, tw)
                   
                   latSalout.write('%s\n' % salrow) 
                   latFineout.write('%s\n' % finerow)
                   latSandout.write('%s\n' % sandrow)
                   latTwout.write('%s\n' % twrow)
               
                   dt += 1440

                latSalout.close()
                latFineout.close()
                latSandout.close()
                latTwout.close()




