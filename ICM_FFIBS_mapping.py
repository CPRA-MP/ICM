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
asc_grid_rows = 371
ngrid = 173898



#############################
##      Setup folders      ##
#############################
print('\nsetting up folders')
veg_fol          = 'S%02d/G%03d/veg' % (s,g)
in_fol          = 'S%02d/G%03d/geomorph/input' % (s,g)
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




try:
    LVMout_pth      = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_%02d_%02d_V_vegty.asc+' % (veg_fol,s,g,elapsedyear,elapsedyear)
    FFIBSasc_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_%02d_%02d_W_FFIBS.asc' % (veg_fol,s,g,elapsedyear,elapsedyear)
    FFIBStif_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_FFIBS.tif' % (tif_fol,s,g,elapsedyear,elapsedyear)
    LTtif_pth       = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_%02d_%02d_W_lndtyp.tif' % (tif_fol,s,g,elapsedyear,elapsedyear)
    LVgridtif_pth   = '%s/MP2023_S00_G000_C000_U00_V00_SLA_I_00_00_W_grid30.tif' % (in_fol)
    png_pth         = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_%02d_%02d_W_FFIBS.png' % (png_fol,s,g,elapsedyear,elapsedyear)

    png_title = 'Habitat Classification - S%02d - G%03d - Year %02d' % (s,g,elapsedyear-spinup_years)
    

    
    ############################################
    ##           Read in TIF rasters          ##
    ############################################
    print('\ncombining FFIBS and landtype files')

    # open and read landtype TIF raster with rasterio  - then filter for NoData
    with rio.open(LTtif_pth) as open_tif:
        LTtif = open_tif.read(1)
        LTtrans = open_tif.transform        # save transformation settings to properly set raster resolution and coordinates when writing output TIF
    LTcrs = 'EPSG:26915'                    # EPSG code for UTM Zone 15N projection

    # read in ICM-LAVegMod grid raster        
    with rio.open(LVgridtif_pth) as open_tif:
        LVgridtif = open_tif.read(1)
    LVgridtif = LVgridtif[:-20]       # input grid TIF for grid has 20 additional rows of NoData at the bottom of the raster compared to the LT tif from Morph
    
    if LVgridtif.shape != LTtif.shape:
        print('Grid and landtype rasters are not of the same shape')
        sys.exit()

    # read in FFIBS score for each LAVegMod grid cell
    sp_names = np.genfromtxt( LVMout_pth, skip_header=asc_grid_rows, skip_footer=ngrid, delimiter=',', dtype='str').tolist()
    sp_names = [sn.strip() for sn in sp_names]
    
    grdID_i = sp_names.index('CELLID')
    FFIBS_i = sp_names.index('FFIBS')

    LVMout   = np.genfromtxt( LVMout_pth, skip_header=asc_grid_rows+1,usecols=[grdID_i,FFIBS_i], delimiter=',', dtype='float')
    FFIBS_d = {}
    for row in LVMout:
        cID = int(row[0])               # grid cell ID must be integer since grid30.tif is an integer raster
        FFIBS_d[cID] = row[1]


    ############################
    ##  FFIBS_30 data values  ##
    ############################
    ##  -9999       :   either NoData in GridID or Landtype rasters
    ##  0.0 - 24.0  :   pixel is vegetated and has a  FFIBS score
    ##  200         :   pixel is water
    ##  300         :   pixel is unvegetated mudflat
    ##  400         :   pixel is upland/developed land
    ##  500         :   pixel is flotant
    ##  +9999       :   land pixel is of vegetated land landtype, but there is NoData in the FFIBS output data from LAVegMod
    ############################
    # map FFIBS score to 30-m grid when the Landtype = 1, otherwise remap Landtype to higher values
    
    FFIBS_30 = LVgridtif*0.0     # build zero array in equal dimensions of grid30 tif
    rows,cols = LVgridtif.shape
    for r in range(0,rows):
        if r in range(0,rows,int(rows/10)):
            print('processed %s of %s rows...' % (r,rows))
        for c in range(0,cols):
            gridID = LVgridtif[r][c]
            LT   = LTtif[r][c]
            if gridID > 0:
                if LT > 0:
                    if LT == 1:
                        FFIBS = FFIBS_d[gridID]
                        if FFIBS > 0:            # FFIBS is NoData, but it is on vegetated landtype - set to new NoData value of +9999
                             ffibs2map = FFIBS
                        else:
                            ffibs2map = 9999
                    else:
                        ffibs2map = LT*100
                else:
                    ffibs2map = -9999              # landtype is NoData, keep NoData value as -9999
            else:
                ffibs2map = -9999                  # gridID is NoData, keep NoData value as -9999
            FFIBS_30[r][c] = ffibs2map

    # update grids to account for NoData
    FFIBS_30_na = FFIBS_30 #np.ma.masked_where(FFIBS_30 < -9990 ,FFIBS_30,copy=True)
    
    ##################################################################
    ##       Export FFIBS landtype combination raster as a TIF      ##
    ##################################################################
    print('\nSaving %s' % FFIBStif_pth)
    with rio.open(FFIBStif_pth,'w',dtype=rio.float32,count=1,driver='GTiff',height=rows,width=cols,crs=LTcrs,transform=LTtrans) as dest:
        dest.write(FFIBS_30.astype(rio.float32),1)

    ##################################################################
    ##      Setup colormaps to be used in mapping each datatype     ##
    ##################################################################
    print('\nSaving FFIBS map as PNG file.')
    # color map and legend used for LandType rasters
    # BoundaryNorm sets the edge of bins to which ListedColormap colors are applied
    cmap = ListedColormap(['white','darkgreen','green','yellow','orange','red','cornflowerblue','saddlebrown','silver','paleturquoise','black'])
    norm = colors.BoundaryNorm([-9999.999,-0.01,0.151,1.51,5.01,18.01,25.01,200.01,300.01,400.1,500.1,9999.999],12)                  # BoundaryNorm bins set to map integer values of 1, 2, 3, 4, & 5
    legend_labels = {'darkgreen': 'forested','green':'fresh marsh','yellow':'intermediate marsh','orange':'brackish marsh','red':'saline marsh','cornflowerblue':'water','saddlebrown':'mudflat/bareground','silver':'developed/upland','paleturquoise':'flotant'}



    fig,ax = plt.subplots(figsize=(11,5))
    tif_map = ax.imshow(FFIBS_30_na,cmap=cmap,norm=norm,interpolation='none')
    patches = [Patch(color=color,label=label) for color,label in legend_labels.items()]
    ax.legend(handles=patches,bbox_to_anchor=[0,0],loc='lower left',frameon=False,facecolor=None,fontsize='small',ncol=2)
    
    # generic figure edits
    ax.set_axis_off()
    ax.set_title(png_title,fontsize='small')
    plt.figtext(0.99,0.01,footnote,horizontalalignment='right',fontsize='xx-small')
    
    # save as image
    plt.savefig(png_pth,dpi=1800)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
    
except:
        print('failed to convert and/or map %s' % ftype)
