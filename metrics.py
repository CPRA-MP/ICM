import numpy as np
import os
import csv

def readLWF(LWFcsv):
    land = {}
    water = {}
    floatant = {}
    with open(LWFcsv,mode='rU') as infile:
        lineno = 0
        reader = csv.reader(infile)
        for rows in reader:
            if lineno != 0:     # skip header row
                land[rows[0]] = float(rows[1])
                water[rows[0]] = float(rows[2])
                floatant[rows[0]] = float(rows[3])
            lineno += 1
    return [land,water,floatant]
    
def readGridData(gridcsv):
    elevbed ={}
    pctwater = {}
    pctland = {}
    elevland = {}
    csvdata = np.genfromtxt(gridcsv,delimiter=',',skiprows=1)
    for row in csvdata:
        gridID = row[0]
        elevbed[gridID] = row[1]
        elevland[gridID] = row[2]
        pctland[gridID] = row[3]
        pctwater[gridID] = row[5]
    del csvdata    
    return [elevbed,pctland,pctwater,elevland]


# sumCoast is a function that takes an input dictionary of values and returns a single value that is the sum of a subset of the values in the dictionary.
# The keys located in the dictionary that are to be included in the sum are passed into the function via the input 'zones' array.
# inval is the starting value to be used, if you want to add a subet to some value already calculated.
def sumCoast(indict,zones,inval=0):
    outval = inval
    for zone in zones:
        outval += indict[zone]
    return outval

S = 'S01'
Gfwoa = 'G001'

maindir = os.path.normpath(r'N:\Natural_Systems\MP\Production\Results')
fwoadir = os.path.normpath(r'%s\\%s\\%s' % (maindir,S,Gfwoa))        

inputdir = os.path.normpath(r'C:\\Eric\\CodeIntegration\\ICM\\ICM_working')

project_list_file = os.path.normpath('%s\\project_list_WI_test.csv' % inputdir)  
prj_eco_file = os.path.normpath('%s\\project_ecoregions.csv' % inputdir)

gridEcolookupFile = os.path.normpath('%s\\EcoRegionGridPoints.csv' % inputdir)

gridICMlookupFile = os.path.normpath('%s\\hydro\grid_lookup_500m.csv' % fwoadir)


HR_RC_info_file = os.path.normpath('%s\\metrics_input_HR_RC.csv' % inputdir)
MC_info_file = os.path.normpath('%s\\metrics_input_MC.csv' % inputdir)
HP_info_file = os.path.normpath('%s\\metrics_input_HP.csv' % inputdir)
BH_info_file = os.path.normpath('%s\\metrics_input_BH.csv' % inputdir)
DI_info_file = os.path.normpath('%s\\metrics_input_DI.csv' % inputdir)
outputfile = os.path.normpath('%s\\metrics.csv' % inputdir)

outputfile = os.path.normpath('T:\\for Eric\\metrics\\metrics.csv')

stage_error = 0.11
navregions = ['NAVMR','NAVFC']

calc_flood = 'no'
attenuation_interval = 1
flood_atten_years = range(2015,2064,attenuation_interval)
flood_atten_years.append(2064)


# check if output file already exists
if os.path.isfile(outputfile):
    print ' Output file already exixts - type suffix to append to name and press enter:'
    suffix = raw_input()
    split = outputfile.split('.')
    outputfile = os.path.normpath('%s_%s.%s' % (split[0],suffix,split[1]))
    print ' Output file now named: %s' % outputfile

print ' Reading in grid-ICM lookup table.'
gridICM = np.genfromtxt(gridICMlookupFile,delimiter=',',skiprows=1,usecols=[0,1])
grid_ICM = {}

for row in gridICM:
    gridid = row[0]
    grid_ICM[gridid] = row[1]

del gridICM

print ' Reading in project-ecoregion lookup table.'
prj_eco_lookup =np.genfromtxt(prj_eco_file,delimiter=',',dtype=str)

#first row of prj_eco_lookup is ecoregions header
prj_eco_head = prj_eco_lookup[0]
ecoregions = prj_eco_head[1:]
nrows = int(prj_eco_lookup.shape[0])
ncols = int(prj_eco_lookup.shape[1])

prj_groups = {}
# loop through table and assign Group number to use for each ecoregion for the project (e.g. FWOA or FWA)
# first row is ecoregions text - skip this row
for row in range(1,nrows): 
    groups = {}
#first column is project number
    prjid = prj_eco_lookup[row][0]
