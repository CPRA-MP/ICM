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


outpath = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/PDD_bk/clara.nsrisk.EAD50_all_asset.csv'

table = 'clara.nsrisk'
q = []
q.append('SELECT "CommunityID" ')
q.append(', SUM( "EAD_50") AS EAD_50_')
q.append(' FROM %s' % table)
q.append(' WHERE "NSProjectID"=1')
q.append(' AND "Scenario"=7')
q.append(' AND "ModelGroup"=500')
q.append(' AND "FragilityScenario"=1')
q.append(' AND "PumpingID"=0.5')
q.append(' AND "Year_FWOA"=1')
q.append(' GROUP BY "CommunityID"')
q.append(' ORDER BY "CommunityID" ASC')



nspid   = 1     # Nonstructural Project Variant ID (1 = initial conditions landscape under S07; 3 = year 30 landscape under S07)(defined in clara.nsprojects)
nspr    = 1     # Nonstructural Participation Rate  (0.5 = 50% participation; 0.75 = 75% participation; 1.0 = 100% participation)
pmid    = 0.5   # Pumping Scenario ID (0.0 = 0% pumping; *0.5 = 50% pumping; 1.0 = 100% pumping)  *scenario used for default MP2023 analysis
frid    = 1     # Fragiligy Scenario ID (0 = no fragility of levees; *1 = IPET fragility assumptions)  *scenario used for default MP2023 analysis

asset_types = {}
asset_types[1] = 'Small Residential (single-family; manufactured homes; duplex)'
asset_types[2] = 'Other Multi-family Residential'
asset_types[3] = 'Commercial; Industrial; Agricultural'
asset_types[4] = 'Other Structural (public; education; religion)'
asset_types[5] = 'Non-structural Assets(crops; vehicles; roads)'


cic = {}                        # critical infrastructure categories
cic['Schools and Daycares']    = ['Daycare_2021_ESRI_CoastalLouisiana','PublicSchools']
cic['Hospitals']               = ['Hospitals']#,'Veterans_Health_Administration_Medical_Facilities']
cic['Nursing Homes']           = ['Nursing_Residential_Care_Facilities','NursingHomes']
cic['Emergency Services']      = ['Emergency_Medical_Service_EMS_Stations','Fire_Stations','Local_Emergency_Operations_Centers','Local_Law_Enforcement']
cic['Water Supply']            = ['DrinkingWaterSources','DrinkingWaterTreatmentPlants']
cic['Gas Stations']            = ['GasStations_2021_ESRI_CoastalLouisiana']
cic['Electrical Substations and Power Plants'] = ['Electric_Substations']#,'Power_Plants']


communities = [186]

