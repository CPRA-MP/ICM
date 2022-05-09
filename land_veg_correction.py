import numpy as np
import sys
# cy    : calendar year
# y     : elapsed year of ICM simulation (ICM year 01:52)

print('setting things up.')

veg_codes   = ['UPL', 'LND', 'WAT', 'FLT', 'FOR', 'FRM', 'INM', 'BRM', 'SAM', 'BRG']
Ss          = [7,8]
g_fwoa      = 500
cy00         = 2018
cy52         = 2070
grArea       = 480*480       # grid area in sq meters

g_c_mask = {}       # dictionary of model groups to update - with values being  a list ICM-Hydro compIDs to be corrected 
g_years  = {}       # dictionary of years (in  ICM year format, 01:52) that need to corrected for each respective model group
comp_eco = {}

# assign all years to the FWOA run
g_years[g_fwoa] = []
for cy in range(cy00+1,cy52+1):
    y = cy - cy00
    g_years[g_fwoa].append(y)

# input files
g_c_y_mask_file = 'PDD_group_compartment_correctors.csv'      # header will be 'ModelGroup,ICM-Hydro_CompID,ICM_years_to_correct('all' or space delimited integers),Notes'
comp_eco_file = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/S07/G500/geomorph/input/compartment_ecoregion.csv'

# remapping dictionary to use the PDD lumped ecoregions for barrier island ecoregions
eco2bi ={ 'CHSbi':'EBbi','LBRbi':'EBbi', 'LBAnebi':'WBbi','LBAsebi':'WBbi','LBAswbi':'WBbi','ETBbi':'TEbi','WTEbi':'TEbi' }

# read in compartment-to-ecoregion mapping
with open(comp_eco_file,mode='r') as infile:                    # ICM-Hydro_comp,er_n,upland_area_m2_outside_of_Morph_domain,water_area_m2_outside_of_Morph_domain,er,name
    nl = 0
    for line in infile:
        if nl > 0:
            c = int(line.split(',')[0])
            e = line.split(',')[4]
            if e in eco2bi:                                     # check if ecoregion is a barrier island - if so, remap to the PDD version of BI ecoregions
                comp_eco[c] = eco2bi[e] 
            else:
                comp_eco[c] = e
        nl += 1

# read in project list of groups and years that need to be corrected in PDD
print('reading in list of groups/compartments/years that are being corrected in the PDD.')
with open(g_c_y_mask_file,mode='r') as infile:
    nl = 0
    for line in infile:
        if nl > 0:
            p = int(line.split(',')[0])
            g = int(line.split(',')[0])
            c = int(line.split(',')[1])
            years_str = line.split(',')[2]
            n = line.split(',')[3]
            
            if g not in g_c_mask.keys():
                g_c_mask[g] = []
            g_c_mask[g].append(c)

            if g not in g_years.keys():
                g_years[g] = []
            
            if years_str == 'all':
                for cy in range(cy00+1,cy52+1):
                    y = cy - cy00
                    g_years[g].append(y)
            else:
                for y in years_str.split():
                    g_years[g].append(y)
        nl += 1

# initialize dictionaries that are going to store the FWOA and FWA ICM-Hydro compartment-level yearly data
groups2correct  = g_c_mask.keys()
comps2correct   = g_c_mask.values()

csgyva = {}
for c in comps2correct:
    csgyva[c] = {}

    for s in Ss:
        csgyva[c][s] = {}
        csgyva[c][s][g_fwoa] = {}
        
        # initialize dictionary that will hold FWOA output data
        for cy in range(cy00+1,cy52+1):
            y = cy - cy00
            csgyva[c][s][g_fwoa][y] = {}
            for v in veg_codes:
                csgyva[c][s][g_fwoa][y][v] = 0.0
        
        # initialize dictionaries that will hold FWA output data
        for g_fwa in groups2correct:
            csgyva[c][s][g_fwa] = {}
            for cy in range(cy00+1,cy52+1):
                y = cy - cy00
                csgyva[c][s][g_fwa][y] = {}
                for v in veg_codes:
                    csgyva[c][s][g_fwa][y][v] = 0.0


