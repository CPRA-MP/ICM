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

for fol in [asc_fol,png_fol]:
    try:
        if os.path.isdir(fol) == False:
            os.mkdir(fol)
        else:
            print('%s already exists' % fol)
    except:
        print('could not build %s' % fol)



if g1 == g0:
    png_path = '%s/MP2023_S%02d_G%03d_C000_U%02d_V00_SLA_O_%02d_%02d_X_%s.png' (png_fol,s,g1,s,g1,u,yr1,yr0,spec)
else:
    png_path = '%s/MP2023_S%02d_G%03d_C000_U%02d_V00_SLA_O_%02d_%02d_X_%s_diff.png' (png_fol,s,g1,u,yr1,yr0,spec)

asc1_path = '%s/S%02d/G%03d/hsi/asc/MP2023_S%02d_G%03d_C000_U%02d_V00_SLA_O_%02d_%02d_X_%s.asc' (asc_fol,s,g1,u,yr1,yr1,spec)
hsi1 = np.genfromtxt(asc1_path,delimiter=' ',dtype=float,skip_header=6)
hsi1 = np.ma.masked_where(hsi1<0,hsi0,copy=True)   # mask out NoData -9999 values

if g1 == g0:
    if yr1 == yr0:
        hsi = hsi1
        cbmin = 0
        png_title = 'S%02d G%03d year %02d - HSI: %s'  % (s,g1,yr1-spinup,spec)
    else:
        asc0_path = '%s/S%02d/G%03d/hsi/asc/MP2023_S%02d_G%03d_C000_U%02d_V00_SLA_O_%02d_%02d_X_%s.asc' (asc_fol,s,g0,u,yr0,yr0,spec)
        hsi0 = np.genfromtxt(asc0_path,delimiter=' ',dtype=float,skip_header=6)
        hsi0 = np.ma.masked_where(hsi0<0,hsi0,copy=True)   # mask out NoData -9999 values
        hsi = hsi1 - hsi0
        cbmin = -1
        png_title = 'S%02d G%03d year %02d compared to year %02d - HSI: %s'  % (s,g1,yr1-spinup,yr0-spinup,spec)
        
else:
    asc0_path = '%s/S%02d/G%03d/hsi/asc/MP2023_S%02d_G%03d_C000_U%02d_V00_SLA_O_%02d_%02d_X_%s.asc' (asc_fol,s,g0,u,yr0,yr0,spec)
    hsi0 = np.genfromtxt(asc0_path,delimiter=' ',dtype=float,skip_header=6)
    hsi0 = np.ma.masked_where(hsi0<0,hsi0,copy=True)   # mask out NoData -9999 values
    hsi = hsi1 - hsi0
    png_title = 'S%02d G%03d year %02d compared to S%02d G%03d year %02d - HSI: %s'  % (s,g1,yr1-spinup,s,g0,yr0-spinup,spec)
    cbmin = -1

# plot HSI grid (set min/max on color map to 0 and 1, respectively)
fig,ax = plt.subplots(figsize=(11,5))
asc_map = ax.imshow(hsi,cmap='coolwarm',vmin=cbmin,vmax=1,interpolation='none')
plt.colorbar(asc_map)

# generic figure edits
ax.set_axis_off()
ax.set_title(png_title,fontsize='small')
plt.figtext(0.99,0.01,footnote,horizontalalignment='right',fontsize='xx-small')

# save as image
plt.savefig(png_pth,dpi=1800)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
            
    
