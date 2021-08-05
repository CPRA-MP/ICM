#Generates a csv properly formatted for use in 'Barplots_allspecies_selectcells.py' 
import numpy as np
import os

s = 7
g = 503
S = 'S%02d' % s
G = 'G%03d' % g
years = range(1,31)
asc_grid_rows = 371
ngrid = 173898

#specify all directories needed: 
path_cellID = r'./%s/%s/geomorph/output_qaqc/CellIDs_to_plot.csv' %(S,G)
#read the cell IDs of where we want output 
cell_ID =  np.genfromtxt(path_cellID,skip_header=1, delimiter=',', dtype='int') ###INPUT csv containing the cell IDs for the cells of interest 

veg_dir = r'./%s/%s/veg' % (S,G)
outdir = veg_dir
os.chdir(veg_dir)

out_name = ('MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_V_barplot_input.csv' % (s,g) )

with open(out_name,mode='w') as outcsv:
    outcsv.write(',pro_no,S,year,coverage_code,cell_ID,value\n')
    m = 0
    for Y in years: 
        print('On year '+ str(Y))
        LVMout_f = 'MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_%02d_%02d_V_vegty.asc+' % (s,g,Y,Y)
        sp_names = np.genfromtxt( LVMout_f, skip_header=asc_grid_rows, skip_footer=ngrid, delimiter=',', dtype='str') 
        sp_names = sp_names[1:-7]       # the first column is CellID and the last 7 columns are FFIBS and habitat summations - remove these from the species name list
        sp_names = [sn.strip() for sn in sp_names]

        LVMout   = np.genfromtxt( LVMout_f, skip_header=asc_grid_rows+1, delimiter=',', dtype='float' )

        # convert numpy array of LVMout into a dictionary with the grid cell ID (first column in each row) as the keys - this is so the LVMout_f asc+ file can be printed out of sequential order and the correct data is still pulled
        LVMout_d = {}
        for row in LVMout:
            cID = int(row[0])   # grid cell ID must be integer since it is read in to cell_ID above as int
            LVMout_d[cID] = row[1:]
        
        # write to file
        for cell in cell_ID:
            coverages = LVMout_d[cell]
            for i in range(0,len(sp_names)):
                outcsv.write('%d,%s,%s,%d,%s,%d,%f\n' % (m,G,S,Y,sp_names[i],cell,coverages[i]) )
        
                m += 1

