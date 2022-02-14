from sqlalchemy import create_engine
import os
import psycopg2
import io
import pandas as pd
import numpy as np
from datetime import datetime as dt
datestr = dt.now()

scens2update = []
groups2update = []
years2update = range(1,53)  #[]
backup = True
tables_to_backup = ['land_veg','mc']
overwrite = False
update_ecoregion_values = False
update_MC_direct_benefits = True

# connection info for PDD SQL engine
host = 'vm007.bridges2.psc.edu'
db_name = 'mp23_pdd'
port = '5432'
user = 'ewhite12'
password = input('\npassword for SQL connection?')

pdd_bk_dir = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/PDD_bk'

logfile = '%s/_logfile.csv' % pdd_bk_dir

if os.path.isfile(logfile) == False:
    with open(logfile,mode='w') as lf:
        lf.write('datetime,user,action\n')

connection_info = {'host': host,'dbname':db_name,'user':user,'password':password}
connection_string = ' '.join([f"{key}='{value}'" for key, value in connection_info.items()])

if backup == True:
    for dbtable in tables_to_backup:
# Running query using PANDAS dataframes & PSYCOPG2
        print('Backing up PDD icm.%s to %s' % ( dbtable, pdd_bk_dir))
        datestr = dt.now()
        conn = psycopg2.connect(connection_string)
        sqlstr = "select * from icm.%s;" % dbtable
        output=pd.read_sql_query(sqlstr,conn)
    
        bkfile = '%s/mp23_pdd_icm.%s_%04d.%02d.%02d.%02d.%02d.%02d.csv' % ( pdd_bk_dir,dbtable,dt.now().year,dt.now().month,dt.now().day,dt.now().hour,dt.now().minute,dt.now().second )
        output.to_csv(bkfile)
        actionnote = 'downloaded backup copy of icm.%s to file: %s' % (dbtable,bkfile)
        with open(logfile,mode='a') as lf:
            lf.write('%s,%s,%s\n' % (datestr,user,actionnote))

if overwrite == True:
#Running delete SQL queries using PSYCOPG2 instead of PANDAS
    print('Deleting icm.land_veg from mp23_pdd')
    datestr = dt.now()
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
#    sqlstr = "delete from icm.land_veg;"  # deletes all rows in table
#    actionnote = 'deleted all rows in SQL server copy of icm.land_veg'
    data2delete ='"ModelGroup"=606'            #'"Scenario"=7'
    sqlstr = 'delete from icm.land_veg where land_veg.%s;' % data2delete
    actionnote = 'deleted all %s data in SQL server copy of icm.land_veg' % data2delete
    cur.execute(sqlstr)
    conn.commit()
    cur.close()
    conn.close()

    with open(logfile,mode='a') as lf:
        lf.write('%s,%s,%s\n' % (datestr,user,actionnote))

codes2update = ['LND','WAT','FLT','FOR','FRM','INM','BRM','SAM','BRG','UPL']
eco2update = ['ATD','BFD','CAL','CHR','CHS','ETB','LBAne','LBAnw','LBAse','LBAsw','LBO','LBR','LPO','MBA','MEL','MRP','PEN','SAB','TVB','UBA','UBR','UVR','VRT','WTE','EBbi','WBbi','TEbi']
eco2bi ={ 'CHSbi':'EBbi','LBRbi':'EBbi', 'LBAnebi':'WBbi','LBAsebi':'WBbi','LBAswbi':'WBbi','ETBbi':'TEbi','WTEbi':'TEbi' }
eco3skip = ['ATB']

actionnote = 'uploaded ICM output for: '

d = {}
for S in scens2update:
    d[S] = {}
    for G in groups2update:
        d[S][G] = {}
        actionnote = '%s S%02dG%03d' % (actionnote,S,G)
        for Y in years2update:
            d[S][G][Y] = {}
            for C in codes2update:
                d[S][G][Y][C] = {}
                for E in eco2update:
                    d[S][G][Y][C][E] = 0
             

