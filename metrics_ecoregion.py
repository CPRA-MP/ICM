import numpy as np
import os
import csv
import datetime

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

maindir = os.path.normpath(r'C:\\ICM\\metrics\\metrics_input_from_SFTP')
fwoadir = os.path.normpath(r'%s\\%s\\%s' % (maindir,S,Gfwoa))        

inputdir = os.path.normpath(r'C:\\ICM\\metrics')

project_list_file = os.path.normpath('%s\\project_list.csv' % inputdir)  
prj_eco_file = os.path.normpath('%s\\project_ecoregions.csv' % inputdir)

HR_RC_info_file = os.path.normpath('%s\\metrics_input_HR_RC.csv' % inputdir)
MC_info_file = os.path.normpath('%s\\metrics_input_MC.csv' % inputdir)
HP_info_file = os.path.normpath('%s\\metrics_input_HP.csv' % inputdir)
BH_info_file = os.path.normpath('%s\\metrics_input_BH.csv' % inputdir)
DI_info_file = os.path.normpath('%s\\metrics_input_DI.csv' % inputdir)
comm_info_file = os.path.normpath('%s\\metrics_input_communities.csv' % inputdir)           
                                                                                            
                                                                                            
ecor_date_outputfile = os.path.normpath('%s\\S01_metrics_attenuation_dates_by_ecoregion.csv' % inputdir)
ecor_outputfile = os.path.normpath('%s\\S01_metrics_attenuation_by_ecoregion.csv' % inputdir)   
comm_date_outputfile = os.path.normpath('%s\\S01_metrics_attenuation_dates_by_community.csv' % inputdir)
comm_outputfile = os.path.normpath('%s\\S01_metrics_attenuation_by_community.csv' % inputdir)
grid_date_outputfile = os.path.normpath('%s\\S01_metrics_attenuation_dates_by_grid.csv' % inputdir)
grid_outputfile = os.path.normpath('%s\\S01_metrics_attenuation_by_grid.csv' % inputdir)

# check if output files already exist
if os.path.isfile(ecor_date_outputfile):
    print ' Output file already exixts - type suffix to append to name and press enter:'
    suffix = raw_input()
    split = ecor_date_outputfile.split('.')
    ecor_date_outputfile = os.path.normpath('%s_%s.%s' % (split[0],suffix,split[1]))
    print ' Output file now named: %s' % ecor_date_outputfile
if os.path.isfile(ecor_outputfile):
    print ' Output file already exixts - type suffix to append to name and press enter:'
    suffix = raw_input()
    split = ecor_outputfile.split('.')
    ecor_date_outputfile = os.path.normpath('%s_%s.%s' % (split[0],suffix,split[1]))
    print ' Output file now named: %s' % ecor_date_outputfile
if os.path.isfile(comm_date_outputfile):
    print ' Output file already exixts - type suffix to append to name and press enter:'
    suffix = raw_input()
    split = comm_date_outputfile.split('.')
    comm__date_outputfile = os.path.normpath('%s_%s.%s' % (split[0],suffix,split[1]))
    print ' Output file now named: %s' % comm__date_outputfile
if os.path.isfile(comm_outputfile):
    print ' Output file already exixts - type suffix to append to name and press enter:'
    suffix = raw_input()
    split = comm_outputfile.split('.')
    comm_outputfile = os.path.normpath('%s_%s.%s' % (split[0],suffix,split[1]))
    print ' Output file now named: %s' % comm_outputfile


stage_error = 0.11
navregions = ['NAVMR','NAVFC']

attenuation_interval = 1
flood_atten_years = range(2015,2064,attenuation_interval)
flood_atten_years.append(2064)

##################################
#### build empty dictionaries ####
##################################
# key will be grid ID
grid_eco = {}
grid_ICM = {}
grid_comm = {}
grid_max_atten = {}
grid_max_atten_date = {}

# key will be project
prjgrp = {}
NewStructures = {}
prjtype = {}
prjdesc = {}
prj_groups = {}
prj_atten = {}
prj_dates = {}

# key will be community            
comm_er = {}
comm_atten = {}
comm_date = {}

# key will be ecoregion
er_atten = {}
er_date = {}
             


####################################
#### done building dictionaries ####
####################################

print ' Reading in project-ecoregion lookup table.'
prj_eco_lookup =np.genfromtxt(prj_eco_file,delimiter=',',dtype=str)

#first row of prj_eco_lookup is ecoregions header
prj_eco_head = prj_eco_lookup[0]
ecoregions = prj_eco_head[1:]
nrows = int(prj_eco_lookup.shape[0])
ncols = int(prj_eco_lookup.shape[1])

