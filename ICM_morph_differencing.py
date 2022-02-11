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
spinup = 2

# difftype = 'lndtypdiff'    # land type comparison to FWOA at same year - uses input rastype = 'lndtyp30'
#difftype = 'lndchg'        # land type comparison to initial conditions - uses input rastype = 'lndtyp30'
#difftype = 'salavdiff'     # annual mean salinity comparison to FWOA at same year - uses input rastype = 'salav30'
#difftype = 'salmxdiff'     # annual max salinity comparison to FWOA at same year - uses input rastype = 'salmx30'
#difftype = 'mwldiff'       # annual mean water level comparison to FWOA at same year - uses input rastype = 'mwl30'
#difftype = 'elevdiff'      # elevation comparison to FWOA at same year - uses input rastype = 'dem30'

difftype_titles                 = {}
difftype_titles['lndtypdiff']   = 'Land type'
difftype_titles['lndchg']       = 'Land type'
difftype_titles['salavdiff']    = 'Mean annual salinity (ppt)' 
difftype_titles['salmxdiff']    = 'Maximum 2-week mean salinity (ppt)'
difftype_titles['mwldiff']      = 'Mean annual water level (m)'
difftype_titles['elevdiff']     = 'Elevation (m)'


print('\n\nComparing year %02d to year %02d for for S%02d G%03d:' % (yr1,yr0,s,g1) )

#############################
##      Setup folders      ##
#############################
print('\nsetting up folders')
out_fol0         = 'S%02d/G%03d/geomorph/output' % (s,g0)
out_fol1         = 'S%02d/G%03d/geomorph/output' % (s,g1)
xyz_fol         = '%s/xyz' % out_fol1
tif_fol         = '%s/tif' % out_fol1
png_fol         = '%s/png' % out_fol1
ts_fol          = '%s/ts'  % out_fol1


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

ras1_bin_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol1,s,g1,yr1,yr1,rastype)
if yr0 == 0:
    ras0_bin_pth    = 'S%02d/G500/geomorph/input/MP2023_S00_G500_C000_U00_V00_SLA_I_00_00_W_%s.xyz.b' % (s,rastype)
else:
    ras0_bin_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol0,s,g0,yr0,yr0,rastype)

ras01_bin_pth   = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol1,s,g1,yr0,yr1,difftype)

if rastype == 'lndtyp30':
    morph_difftype = 'dlw'
    dtype          = 'int'
else:
    morph_difftype = 'dz'
    dtype          = 'flt'
    
nras_str        = '170852857'
noData_str      = '-9999'

cmdstr1 = ['./morph_diff_v23.0.0', ras1_bin_pth, ras0_bin_pth, ras01_bin_pth, morph_difftype, nras_str, noData_str]
subprocess.call(cmdstr1)


#############################################################
##      Convert land change raster from binary to ASCI     ##
#############################################################
print('\nconverting binary file to ASCI raster')
xyz_asc_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz' % (xyz_fol,s,g1,yr0,yr1,difftype)
x_bin_pth       = '%s/raster_x_coord.b' % out_fol1
y_bin_pth       = '%s/raster_y_coord.b' % out_fol1


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
png_title = 'S%02d G%03d year %02d compared to S%02d G%03d year %02d - %s'  % (s,g1,yr1-spinup,s,g0,yr0-spinup,difftype_title)
footnote = ''


# color map and legend used for LandWater Difference rasters.
if difftype in ['lndtypdiff','lndchg']:
    diff_map = {}
    diff_map[-9999] = ['white',        'no data']
    diff_map[11]    = ['silver',       'land']
    diff_map[12]    = ['darkred',      'land->water (LOSS)']
    diff_map[13]    = ['tan',          'land->bare']
    diff_map[21]    = ['green',        'water->land (GAIN)']
    diff_map[22]    = ['darkblue',     'water']
    diff_map[23]    = ['aquamarine',   'water->bare (GAIN)']
    diff_map[31]    = ['gainsboro',    'bare->land']
    diff_map[32]    = ['pink',         'bare->water (LOSS)']
    diff_map[33]    = ['saddlebrown',  'bare']
    diff_map[44]    = ['grey',         'upland']
    diff_map[51]    = ['lightgreen',   'flotant->water->land']
    diff_map[52]    = ['lightcoral',   'flotant to water (LOSS)']
    diff_map[53]    = ['beige',        'flotant->water->bare']
    diff_map[55]    = ['lightgray',    'flotant']
       
