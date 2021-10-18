import subprocess
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import rasterio as rio
from rasterio.plot import plotting_extent

s   = int(sys.argv[1])
g   = int(sys.argv[2])
yr1 = int(sys.argv[3])
yr0 = int(sys.argv[4])

print('\n\nComparing year %02d to year %02d for for S%02d G%03d:' % (yr1,yr0,s,g) )

#############################
##      Setup folders      ##
#############################
print('\nsetting up folders')
out_fol         = 'S%02d/G%03d/geomorph/output' % (s,g)
xyz_fol         = '%s/xyz' % out_fol 
tif_fol         = '%s/tif' % out_fol
png_fol         = '%s/png' % out_fol
ts_fol          = '%s/ts'  % out_fol


for fol in [xyz_fol,tif_fol,png_fol,ts_fol]:
    try:
        if os.path.isdir(fol) == False:
            os.mkdir(fol)
        else:
            print('%s already exists' % fol)
    except:
        print('could not build %s' % fol)



############################################
##      Calculate land change raster      ##
############################################
print('\ncalculating land change (binary file)')

ras1_bin_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_lndtyp30.xyz.b' % (out_fol,s,g,yr1,yr1)
if yr0 == 0:
    ras0_bin_pth    = 'S%02d/G%03d/geomorph/input/MP2023_S00_G500_C000_U00_V00_SLA_I_00_00_W_lndtyp30.xyz.b' % (s,g)
else:
    ras0_bin_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_lndtyp30.xyz.b' % (out_fol,s,g,yr0,yr0)



ras01_bin_pth   = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_lndchg.xyz.b' % (out_fol,s,g,yr0,yr1)
difftype        = 'dlw'
nras_str        = '170852857'
noData_str      = '-9999'

cmdstr1 = ['./morph_diff_v23.0.0', ras1_bin_pth, ras0_bin_pth, ras01_bin_pth, difftype, nras_str, noData_str]
subprocess.call(cmdstr1)


#############################################################
##      Convert land change raster from binary to ASCI     ##
#############################################################
print('\nconverting binary file to ASCI raster')
xyz_asc_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_lndchg.xyz' % (xyz_fol,s,g,yr0,yr1)
x_bin_pth       = '%s/raster_x_coord.b' % out_fol
y_bin_pth       = '%s/raster_y_coord.b' % out_fol
dtype           = 'int' #'flt'

cmdstr2 = ['./morph_rasters_bin2xyz_v23.0.0',xyz_asc_pth, x_bin_pth, y_bin_pth, ras01_bin_pth, dtype, nras_str]
subprocess.call(cmdstr2)


#############################################################
##      Convert land change raster from ASCI to TIF        ##
#############################################################
print('\nconverting ASCI raster to TIF')
tif_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_lndchg.tif' % (tif_fol,s,g,yr0,yr1)
footnote = 'MP2023 FWOA simulations'
cmdstr3 = ['gdal_translate', xyz_asc_pth, tif_pth]
subprocess.call(cmdstr3)


#############################################################
##      Convert land change raster from TIF to PNG         ##
#############################################################
print('\nmapping TIF to PNG image')
png_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_lndchg.png' % (png_fol,s,g,yr0,yr1)
png_title = 'S%02d G%03d - Land Change from year %02d to %02d'  % (s,g,yr0,yr1)
footnote = 'MP2023 FWOA simulations scenario selection - July 2021'

# color map and legend used for LandWater Difference rasters.
lwdiff_map = {}
lwdiff_map[-9999]=[-9999.5, 10.5, 'white','no data']
lwdiff_map[11] = [10.5,11.5,'silver',     'land']
lwdiff_map[12] = [11.5,12.5,'darkred',    'land->water (LOSS)']
lwdiff_map[13] = [12.5,13.5,'tan',        'land->bare']
lwdiff_map[21] = [13.5,21.5,'green',      'water->land (GAIN)']
lwdiff_map[22] = [21.5,22.5,'darkblue',   'water']
lwdiff_map[23] = [22.5,23.5,'aquamarine', 'water->bare (GAIN)']
lwdiff_map[31] = [23.5,31.5,'gainsboro',  'bare->land']
lwdiff_map[32] = [31.5,32.5,'pink',       'bare->water (LOSS)']
lwdiff_map[33] = [32.5,33.5,'saddlebrown','bare']
lwdiff_map[44] = [33.5,44.5,'grey',      'upland']
lwdiff_map[51] = [50.5,51.5,'lightgreen', 'flotant->water->land']
lwdiff_map[52] = [51.5,52.5,'lightcoral', 'flotant to water (LOSS)']
lwdiff_map[53] = [52.5,53.5,'beige', 'flotant->water->bare']
lwdiff_map[55] = [54.5,55.5,'lightgray',  'flotant']

cmap_list_lwd = []
cmap_norm_list_lwd = [lwdiff_map[-9999][0]]
leg_lab_lwd = {}
for lwdt in lwdiff_map.keys():
    cmap_norm_list_lwd.append(lwdiff_map[lwdt][1])
    cmap_list_lwd.append(lwdiff_map[lwdt][2])
    leg_lab_lwd[lwdiff_map[lwdt][2]] = lwdiff_map[lwdt][3]
cmap          = ListedColormap(cmap_list_lwd)
norm          = colors.BoundaryNorm(cmap_norm_list_lwd, len(cmap_norm_list_lwd) )
legend_labels = leg_lab_lwd

# open and read TIF raster with rasterio
with rio.open(tif_pth) as open_tif:
    tif = open_tif.read(1)

# map 2D raster with matplotlib
fig,ax = plt.subplots(figsize=(11,5))               # figsize in inches
tif_map = ax.imshow(tif,cmap=cmap,norm=norm)

# build legend
patches = [Patch(color=color,label=label) for color,label in legend_labels.items()]
ax.legend(handles=patches,bbox_to_anchor=[0,0],loc='lower left',frameon=False,facecolor=None,fontsize='x-small',ncol=3)

# generic figure edits
ax.set_axis_off()
ax.set_title(png_title,fontsize='small')
plt.figtext(0.9,0.1,footnote,fontsize='xx-small',horizontalalignment='right')
plt.tight_layout()

# save as image
plt.savefig(png_pth,dpi=1800)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
