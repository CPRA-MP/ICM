from sqlalchemy import create_engine
import os
import psycopg2
import io
import pandas as pd
from datetime import datetime as dt

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

backup = True
overwrite = False

connection_info = {'host': host,'dbname':db_name,'user':user,'password':password}
connection_string = ' '.join([f"{key}='{value}'" for key, value in connection_info.items()])

if backup == True:
# Running query using PANDAS dataframes & PSYCOPG2
    print('Backing up PDD icm.land_veg to %s' % pdd_bk_dir)
    datestr = dt.now()
    conn = psycopg2.connect(connection_string)
    sqlstr = "select * from icm.land_veg;"
    output=pd.read_sql_query(sqlstr,conn)
    
    bkfile = '%s/mp23_pdd_icm.land_veg_%04d.%02d.%02d.%02d.%02d.%02d.csv' % ( pdd_bk_dir,dt.now().year,dt.now().month,dt.now().day,dt.now().hour,dt.now().minute,dt.now().second )
    output.to_csv(bkfile)
    actionnote = 'downloaded backup copy of icm.land_veg to file: %s' % bkfile
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
    sv = 7
    sqlstr = 'delete from icm.land_veg where land_veg."Scenario"=%d;' % sv
    actionnote = 'deleted all S07 data in SQL server copy of icm.land_veg'
    cur.execute(sqlstr)
    conn.commit()
    cur.close()
    conn.close()

    with open(logfile,mode='a') as lf:
        lf.write('%s,%s,%s\n' % (datestr,user,actionnote))


scens2update = []
groups2update = []
years2update = []

#scens2update = [0]
#groups2update = [0]
#years2update = [2018]

#scens2update = [7]#[6,8,9]
#groups2update =[500]
#years2update = range(1,48)#53)




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

datestr = dt.now()

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

# look up marsh creation element volumes and footprints
for S in scens2update:
    for G in groups2update:
        geoout = 'S%02d/G%03d/geomorph/output/' % (S,G)
        eid_yr_vol = {}
        eid_yr_area = {}       
        for f in os.listdir(geoout):
            if f.endswith('MC_VolArea.csv')
                print('Found MC projects implemented in this run: %s %s. % (S,G) )
                MCVA = np.genfromtxt(f,delimiter=',',skip_header=1,dtype='str')
                impyear = f.split('_')[8]
                for row in MCVA:
                    element = row[0]
                    volume = row[1]
                
                    # found a new MC element - build empty dictionary for yearly values
                    if element not in eid_yr_vol.keys():
                        print('  - Element: %s' % element)
                        eid_yr_vol[element] = {}
                        eid_yr_area[element] = {}
                        for year in range(1,53):
                            eid_yr_vol[element][year] = 0.0
                            eid_yr_area[element][year] = 0.0
                
                    # update sediment volume for implementation year (leave all other years 0)
                    eid_yr_vol[int(impyear)][int(element)] = float(volume)
                    
                     
        
        
        
        
        
        
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