# land_veg columns [data format]:
#       ModelGroup [%03d]
#       Scenario [%02d]
#       Year_ICM [%d]
#       VegetationCode [%s - max length of 3]
#       Ecoregion [%s]
#       Area_m2 [%d or %f]
#       Date [%s (MM-DD-YYYY )]
#       Year_FWOA [%d]
#       Note [%s]


for S in scens2update:
    for G in groups2update:
        if G == 0:
            lvfile =  'MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_00_00_land_veg.csv' % (S,G)
        else:
            lvfile = './S%02d/G%03d/geomorph/output/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_01_52_land_veg.csv' % (S,G,S,G)
        print('\nreading output data from: %s' % lvfile)
        with open(lvfile,mode='r') as lvf:
            badrows = []
            nrb = 0
            nr = 0
            for r in lvf:   # 'prj_no', 'S', 'ICMyear', 'code', 'ecoregion', 'value'
                nr += 1
                try:
                    #print (r)
                    g = int(r.split(',')[0].strip()[1:4])
                    s = int(r.split(',')[1].strip()[1:3])
                    y = int(r.split(',')[2].strip())
                    c = r.split(',')[3].strip()
                    e = r.split(',')[4].strip()
                    v = float(r.split(',')[5].strip())
                    if e in eco2bi.keys():
                        er = eco2bi[e]
                    else:
                        er = e
                    if er in eco2update:
                        if s == S:
                            if g == G:
                                if c in codes2update:
                                    d[s][g][y][c][er] += v
                except:
                    nrb += 1
                    badrows.append(nr)
            if nrb > 0:
                print(' Failed to parse %d rows in %s. Check lines:' % (nrb,lvfile))
                print(badrows)
        

        
print('\nupdating PDD (via Pandas SQL functions) ')
engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}')

if update_ecoregion_values == True:
    for S in scens2update:
        for G in groups2update:
            print('uploading S%02d G%03d...' % (S,G) )
            note = ''
            for Y in years2update:
                if Y == 1:
                    FWOAY = -2
                    note = 'landscape at end of first ICM Spinup Year'
                elif Y == 2:
                    FWOAY = -1
                    note = 'FWOA Initial Conditions; landscape at end of second ICM Spinup Year'
                elif Y == 2018:
                    FWOAY = 2018
                    note = 'existing conditions; landscape from 2018 USGS data'
                else:
                    FWOAY = Y-2
                    note = 'landscape at end of ICM year'
                for C in codes2update:
                    for E in eco2update:
                        val2write = d[S][G][Y][C][E]
                        try:
                            df2up = pd.DataFrame({ 'ModelGroup':G,'Scenario':S,'Year_ICM':Y,'VegetationCode':C,'Ecoregion':E,'Area_m2':val2write,'Date':datestr,'Year_FWOA':FWOAY,'Note':note},index=[0])
                            df2up.to_sql('land_veg', engine, if_exists='append', schema='icm', index=False)
                        except:
                            print('  failed to upload to PDD for : S%02d G%03d %s %s - yr %s ' % (S,G,C,E,Y))
    with open(logfile,mode='a') as lf:
        lf.write('%s,%s,%s\n' % (datestr,user,actionnote))


