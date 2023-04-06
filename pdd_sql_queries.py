import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os
import sys


host, db_name, port, user, password = '<ENTER HOST>','<ENTER DATABASE NAME>', '5432', '<ENTER USER NAME>', '<ENTER PASSWORD>'
connection_info = {'host': host,'dbname':db_name,'user':user,'password':password}
connection_string = ' '.join([f"{key}='{value}'" for key, value in connection_info.items()])
engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}')

conn = psycopg2.connect(connection_string)

outpath = '<ENTER PROJECT DIRECTORY>\clara.nsrisk.EAD50_all_asset.csv'

if os.path.isfile(outpath):
    print('%s already exists.\nRename (or delete) output file and rerun.' % outpath)
    sys.exit()

table = 'clara.nsrisk'
q = []
q.append('SELECT "CommunityID" ')
q.append(', SUM( "EAD_50")')
q.append(' FROM %s' % table)
q.append(' WHERE "NSProjectID"=1')
q.append(' AND "Scenario"=7')
q.append(' AND "ModelGroup"=500')
q.append(' AND "FragilityScenario"=1')
q.append(' AND "PumpingID"=0.5')
q.append(' AND "Year_FWOA"=1')
q.append(' GROUP BY "CommunityID"')
q.append(' ORDER BY "CommunityID" ASC')



sqlstr = ''
for st in range(0,len(q)):
    sqlstr = '%s%s' % (sqlstr,q[st])
sqlstr = '%s;' % sqlstr
output=pd.read_sql_query(sqlstr,conn)
header_string = '### %s\n' % sqlstr

with open(outpath,mode='a') as outfile:
    outfile.write(header_string)
    output.to_csv(outfile,index=False)

conn.close()