for cid in communities:             ## cid : CommunityID
    for s in [7,8]:
        #########################
        # TABLE : Residual Risk #
        #########################
        g = 500
        y = 1
        sql = 'SELECT * from clara.risk WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d ;' % (cid,s,g,pmid,frid,y)
        fwoa_ic = pd.read_sql_query(sql,conn)
        
        sql = 'SELECT * from clara.nsrisk WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "NSProjectID"=%d AND "ParticipationRate"=%d AND "Year_FWOA"=%d ;' % (cid,s,g,pmid,frid,nspid,nspr,y)
        fwoa_ns_ic = pd.read_sql_query(sql,conn)
        
        y = 20    
        sql = 'SELECT * from clara.risk WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d ;' % (cid,s,g,pmid,frid,y)
        fwoa_20 = pd.read_sql_query(sql,conn)
        
        sql = 'SELECT * from clara.nsrisk WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "NSProjectID"=%d AND "ParticipationRate"=%d AND "Year_FWOA"=%d ;' % (cid,s,g,pmid,frid,nspid,nspr,y)
        fwoa_ns_20 = pd.read_sql_query(sql,conn)
                
        y = 50    
        sql = 'SELECT * from clara.risk WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d ;' % (cid,s,g,pmid,frid,y)
        fwoa_50 = pd.read_sql_query(sql,conn)
                
        sql = 'SELECT * from clara.nsrisk WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "NSProjectID"=%d AND "ParticipationRate"=%d AND "Year_FWOA"=%d ;' % (cid,s,g,pmid,frid,nspid,nspr,y)
        fwoa_ns_50 = pd.read_sql_query(sql,conn)

        g=515
        y = 20    
        sql = 'SELECT * from clara.risk WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d ;' % (cid,s,g,pmid,frid,y)
        fwmp_20 = pd.read_sql_query(sql,conn)
        
        sql = 'SELECT * from clara.nsrisk WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "NSProjectID"=%d AND "ParticipationRate"=%d AND "Year_FWOA"=%d ;' % (cid,s,g,pmid,frid,nspid,nspr,y)
        fwmp_ns_20 = pd.read_sql_query(sql,conn)
        
        g=516
        y = 50    
        sql = 'SELECT * from clara.risk WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d ;' % (cid,s,g,pmid,frid,y)
        fwmp_50 = pd.read_sql_query(sql,conn)
        
        sql = 'SELECT * from clara.nsrisk WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "NSProjectID"=%d AND "ParticipationRate"=%d AND "Year_FWOA"=%d ;' % (cid,s,g,pmid,frid,nspid,nspr,y)
        fwmp_ns_50 = pd.read_sql_query(sql,conn)

        fwoa_ic     =    fwoa_ic.set_index("AssetType",drop=True)
        fwoa_20     =    fwoa_20.set_index("AssetType",drop=True)
        fwmp_20     =    fwmp_20.set_index("AssetType",drop=True)
        fwoa_50     =    fwoa_50.set_index("AssetType",drop=True)
        fwmp_50     =    fwmp_50.set_index("AssetType",drop=True)
        fwoa_ns_ic  = fwoa_ns_ic.set_index("AssetType",drop=True)
        fwoa_ns_20  = fwoa_ns_20.set_index("AssetType",drop=True)
        fwmp_ns_20  = fwmp_ns_20.set_index("AssetType",drop=True)
        fwoa_ns_50  = fwoa_ns_50.set_index("AssetType",drop=True)
        fwmp_ns_50  = fwmp_ns_50.set_index("AssetType",drop=True)
        
        # EADD table
        eadd_table = ['AssetType','InitCond','InitCond+NS','FWOA Yr20', 'FWOA+NS Yr20','FWMP Yr20','FWMP+NS Yr20','FWOA Yr50', 'FWOA+NS Yr50','FWMP Yr50','FWMP+NS Yr50']
        cn = 'EAD_50'
        for at in asset_types.keys():
            if s == 7:
                v0 = '$%d' % round(fwoa_ic.loc[at,cn],-3)
                v1 = '$%d' % round(fwoa_ns_ic.loc[at,cn],-3)
            else:
                v0 = 'na'
                v1 = 'na'
            v2 = '$%d' % round(fwoa_20.loc[at,cn],-3)
            v3 = '$%d' % round(fwoa_ns_20.loc[at,cn],-3)
            v4 = '$%d' % round(fwmp_20.loc[at,cn],-3)
            v5 = '$%d' % round(fwmp_ns_20.loc[at,cn],-3)
            v6 = '$%d' % round(fwoa_50.loc[at,cn],-3)
            v7 = '$%d' % round(fwoa_ns_50.loc[at,cn],-3)
            v8 = '$%d' % round(fwmp_50.loc[at,cn],-3)
            v9 = '$%d' % round(fwmp_ns_50.loc[at,cn],-3)

            new_row = [asset_types[at],v0,v1,v2,v3,v4,v5,v6,v7,v8,v9]
            eadd_table = np.vstack([eadd_table,new_row])
        
        if s == 7:
            v0 = '$%d' % round(sum(fwoa_ic.loc[:,cn]),-3)
            v1 = '$%d' % round(sum(fwoa_ns_ic.loc[:,cn]),-3)
        else:
            v0 = 'na'
            v1 = 'na'
        v2 = '$%d' % round(sum(fwoa_20.loc[:,cn]),-3)
        v3 = '$%d' % round(sum(fwoa_ns_20.loc[:,cn]),-3)
        v4 = '$%d' % round(sum(fwmp_20.loc[:,cn]),-3)
        v5 = '$%d' % round(sum(fwmp_ns_20.loc[:,cn]),-3)
        v6 = '$%d' % round(sum(fwoa_50.loc[:,cn]),-3)
        v7 = '$%d' % round(sum(fwoa_ns_50.loc[:,cn]),-3)
        v8 = '$%d' % round(sum(fwmp_50.loc[:,cn]),-3)
        v9 = '$%d' % round(sum(fwmp_ns_50.loc[:,cn]),-3)
        new_row = ['Total',v0,v1,v2,v3,v4,v5,v6,v7,v8,v9]
        eadd_table = np.vstack([eadd_table,new_row])
        np.savetxt('eadd_table_%d_S%02d.csv'%(cid,s),eadd_table,delimiter=',',fmt='%s')
        
            
        # EASD table
        easd_table = ['AssetType','InitCond','InitCond+NS','FWOA Yr20', 'FWOA+NS Yr20','FWMP Yr20','FWMP+NS Yr20','FWOA Yr50', 'FWOA+NS Yr50','FWMP Yr50','FWMP+NS Yr50']
        cn = 'EASD_50'
        for at in asset_types.keys():
            if s ==7:
                v0 = '%0.2f' % fwoa_ic.loc[at,cn]
                v1 = '%0.2f' % fwoa_ns_ic.loc[at,cn]
            else:
                v0 = 'na'
                v1 = 'na'
            v2 = '%0.2f' % fwoa_20.loc[at,cn]
            v3 = '%0.2f' % fwoa_ns_20.loc[at,cn]
            v4 = '%0.2f' % fwmp_20.loc[at,cn]
            v5 = '%0.2f' % fwmp_ns_20.loc[at,cn]
            v6 = '%0.2f' % fwoa_50.loc[at,cn]
            v7 = '%0.2f' % fwoa_ns_50.loc[at,cn]
            v8 = '%0.2f' % fwmp_50.loc[at,cn]
            v9 = '%0.2f' % fwmp_ns_50.loc[at,cn]

            new_row = [asset_types[at],v0,v1,v2,v3,v4,v5,v6,v7,v8,v9]
            easd_table = np.vstack([easd_table,new_row])
            
        if s == 7:
            v0 = '%0.2f' % sum(fwoa_ic.loc[:,cn])
            v1 = '%0.2f' % sum(fwoa_ns_ic.loc[:,cn])
        else:
            v0 = 'na'
            v1 = 'na'
        v2 = '%0.2f' % sum(fwoa_20.loc[:,cn])
        v3 = '%0.2f' % sum(fwoa_ns_20.loc[:,cn])
        v4 = '%0.2f' % sum(fwmp_20.loc[:,cn])
        v5 = '%0.2f' % sum(fwmp_ns_20.loc[:,cn])
        v6 = '%0.2f' % sum(fwoa_50.loc[:,cn])
        v7 = '%0.2f' % sum(fwoa_ns_50.loc[:,cn])
        v8 = '%0.2f' % sum(fwmp_50.loc[:,cn])
        v9 = '%0.2f' % sum(fwmp_ns_50.loc[:,cn])
        new_row = ['Total',v0,v1,v2,v3,v4,v5,v6,v7,v8,v9]
        easd_table = np.vstack([easd_table,new_row])
        np.savetxt('easd_table_%d_S%02d.csv'%(cid,s),easd_table,delimiter=',',fmt='%s')
            
            
            
            
          
        #################################
        # TABLE : NS Candidate Projects #
        #################################
        # list of candidate properties for NS mitigation - arranged by Asset Type for initial conditions and year 30
        nspid = 1
        sql = 'SELECT * from clara.nsattributes WHERE "CommunityID"=%d AND "NSProjectID"=%d AND "ParticipationRate"=%d;' % (cid,nspid,nspr)
        out_ic = pd.read_sql_query(sql,conn)
        out_ic = out_ic.set_index("AssetType",drop=True)
        
        nspid = 3
        sql = 'SELECT * from clara.nsattributes WHERE "CommunityID"=%d AND "NSProjectID"=%d AND "ParticipationRate"=%d;' % (cid,nspid,nspr)
        out_30 = pd.read_sql_query(sql,conn)
        out_30 = out_30.set_index("AssetType",drop=True)
        
        r_v = 'FpNum'
        ns_assets = {}
        ns_assets['Floodproofing'] = [1,2,3,4]
        ns_assets['Home Elevation'] = [1]
        ns_assets['Voluntary Acquisition'] = [1,2]
        
        ns_cnt_col = {}
        ns_cnt_col['Floodproofing'] = 'FpNum'
        ns_cnt_col['Home Elevation'] = 'ElNum'
        ns_cnt_col['Voluntary Acquisition'] = 'AcNum'
        
        ns_cst_col = {}
        ns_cst_col['Floodproofing'] = 'FpCost'
        ns_cst_col['Home Elevation'] = 'ElCost'
        ns_cst_col['Voluntary Acquisition'] = 'AcCost'
    
        ns_proj_table = ['Nonstructural Mitigation Measure','NS Candidates under Initial Conditions','NS Candidates under FWOA Year 30']
        for ns_type in ns_assets.keys():
            ns_col = ns_cnt_col[ns_type]
            val_ic = 0
            val_30 = 0
            for as_type in ns_assets[ns_type]:
                val_ic += out_ic.loc[as_type,ns_col]
                val_30 += out_30.loc[as_type,ns_col]
            new_row = [ns_type,val_ic,val_30]
            ns_proj_table = np.vstack([ns_proj_table,new_row])
        np.savetxt('ns_proj_table_%d.csv'%(cid),ns_proj_table,delimiter=',',fmt='%s')

        ns_cost_table = ['Nonstructural Mitigation Measure','Total NS Cost under Initial Conditions','Total NS Cost under FWOA Year 30']
        for ns_type in ns_assets.keys():
            ns_col = ns_cst_col[ns_type]
            val_ic = 0
            val_30 = 0
            for as_type in ns_assets[ns_type]:
                val_ic += out_ic.loc[as_type,ns_col]
                val_30 += out_30.loc[as_type,ns_col]
            new_row = [ns_type,'$%d' % round(val_ic,-3),'$%d' % round(val_30,-3)]
            ns_cost_table = np.vstack([ns_cost_table,new_row])
        np.savetxt('ns_cost_table_%d.csv'%(cid),ns_cost_table,delimiter=',',fmt='%s')
        
        
        #########################
        # TABLE : Exposure      #
        #########################
        sql = 'SELECT * from clara.asset_count WHERE "CommunityID"=%d;' % cid
        count = pd.read_sql_query(sql,conn)
        count = count.set_index("AssetType",drop=True)
        
        sql = 'SELECT * from clara.asset_count_historic_properties WHERE "CommunityID"=%d;' % cid
        count_hp = pd.read_sql_query(sql,conn)

        sql = 'SELECT * from clara.asset_count_critical_infrastructure WHERE "CommunityID"=%d;' % cid
        count_ci = pd.read_sql_query(sql,conn)
        count_ci = count_ci.set_index("SourceDataset",drop=True)
        
        for aep in [0.1, 0.02, 0.01, 0.002]:
            g = 500
            y = 1
            sql = 'SELECT * from clara.exposure WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwoa_exp_ic = pd.read_sql_query(sql,conn)
            fwoa_exp_ic = fwoa_exp_ic.set_index("AssetType",drop=True)
           # fields = "ExposureCount","ModerateExposure" "SevereExposure"
            
            sql = 'SELECT * from clara.exposure_historic_properties WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwoa_exp_hp_ic = pd.read_sql_query(sql,conn)
            # fields = "ModerateExposure" "SevereExposure"
            
            sql = 'SELECT * from clara.exposure_critical_infrastructure WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwoa_exp_ci_ic = pd.read_sql_query(sql,conn)
            fwoa_exp_ci_ic = fwoa_exp_ci_ic.set_index("SourceDataset",drop=True)
            # fields = "SourceDataset" "ModerateExposure" "SevereExposure"
    
            y = 20
            sql = 'SELECT * from clara.exposure WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwoa_exp_20 = pd.read_sql_query(sql,conn)
            fwoa_exp_20 = fwoa_exp_20.set_index("AssetType",drop=True)
            
            sql = 'SELECT * from clara.exposure_historic_properties WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwoa_exp_hp_20 = pd.read_sql_query(sql,conn)
            
            sql = 'SELECT * from clara.exposure_critical_infrastructure WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwoa_exp_ci_20 = pd.read_sql_query(sql,conn)
            fwoa_exp_ci_20 = fwoa_exp_ci_20.set_index("SourceDataset",drop=True)
            
            y = 50
            sql = 'SELECT * from clara.exposure WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwoa_exp_50 = pd.read_sql_query(sql,conn)
            fwoa_exp_50 = fwoa_exp_50.set_index("AssetType",drop=True)
            
            sql = 'SELECT * from clara.exposure_historic_properties WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwoa_exp_hp_50 = pd.read_sql_query(sql,conn)
            
            sql = 'SELECT * from clara.exposure_critical_infrastructure WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwoa_exp_ci_50 = pd.read_sql_query(sql,conn)
            fwoa_exp_ci_50 = fwoa_exp_ci_50.set_index("SourceDataset",drop=True)
            
            g = 515
            y = 20
            sql = 'SELECT * from clara.exposure WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwmp_exp_20 = pd.read_sql_query(sql,conn)
            fwmp_exp_20 = fwmp_exp_20.set_index("AssetType",drop=True)
                        
            sql = 'SELECT * from clara.exposure_historic_properties WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwmp_exp_hp_20 = pd.read_sql_query(sql,conn)
            
            sql = 'SELECT * from clara.exposure_critical_infrastructure WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwmp_exp_ci_20 = pd.read_sql_query(sql,conn)
            fwmp_exp_ci_20 = fwmp_exp_ci_20.set_index("SourceDataset",drop=True)
            
            g = 516
            y = 50
            sql = 'SELECT * from clara.exposure WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwmp_exp_50 = pd.read_sql_query(sql,conn)
            fwmp_exp_50 = fwmp_exp_50.set_index("AssetType",drop=True)
            
            sql = 'SELECT * from clara.exposure_historic_properties WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwmp_exp_hp_50 = pd.read_sql_query(sql,conn)
            
            sql = 'SELECT * from clara.exposure_critical_infrastructure WHERE "CommunityID"=%d AND "Scenario"=%d AND "ModelGroup"=%d AND "PumpingID"=%s AND "FragilityScenario"=%d AND "Year_FWOA"=%d AND "AEP"=%f;' % (cid,s,g,pmid,frid,y,aep)
            fwmp_exp_ci_50 = pd.read_sql_query(sql,conn)
            fwmp_exp_ci_50 = fwmp_exp_ci_50.set_index("SourceDataset",drop=True)
    
            
            # Severe Exposure
            exp_type = "SevereExposure"     # fields = "AssetType" "ExposureCount" "ModerateExposure" "SevereExposure"
            sev_exp_table = ['Asset Type','Total Count of Assets','Assets with Severe Flood Exposure at %s AEP Initial Conditions' % aep,'Assets with Severe Flood Exposure at %s AEP under FWOA Year 20' % aep,'Assets with Severe Flood Exposure at %s AEP under FWMP Year 20' % aep,'Assets with Severe Flood Exposure at %s AEP under FWOA Year 50' % aep,'Assets with Severe Flood Exposure at %s AEP under FWMP Year 50' % aep]
            for ast_type in asset_types.keys():
                ast_type_txt = asset_types[ast_type]
                if ast_type != 5:
                    new_row = [ast_type_txt,count.loc[ast_type,"StructureCount"],fwoa_exp_ic.loc[ast_type,exp_type],fwoa_exp_20.loc[ast_type,exp_type],fwmp_exp_20.loc[ast_type,exp_type],fwoa_exp_50.loc[ast_type,exp_type],fwmp_exp_50.loc[ast_type,exp_type]]
                    sev_exp_table = np.vstack([sev_exp_table,new_row])
            
            new_row = ['Historic Properties',count_hp.loc[:,"StructureCount"],fwoa_exp_hp_ic.loc[:,exp_type],fwoa_exp_hp_20.loc[:,exp_type],fwmp_exp_hp_20.loc[:,exp_type],fwoa_exp_hp_50.loc[:,exp_type],fwmp_exp_hp_50.loc[:,exp_type]]
            #sev_exp_table = np.vstack([sev_exp_table,new_row])
            for ci_cat in cic.keys():
                count_val = 0
                fwoa_ic_val = 0
                fwoa_20_val = 0
                fwoa_50_val = 0
                fwmp_20_val = 0
                fwmp_50_val = 0
            
                for ds_cat in cic[ci_cat]:
                    count_val   += count_ci.loc[ds_cat,"StructureCount"]
                    fwoa_ic_val += fwoa_exp_ci_ic.loc[ds_cat,exp_type]
                    fwoa_20_val += fwoa_exp_ci_20.loc[ds_cat,exp_type]
                    fwoa_50_val += fwoa_exp_ci_50.loc[ds_cat,exp_type]
                    fwmp_20_val += fwmp_exp_ci_20.loc[ds_cat,exp_type]
                    fwmp_50_val += fwmp_exp_ci_50.loc[ds_cat,exp_type]
            
                new_row = [ci_cat,count_val,fwoa_ic_val,fwoa_20_val,fwoa_50_val,fwmp_20_val,fwmp_50_val]
                sev_exp_table = np.vstack([sev_exp_table,new_row])

            np.savetxt('severe_exposure_table_%d_S%02d_%saep.csv'%(cid,s,aep),sev_exp_table,delimiter=',',fmt='%s')

conn.close()
