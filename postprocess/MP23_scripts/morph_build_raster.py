import subprocess
import os
import sys

s   = int(sys.argv[1])
g   = int(sys.argv[2])
yr = int(sys.argv[3])
ftype = sys.argv[4]
dtype = sys.argv[5] #int or flt

#s = 6
#g = 501
#yr1 = 7
#ftyp = 'lndtyp30'


print('\n\nConverting rasters formats for S%02d G%03d - %s - yr %02d:' % (s,g,ftype,yr) )

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
    except:
        print('could not build %s' % fol)



#############################################################
##      Convert land change raster from binary to ASCI     ##
#############################################################
print('\nconverting binary file to ASCI raster')

ras_bin_pth   = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz.b' % (out_fol,s,g,yr,yr,ftype)
xyz_asc_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.xyz' % (xyz_fol,s,g,yr,yr,ftype)
x_bin_pth       = '%s/raster_x_coord.b' % out_fol
y_bin_pth       = '%s/raster_y_coord.b' % out_fol
#dtype           = 'int' #'flt'
nras_str        = '170852857'
noData_str      = '-9999'


cmdstr2 = ['./morph_rasters_bin2xyz_v23.0.0',xyz_asc_pth, x_bin_pth, y_bin_pth, ras_bin_pth, dtype, nras_str]
subprocess.call(cmdstr2)


#############################################################
##      Convert land change raster from ASCI to TIF        ##
#############################################################
print('\nconverting ASCI raster to TIF')
tif_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_%s.tif' % (tif_fol,s,g,yr,yr,ftype)
footnote = 'MP2023 FWOA simulations scenario selection - July 2021'
cmdstr3 = ['gdal_translate', xyz_asc_pth, tif_pth]
subprocess.call(cmdstr3)


