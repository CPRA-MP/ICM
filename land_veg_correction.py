import numpy as np
import sys

veg_codes   = ['UPL', 'LND', 'WAT', 'FLT', 'FOR', 'FRM', 'INM', 'BRM', 'SAM', 'BRG']
Ss          = [7,8]
g_fwoa      = 500
y00         = 2018
y52         = 2070
gridA       = 480*480       # grid area in sq meters

p_c_mask = {}
p_g_list = {}
g_years = {}
p_g_c_mask_file = 'PDD_project_compartment_correctors.csv'       # header will be 'ProjectNumber,ModelGroup,ICM-Hydro_CompID,ICM_years_to_correct('all' or space delimited integers),Notes'

with open(p_g_c_mask_file,mode='r') as infile:
    nl = 0
    for line in infile:
        if nl > 0:
            p = int(line.split(',')[0])
            g = int(line.split(',')[1])
            c = int(line.split(',')[2])
            years_str = line.split(',')[3]
            n = line.split(',')[4]
            
            if p not in p_g_c_mask.keys():
                p_c_mask[p] = []
                p_g_list[p] = g
            p_c_mask[p].append(c)

            if g not in g_years.keys():
                g_years[g] = []
            
            if years_str == 'all':
                for cy in range(y00+1,y52+1):
                    g_years[g].append(cy)
            else:
                for y in years_str.split():
                    cy = y00 + int(y)
                    g_years[g].append(cy)
                    
groups2correct  = p_g_list.values()
comps2correct   = p_c_mask.values()

csgyva = {}
for c in comps2correct:
    csgyva[c] = {}

for s in Ss:
    csgyva[c][s] = {}
    csgyva[c][s][g_fwoa] = {}
    
    for cy in range(y00+1,y52+1):
        y = cy - y00
        csgyva[c][s][g_fwoa][y] = {}
        for v in veg_codes:
            csgyva[c][s][g_fwoa][y][v] = 0.0
        
        
    for g_fwa in groups2correct:
        csgyva[c][s][g_fwa] = {}
        for cy in range(y00+1,y52+1):
            y = cy - y00
            csgyva[c][s][g_fwa][y] = {}
            for v in veg_codes:
                csgyva[c][s][g_fwa][y][v] = 0.0
        
g_all = [g_fwoa] + groups2correct

for s in Ss:
    for g in g_all:                 # only process model groups that are included in the input file (plus FWOA)
        for cy in g_years[g]:       # only process the specific years that are assigned to each group in the input file
            y = cy - y00
            print( 'reading in gridded data for S%02d G%03d - %04d' % (s,g,cy) )
            
            grid_eoy_file = 'S%02d/G%03d/geomorph/output/grid_summary_eoy_%04d.csv' % (s,g,cy)              #gridID,compID,stage_m_NAVD88,stg_wlv_smr_m,mean_sal_ppt,mean_smr_sal_ppt,2wk_max_sal_ppt,mean_temp_degC,mean_TSS_mgL,pct_water,pct_flotant,pct_land_veg,pct_land_bare,pct_land_upland_dry,pct_land_upland_wet,pct_vglnd_BLHF,pct_vglnd_SWF,pct_vglnd_FM,pct_vglnd_IM,pct_vglnd_BM,pct_vglnd_SM,FIBS_score
            
            grid_eoy = np.genfromtxt(grid_eoy_file,delimiter=',',dtype=str,skip_header=1)        
            
            for line in grid_eoy:
                c   =    int(line[1]) # compID

                if c in comps2correct:
                    csgyva[c][s][g][y]['UPL'] += grA*(float(line[13]) + float(line[14]))    # pct_land_upland_dry + pct_land_upland_wet
                    csgyva[c][s][g][y]['LND'] += grA*float(line[11])                        # pct_land_veg
                    csgyva[c][s][g][y]['WAT'] += grA*float(line[ 9])                        # pct_water
                    csgyva[c][s][g][y]['FLT'] += grA*float(line[10])                        # pct_flotant
                    csgyva[c][s][g][y]['FOR'] += grA*(float(line[15]) + float(line[16]))    # pct_vglnd_BLHF + pct_vglnd_SWF
                    csgyva[c][s][g][y]['INM'] += grA*float(line[18])                        # pct_vglnd_IM
                    csgyva[c][s][g][y]['BRM'] += grA*float(line[19])                        # pct_vglnd_BM
                    csgyva[c][s][g][y]['FRM'] += grA*float(line[17])                        # pct_vglnd_FM
                    csgyva[c][s][g][y]['SAM'] += grA*float(line[20])                        # pct_vglnd_SM
                    csgyva[c][s][g][y]['BRG'] += grA*float(line[12])                        # pct_land_bare
    


# ModelGroup,Scenario,Year_ICM,VegetationCode,Ecoregion,Area_m2,Date,Year_FWOA,Note

# VegetationCode
# 

S08 G605
S08 G607
S08 G613
S08 G631
S08 G632
S08 G639
S08 G640 48.8
    

S07 G634
S07 G628 
S08 G628
S07 G642
S08 G642 - need permissions
S07 G622
S08 G622 - need permissions


S08,G608,13514,37.0,20220503 2144
# 
