

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

def readVgTyp(VgTypcsv):
    fresh_forest = {}
    fresh_marsh = {}
    int_marsh = {}
    brack_marsh = {}
    salt_marsh = {}
    water = {}
    upland = {}
    with open(VgTypcsv,mode='rU') as infile:
        lineno = 0
        reader = csv.reader(infile)
        for rows in reader:
            if lineno != 0:     # skip header row
                fresh_forest[rows[0]] = float(rows[1])
                fresh_marsh[rows[0]] = float(rows[2])
                int_marsh[rows[0]] = float(rows[3])
                brack_marsh[rows[0]] = float(rows[4])
                salt_marsh[rows[0]] = float(rows[5])
                water[rows[0]] = float(rows[6])
                upland[rows[0]] = float(rows[7])
            lineno += 1
    return [fresh_forest,fresh_marsh,int_marsh,brack_marsh,salt_marsh,water,upland]

def Ave3yrHSI_ecoregion_sum(HSItyp,location,year,sterm,gterm,ascii_grid_lookup,nrows,ncols,ecogrid):
    HSIfile3 = os.path.normpath(r'%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_O_%02d_%02d_X_%s.asc' % (location,year,sterm,gterm,year,year,HSItyp) )
    HSIfile2 = os.path.normpath(r'%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_O_%02d_%02d_X_%s.asc' % (location,year-1,sterm,gterm,year-1,year-1,HSItyp) )
    HSIfile1 = os.path.normpath(r'%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_O_%02d_%02d_X_%s.asc' % (location,year-2,sterm,gterm,year-2,year-2,HSItyp) )
    h1 = np.genfromtxt(HSIfile1,skiprows=6,delimiter=' ',dtype=float)
    h2 = np.genfromtxt(HSIfile2,skiprows=6,delimiter=' ',dtype=float)
    h3 = np.genfromtxt(HSIfile3,skiprows=6,delimiter=' ',dtype=float)
    
    h123mean = (h1+h2+h3)/3
    
    meanHSI = {}
    for m in range(0,nrows):                                                           
        for n in range(0,ncols):                                                       
            gridID = ascii_grid_lookup[m][n]                                           
            if gridID == -9999:                                                        
                meanHSI[gridID] = -9999                                                  
            else:                                                                      
                try:                                                                   
                    meanHSI[gridID] = h123mean[m][n]
                except:
                    meanHSI[gridID] = -9999                         
    
    # sum mean HSI value from all grid points within each Ecoregion
    meanHSI_er_sum = {}
    for er in ecogrid.keys():
        meanHSI_er_sum[er] = 0.0
        for grid in ecogrid[er]:
            if meanHSI[grid] != -9999:
                meanHSI_er_sum[er] += meanHSI[grid]
        
    del meanHSI
    
    return[meanHSI_er_sum]


print 'Formatting output for Planning Tool...'

import os
import csv
import sys
import numpy as np

# Set some specific, hardcoded variables
inputdir = os.path.normpath(r'C:\\Eric\\CodeIntegration\\ICM\\ICM_working')
outputfile = os.path.normpath('%s\\metrics_to_PT_20151218.csv' % inputdir)
Ss = ['S01','S03','S04']
Gfwoa = 'G001'
prjdir = os.path.normpath('N:\\Natural_Systems\\MP\\Production\\Results')
prj_eco_file = os.path.normpath('C:\\Eric\\CodeIntegration\\ICM\\ICM_working\\project_ecoregions.csv')
years = [5,10,15,20,25,30,35,40,45,50]
PTcodes = ['LND','BLH','SWA','FRM','INM','BMH','SAM','ALLIG']#,'BAYAA',' BAYAJ','BLUCJ','BRWNP','BSHRL','BSHRS','CRAYF','GADWA','GMENA','GMENJ','GTEAL','LMBAS','MOTDK','NITUP','OYSTE','SPSTA','SPSTJ','WSHRL','WSHRS']