#loop through columns and add group number from file to dictionary for each project number
    for col in range(1,ncols):
        groups[prj_eco_head[col]] = prj_eco_lookup[row][col]

    prj_groups[prjid] = groups

del prjid, prj_eco_lookup,groups,nrows,ncols

   
# read in project and group numbers
p = np.genfromtxt(project_list_file,dtype='str',skiprows=1,delimiter=',')
prjgrp = {}
NewStructures = {}
prjtype = {}
prjdesc = {}
for row in p:
    pr = row[1]
    gr = row[0]
    prjgrp[pr] = gr
    NewStructures[pr] = float(row[4])
    prjtype[pr] = str.split(pr,'.')[1]
    prjdesc[pr] = row[2]

projects = prjgrp.keys()

del p

# read in grid-ecoregion lookup table
# build dictionary where each key is an ecoregion and each value is a list of grid cells contained in that ecoregion
ecogrid = {}
grid_eco = {}
for e in ecoregions:
    ecogrid[e]=[]    
with open(gridEcolookupFile,mode='rU') as infile:
    lineno = 0
    reader = csv.reader(infile)
    for rows in reader:
        if lineno != 0:     # skip header row
            # ecogrid is dictionary where each key is ecoregion with values that are an array of grid IDs in that ecoregion
            ecogrid[rows[1]].append(int(rows[0]))
            
            # grid_eco is a dictionary where each key is the grid ID with value that is the Ecoregion that grid ID is in
            grid_eco[int(rows[0])] = rows[1]
        
        lineno += 1


# set empty dictionaries for marsh creation data & link cross sectional areas
sustainability = {}
NavMSR = {}
NavFC = {}
NP_HP = {}
    
SedVol = {}
dXarea = {}

###################################################
## Read in Hydrologic and Ridge Restoration data ##
###################################################
print ' Reading in link cross-sectional area changes for Hydrologic and Ridge Restoration projects'

HR_RC_info = np.genfromtxt(HR_RC_info_file,skiprows=1,delimiter=',',dtype='string')

for row in HR_RC_info:
    Gfwa = row[0]
    prj = row[1]
    print '  Calculating change in link cross-sectional areas for %s' % prj
    dXarea[prj] = float(row[5])-float(row[4])

##################################################
## Read in Hurricane/Structural Protection data ##
##################################################
print ' Reading in information for Structural Protection projects'

HP_info = np.genfromtxt(HP_info_file,skiprows=1,delimiter=',',dtype='string')

for row in HP_info:
    Gfwa = row[0]
    prj = row[1]
    NP_HP[prj] = float(row[4])
    
#################################
## Read in Marsh Creation data ##
#################################
print ' Reading in sediment volumes for Marsh Creation projects'

MC_info = np.genfromtxt(MC_info_file,skiprows=1,delimiter=',',dtype='string')

for row in MC_info:    
    Gfwa = row[0]
    fwadir = os.path.normpath(r'%s\\%s\\%s' % (maindir,S,Gfwa))
    prj = row[1]
    imp_yr = int(float(row[2]))+1
    imp_yr_hydro = imp_yr + 2015 + 1
    links_typ11 = str.split(row[3],';')
    links_changed = []
    for link in links_typ11:
        if link != '':
            links_changed.append(int(float(link)))                
    print ' Processing link and sediment info for project: %s' % prj
    
    if prj in projects:
        if imp_yr != -9999:
            print '  Calculating total volume of sediment for %s' % prj
            volumefile = os.path.normpath(r'%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_O_%02d_%02d_W_MCPTv.csv' % (fwadir,imp_yr,S,Gfwa,imp_yr,imp_yr))
            volumes = np.genfromtxt(volumefile,skiprows=1,usecols=1,delimiter=',',dtype='float')
            if np.size(volumes) > 1:
                SedVol[prj] = sum(volumes)
            else:
                SedVol[prj] = float(volumes)
        else:
            print '  No implementation year info provided for %s' % prj

del MC_info

#################################
## Read in Barrier Island data ##
#################################
print ' Reading in sediment volumes for Barrier Island projects'

BH_info = np.genfromtxt(BH_info_file,skiprows=1,delimiter=',',dtype='string')

if S == 'S01':
    BHcol = 2
elif S == 'S03':
    BHcol = 3
elif S == 'S04':
    BHcol = 4

for row in BH_info:    
    prj = row[1]
    SedVol[prj] = float(row[BHcol])

del BH_info
        

