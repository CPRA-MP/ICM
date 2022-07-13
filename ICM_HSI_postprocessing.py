def dict2asc_flt(mapping_dict,outfile,asc_grid,asc_header,write_mode):
    # this function maps a dictionary of floating point data into XY space and saves as a raster file of ASCII grid format
    # this function does not return anything but it will save 'outfile' to disk

    # ASCII grid format description: http://resources.esri.com/help/9.3/arcgisengine/java/GP_ToolRef/spatial_analyst_tools/esri_ascii_raster_format.htm

    # 'mapping_dict' is a dictionary with grid cell ID as the key and some value for each key
    # 'outfile' is the filename (full path) of the output .asc raster text file to be saved
    # 'asc_grid' is a numpy array that is the grid structure of an ASCII text raster
    # 'asc_header' is a string that includes the 6 lines of text required by the ASCII grid format

    msg = '\ndid not save %s' % (outfile)
    with open(outfile, mode=write_mode) as outf:
        outf.write(asc_header)
        for row in asc_grid:
            nc = 0
            for col in row:
                gid_map = row[nc]
                if gid_map > 0:                     # if the ASC grid has a no data cell (-9999) there will be no dictionary key, the else criterion is met and it keeps the no data value (-9999)
                    gid_val = float(mapping_dict[gid_map] )
                else:
                    gid_val = float(gid_map)
                if nc == 0:
                    rowout = '%0.4f'  % gid_val
                else:
                    rowout = '%s %0.4f' % (rowout,gid_val)
                nc += 1
            outf.write('%s\n' % rowout)
            msg = ' - successfully saved %s' % (outfile)
    return msg


import matplotlib.pyplot as plt
import os
import numpy as np
import sys

s   = int(sys.argv[1])
g1  = int(sys.argv[2])
g0  = int(sys.argv[3])
yr1 = int(sys.argv[4])
yr0 = int(sys.argv[5])
u   = int(sys.argv[6])
spec =    sys.argv[7]
spinup = 2

print('\nsetting up folders')
out_fol0 = 'S%02d/G%03d/hsi' % (s,g0)
out_fol1 = 'S%02d/G%03d/hsi' % (s,g1)
asc_fol  = '%s/asc' % out_fol1
png_fol  = '%s/png' % out_fol1
veg_fol  = 'S%02d/G%03d/veg' % (s,g1)

for fol in [asc_fol,png_fol]:
    try:
        if os.path.isdir(fol) == False:
            os.mkdir(fol)
        else:
            print('%s already exists' % fol)
    except:
        print('could not build %s' % fol)

if g1 == g0:
    png_path = '%s/MP2023_S%02d_G%03d_C000_U%02d_V00_SLA_O_%02d_%02d_X_%s.png' % (png_fol,s,g1,u,yr1,yr0,spec)
else:
    png_path = '%s/MP2023_S%02d_G%03d_C000_U%02d_V00_SLA_O_%02d_%02d_X_%s_diff.png' % (png_fol,s,g1,u,yr1,yr0,spec)

asc1_path = '%s/MP2023_S%02d_G%03d_C000_U%02d_V00_SLA_O_%02d_%02d_X_%s.asc' % (asc_fol,s,g1,u,yr1,yr1,spec)

if os.path.isfile(asc1_path) == False:
    print('need to build ASCI grid file')
    hsi_dict = {}
    csv1_path = '%s/MP2023_S%02d_G%03d_C000_U%02d_V00_SLA_O_%02d_%02d_X_%s.csv' % (out_fol1,s,g1,u,yr1,yr1,spec)
    
    # read in asci grid structure
    asc_grid_file = os.path.normpath(r'%s/veg_grid.asc' % veg_fol)
    asc_grid_ids = np.genfromtxt(asc_grid_file,skip_header=6,delimiter=' ',dtype='int')
    asc_grid_head = 'ncols 1052\nnrows 365\nxllcorner 404710\nyllcorner 3199480\ncellsize 480\nNODATA_value -9999\n'
    
    with open(csv1_path,mode='r') as grid_data:
        nline = 0
        for line in grid_data:
            if nline > 0:
                gr = int(float(line.split(',')[0]))
                hsi_val = line.split(',')[0]          # in HSI csv files, 1st column is grid cell ID; 2nd column is HSI value
                hsi_dict[gr] = hsi_val
            nline += 1
    
    print(dict2asc_flt(hsi_dict,asc1_path,asc_grid_ids,asc_grid_head,write_mode='w') )



hsi1 = np.genfromtxt(asc1_path,delimiter=' ',dtype=float,skip_header=6)
hsi1 = np.ma.masked_where(hsi1<0,hsi1,copy=True)   # mask out NoData -9999 values

if g1 == g0:
    if yr1 == yr0:
        hsi = hsi1
        cbmin = 0
        png_title = 'S%02d G%03d year %02d - HSI: %s'  % (s,g1,yr1-spinup,spec)
    else:
        asc0_path = '%s/MP2023_S%02d_G%03d_C000_U%02d_V00_SLA_O_%02d_%02d_X_%s.asc' % (asc_fol,s,g0,u,yr0,yr0,spec)
        hsi0 = np.genfromtxt(asc0_path,delimiter=' ',dtype=float,skip_header=6)
        hsi0 = np.ma.masked_where(hsi0<0,hsi0,copy=True)   # mask out NoData -9999 values
        hsi = hsi1 - hsi0
        cbmin = -1
        png_title = 'S%02d G%03d year %02d compared to year %02d - HSI: %s'  % (s,g1,yr1-spinup,yr0-spinup,spec)
        
else:
    asc0_path = '%s/MP2023_S%02d_G%03d_C000_U%02d_V00_SLA_O_%02d_%02d_X_%s.asc' % (asc_fol,s,g0,u,yr0,yr0,spec)
    hsi0 = np.genfromtxt(asc0_path,delimiter=' ',dtype=float,skip_header=6)
    hsi0 = np.ma.masked_where(hsi0<0,hsi0,copy=True)   # mask out NoData -9999 values
    hsi = hsi1 - hsi0
    png_title = 'S%02d G%03d year %02d compared to S%02d G%03d year %02d - HSI: %s'  % (s,g1,yr1-spinup,s,g0,yr0-spinup,spec)
    cbmin = -1

print('plotting %s' % png_title)
# plot HSI grid (set min/max on color map to 0 and 1, respectively)
fig,ax = plt.subplots(figsize=(11,5))
asc_map = ax.imshow(hsi,cmap='coolwarm',vmin=cbmin,vmax=1,interpolation='none')
plt.colorbar(asc_map)

# generic figure edits
ax.set_axis_off()
ax.set_title(png_title,fontsize='small')
footnote = ''
plt.figtext(0.99,0.01,footnote,horizontalalignment='right',fontsize='xx-small')

# save as image
plt.savefig(png_pth,dpi=1800)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
            
    