HSIcodes = ['ALLIG']#,'BAYAA','BAYAJ','BLUCJ','BRWNP','BSHRL','BSHRS','CRAYF','GADWA','GMENA','GMENJ','GTEAL','LMBAS','MOTDK','NITUP','OYSTE','SPSTA','SPSTJ','WSHRL','WSHRS']


# check if output file already exists
if os.path.isfile(outputfile):
    print ' Output file already exixts - type suffix to append to name and press enter:'
    suffix = raw_input()
    split = outputfile.split('.')
    outputfile = os.path.normpath('%s_%s.%s' % (split[0],suffix,split[1]))
    print ' Output file now named: %s' % outputfile

            
ascii_grid_lookup_file = os.path.normpath('C:\\Eric\\CodeIntegration\\ICM\\ICM_working\\veg_grid.asc')
ascii_grid_lookup = np.genfromtxt(ascii_grid_lookup_file,skiprows=6,delimiter=' ',dtype=float)

project_list_file = os.path.normpath('%s\\project_list_WI_G020.csv' % inputdir)
# read in project and group numbers
p = np.genfromtxt(project_list_file,dtype='str',skiprows=1,delimiter=',')
prjgrp = {}
for row in p:
    pr = row[1]
    gr = row[0]
    prjgrp[pr] = gr

                       
print ' Reading in project-ecoregion lookup table.'
prj_eco_lookup =np.genfromtxt(prj_eco_file,delimiter=',',dtype=str)

nrows = int(prj_eco_lookup.shape[0])
ncols = int(prj_eco_lookup.shape[1])

prj_groups = {}

#first row of prj_eco_lookup is ecoregions header
prj_eco_head = prj_eco_lookup[0]
ecoregions = prj_eco_head[1:]

for row in range(1,nrows):
    groups = {}
#first column is project number
    prj = prj_eco_lookup[row][0]
#loop through columns and add group number from file to dictionary for each project number
    for col in range(1,ncols):
	groups[prj_eco_head[col]] = prj_eco_lookup[row][col]

    prj_groups[prj] = groups

del prj, prj_eco_lookup,groups,nrows,ncols

print ' Reading in grid-to-ecoregion lookup.'
gridEcolookupFile = os.path.normpath('%s\\EcoRegionGridPoints.csv' % inputdir)
grid_eco = {}
ecogrid={}
for e in ecoregions:
    ecogrid[e]=[]    

with open(gridEcolookupFile,mode='rU') as infile:
    lineno = 0
    reader = csv.reader(infile)
    for rows in reader:
        if lineno != 0:     # skip header row
            # grid_eco is a dictionary where each key is the grid ID with value that is the Ecoregion that grid ID is in
            grid_eco[int(rows[0])] = rows[1]
            # ecogrid is dictionary where each key is ecoregion with values that are an array of grid IDs in that ecoregion
            ecogrid[rows[1]].append(int(rows[0]))