# loop through table and assign Group number to use for each ecoregion for the project (e.g. FWOA or FWA)
# first row is ecoregions text - skip this row
for row in range(1,nrows): 
    groups = {}
#first column is prj_eco_lookup[row][0]project number
    prjid = prj_eco_lookup[row][0]
#loop through columns and add group number from file to dictionary for each project number
    for col in range(1,ncols):
        groups[prj_eco_head[col]] = prj_eco_lookup[row][col]

    prj_groups[prjid] = groups



   
# read in project and group numbers
p = np.genfromtxt(project_list_file,dtype='str',skiprows=1,delimiter=',')
for row in p:
    pr = row[1]
    gr = row[0]
    prjgrp[pr] = gr
    NewStructures[pr] = float(row[4])
    prjtype[pr] = str.split(pr,'.')[1]
    prjdesc[pr] = row[2]

projects = prjgrp.keys()

del p

# assign ICM compartment IDs and communities to grid cell in dictionary
comm_info = np.genfromtxt(comm_info_file,delimiter=',',skiprows=1,dtype=str)
for row in comm_info:
    grid = int(float(row[2]))
    comm = row[0]
    er = row[4]
    icm = int(float(row[3]))
    
    grid_comm[grid] = comm 
    grid_ICM[grid] = icm
    grid_eco[grid] = er

    if not comm in comm_er.keys():
        comm_er[comm] = er

dates = []
start = datetime.datetime.strptime('2015-01-01','%Y-%m-%d')
end = datetime.datetime.strptime('2064-12-31','%Y-%m-%d')
step = datetime.timedelta(days=1)
while start <= end:
    dates.append(start.date())
    start += step

# read in stage timeseries for FWOA
FWOA_STG = os.path.normpath(r'%s\\hydro\\output_timeseries\\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_50_H_STGxx.out' % (fwoadir,S,Gfwoa))
FWOAstage = np.genfromtxt(FWOA_STG,delimiter=',')