# read in ICM-LAVegMod grid-level output and sum over each  ICM-Hydro compartment - store in previously initialized dictionaries        
print('read in gridded data and accumulate up to the ICM-Hydro comparment level:')
g_all = [g_fwoa] + groups2correct

for s in Ss:
    for g in g_all:                 # only process model groups that are included in the input file (plus FWOA)
        for y in g_years[g]:        # only process the specific years that are assigned to each group in the input file
            cy = y + cy00
            print( '    - reading in gridded data for S%02d G%03d - %04d' % (s,g,cy) )
            
            grid_eoy_file = 'S%02d/G%03d/geomorph/output/grid_summary_eoy_%04d.csv' % (s,g,cy) # gridID,compID,stage_m_NAVD88,stg_wlv_smr_m,mean_sal_ppt,mean_smr_sal_ppt,2wk_max_sal_ppt,mean_temp_degC,mean_TSS_mgL,pct_water,pct_flotant,pct_land_veg,pct_land_bare,pct_land_upland_dry,pct_land_upland_wet,pct_vglnd_BLHF,pct_vglnd_SWF,pct_vglnd_FM,pct_vglnd_IM,pct_vglnd_BM,pct_vglnd_SM,FIBS_score
            
            grid_eoy = np.genfromtxt(grid_eoy_file,delimiter=',',dtype=str,skip_header=1)        
            
            for line in grid_eoy:
                c   =    int(line[1]) # compID

                if c in comps2correct:
                    csgyva[c][s][g][y]['UPL'] += grArea*(float(line[13]) + float(line[14]))    # pct_land_upland_dry + pct_land_upland_wet
                    csgyva[c][s][g][y]['LND'] += grArea*float(line[11])                        # pct_land_veg
                    csgyva[c][s][g][y]['WAT'] += grArea*float(line[ 9])                        # pct_water
                    csgyva[c][s][g][y]['FLT'] += grArea*float(line[10])                        # pct_flotant
                    csgyva[c][s][g][y]['FOR'] += grArea*(float(line[15]) + float(line[16]))    # pct_vglnd_BLHF + pct_vglnd_SWF
                    csgyva[c][s][g][y]['INM'] += grArea*float(line[18])                        # pct_vglnd_IM
                    csgyva[c][s][g][y]['BRM'] += grArea*float(line[19])                        # pct_vglnd_BM
                    csgyva[c][s][g][y]['FRM'] += grArea*float(line[17])                        # pct_vglnd_FM
                    csgyva[c][s][g][y]['SAM'] += grArea*float(line[20])                        # pct_vglnd_SM
                    csgyva[c][s][g][y]['BRG'] += grArea*float(line[12])                        # pct_land_bare
    
# roll up compartment-level values to the ecoregion for applying correctors to PDD data
# structure of dictionary will match the dictionary used by upload_to_pdd.py: d[scen][group][ICMyear][vegcode][ecoregion]
print('accumulate compartment-level summed data up to the ecoregion:')
correctors = {}

for s in Ss:
    correctors[s] = {}
    for g_fwa in g_c_mask.keys():
        correctors[s][g_fwa] = {}
        
        for y in g_years[g_fwa]:       # only process the specific years that are assigned to each group in the input file
            cy = y + cy00
            
            print( '    - rolling up compartment sums to ecoregion for S%02d G%03d - %04d' % (s,g_fwa,cy) )
            correctors[s][g_fwa][y] = {}
        
            for v in veg_codes:
                correctors[s][g_fwa][y][v] = {}

                for comp in p_c_mask[p]:
                    e = comp_eco[comp]
                    
                    if e not in correctors[s][g_fwa][y][v].keys():
                        correctors[s][g_fwa][y][v][e] = {'FWOA':0.0,'FWA':0.0}
                    
                    correctors[s][g_fwa][y][v][e]['FWOA'] += csgyva[c][s][g_fwoa][y][v]
                    correctors[s][g_fwa][y][v][e]['FWA' ] += csgyva[c][s][g_fwa][y][v]
                    


# ModelGroup,Scenario,Year_ICM,VegetationCode,Ecoregion,Area_m2,Date,Year_FWOA,Note
