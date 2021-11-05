from sqlalchemy import create_engine
import psycopg2
import io
import pandas as pd
from datetime import datetime as dt

# connection info for PDD SQL engine
host = 'vm007.bridges2.psc.edu'
db_name = 'mp23_pdd'
port = '5432'
user = 'ewhite12'
password = input('\npassword for SQL connection?')#'###'

scens2update = [6,8,9]
groups2update = [500]
years2update = range(1,53)
codes2update = ['LND','WAT','FLT','FOR','FRM','INM','BRM','SAM','BRG','UPL']
eco2update = ['ATD','BFD','CAL','CHR','CHS','ETB','LBAne','LBAnw','LBAse','LBAsw','LBO','LBR','LPO','MBA','MEL','MRP','PEN','SAB','TVB','UBA','UBR','UVR','VRT','WTE']
eco2add =['CHSbi','ETBbi','LBAnebi','LBAsebi','LBAswbi','LBRbi','WTEbi']
eco2skip = ['ATB']

d = {}
for S in scens2update:
    d[S] = {}
    for G in groups2update:
        d[S][G] = {}
        for Y in years2update:
            d[S][G][Y] = {}
            for C in codes2update:
                d[S][G][Y][C] = {}
                for E in eco2update:
                    d[S][G][Y][C][E] = 0

# land_veg columns [data format]:
#       ModelGroup [%03d]
#       Scenario [%02d]
#       Year [%d]
#       VegetationCode [%s - max length of 3]
#       Ecoregion [%s]
#       Area_m2 [%d or %f]
#       Date [%s (MM-DD-YYYY)]

datestr = '%02d-%02d-%04d' % (dt.now().month,dt.now().day,dt.now().year)

for S in scens2update:
    for G in groups2update:
        lvfile = './S%02d/G%03d/geomorph/output/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_01_52_land_veg.csv' % (S,G,S,G)
        print('\nreading output data from: %s' % lvfile)
        with open(lvfile,mode='r') as lvf:
            badrows = []
            nrb = 0
            nr = 0
            for r in lvf:   # 'prj_no', 'S', 'year', 'code', 'ecoregion', 'value'
                nr += 1
                try:
                    g = int(r.split(',')[0].strip()[1:4])
                    s = int(r.split(',')[1].strip()[1:3])
                    y = int(r.split(',')[2].strip())
                    c = r.split(',')[3].strip()
                    e = r.split(',')[4].strip()
                    v = float(r.split(',')[5].strip())
                    if e in eco2add:
                        er = e[0:-2]
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
        print('uploading S%02d G %03d...')
        for Y in years2update:
            for C in codes2update:
                for E in eco2update:
                    val2write = d[S][G][Y][C][E]
                    try:
                        df2up = pd.DataFrame({ 'ModelGroup':G,'Scenario':S,'Year':Y,'VegetationCode':C,'Ecoregion':E,'Area_m2':val2write,'Date':datestr},index=[0])
                        df2up.to_sql('land_veg', engine, if_exists='append', schema='icm', index=False)
                    except:
                        print('  failed to upload to PDD for : S%02d G%03d %s %s - yr %s ' % (S,G,C,E,Y))





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