# look up marsh creation element volumes and footprints
if update_MC_direct_benefits == True:
    actionnote = 'Uploaded direct benefits for MC elements in: '
    for S in scens2update:
        for G in groups2update:
            actionnote = '%s S%02dG%03d' % (actionnote,S,G)
            geoout = 'S%02d/G%03d/geomorph/output/' % (S,G)
            direct_benefit_file = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_01_52_W_MCdir.csv' % (geoout,S,G)                          
            db = np.genfromtxt(direct_benefit_file,delimiter=',',dtype='str',skip_header=1)
            print('Importing direct land area benefits from: %s' % direct_benefit_file)
            eid_yr_vol = {}
            eid_yr_area = {}
            eid_ip = {}
            
            # read in direct benefit land area per zone for FWOA
            if G == 500:
                for row in db:
                    y = int(row[2])
                    c = row[3]
                    e = int(row[4])
                    a = int(row[5])
                    # if new element, build empty timeseries dictionary for element
                    if e not in eid_yr_area.keys():
                        print('Processing FWOA data for MC element: %s' % e)
                        eid_yr_vol[e] = {}
                        eid_yr_area[e] = {}
                        for year in range(1,53):
                            eid_yr_vol[e][year] = 0.0
                            eid_yr_area[e][year] = 0.0
                            eid_ip[e] = 0
                    if c in ['LND','BRG','UPL','FLT']:
                        eid_yr_area[e][y] += a
            
            # if not FWOA, check to see if there are any MC elements implemented in run
            else:
                update_volume = 0
                for f in os.listdir(geoout):
                    if f.endswith('MC_VolArea.csv'):
                        MCVA = np.genfromtxt('%s/%s' % (geoout,f),delimiter=',',skip_header=1,dtype='str')
                        impyear = int(f.split('_')[8])
                        print('Found MC projects implemented in this run: %s %s - year %02d.' % (S,G,impyear) )
                        update_volume = 1
                        if MCVA.ndim == 1:
                            nMCVArows = 1
                        else:
                            nMCVArows = MCVA.shape[0]
                    
                        for nr in range(0,nMCVArows):
                            if nMCVArows == 1:
                                data = MCVA
                            else:
                                data = MCVA[nr]
                            element = int(data[0])
                            volume = float(data[1])
                                            
                            # found a new MC element - build empty dictionary for yearly values
                            if element not in eid_yr_vol.keys():
                                print('  - Element: %s' % element)
                                eid_yr_vol[element] = {}
                                eid_yr_area[element] = {}
                                for year in range(1,53):
                                    eid_yr_vol[element][year] = 0.0
                                    eid_yr_area[element][year] = 0.0
                    
                            # update sediment volume for implementation year (leave all other years 0)
                            eid_yr_vol[element][impyear] = volume
                            
                            # update implementation period for element
                            if impyear < 23:
                                eid_ip[element] = 1
                            else:
                                eid_ip[element] = 2                      
                # look up direct benefit calculations for elementID for all years
                if update_volume > 0:
                    for row in db:
                        y = int(row[2])
                        c = row[3]
                        e = int(row[4])
                        a = int(row[5])
                        if e in eid_yr_area.keys():
                            if c in ['LND','BRG','UPL','FLT']:
                                eid_yr_area[e][y] += a
            # done looking up volumes and areas for all elements and all years in this run
            # uploading to PDD
            print('Uploading direct benefit area and marsh creation volumes for run S%02d G%03d' % (S,G))
            for Y in years2update:
                if Y == 1:
                    FWOAY = -2
                elif Y == 2:
                    FWOAY = -1
                else:
                    FWOAY = Y-2
                for eid in eid_yr_vol.keys():
                    V = eid_yr_vol[eid][Y]
                    A = eid_yr_area[eid][Y]
                    IP = eid_ip[eid]           
                            
                    df2up = pd.DataFrame({ 'ModelGroup':G,'Scenario':S,'ElementID':eid,'Year_ICM':Y,'Year_FWOA':FWOAY,'MarshArea_m2':A,'MarshVolume_m3':V,'Date':datestr,'ImplementationPeriod':IP},index=[0])
                    df2up.to_sql('mc', engine, if_exists='append', schema='icm', index=False)     
                          
    with open(logfile,mode='a') as lf:
        lf.write('%s,%s,%s\n' % (datestr,user,actionnote))
                     
        
        
        
        
        
        





#Running random SQL queries using PSYCOPG2 instead of PANDAS
#connection_info = {'host': host,'dbname':db_name,'user':user,'password':password}
#connection_string = ' '.join([f"{key}='{value}'" for key, value in connection_info.items()])
#conn = psycopg2.connect(connection_string)
#cur = conn.cursor()
#sqlstr = 'select * from icm.land_veg;'
#sqlstr = 'delete from icm.land_veg;'  # deletes all rows in table
#cur.execute(sqlstr)
#conn.commit()
#cur.close()
#conn.close()


# Running query using PANDAS dataframes & PSYCOPG2
# output=pd.read_sql_query(sqlstr,conn)