#################################
## Read in Divserion data ##
#################################
print ' Reading in sediment volumes for Barrier Island projects'

DI_info = np.genfromtxt(DI_info_file,skiprows=1,delimiter=',',dtype='string')

SMSR = {}
DIsed = {}

for row in DI_info:    
    Gfwa = row[0]
    fwadir = os.path.normpath(r'%s\\%s\\%s' % (maindir,S,Gfwa))
    prj = row[1]
    imp_yr = int(float(row[2]))
    Vmax = abs(float(row[3]))
    Vfwoa = abs(float(row[4]))
    Vbc =  abs(float(row[5]))
    TribCol = float(row[6])
    TribColPy = int(TribCol-1)
    startrow = int(round(imp_yr*365.25,0)) + 1
    
    if Vmax == Vfwoa:
        SMSR[prj] = 0.0
    elif Vmax > Vbc:
        SMSR[prj] = -1
    else:
        SMSR[prj] = -(Vmax-Vfwoa)/Vbc

    
    
    
    if prj in projects:
        Q_divfile = os.path.normpath(r'%s\\hydro\TribQ.csv' % fwadir)
        TSSfines_divfile = os.path.normpath(r'%s\\hydro\TribF.csv' % fwadir)
        TSSsand_divfile = os.path.normpath(r'%s\\hydro\TribS.csv' % fwadir)
        
        Qdiv = np.genfromtxt(Q_divfile,dtype='string',delimiter=',',skiprows=startrow,usecols=TribColPy)
        Finesdiv = np.genfromtxt(TSSfines_divfile,dtype='string',delimiter=',',skiprows=startrow,usecols=TribColPy)
        Sanddiv = np.genfromtxt(TSSsand_divfile,dtype='string',delimiter=',',skiprows=startrow,usecols=TribColPy)
        
        DI_sed_sum = 0.0
        ndays = len(Sanddiv)
        for day in range(0,ndays-1):
            DI_sed_sum += float(Qdiv[day])*(float(Finesdiv[day]) + float(Sanddiv[day]))
        
        DIsed[prj] = DI_sed_sum*3600.0*24.0*ndays/2640.0
  
del DI_info


#######################
## Calculate Metrics ##
#######################

minSed = min(SedVol.values())
maxSed = max(SedVol.values())
minDIsed = min(DIsed.values())
maxDIsed = max(DIsed.values())

maxdXmag = 0.0
for dX in dXarea.values():
    dXmag = abs(dX)
    new_maxdXmag = max(dXmag,maxdXmag)
    maxdXmag = new_maxdXmag