# color map and legend used for Salinity Difference rasters    
elif difftype in ['salavdiff','salmxdiff']:
    diff_map = {}
    diff_map[-9999] = ['white',        'no data']
    diff_map[-36]   = ['indigo',       'dSal <  -20 ppt']
    diff_map[-20]   = ['darkblue',     '-20 ppt ≤ dSal < -10 ppt']
    diff_map[-10]   = ['blue',         '-10 ppt ≤ dSal < -5 ppt']
    diff_map[-5]    = ['dodgerblue',   '-5 ppt ≤ dSal < -2 ppt']
    diff_map[-2]    = ['deepskyblue',  '-2 ppt ≤ dSal < -1 ppt']
    diff_map[-1]    = ['lightskyblue', '-1 ppt ≤ dSal < -0.5 ppt']
    diff_map[-0.5]  = ['paleturquoise','-0.5 ppt ≤ dSal < -0.1 ppt']
    diff_map[-0.1]  = ['lightgray',    '-0.1 ppt ≤ dSal < +0.1 ppt']
    diff_map[0.1]   = ['yellow',       '+0.1 ppt ≤ dSal < +0.5 ppt']
    diff_map[0.5]   = ['gold',         '+0.5 ppt ≤ dSal < +1 ppt']
    diff_map[1]     = ['orange',       '+1 ppt ≤ dSal < +2 ppt']
    diff_map[2]     = ['darkorange',   '+2 ppt ≤ dSal < +5 ppt']
    diff_map[5]     = ['red',          '+5 ppt ≤ dSal < +10 ppt']
    diff_map[10]    = ['firebrick',    '+10 ppt ≤ dSal < +20 ppt']
    diff_map[20]    = ['darkred',      '+20 ppt ≤ dSal']
    
# color map and legend used for Stage and Elevation Difference rasters
elif ['mwldiff','elevdiff']:
    diff_map = {}
    diff_map[-9999] = ['white',        'no data']
    diff_map[-100]  = ['darkred',      'dZ < -2.0 m']
    diff_map[-2.0]  = ['firebrick',    '-2.0 m ≤ dZ < -1.5 m']
    diff_map[-1.5]  = ['red',          '-1.5≤ dZ < -1.0 ']
    diff_map[-1.0]  = ['darkorange',   '-1.0 m ≤ dZ < -0.5 m']
    diff_map[-0.5]  = ['orange',       '-0.5 m ≤ dZ < -0.2 m']
    diff_map[-0.2]  = ['gold',         '-0.2 m ≤ dZ < -0.1 m']
    diff_map[-0.1]  = ['yellow',       '-0.1 m ≤ dZ < -0.05 m']
    diff_map[-0.05] = ['lightgray',    '-0.05 m ≤ dZ < +0.05 m']
    diff_map[0.05]  = ['paleturquoise','+0.05 m ≤ dZ < +0.1 m']
    diff_map[0.1]   = ['lightskyblue',  '+0.1 m ≤ dZ < +0.2 m']
    diff_map[0.2]   = ['deepskyblue',   '+0.2 m ≤ dZ < +0.5 m']
    diff_map[0.5]   = ['dodgerblue',    '+0.5 m ≤ dZ < +1.0 m']
    diff_map[1.0]   = ['blue',          '+1.0 m ≤ dZ < +1.5 m']
    diff_map[1.5]   = ['darkblue',      '+1.5 m ≤ dZ < 2.0 m']
    diff_map[2.0]   = ['indigo',        '+2.0 m ≤ dZ']
        
    
    
vals = []
bounds = []
cmap_list = []
label_list = []
patches = []

for dt in diff_map.keys():
    vals.append(dt)
    bounds.append(dt - 0.01)        # set bound to just to the left of mapping value bins set about in 'diff_map' dict
    cmap_list.append(diff_map[dt][0])
    label_list.append(diff_map[dt][1])
    patches.append( Patch( color=diff_map[dt][0],label=diff_map[dt][1] ) )

cmap = colors.ListedColormap(cmap_list)
norm = colors.BoundaryNorm(bounds,len(bounds))
    


# open and read TIF raster with rasterio
with rio.open(tif_pth) as open_tif:
    tif = open_tif.read(1)

# map 2D raster with matplotlib
fig,ax = plt.subplots(figsize=(11,5))               # figsize in inches
tif_map = ax.imshow(tif,cmap=cmap,norm=norm,interpolation='none')

# build legend
ax.legend(handles=patches,bbox_to_anchor=[0.5,0],loc='upper center',frameon=False,edgecolor='black',facecolor='white',fontsize='xx-small',ncol=6)
    
# generic figure edits
ax.set_axis_off()
ax.set_title(png_title,fontsize='small')
plt.figtext(0.9,0.1,footnote,fontsize='xx-small',horizontalalignment='right')
plt.tight_layout()

# save as image
plt.savefig(png_pth,dpi=1800)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