for Gfwa in set(unique_g for Gs in prjgrp for unique_g in prjgrp.values()):
    outputfile = 'C:\\ICM\\metrics\\S01_atten_all_data_%s.csv' % Gfwa
    with open(outputfile, 'w' ) as outfile:
        outfile.write('year,ecoregion,comm,ICMID,grid,atten_m,FWOA_wsel_in_max_diff,FWOAelev,FWOA_land,FWOA_land_elev,FWOA_bed_elev,FWA_wsel_in_max_diff,FWAelev,FWA_land,FWA_land_elev,FWA_bed_elev')
      
        print ' Reading in stage and elevation data for %s' % Gfwa
        
        fwadir = os.path.normpath(r'%s\\%s\\%s' % (maindir,S,Gfwa))
        
        FWA_STG = os.path.normpath(r'%s\\hydro\\output_timeseries\\MPM2017_%s_%s_C000_U00_V00_SLA_O_01_50_H_STGxx.out' % (fwadir,S,Gfwa))
        FWAstage = np.genfromtxt(FWA_STG,delimiter=',')
        
        # initialize dictionaries where key is year and initial value is zero
        stage_diff_max = {}
        stage_diff_max_date = {}
        FWOA_stg = {}
        FWA_stg = {}
            
        
        for yr in range(2015,2065):#flood_atten_years:
            stage_diff_max[yr] = {}
            stage_diff_max_date[yr] = {}
            FWOA_stg[yr] = {}
            FWA_stg[yr] = {}
            for gridid in grid_ICM.keys():
                stage_diff_max[yr][gridid] = 0.0
                stage_diff_max_date[yr][gridid] = 'nochange'
                FWOA_stg[yr][gridid] = -9999
                FWA_stg[yr][gridid] = -9999
        # calculate daily difference in stage between FWOA and FWA and find maximum difference for each year
        # this will be used with annual elevation changes to determine maximum difference in depth between FWOA and FWA
        
        for row in range(0,len(dates)):
            yr = dates[row].year
            mn = dates[row].month
            dy = dates[row].day
            for gridid in grid_ICM.keys():
                ICMID = grid_ICM[gridid]
                col = ICMID - 1
                stage_diff_day = FWOAstage[row][col] - FWAstage[row][col]

                if (stage_diff_day > stage_diff_max[yr][gridid]):
                    FWOA_stg[yr][gridid] = FWOAstage[row][col]
                    FWA_stg[yr][gridid] = FWAstage[row][col]
                    stage_diff_max[yr][gridid] = stage_diff_day
                    stage_diff_max_date[yr][gridid] = dates[row]

        del FWAstage,stage_diff_max
        
        for yr in flood_atten_years:
            print '  Calculating maximum flood attenuation in each community for year %s' % yr
            
        # read in elevaiton of bed for FWOA and FWA for each grid cell
            FWOAgridfile = os.path.normpath(r'%s\\hydro\\TempFiles\\grid_data_500m_%s.csv' % (fwoadir,yr))
            FWAgridfile = os.path.normpath(r'%s\\hydro\\TempFiles\\grid_data_500m_%s.csv' % (fwadir,yr))
        
            FWOAgrid = readGridData(FWOAgridfile)        
            FWOAbedelev = FWOAgrid[0]
            FWOApctland = FWOAgrid[1]
            FWOAlandelev = FWOAgrid[3]
            
            FWAgrid = readGridData(FWAgridfile)        
            FWAbedelev = FWAgrid[0]
            FWApctland = FWAgrid[1]
            FWAlandelev = FWAgrid[3]

            
            for gridid in grid_ICM.keys():
                # calculate change in land elevation for each grid cell associated with a community
                # check if community's grid cell is within ICM grid domain
                FWOA_wsel = FWOA_stg[yr][gridid]
                FWA_wsel = FWA_stg[yr][gridid]
                
                if gridid == -9999:
                    FWOAelev = 0.0
                    FWAelev = 0.0
                else:
                    try:
                        FWOA_land = max(0.0,FWOApctland[gridid]/100.0) # max-zero filter sets -9999 percent land to 0% land
                    except:
                        FWOA_land = 0.0
                        
                    try:
                        FWOA_land_elev = FWOAlandelev[gridid]
                        if FWOA_land_elev == -9999:
                            FWOA_land_elev = 0.0
                    except:
                        FWOA_land_elev = 0.0
                    
                    try:
                        FWOA_bed_elev = FWOAbedelev[gridid]
                        if FWOA_bed_elev == -9999:
                            FWOA_bed_elev = 0.0
                    except:
                        FWOA_bed_elev = 0.0
                    
                    FWOAelev = FWOA_land_elev*FWOA_land + FWOA_bed_elev*(1.0-FWOA_land)
                    
                    try:
                        FWA_land = max(0.0,FWApctland[gridid]/100.0) # max-zero filter sets -9999 percent land to 0% land
                    except:
                        FWA_land = 0.0    
                    try:
                        FWA_land_elev = FWAlandelev[gridid]
                        if FWA_land_elev == -9999:
                            FWA_land_elev = 0.0
                    except:
                        FWA_land_elev = 0.0
                    
                    try:
                        FWA_bed_elev = FWAbedelev[gridid]
                        if FWA_bed_elev == -9999:
                            FWA_bed_elev = 0.0
                    except:
                        FWA_bed_elev = 0.0

                    FWAelev = FWA_land_elev*FWA_land + FWA_bed_elev*(1.0-FWA_land)
                    
                #calculate attenuation between FWA and FWOA by taking max stage difference for year and land elevation difference for year
                if abs(FWA_wsel - FWOA_wsel) <= stage_error:
                    attenuation = 0.0
                else:
                    try:
                        attenuation = (FWOA_wsel - FWOAelev) - (FWA_wsel - FWAelev)
                    except:
                        attenuation = 0.0
                
                try:
                    if attenuation > grid_max_atten[gridid]:
                        grid_max_atten[gridid] = attenuation
                        grid_max_atten_date[gridid] = stage_diff_max_date[yr][gridid]
                except:
                    grid_max_atten[gridid] = 0.0
                    grid_max_atten_date[gridid] = 'no_change'
                    
                outfile.write('\n%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (yr,grid_eco[gridid],grid_comm[gridid],grid_ICM[gridid],gridid,attenuation,FWOA_wsel,FWOAelev,FWOA_land,FWOA_land_elev,FWOA_bed_elev,FWA_wsel,FWAelev,FWA_land,FWA_land_elev,FWA_bed_elev))

# finished looping over grid - and close output file for Group

    # cycle through projects and update output file if project is in current group, Gfwa
    for prj in projects:
        if prjgrp[prj] == Gfwa:
            #determine which ecoregions are impacted by project                
            FWOAecoregions = []
            FWAecoregions = []
            for er in ecoregions:
                G_ecoR = prj_groups[prj][er]
                if G_ecoR == 'G001':
                    FWOAecoregions.append(er)
                else:
                    FWAecoregions.append(er)

            prj_atten[prj] = {}
            prj_dates[prj] = {}

            for gridid in grid_ICM.keys(): 
                er = grid_eco[gridid]
                if er in FWAecoregions:
                    prj_atten[prj][gridid] = grid_max_atten[gridid]
                    prj_dates[prj][gridid] = grid_max_atten_date[gridid]
                else:
                    prj_atten[prj][gridid] = 0.0
                    prj_dates[prj][gridid] = 'outside_of_impact_area'

#Finished looping through each group - now summarize output

print ' Determining max attenuation in each community and ecoregion.'

for prj in projects:
    comm_atten[prj] = {}
    comm_date[prj] = {}
    er_atten[prj] ={}
    er_date[prj] = {}
        
    for gridid in grid_ICM.keys():
        comm = grid_comm[gridid]
        atten = prj_atten[prj][gridid]
        date = prj_dates[prj][gridid]
        
        er = comm_er[comm]
        
        try:
            comm_max_so_far = comm_atten[prj][comm]
        except:
            comm_atten[prj][comm] = 0.0
            comm_max_so_far = 0.0
            comm_date[prj][comm] = 'no_change'
        if er <> 'extended_grid':    
            if atten > comm_max_so_far:
                comm_atten[prj][comm] = atten
                comm_date[prj][comm] = date
            
    for comm in comm_atten[prj].keys():
        er = comm_er[comm]
        atten = comm_atten[prj][comm]
        date = comm_date[prj][comm]
        
        try:
            er_max_so_far = er_atten[prj][er]
        except:
            er_atten[prj][er] = 0.0
            er_max_so_far = 0.0
            er_date[prj][er] = 'no_change'
        
        if atten > er_max_so_far:
            er_atten[prj][er] = atten
            er_date[prj][er] = date





print ' Writing attenuation grid output file.'
with open(grid_outputfile, 'w' ) as outfile:
    # write header in output file
    outfile.write('GRID,ECOREGION,COMMUNITY')
    for prj in projects:
        outfile.write(',%s' % prj)
    # write output data, each row is grid, each column is project
    for gridid in grid_ICM.keys():
        outfile.write('\n%s,%s,%s' % (gridid,grid_eco[gridid],grid_comm[gridid]))
        for prj in projects:
             outfile.write(',%s' % prj_atten[prj][gridid])
        
    
print ' Writing attenuation dates grid output file.'
with open(grid_date_outputfile, 'w' ) as outfile:
    # write header in output file
    outfile.write('GRID,ECOREGION,COMMUNITY')
    for prj in projects:
        outfile.write(',%s' % prj)
    # write output data, each row is grid, each column is project
    for gridid in grid_ICM.keys():
        outfile.write('\n%s,%s,%s' % (gridid,grid_eco[gridid],grid_comm[gridid]))
        for prj in projects:
             outfile.write(',%s' % prj_dates[prj][gridid])
             
print ' Writing attenuation community output file.'
with open(comm_outputfile, 'w' ) as outfile:
    # write header in output file
    outfile.write('ECOREGION,COMMUNITY')
    for prj in projects:
        outfile.write(',%s' % prj)
    # write output data, each row is grid, each column is project
    for comm in comm_atten[prj].keys():
        outfile.write('\n%s,%s' % (comm_er[comm],comm))
        for prj in projects:
             outfile.write(',%s' % comm_atten[prj][comm])

print ' Writing attenuation dates community output file.'
with open(comm_date_outputfile, 'w' ) as outfile:
    # write header in output file
    outfile.write('ECOREGION,COMMUNITY')
    for prj in projects:
        outfile.write(',%s' % prj)
    # write output data, each row is grid, each column is project
    for comm in comm_atten[prj].keys():
        outfile.write('\n%s,%s' % (comm_er[comm],comm))
        for prj in projects:
             outfile.write(',%s' % comm_date[prj][comm])

print ' Writing attenuation ecoregion output file.'
with open(ecor_outputfile, 'w' ) as outfile:
    # write header in output file
    outfile.write('ECOREGION')
    for prj in projects:
        outfile.write(',%s' % prj)
    # write output data, each row is grid, each column is project
    for er in er_atten[prj].keys():
        outfile.write('\n%s' % er)
        for prj in projects:
             outfile.write(',%s' % er_atten[prj][er])

print ' Writing attenuation dates community output file.'
with open(ecor_date_outputfile, 'w' ) as outfile:
    # write header in output file
    outfile.write('ECOREGION')
    for prj in projects:
        outfile.write(',%s' % prj)
    # write output data, each row is grid, each column is project
    for er in er_atten[prj].keys():
        outfile.write('\n%s' % er)
        for prj in projects:
             outfile.write(',%s' % er_date[prj][er])