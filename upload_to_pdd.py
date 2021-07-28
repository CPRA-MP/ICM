from sqlalchemy import create_engine
import psycopg2
import io
import pandas as pd
from datetime import datetime as dt




host = ''
db_name = ''
port = ''
user = ''
password = input('\npassword for SQL connection?')#'###'

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}')


###########################
## Sample SQL Connection ##
###########################
#Running random SQL queries using PSYCOPG2 instead of PANDAS
#
#connection_info = {'host': host,'dbname':db_name,'user':user,'password':password}
#connection_string = ' '.join([f"{key}='{value}'" for key, value in connection_info.items()])
#conn = psycopg2.connect(connection_string)
#cur = conn.cursor()
#sqlstr = 'select * from icm.land_veg;'
#sqlstr = 'delete from icm.land_veg;'
#cur.execute(sqlstr)
#conn.commit()
#cur.close()
#conn.close()
#
#
# Running query using PANDAS dataframes & PSYCOPG2
#
#output=pd.read_sql_query(sqlstr,conn)
#
#df2up = pd.DataFrame({ 'ModelGroup':g,'Scenario':s,'Year':yy,'VegetationCode':c,'Ecoregion':e,'Area_m2':v,'Date':datestr},index=[0])
#df2up.to_sql('land_veg', engine, if_exists='append', schema='icm', index=False)# append PANDAS dataframe to existing sql table using  SQLALCHEMY connection engine 



######################
## Sample SQL query ##
######################
# SELECT "Year","Ecoregion","VegetationCode","Area_m2"
# FROM icm.land_veg 
# WHERE "VegetationCode" = 'LND' OR "VegetationCode" = 'WAT'
# ORDER BY "Ecoregion","VegetationCode","Year";
######################




# land_veg columns [data format]:
#       ModelGroup [%03d]
#       Scenario [%02d]
#       Year [%d]
#       VegetationCode [%s - max length of 3]
#       Ecoregion [%s]
#       Area_m2 [%d or %f]
#       Date [%s (MM-DD-YYYY)]





datestr = '%02d-%02d-%04d' % (dt.now().month,dt.now().day,dt.now().year)
scens2update = [7]
groups2update = [502]
years2update = [31]
codes2update = ['LND','WAT','FLT','FOR','FRM','INM','BRM','SAM','BRG','UPL']

for S in scens2update:
    for G in groups2update:
    
        lvfile = './S%02d/G%03d/geomorph/output/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_01_52_land_veg.csv' % (S,G,S,G)
        
        print('\nuploading data to PDD from %s' % lvfile)
        
        with open(lvfile,mode='r') as lvf:
            badrows = []
            nrb = 0
            nr = 0
            for r in lvf:   # 'prj_no', 'S', 'year', 'code', 'ecoregion', 'value'
                nr += 1
                try:
                #if nr > 1:
                    g = int(r.split(',')[0].strip()[1:4])
                    s = int(r.split(',')[1].strip()[1:3])
                    y = int(r.split(',')[2].strip())
                    c = r.split(',')[3].strip()
                    e = r.split(',')[4].strip()
                    v = float(r.split(',')[5].strip())
            
                    if s == S:
                        if g == G:
                            for yy in range(32,51):
                                if c in codes2update:
                                    df2up = pd.DataFrame({ 'ModelGroup':g,'Scenario':s,'Year':y,'VegetationCode':c,'Ecoregion':e,'Area_m2':v,'Date':datestr},index=[0])
                                    df2up.to_sql('land_veg', engine, if_exists='append', schema='icm', index=False)
            
                except:
                    nrb += 1
                    badrows.append(nr)                        
        
            if nrb > 0:
                print(' Failed to parse %d rows in %s. Check lines:' % (nrb,lvfile))
                print(badrows)
    
