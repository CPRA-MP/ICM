import subprocess
import os

s   = int(sys.argv[1])
g   = int(sys.argv[2])
yr1 = int(sys.argv[3])
yr0 = int(sys.argv[4])

#s = 6
#g = 501
#yr1 = 7
#yr0 = 2


#############################
##      Setup folders      ##
#############################
out_fol         = './S%02d/G%03d/geomorph/output' % (s,g)
xyz_fol         = '%s/xyz' % out_fol 
tif_fol         = '%s/tif' % out_fol
png_fol         = '%s/png' % out_fol
ts_fol          = '%s/ts'  % out_fol

for fol in [xyz_fol,tif_fol,png_fol,ts_fol]:
    if os.path.isdir(fol) == False:
        os.mkdir(fol)


############################################
##      Calculate land change raster      ##
############################################
#lw0 = './S%02d/G%03d/geomorph/input/MP2023_S00_G500_C000_U00_V00_SLA_I_00_00_W_lndtyp30.xyz.b'
ras1_bin_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_lndtyp30.xyz.b' % (out_fol,s,g,yr1,yr1)
ras0_bin_pth    = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_lndtyp30.xyz.b' % (out_fol,s,g,yr0,yr0)
ras01_bin_pth   = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_lndchange.xyz.b' % (out_fol,s,g,yr0,yr1)
difftype        = 'dlw'
nras_str        = 170852857
noData_str      = -9999

cmdstr1 = ['./morph_diff_v23.0.0', ras1_bin_pth, ras0_bin_pth, ras01_bin_pth, difftype, nras_str, noData_str]
subprocess.call(cmdstr1)


#############################################################
##      Convert land change raster from binary to ASCI     ##
#############################################################
xyz_asc_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_lndchange.xyz' % (xyz_fol,s,g,yr0,yr1)
x_bin_pth       = '%s/raster_x_coord.b' % out_fol
y_bin_pth       = '%s/raster_y_coord.b' % out_fol
dtype           = 'int' #'flt'

cmdstr2 = ['./morph_rasters_v23.0.0',xyz_asc_pth, x_bin_pth, y_bin_pth, ras01_bin_pth, dtype, nras_str]
subprocess.call(cmdstr2)


#############################################################
##      Convert land change raster from ASCI to TIF        ##
#############################################################
tif_pth     = '%s/MP2023_S%02d_G%03d_C000_U00_V00_SLA_N_%02d_%02d_W_lndchange.tif' % (tif_fol,s,g,yr0,yr1)

cmdstr3 = ['gdal_translate', xyz_asc_pth, tif_pth]
subprocess.call(cmdstr2)