with open(outputfile,'wb') as of:
    outhead = 'project,type,description,S,EL[NAVMR],EL[NAVFC],SMSRp,SFC,NavMSR,NavFNC,NavHP,Nav,Progress,Trajectory,Sus,dXarea,NP_H,SedVol,NP_M,DIsed,NP_D,NP_HP,NP,'
    outcomments ='Project,Project Type,Description,Scenario,Extent of Land Adjacent to MSR,Extent of Land Adjacent to Federal Nav Channels,Steerage term on MSR,Shoaling term on FC,Nav Score for MSR,Nav Score for Federal Nav Channels,Nav Score for Projects with new structures,Nav Score to PT,Progress Towards Building Land,Trajectory of Land Building,Sus Land Score,Cross sectional area link modifications used for NP_H score,Natural Processes score for HR and RI,Sediment volume used for NP_M score,Natural Processes score for MC and BS,sediment volume of diversions,Natural Processes score for DI,Natural Processes score for Structural Protection projects,NP Score to PT,Flood Attenuation Score by Ecoregion,\n'
    of.write(outcomments)
    of.write(outhead)
    for er in ecoregions:
        of.write('FA_%s,' % er)

    ncomplete = 0
    for prj in projects:
        ncomplete += 1
        print ''
        print ' Calculating metrics for %s: project %s out of %s' % (prj,ncomplete,len(projects))
        if prjtype[prj] == 'HP': # no ICM G runs for HP projects - use FWOA
            Gfwa = 'G001'
        else:
            Gfwa = prjgrp[prj]
        fwadir = os.path.normpath(r'%s\\%s\\%s' % (maindir,S,Gfwa))
        
        # Generate two lists, one for ecoregions that use FWOA and on for ecoregions that use FWA
        FWOAecoregions = []
        FWAecoregions = []
        
        for ecoR in ecoregions:
            G_ecoR = prj_groups[prj][ecoR]
            if G_ecoR == 'G001':
                FWOAecoregions.append(ecoR)
            else:
                FWAecoregions.append(ecoR)

        # generate blank dictionaries that will save output values
        # these dictionaries will have the project number as the key
        # set some file names based on years and S/G numbers
        FWOA00file = os.path.normpath(r'C:\\ICM\\ICM_postprocessors\\Land_graphs\\Initial_LandWaterAreas_FWOA.csv')
        
        FWOA50file = os.path.normpath(r'%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_N_%02d_%02d_W_LWFzn.csv' % (fwoadir,50,S,Gfwoa,50,50))
        FWOA40file = os.path.normpath(r'%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_N_%02d_%02d_W_LWFzn.csv' % (fwoadir,40,S,Gfwoa,40,40))
        
        FWA50file = os.path.normpath(r'%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_N_%02d_%02d_W_LWFzn.csv' % (fwadir,50,S,Gfwa,50,50))
        FWA40file = os.path.normpath(r'%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_N_%02d_%02d_W_LWFzn.csv' % (fwadir,40,S,Gfwa,40,40))
        
        FWOA00gridfile = os.path.normpath(r'%s\\hydro\\TempFiles\\grid_data_500m_%s.csv' % (fwoadir,2015))
        FWOA50gridfile = os.path.normpath(r'%s\\hydro\\TempFiles\\grid_data_500m_%s.csv' % (fwoadir,2064))
        FWOA30gridfile = os.path.normpath(r'%s\\hydro\\TempFiles\\grid_data_500m_%s.csv' % (fwoadir,2044))
        FWOA10gridfile = os.path.normpath(r'%s\\hydro\\TempFiles\\grid_data_500m_%s.csv' % (fwoadir,2024))
        
        FWA50gridfile = os.path.normpath(r'%s\\hydro\\TempFiles\\grid_data_500m_%s.csv' % (fwadir,2064))
        FWA30gridfile = os.path.normpath(r'%s\\hydro\\TempFiles\\grid_data_500m_%s.csv' % (fwadir,2044))
        FWA10gridfile = os.path.normpath(r'%s\\hydro\\TempFiles\\grid_data_500m_%s.csv' % (fwadir,2024))
                                         
        ###########################
        ##  Read ecoregion data  ##
        ###########################
        print '  Reading in land/water/floatant areas summarized by ecoregion'
        LWF_fwoa00 = readLWF(FWOA00file)
        Land_FWOA_00 = sumCoast(LWF_fwoa00[0],ecoregions) + sumCoast(LWF_fwoa00[2],ecoregions) 
        
        LWF_fwoa50 = readLWF(FWOA50file)
        Land_FWOA_50 = sumCoast(LWF_fwoa50[0],ecoregions) + sumCoast(LWF_fwoa50[2],ecoregions) 
        
        LWF_fwoa40 = readLWF(FWOA40file)
        Land_FWOA_40 = sumCoast(LWF_fwoa40[0],ecoregions) + sumCoast(LWF_fwoa40[2],ecoregions) 
        
        #FWA land areas are summarized from FWA data in ecoregions that are impacted by project and from FWOA data in ecoregions that are not impacted by the project
        LWF_fwa50 = readLWF(FWA50file)
        Land_FWA_50 = sumCoast(LWF_fwa50[0],FWAecoregions) + sumCoast(LWF_fwa50[2],FWAecoregions) + sumCoast(LWF_fwoa50[0],FWOAecoregions) + sumCoast(LWF_fwoa50[2],FWOAecoregions) 
        
        LWF_fwa40 = readLWF(FWA40file)
        Land_FWA_40 = sumCoast(LWF_fwa40[0],FWAecoregions) + sumCoast(LWF_fwa40[2],FWAecoregions) + sumCoast(LWF_fwoa40[0],FWOAecoregions) + sumCoast(LWF_fwoa40[2],FWOAecoregions)
        
        ###########################
        ## Flood Attenuation ##
        ###########################
        print '  Calculating maximum change in inundation depth during 50-year simulation.'

        if calc_flood != 'yes':
            EcoR_flood_atten = {}
            for er in ecoregions:
                EcoR_flood_atten[er] = 0.0
        else:
            d_depth_max = {}
            if prjtype[prj] != 'HP':
                
                comm_info = np.genfromtxt('C:\Eric\CodeIntegration\ICM\ICM_working\metrics_input_communities.csv',delimiter=',',skiprows=1,dtype=str)
                community_ICM = {}
                community_grid = {}
                comm_flood_atten = {}
                comm_flood_atten_date = {}
                
                # assign ICM compartment IDs to communities in dictionary
                for row in comm_info:
                    community = row[0]
                    community_ICM[community]=int(float(row[3]))
                
                communities_for_flood = community_ICM.keys()
                
                # initiliaze community-sized dictionaries to zero or empty arrays
                for community in communities_for_flood:
                    community_grid[community]=[]
                    comm_flood_atten[community] = 0.0
                    comm_flood_atten_date[community] = 'no change'
                # generate arrays of grids associated with each community
                for row in comm_info:
                    community = row[0]
                    community_grid[community].append(int(float(row[1])))    
                
                
                comps_for_flood = community_ICM.values()

                grid_for_flood =  community_grid.values()               
                

                # read in stage timeseries
                FWOA_STG = os.path.normpath(r'%s\\hydro\\output_timeseries\\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_55_H_STGxx.out' % (fwoadir,S,Gfwoa))
                FWOAstage = np.genfromtxt(FWOA_STG,delimiter=',')
                    
                FWA_STG = os.path.normpath(r'%s\\hydro\\output_timeseries\\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_55_H_STGxx.out' % (fwadir,S,Gfwoa))
                FWAstage = np.genfromtxt(FWA_STG,delimiter=',')
                
                dates = []
                start = datetime.datetime.strptime('2015-01-01','%Y-%m-%d')
                end = datetime.datetime.strptime('2064-12-31','%Y-%m-%d')
                step = datetime.timedelta(days=1)
                while start <= end:
                    dates.append(start.date())
                    start += step
                
                # initialize dictionaries where key is year and initial value is zero
                stage_diff_max = {}
                stage_diff_max_date = {}
                
                for yr in flood_atten_years:
                    stage_diff_max[yr] = {}
                    stage_diff_max_date[yr] = {}
                    for comm in communities_for_flood:
                        stage_diff_max[yr][comm] = 0.0
                        stage_diff_max_date[yr][comm] = 'no change'
                
                # calculate daily difference in stage between FWOA and FWA and find maximum difference for each year
                # this will be used with annual elevation changes to determine maximum difference in depth between FWOA and FWA
                for row in range(0,len(dates)):
                    yr = dates[row].year
                    for comm in communities_for_flood:
                        ICMID = community_ICM[comm]
                        col = ICMID - 1
                        stage_diff_day = FWOAstage[row][col] - FWAstage[row][col]
                        if (stage_diff_day > stage_diff_max[yr][ICMID]) :
                            stage_diff_max[yr][comm] = stage_diff_day
                            stage_diff_max_date[yr][comm] = dates[row]
                
                del FWOAstage,FWAstage
                

                
                for yr in flood_atten_years:
                    print '  Calculating maximum flood attenuation in each community for year %s' % yr
                    
                # read in elevaiton of bed for FWOA and FWA for each grid cell
                    FWOAgridfile = os.path.normpath(r'%s\\hydro\\TempFiles\\grid_data_500m_%s.csv' % (fwoadir,yr))
                    FWAgridfile = os.path.normpath(r'%s\\hydro\\TempFiles\\grid_data_500m_%s.csv' % (fwadir,yr))

                    FWOAlandelev = readGridData(FWOAgridfile)[3]
                    FWAlandelev = readGridData(FWAgridfile)[3]
                    
                    for comm in communities_for_flood:
                        print '    %s' % comm
                        ICMID = community_ICM[comm]
                        
                        # calculate change in land elevation for each grid cell associated with a community
                        for gridid in community_grid[comm]:
                            FWOAelev = FWOAlandelev[gridid]
                            if FWOAelev == -9999:
                                FWOAelev = 0.0
                        
                            FWAelev = FWAlandelev[gridid]
                            if FWAelev == -9999:
                                FWAelev = 0.0
                        # calculate attenuation between FWA and FWOA by taking max stage difference for year and land elevation difference for year
                            attenuation = stage_diff_max[yr][comm] - (FWOAelev-FWAelev)
                            if attenuation > comm_flood_atten[comm]:
                                comm_flood_atten[comm] = attenuation
                                comm_flood_atten_date[comm] = stage_diff_max_date[yr][comm]
                            
                        

                EcoR_flood_atten = {}                  
                EcoR_flood_atten_date = {}
                for er in ecoregions:
                    EcoR_flood_atten[er] = 0.0
                    EcoR_flood_atten_date[er] = 'no change'
                    for comm in communities_for_flood:
                        if comm_flood_atten[comm] > EcoR_flood_atten[er]
                            EcoR_flood_atten[er] = comm_flood_atten[comm]
                            EcoR_flood_atten_date[er] = comm_flood_atten_date[comm]
                        
            
            else: # if flood attenuation is 
                EcoR_flood_atten = {}
                for er in ecoregions:
                    EcoR_flood_atten[er] = 0.0

        ######################
        ##  Read grid data  ##
        ######################
        print '  Reading in land/water/elevation data summarized by 500-m grid cell'
        griddata = readGridData(FWOA00gridfile)
        FWOA_elev_m_00 = griddata[0]
        FWOA_lnd_pct_00 = griddata[1]
        FWOA_wat_pct_00 = griddata[2]
        
        griddata = readGridData(FWOA50gridfile)
        FWOA_elev_m_50 = griddata[0]
        FWOA_lnd_pct_50 = griddata[1]
        FWOA_wat_pct_50 = griddata[2]
        
        griddata = readGridData(FWOA30gridfile)
        FWOA_elev_m_30 = griddata[0]
        FWOA_lnd_pct_30 = griddata[1]
        FWOA_wat_pct_30 = griddata[2]
        
        griddata = readGridData(FWOA10gridfile)
        FWOA_elev_m_10 = griddata[0]
        FWOA_lnd_pct_10 = griddata[1]
        FWOA_wat_pct_10 = griddata[2]
        
        griddata = readGridData(FWA50gridfile)
        FWA_elev_m_50 = griddata[0]
        FWA_lnd_pct_50 = griddata[1]
        FWA_wat_pct_50 = griddata[2]
        
        griddata = readGridData(FWA30gridfile)
        FWA_elev_m_30 = griddata[0]
        FWA_lnd_pct_30 = griddata[1]
        FWA_wat_pct_30 = griddata[2]
        
        griddata = readGridData(FWA10gridfile)
        FWA_elev_m_10 = griddata[0]
        FWA_lnd_pct_10 = griddata[1]
        FWA_wat_pct_10 = griddata[2]
        
        del griddata

        # filter FWA grid data so that only ecoregions with project impacts are used, all others will use FWOA data
        print '  Filter FWA data to only use output from impacted Ecoregions.'
        for g in grid_eco.keys():
            EcoR = grid_eco[g]
            G_to_use = prj_groups[prj][EcoR]
            if (G_to_use == 'G001'):
                FWA_elev_m_10[g] = FWOA_elev_m_10[g]
                FWA_elev_m_10[g] = FWOA_elev_m_30[g]
                FWA_elev_m_10[g] = FWOA_elev_m_50[g]            
                
                FWA_lnd_pct_10[g] = FWOA_lnd_pct_10[g]
                FWA_lnd_pct_10[g] = FWOA_lnd_pct_30[g]
                FWA_lnd_pct_10[g] = FWOA_lnd_pct_50[g]

                FWA_wat_pct_10[g] = FWOA_wat_pct_10[g]
                FWA_wat_pct_10[g] = FWOA_wat_pct_30[g]
                FWA_wat_pct_10[g] = FWOA_wat_pct_50[g]
        
        ######################################
        ##  Read grid-to-zone lookup tables ##
        ######################################
        gridNavlookupFile = 'C:\\Eric\\ICM\\2017MP\\Metrics\\NavChannelGridPoints.csv'
        navgrid = {}
        for n in navregions:
            navgrid[n]=[]
            
        with open(gridNavlookupFile,mode='rU') as infile:
            lineno = 0
            reader = csv.reader(infile)
            for rows in reader:
                if lineno != 0:     # skip header row
                    navgrid[rows[1]].append(int(rows[0]))
                lineno += 1
                        
        ##############################
        ##  Sustainability of land  ##
        ##############################
        ##  coastwide metric  ##
        ########################
        ## project-level calc ##
        ########################
        print '  Calculating Sustainability of land'
        
        if Land_FWOA_50 >= Land_FWOA_00:
            progress = (Land_FWA_50 - Land_FWOA_50) / (Land_FWOA_50 - Land_FWOA_00)
        else:
            progress = (Land_FWA_50 - Land_FWOA_50) / (Land_FWOA_00 - Land_FWOA_50)

        trajectory = (Land_FWA_50 - Land_FWA_40)/(Land_FWOA_50 - Land_FWOA_40)

        sustainability[prj] = 0.5*(trajectory + progress)
        
        ##################################
        ##  Suitability for Navigation  ##
        ##################################
        ##  coastwide metric  ##
        ########################
        ## project-level calc ##
        ########################
        
        print '  Calculating Support for Navigation'
    
        Li = {}
        EL = {}
        SFC_10 = {}
        SFC_30 = {}
        SFC_50 = {}
        
        # loop over each nav region    
        for r in navregions:
        # set intial Li dictionary value to an empty array for each nav region
            Li[r] = []
        # set multiplier for extent of land equations (EL) for Mississippi River channel
            if r == 'NAVMR':
                NC = 0.5
            else:
                NC = 1.0

        # loop over grid cells that are in the nav region - some grid cells in Nav channels are outside of morph/veg domain, set land area to 0 for these grid cells
        # land_pct is percentage from 0-100, multiply by grid cell area and divide by 100 to get actual area in square meters
            for g in navgrid[r]:   
                try:
                    FWA_land_50 = max(FWA_lnd_pct_50[g]*500.0*500.0/100.0,0.0)
                except:
                    FWOA_land_50 = 0.0
                try:
                    FWOA_land_0 = max(FWOA_lnd_pct_00[g]*500.0*500.0/100.0,0.0)
                except:
                    FWOA_land_0 = 0.0
                try:
                    FWOA_land_50 = max(FWOA_lnd_pct_50[g]*500.0*500.0/100.0,0.0)
                except:
                    FWOA_land_50 = 0.0

        # calculate extent of land at year 50 term, L, for each grid cell (includes region-specific MSR value)
                if FWA_land_50 <= FWOA_land_50:
                    li_value = 0.0
                elif FWOA_land_50 > FWOA_land_0:
                    li_value = NC*(FWA_land_50 - FWOA_land_50)/(FWOA_land_50 - FWOA_land_0)
                elif FWOA_land_50 < FWOA_land_0:
                    li_value = NC*(FWA_land_50 - FWOA_land_50)/ (FWOA_land_0 - FWOA_land_50)
                else: # this else case covers the condition where (FWOA_land_0 = FWOA_land_50) and there is gain from the project
                    li_value = 1.0
                    
                
                Li[r].append(li_value)
        # if not in Mississippi River channel, calculate additional shoaling term from years 10, 30, and 50(SFC)
                if r == 'NAVFC':
                    try:
                        if (FWA_elev_m_10[g] == -9999) or (FWOA_elev_m_10[g] == -9999):
                            dElev_10 = 0.0
                        else:
                            dElev_10 = FWA_elev_m_10[g] - FWOA_elev_m_10[g]
                    except:
                        dElev_10 = 0.0
 
                    try:
                        if (FWA_elev_m_30[g] == -9999) or (FWOA_elev_m_30[g] == -9999):
                            dElev_30 = 0.0
                        else:
                            dElev_30 = FWA_elev_m_30[g] - FWOA_elev_m_30[g]
                    except:
                         dElev_30 = 0.0
 
                    try:
                        if (FWA_elev_m_50[g] == -9999) or (FWOA_elev_m_50[g] == -9999):
                            dElev_50 = 0.0
                        else:
                            dElev_50 = FWA_elev_m_50[g] - FWOA_elev_m_50[g]
                    except:
                        dElev_50 = 0.0

                    if dElev_10 <= 0:
                        SFC_10[g] = 0.0
                    elif dElev_10 <= 0.15:
                        SFC_10[g] = -0.5*dElev_10/0.15
                    elif dElev_10<= 0.3:
                        SFC_10[g] = -0.7                
                    elif dElev_10 <= 0.6:
                        SFC_10[g] = -0.9
                    else:
                        SFC_10[g] = -1.0

                    if dElev_30 <= 0:
                        SFC_30[g] = 0.0
                    elif dElev_30 <= 0.15:
                        SFC_30[g] = -0.5*dElev_30/0.15
                    elif dElev_30<= 0.3:
                        SFC_30[g] = -0.7                
                    elif dElev_30 <= 0.6:
                        SFC_30[g] = -0.9
                    else:
                        SFC_30[g] = -1.0
                        
                    if dElev_50 <= 0:
                        SFC_50[g] = 0.0
                    elif dElev_50 <= 0.15:
                        SFC_50[g] = -0.5*dElev_50/0.15
                    elif dElev_50<= 0.3:
                        SFC_50[g] = -0.7                
                    elif dElev_50 <= 0.6:
                        SFC_50[g] = -0.9
                    else:
                        SFC_50[g] = -1.0
            if prjtype[prj] == 'SP' or prjtype[prj] == 'BS':
                EL[r] = 1.0
            else:
                EL[r] = float(sum(Li[r]))/float(len(Li[r]))
        
        
        
        ####################################
        ## Non-Mississippi River Shoaling ##
        ####################################
        SFC_10_all = float(sum(SFC_10.values()))/float(len(SFC_10))   
        SFC_30_all = float(sum(SFC_30.values()))/float(len(SFC_30))   
        SFC_50_all = float(sum(SFC_50.values()))/float(len(SFC_50))   
        SFC = 0.5*SFC_10_all + 0.25*SFC_30_all + 0.25*SFC_50_all
        ##################################
        ##  Mississippi River Steerage  ##
        ##################################
        try:
            SMSRp = SMSR[prj]
        except:
            SMSRp = 0.0
        ###################################
        ## Support for Navigation Metric ##
        ###################################
    
        NavMSR[prj] = (EL['NAVMR'] + SMSRp + NewStructures[prj])/3.0
        NavFC[prj] = (EL['NAVFC'] + SFC + NewStructures[prj])/3.0
        
        # Write informative output terms
        of.write('\n%s,' % prj)   
        of.write('%s,' % prjtype[prj])
        of.write('%s,' % prjdesc[prj])
        of.write('%s,' % S)
        
        # Write Support for Nav terms
        try:
            of.write('%s,' % EL['NAVMR'])
        except:
            of.write('NA,')
        try:
            of.write('%s,' % EL['NAVFC'])
        except:
            of.write('NA,')
        try:
            of.write('%s,' % SMSRp)
        except:
            of.write('NA,')
        try:
            of.write('%s,' % SFC)
        except:
            of.write('NA,')
        try:
            of.write('%s,' % NavMSR[prj])
        except:
            of.write('NA,')
        try:
            of.write('%s,' % NavFC[prj])
        except:
            of.write('NA,')
        try:
            of.write('%s,' % NewStructures[prj])
        except:
            of.write('NA,')
        
        # Write Support for Nav Metric that is final output    
        if prjtype[prj] == 'DI':
            of.write('%s,' % NavMSR[prj])
        elif prjtype[prj] == 'HP':
            of.write('%s,' % NewStructures[prj])
        else:
            of.write('%s,' % NavFC[prj])
           
       
       # write Sustainability of Land Metric
        try:
            of.write('%s,' % progress)
        except:
            of.write('NA,') 
        try:
            of.write('%s,' % trajectory)
        except:
            of.write('NA,') 
        try:
            of.write('%s,' % sustainability[prj])
        except:
            of.write('NA,') 
        
        # write Natural Processes metric terms
        try:
            of.write('%s,' % dXarea[prj])
            NP_H = abs(dXarea[prj])/maxdXmag
        except:
            of.write('NA,') 
        try:
            of.write('%s,' % (abs(dXarea[prj])/maxdXmag) )
        except:
            of.write('NA,') 
        
        try:
            of.write('%s,' % SedVol[prj])
        except:
            of.write('NA,')
        try:
            of.write('%s,' % (0.1 + 0.3*(SedVol[prj]-minSed)/(maxSed-minSed)) )
            
        except:
            of.write('NA,')
            
        try:
            of.write('%s,' % DIsed[prj])
        except:
            of.write('NA,')
        try:
            of.write('%s,' % (0.4+ 0.6*(DIsed[prj]-minDIsed)/(maxDIsed-minDIsed)) )
        except:
            of.write('NA,')
        
        try:
            of.write('%s,' % NP_HP[prj])
        except:
            of.write('NA,')
        
        # Write Natural Processes Metric that is final output                
        if prjtype[prj] == 'DI':
            NatProc = 0.4+ 0.6*(DIsed[prj]-minDIsed)/(maxDIsed-minDIsed)
        elif prjtype[prj] == 'MC' or prjtype[prj] == 'BH':
            NatProc  = 0.1 + 0.3*(SedVol[prj]-minSed)/(maxSed-minSed)
        elif prjtype[prj] == 'HP':
            NatProc = NP_HP[prj]
        elif prjtype[prj] == 'HR' or prjtype[prj] == 'RC':
            NatProc = abs(dXarea[prj])/maxdXmag
        else:
            NatProc = 0.0
        
        of.write('%s,' % NatProc)
                
        for er in ecoregions:
            try:
                of.write('%s,' % EcoR_flood_atten[er])
            except:
                of.write('NA,')
        
