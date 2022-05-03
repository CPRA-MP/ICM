import numpy as np
import sys

p_c_mask = {}
p_g_list = {}
p_g_c_mask_file = 'PDD_project_compartment_correctors.csv'       # header will be 'ProjectNumber,ModelGroup,ICM-Hydro_CompID,Notes'

with open(p_g_c_mask_file,mode='r') as infile:
    nl = 0
    for line in infile:
        if nl > 0:
            p = int(line.split(',')[0])
            g = int(line.split(',')[1])
            c = int(line.split(',')[2])
            n = line.split(',')[3]
            
            if p not in p_g_c_mask.keys():
                p_c_mask[p] = []
                p_g_list[p] = g
            p_c_mask[p].append(c)

groups2correct  = p_g_list.values()

    
veg_codes       = ['UPL', 'LND', 'WAT', 'FLT', 'FOR', 'FRM', 'INM', 'BRM', 'SAM', 'BRG']
Ss              = [7,8]
g_fwoa          = 500
y0              = 2018

sgyva = {}

for s in Ss:
    sgyva[s] = {}
    sgyva[s][g_fwoa] = {}
    
    for cy in range(2019,2070+1):
        y = cy - y0
        sgyva[s][g_fwoa][y] = {}
        for v in veg_codes:
            sgyva[s][g_fwoa][y][v] = 0.0
        
        
    for g_fwa in groups2correct:
        sgyva[s][g_fwa] = {}
        for cy in range(2019,2070+1):
            y = cy - y0
            sgyva[s][g_fwa][y] = {}
            for v in veg_codes:
                sgyva[s][g_fwa][y][v] = 0.0
        
    
grid_eoy_file = 'S%02d/G%03d/geomorph/output/grid_summary_eoy_%04d.csv' % (s,g_fwoa,cy)
grid_eoy = np.genfromtxt(grid_eoy_file,delimiter=',',dtype=str,skip_header=1)        
for line in grid_eoy:
    
# ModelGroup,Scenario,Year_ICM,VegetationCode,Ecoregion,Area_m2,Date,Year_FWOA,Note

# VegetationCode
# 