with open(outputfile,'wb') as writeout:                 
    print ' Opening %s' % outputfile                    
    writeout.write('prj_no,S,year,code,ecoregion,value\n')

    for S in Ss:
        fwoadir = os.path.normpath('N:\\Natural_Systems\\MP\\Production\\Results\\%s\\%s' % (S,Gfwoa))
        
        #meanHSI_G_HSI_yr_ecor will be a dictionary of dictionaries, keys are: group,HSI,year, and ecoregion
        meanHSI_G_HSI_yr_ecor = {}
        meanHSI_G_HSI_yr_ecor[Gfwoa] = {}
        
        for HSI in HSIcodes:

            meanHSI_G_HSI_yr_ecor[Gfwoa][HSI] = {}

            for year in [3,5,10,15,20,25,30,35,40,45,50]:
                print ' Calculating FWOA mean %s HSI for year %s' % (HSI,year)
                meanHSI_G_HSI_yr_ecor[Gfwoa][HSI][year] = Ave3yrHSI_ecoregion_sum(HSI,fwoadir,year,S,Gfwoa,ascii_grid_lookup,615,1259,ecogrid)

        for Gfwa in set(unique_g for Gs in prjgrp for unique_g in prjgrp.values()):

            fwadir = os.path.normpath('N:\\Natural_Systems\\MP\\Production\\Results\\%s\\%s' % (S,Gfwa))
            
            meanHSI_G_HSI_yr_ecor[Gfwa] = {}
            
            for HSI in HSIcodes:

                meanHSI_G_HSI_yr_ecor[Gfwa][HSI] = {}

                for year in [3,5,10,15,20,25,30,35,40,45,50]:
                    print ' Calculating %s FWA mean %s HSI for year %s' % (Gfwa,HSI,year)
                    meanHSI_G_HSI_yr_ecor[Gfwa][HSI][year] = Ave3yrHSI_ecoregion_sum(HSI,fwadir,year,S,Gfwa,ascii_grid_lookup,615,1259,ecogrid)

        for prj in prjgrp.keys():
            print ' Reformatting output for %s - %s:' % (prj,S)
            for year in years:
                print ' -Year %s' % year
    
                for gr in prj_groups[prj].values():
                    if gr != 'G001':
                        Gfwa = gr

                fwoa_lwfcsv = os.path.normpath(r'%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_N_%02d_%02d_W_LWFzn.csv' % (fwoadir,year,S,Gfwoa,year,year))
                fwoa_vgtcsv = os.path.normpath(r'%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_N_%02d_%02d_W_VgTzn.csv' % (fwoadir,year,S,Gfwoa,year,year))
                fwoaLWF = readLWF(fwoa_lwfcsv)
                fwoaVgT = readVgTyp(fwoa_vgtcsv)
            
                fwa_lwfcsv = os.path.normpath(r'%s\\%s\\%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_N_%02d_%02d_W_LWFzn.csv' % (prjdir,S,Gfwa,year,S,Gfwa,year,year))
                fwa_vgtcsv = os.path.normpath(r'%s\\%s\\%s\\geomorph\\output_%02d\\Deliverables\\MPM2017_%s_%s_C000_U00_V00_SLA_N_%02d_%02d_W_VgTzn.csv' % (prjdir,S,Gfwa,year,S,Gfwa,year,year))
                fwaLWF = readLWF(fwa_lwfcsv)
                fwaVgT = readVgTyp(fwa_vgtcsv)
    
                for ecoregion in ecoregions:
                    group_to_use = prj_groups[prj][ecoregion]
                    if group_to_use == 'G001':
                        lwf_to_use = fwoaLWF
                        vgt_to_use = fwoaVgT
                    else:
                        lwf_to_use = fwaLWF
                        vgt_to_use = fwaVgT
                    # lwf_to_use is a list of dictionaries: [land,water,floatant]
                    # vgt_to_use is a list of dictionaries: [fresh_forest,fresh_marsh,int_marsh,brack_marsh,salt_marsh,water,upland]
                    for code in PTcodes:
                        if code == 'LND':
                            outval = lwf_to_use[0][ecoregion]+lwf_to_use[2][ecoregion]
                        elif code == 'BLH':
                            outval = vgt_to_use[0][ecoregion]
                        elif code == 'SWA':
                            outval = vgt_to_use[0][ecoregion]
                        elif code == 'FRM':
                            outval = vgt_to_use[1][ecoregion]
                        elif code == 'INM':
                            outval = vgt_to_use[2][ecoregion]
                        elif code == 'BMH':
                            outval = vgt_to_use[3][ecoregion]
                        elif code == 'SAM':
                            outval = vgt_to_use[4][ecoregion]
                        elif code in HSIcodes:
                            outval = meanHSI_G_HSI_yr_ecor[group_to_use][code][year][0][ecoregion]
                        writeout.write('%s,%s,%s,%s,%s,%s\n' % (prj,S,year,code,ecoregion,outval))


