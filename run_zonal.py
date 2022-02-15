import subprocess

for S in ['S08']:
    for G in ['G606','G621','G625','G641','G649','G650','G653']:
        exe = '../../code/ICM_MorphZonal/build/morph_zonal_v23.0.0' 
        xyz = 'FWA_project_data/MC_elev_rasters/MP2023_S00_G000_C000_U00_V00_SLA_O_00_00_overlapping_MCelements.xyz'
        csv = 'FWA_project_data/MC_elev_rasters/mp2023_overlapping_MC_elements.csv'
        noz = '22'
        nras = '171284090'
        nd = '-9999'
        sy = '01'
        ey = '52'

        cmdstr = [exe, xyz, csv, noz, nras, nd, S, G, sy, ey]

        subprocess.call(cmdstr)
