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
g2  = int(sys.argv[2])
g1  = int(sys.argv[3])
g0  = int(sys.argv[4])
yr1 = int(sys.argv[5])
yr0 = int(sys.argv[6])
rastype = sys.argv[7]
difftype = sys.argv[8]

overwrite = 0       # overwrite=0 will not overwrite files if they exist, overwrite=1 will overwrite pre-existing files
spinup = 2

difftype_titles                 = {}
difftype_titles['lndtypdiff']   = 'Land type'
difftype_titles['lndchg']       = 'Land type'
difftype_titles['salavdiff']    = 'Mean annual salinity (ppt)' 
difftype_titles['salmxdiff']    = 'Maximum 2-week mean salinity (ppt)'
difftype_titles['inundiff']     = 'Mean annual inundation depth (m)'
difftype_titles['elevdiff']     = 'Elevation (m)'


difftype_title = difftype_titles[difftype]
png_title = 'S%02d G%03d year %02d compared to S%02d G%03d year %02d - %s'  % (s,g1,yr1-spinup,s,g0,yr0-spinup,difftype_title)
footnote = ''

if rastype == 'lndtyp30':
    morph_difftype = 'dlw'
    dtype          = 'int'
else:
    morph_difftype = 'dz'
    dtype          = 'flt'
    
nras_str        = '170852857'
noData_str      = '-9999'


#############################
##      Setup folders      ##
#############################
print('\n\nComparing year %02d to year %02d for for S%02d G%03d:' % (yr1,yr0,s,g1) )
if overwrite == 1:
    print(' - File overwrite flag setting turned ON (1) - output files will be overwritten if they already exist.')
else:
    print(' - File overwrite flag setting turned OFF (0) - output files will NOT be overwritten if they already exist.')      


print('\nsetting up folders')
out_fol0         = 'S%02d/G%03d/geomorph/output' % (s,g0)
out_fol1         = 'S%02d/G%03d/geomorph/output' % (s,g1)
out_fol2         = 'S%02d/G%03d/geomorph/output' % (s,g2)
xyz_fol         = '%s/xyz' % out_fol2
tif_fol         = '%s/tif' % out_fol2
png_fol         = '%s/png' % out_fol2
ts_fol          = '%s/ts'  % out_fol2


for fol in [xyz_fol,tif_fol,png_fol,ts_fol]:
    try:
        if os.path.isdir(fol) == False:
            os.mkdir(fol)
        else:
            print('%s already exists' % fol)
    except:
        print('could not build %s' % fol)

        
if yr0 == 0:
    ras0_bin_pth    = 'S%02d/G500/geomorph/input/MP2023_S00_G500_C000_U00_V00_SLA_I_00_00_W_%s.xyz.b' % (s,rastype)
else:
    ras0_bin_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol0,s,g0,yr0,yr0,rastype)

ras2_bin_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol1,s,g2,yr1,yr1,rastype)    
ras1_bin_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol1,s,g1,yr1,yr1,rastype)
ras012_bin_pth  = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol1,s,g2,yr0,yr1,difftype)
x_bin_pth       = '%s/raster_x_coord.b' % out_fol1
y_bin_pth       = '%s/raster_y_coord.b' % out_fol1
xyz_asc_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz' % (xyz_fol,s,g1,yr0,yr1,difftype)
tif_pth         = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_%02d_%02d_W_%s.tif' % (tif_fol,s,g1,yr0,yr1,difftype)
png_pth         = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_%02d_%02d_W_%s.png' % (png_fol,s,g1,yr0,yr1,difftype)

    
################################################
##      Check for old files for overwrite     ##
################################################
if os.path.isfile(png_pth) == True:
    mapPNG = overwrite
    print('\nPNG image file already exists - will use overwrite flag setting(%d) - %s ' % (overwrite,difftype))
else:
    mapPNG = 1

# skip mapping file to PNG for time being
mapPNG = 0    
    

if os.path.isfile(tif_pth) == True:
    xyz2tif = overwrite
    print('\nTIF raster file already exists - will use overwrite flag setting (%d) - %s ' % (overwrite,difftype))
else:
    xyz2tif = 1
    
if os.path.isfile(xyz_asc_pth) == True:
    bin2xyz = overwrite
    print('\nASCI raster file already exists - will use overwrite flag setting (%d) - %s ' % (overwrite,difftype))
else:
    bin2xyz = 1
bin2xyz = xyz2tif*bin2xyz    # update XYZ flag - if TIF exists and is not being overwritten, then no need to build XYZ

if os.path.isfile(ras01_bin_pth) == True:
    build_bin = overwrite
    print('\nDifference binary raster file already exists - will use overwrite flag setting (%d) - %s ' % (overwrite,difftype))
else:
    build_bin = 1
       

############################################
##      Calculate land change raster      ##
############################################
if build_bin == True:
    print('\ncalculating land change (binary file)')
    cmdstr1 = ['./morph_diff3_v23.0.0', ras2_bin_pth,ras1_bin_pth, ras0_bin_pth, ras012_bin_pth, morph_difftype, nras_str, noData_str]
    subprocess.call(cmdstr1)

    
#############################################################
##      Convert land change raster from binary to ASCI     ##
#############################################################
if bin2xyz == True:
    print('\nconverting binary file to ASCI raster - %s' % difftype)
    cmdstr2 = ['./morph_rasters_bin2xyz_v23.0.0',xyz_asc_pth, x_bin_pth, y_bin_pth, ras012_bin_pth, dtype, nras_str]
    subprocess.call(cmdstr2)

    
#############################################################
##      Convert land change raster from ASCI to TIF        ##
#############################################################
if xyz2tif == True:
    print('\nconverting ASCI raster to TIF - %s' % difftype)
    cmdstr3 = ['gdal_translate', xyz_asc_pth, tif_pth]
    subprocess.call(cmdstr3)

if os.path.isfile(tif_pth) == True:
    print('\ndeleting XYZ ASCI raster file - %s' % difftype)
    cmdstr4 = ['rm',xyz_asc_pth]
    subprocess.call(cmdstr4)
  

#############################################################
##      Convert land change raster from TIF to PNG         ##
#############################################################
if mapPNG == True:    
    print('\n!!!! DO NOT HAVE COLOR MAP - WILL NOT WORK PROPERLY!!!!')
    print('\nmapping TIF to PNG image - %s' % difftype)
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
    
