import subprocess
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib import cm
import rasterio as rio
from rasterio.plot import plotting_extent

s   = int(sys.argv[1])
g1  = int(sys.argv[2])
g0  = int(sys.argv[3])
yr1 = int(sys.argv[4])
yr0 = int(sys.argv[5])
rastype = sys.argv[6]
difftype = sys.argv[7]

# difftype = 'lndtypdiff'    # land type comparison to FWOA at same year - uses input rastype = 'lndtyp30'
#difftype = 'lndchg'        # land type comparison to initial conditions - uses input rastype = 'lndtyp30'
#difftype = 'salavdiff'     # annual mean salinity comparison to FWOA at same year - uses input rastype = 'salav30'
#difftype = 'salmxdiff'     # annual max salinity comparison to FWOA at same year - uses input rastype = 'salmx30'
#difftype = 'mwldiff'       # annual mean water level comparison to FWOA at same year - uses input rastype = 'mwl30'
#difftype = 'elevdiff'      # elevation comparison to FWOA at same year - uses input rastype = 'dem30'






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

ras1_bin_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol,s,g1,yr1,yr1,rastype)
if yr0 == 0:
    ras0_bin_pth    = 'S%02d/G500/geomorph/input/MP2023_S00_G500_C000_U00_V00_SLA_I_00_00_W_%s.xyz.b' % (s,rastype)
else:
    ras0_bin_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol,s,g0,yr0,yr0,rastype)

'lndtypdiff'
'lndchg'

ras01_bin_pth   = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol,s,g1,yr0,yr1,difftype)

if rastype == 'lndtyp30':
    difftype = 'dlw'
else:
    difftype = 'dz'
    
nras_str        = '170852857'
noData_str      = '-9999'

cmdstr1 = ['./morph_diff_v23.0.0', ras1_bin_pth, ras0_bin_pth, ras01_bin_pth, difftype, nras_str, noData_str]
subprocess.call(cmdstr1)


#############################################################
##      Convert land change raster from binary to ASCI     ##
#############################################################
print('\nconverting binary file to ASCI raster')
xyz_asc_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz' % (xyz_fol,s,g1,yr0,yr1,difftype)
x_bin_pth       = '%s/raster_x_coord.b' % out_fol
y_bin_pth       = '%s/raster_y_coord.b' % out_fol
dtype           = 'int' #'flt'

cmdstr2 = ['./morph_rasters_bin2xyz_v23.0.0',xyz_asc_pth, x_bin_pth, y_bin_pth, ras01_bin_pth, dtype, nras_str]
subprocess.call(cmdstr2)


#############################################################
##      Convert land change raster from ASCI to TIF        ##
#############################################################
print('\nconverting ASCI raster to TIF')
tif_pth         = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.tif' % (tif_fol,s,g1,yr0,yr1,difftype)
footnote        = ''
cmdstr3 = ['gdal_translate', xyz_asc_pth, tif_pth]
subprocess.call(cmdstr3)


#############################################################
##      Convert land change raster from TIF to PNG         ##
#############################################################
print('\nmapping TIF to PNG image')

difftype_title = difftype_titles[difftype]
png_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.png' % (png_fol,s,g1,yr0,yr1,difftype)
png_title = 'S%02d G%03d year %02d compared to S%02d G%03d year %02d - %s'  % (s,g1,yr1,s,g0,yr0,difftype_title)
footnote = ''



if difftype in ['lndtypdiff','lndchg']:
    # color map and legend used for LandWater Difference rasters.
    diff_map = {}
    diff_map[-9999]=[-9999.5, 10.5, 'white','no data']
    diff_map[11] = [10.5,11.5,'silver',     'land']
    diff_map[12] = [11.5,12.5,'darkred',    'land->water (LOSS)']
    diff_map[13] = [12.5,13.5,'tan',        'land->bare']
    diff_map[21] = [13.5,21.5,'green',      'water->land (GAIN)']
    diff_map[22] = [21.5,22.5,'darkblue',   'water']
    diff_map[23] = [22.5,23.5,'aquamarine', 'water->bare (GAIN)']
    diff_map[31] = [23.5,31.5,'gainsboro',  'bare->land']
    diff_map[32] = [31.5,32.5,'pink',       'bare->water (LOSS)']
    diff_map[33] = [32.5,33.5,'saddlebrown','bare']
    diff_map[44] = [33.5,44.5,'grey',      'upland']
    diff_map[51] = [50.5,51.5,'lightgreen', 'flotant->water->land']
    diff_map[52] = [51.5,52.5,'lightcoral', 'flotant to water (LOSS)']
    diff_map[53] = [52.5,53.5,'beige', 'flotant->water->bare']
    diff_map[55] = [54.5,55.5,'lightgray',  'flotant']
    
    cmap_list = []
    cmap_norm_list = [diff_map[-9999][0]]       # sets lower left bound on cmap_normalizing to -9999.5, as set in diff_map above
    leg_lab = {}
    for dt in diff_map.keys():
        cmap_norm_list.append(diff_map[dt][1])
        cmap_list.append(diff_map[dt][2])
        leg_lab[diff_map[dt][2]] = diff_map[dt][3]

    cmap = ListedColormap(cmap_list)
    norm = colors.BoundaryNorm(cmap_norm_list, len(cmap_norm_list) )
    legend_labels = leg_lab

elif difftype in ['salavdiff','salmxdiff','mwldiff','elevdiff']:
    # color map and legend used for Salinity Difference rasters
    cmap = cm.seismic
    norm = colors.CenteredNorm() 

# open and read TIF raster with rasterio
with rio.open(tif_pth) as open_tif:
    tif = open_tif.read(1)

# map 2D raster with matplotlib
fig,ax = plt.subplots(figsize=(11,5))               # figsize in inches
tif_map = ax.imshow(tif,cmap=cmap,norm=norm)

# build legend
if difftype in ['lndtypdiff','lndchg']:
    patches = [Patch(color=color,label=label) for color,label in legend_labels.items()]
    ax.legend(handles=patches,bbox_to_anchor=[0,0],loc='lower left',frameon=False,facecolor=None,fontsize='x-small',ncol=3)
elif difftype in ['salavdiff','salmxdiff','mwldiff','elevdiff']:
    fig.colorbar(tif_map,ax=ax)
    
# generic figure edits
ax.set_axis_off()
ax.set_title(png_title,fontsize='small')
plt.figtext(0.9,0.1,footnote,fontsize='xx-small',horizontalalignment='right')
plt.tight_layout()

# save as image
plt.savefig(png_pth,dpi=1800)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions