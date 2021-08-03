import numpy as np
import os
import sys
import subprocess
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib import cm
import rasterio as rio
from rasterio.plot import plotting_extent

# read in simulation and plot settings from command arguments passed into this .py script
s = int(sys.argv[1])                 # s = '7'
g = int(sys.argv[2])                 # g = '503'
year = int(sys.argv[3])         # year = 2015
startyear = int(sys.argv[4])    # startyear = 2015
#ftype = sys.argv[5]
spinup_years = 2
elapsedyear = year - startyear + 1
footnote = ''

######################################
##      Setup file types to map     ##
######################################
ftype_list      = ['lndtyp30', 'lndchg30',  'salav30', 'salmx30']
ftype_labels    = ['Land type', 'Land change for year', 'Annual mean salinity (ppt)','Maximum 2-week mean salinity (ppt)']
ftype_dtypes    = ['int','int','flt','flt']

#############################
##      Setup folders      ##
#############################
print('\nsetting up folders')
out_fol         = 'S%02d/G%03d/geomorph/output' % (s,g)
xyz_fol         = '%s/xyz' % out_fol 
tif_fol         = '%s/tif' % out_fol
png_fol         = '%s/png' % out_fol

for fol in [xyz_fol,tif_fol,png_fol]:
    try:
        if os.path.isdir(fol) == False:
            os.mkdir(fol)
    except:
        print('could not build %s' % fol)




##################################################################
##      Setup colormaps to be used in mapping each datatype     ##
##################################################################
# color map and legend used for LandType rasters
# BoundaryNorm sets the edge of bins to which ListedColormap colors are applied
cmap_lt = ListedColormap(['white','darkgreen','darkblue','yellow','gray','springgreen'])
norm_lt = colors.BoundaryNorm([-9999.999, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5],7)                  # BoundaryNorm bins set to map integer values of 1, 2, 3, 4, & 5
leg_lab_lt = {'darkgreen': 'vegetated land','darkblue':'water','yellow':'unvegetated bare ground','gray':'developed land (not modeled)','springgreen':'floating marsh'}

# color map and legend used for LandChange rasters
cmap_lc = ListedColormap(['white','orange','skyblue','darkblue','whitesmoke','forestgreen'])
norm_lc = colors.BoundaryNorm([-9999.999, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5],7)           # BoundaryNorm bins set to map integer values of -3, -2, -1, 0, & 1
leg_lab_lc = {'darkblue': 'inundation loss','skyblue':'dead flotant','orange':'marsh edge erosion','whitesmoke':'no change','forestgreen':'land gain'}

# color map and legend used for Salinity rasters
bot = cm.get_cmap('summer',128)
top = cm.get_cmap('autumn_r',128)
newcolors = np.vstack( (bot(np.linspace(0, 1, 100)), top(np.linspace(0, 1, 250)) ))
cmap_sal = ListedColormap(newcolors)
norm_sal = ''
leg_lab_sal = ''

# compile various colormaps in arrays the same length as each filetype being mapped
cmap_list       = [cmap_lt,     cmap_lc,    cmap_sal,   cmap_sal]       # must be list the same size as ftype_list above
norm_list       = [norm_lt,     norm_lc,    norm_sal,   norm_sal]       # must be list the same size as ftype_list above
leg_lab_list    = [leg_lab_lt,  leg_lab_lc, leg_lab_sal, leg_lab_sal]   # must be list the same size as ftype_list above


##############################################
##      Start mapping each file type        ##
##############################################
for ftype in ftype_list:
    try:
    # select settings to be used for each filetype
        ntyp = ftype_list.index(ftype)
        cmap          = cmap_list[ntyp]
        norm          = norm_list[ntyp]
        legend_labels = leg_lab_list[ntyp]
        ftype         = ftype_list[ntyp]
        ftype_out = ftype[0:-2]
        dtype = ftype_dtypes[ntyp]
    except:
        print('\n')
        print('  No settings available for **%s** output type' % ftype)
        print('  trying to be mapped. Automated mapping available only for:' )
        for ft in ftype_list:
            print ('     - %s' % ft)
        print('\n')   


    try:
        xyz_bin_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol,s,g,elapsedyear,elapsedyear,ftype)
        xyz_asc_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz' % (xyz_fol,s,g,elapsedyear,elapsedyear,ftype)
        tif_pth         = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_%02d_%02d_W_%s.tif' % (tif_fol,s,g,elapsedyear,elapsedyear,ftype_out)
        png_pth         = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_%02d_%02d_W_%s.png' % (png_fol,s,g,elapsedyear,elapsedyear,ftype_out)
        x_bin_pth       = '%s/raster_x_coord.b' % out_fol
        y_bin_pth       = '%s/raster_y_coord.b' % out_fol
        nras_str        = '170852857'
        noData_str      = '-9999'

        png_title = '%s - S%02d - G%03d - Year %02d' % (ftype_labels[ntyp],s,g,elapsedyear-spinup_years)
        
        #############################################################
        ##      Convert land change raster from binary to ASCI     ##
        #############################################################
        print('\nconverting binary file to ASCI raster')
        cmdstr2 = ['./morph_rasters_bin2xyz_v23.0.0',xyz_asc_pth, x_bin_pth, y_bin_pth, xyz_bin_pth, dtype, nras_str]
        subprocess.call(cmdstr2)
        
        
        #############################################################
        ##      Convert land change raster from ASCI to TIF        ##
        #############################################################
        print('\nconverting ASCI raster to TIF')
        cmdstr3 = ['gdal_translate', xyz_asc_pth, tif_pth]
        subprocess.call(cmdstr3)
        
        
        ############################################
        ##      Map TIF raster to PNG image       ##
        ############################################
        print('\nmapping TIF to PNG image')

        # open and read TIF raster with rasterio  - then filter for NoData
        with rio.open(tif_pth) as open_tif:
            tif = open_tif.read(1)
        tif_na = np.ma.masked_where(tif < -9990 ,tif,copy=True)

        fig,ax = plt.subplots(figsize=(11,5))
        if ftype == 'salav30':
            tif_map = ax.imshow(tif_na,cmap=cmap,vmin=0.0,vmax=36.0)
            plt.colorbar(tif_map)
        elif ftype == 'salmx30':
            tif_map = ax.imshow(tif_na,cmap=cmap,vmin=0.0,vmax=36.0)
            plt.colorbar(tif_map)
        else:
            tif_map = ax.imshow(tif,cmap=cmap,norm=norm)
            patches = [Patch(color=color,label=label) for color,label in legend_labels.items()]
            ax.legend(handles=patches,bbox_to_anchor=[0,0],loc='lower left',frameon=False,facecolor=None,fontsize='small')
        
        # generic figure edits
        ax.set_axis_off()
        ax.set_title(png_title,fontsize='small')
        plt.figtext(0.99,0.01,footnote,horizontalalignment='right',fontsize='xx-small')
        
        # save as image
        plt.savefig(png_pth,dpi=1800)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
        
    except:
            print('failed to convert and/or map %s' % ftype)
