def write_sbatch(sbatch_file,account,email,tag8,ctrl_str,perfflag=1):
    if perfflag == 1:
            perfstr = '/usr/bin/time -v '
    else:
        perfstr = ''

    with open(sbatch_file, mode='w') as sbat:
        out = sbat.write('#!/bin/bash\n')
        out = sbat.write('#SBATCH -p RM-shared\n')                              # use RM-shared partition
        out = sbat.write('#SBATCH -t 03:00:00\n')                               # set max simulation limit to 48 hours
        out = sbat.write('#SBATCH -N 1\n')                                      # use only one node
        out = sbat.write('#SBATCH --ntasks-per-node 20\n')                      # use only 20 cores of one node
        out = sbat.write('#SBATCH -J %s\n' % tag8)                              # assign Job Name
        out = sbat.write('#SBATCH -o %s.log\n' % tag8)                          # set name for log file
        out = sbat.write('#SBATCH --mail-user=%s\n' % email)                    # set email address for notifications
#        out = sbat.write('#SBATCH --mail-type=begin\n')                         # send email when simulation leaves queue
        out = sbat.write('#SBATCH --mail-type=end\n')                           # send email when simulation finishes
        out = sbat.write('#SBATCH -A %s\n' % account)                           # XSEDE allocation for SU accounting
        out = sbat.write('\n')
        #out = sbat.write('date > run.begin\n')                                  # uncomment if want start datetime to be save to 'run.begin' text file
        out = sbat.write('%s%s' % (perfstr, ctrl_str))                          # set call python script being submitted
        #out = sbat.write('date > run.end\n')                                   # uncomment if want start datetime to be save to 'run.begin' text file
    return()



import subprocess
import os
import sys
import shutil

s = int(sys.argv[1])
g_fwa = int(sys.argv[2])
g_fwoa = int(sys.argv[3])
c = 0
u = 0
v = 0
r = 'SLA'

sy = 2019   # start year of model run
syp = 2019  # start year for postprocessing script
ny = 2059
ey_ic = 2       # elapsed year of initial conditions landscape
map_interval = 1

# build list of years that will have outputs mapped
years = []
for yr in range(syp,ny+1,map_interval):
    years.append(yr)

#years = range(2060,2071)

backup_old_file = False
rename_hydro    = False
plot_TIFs       = True
plot_FFIBS      = True
plot_IC_change  = True
plot_FWOA_diff  = True
plot_IC_FWOA_diff  = True
plot_hydro_ts   = False
plot_veg_ts     = False

perf    = 0                                                                     # turn on (1) or off (0) the verbose 'time' function to report out CPU and memory stats for run
account = 'bcs200002p'                                                          # XSEDE allocation account
email   = 'eric.white@la.gov'                                                   # emails for notification on queue
#email   = 'khanegan@moffattnichol.com'
sbatch_file = 'postprocess.submit'

# set raster and difference raster types for FWOA diff function call
diffrastypes = {}
diffrastypes['lndtypdiff']  = 'lndtyp30'
diffrastypes['salavdiff']   = 'salav30'
diffrastypes['salmxdiff']   = 'salmx30'
diffrastypes['inundiff']    = 'inun30'
diffrastypes['elevdiff']    = 'dem30'

if backup_old_file == True:
    out_fol         = 'S%02d/G%03d/geomorph/output' % (s,g_fwa)
    xyz_fol         = '%s/xyz' % out_fol
    tif_fol         = '%s/tif' % out_fol
    png_fol         = '%s/png' % out_fol

    for fol in [xyz_fol,tif_fol,png_fol]:
        try:
            if os.path.isdir(fol) == False:
                os.mv(fol,'%s_old' % fol)
        except:
            print('could not build %s_old' % fol)

if rename_hydro == True:
    out_fol = 'S%02d/G%03d/hydro' % (s,g_fwa)
    print('renaming Hydro *.out files in: %s' % out_fol)
    for out in os.listdir(out_fol):
        if out.endswith('.out'):
            out1 = '%s/%s' % (out_fol,out)
            out2 = '%s/MP2023_S%02d_G%03d_C%03d_U%02d_V%02d_%s_O_01_52_H_%s' % (out_fol,s,g_fwa,c,u,v,r,out)
            if out.startswith('MP2023'):
                print('%s already exists - skipping rename' % out1)
            else:
                os.rename(out1,out2)


for y in years:
    # this script will batch submit ICM_tif_mapping, ICM_FFIBS_mapping and ICM_morph_differencing for one year in the same job to the queue
    # all data types in ICM_tif_mappingwill be looped over BEFORE the job moves on to ICM_FFIBS and ICM_morph_differencing
    print('submitting post-processing jobs for: S%02d G%03d - yr %s' % (s,g_fwa,y) )

    # calculate elaped years used by ICM_morph_differencing
    ey =  y-sy+1

    if plot_TIFs == True:
        print('   - mapping Morph outputs as TIFs/PNGs')
        cmd1 = 'python ICM_tif_mapping.py %s %s %s %s\n' % (s,g_fwa,y,sy)
    else:
        cmd1 = ''

    if plot_FFIBS == True:
        print('   - mapping LAVegMod FFIBS outputs as TIFs/PNGs')
        cmd2 = 'python ICM_FFIBS_mapping.py %s %s %s %s\n' % (s,g_fwa,y,sy)
    else:
        cmd2 = ''

    if plot_IC_change == True:
        if ey > ey_ic:
            cmd3 = 'python ICM_morph_differencing.py %s %s %s %s %s %s %s\n' % (s, g_fwa, g_fwa, ey, ey_ic, 'lndtyp30', 'lndchg')
        else:
            cmd3 = ''
    else:
        cmd3 = ''

    ctrl_str = cmd1 + cmd2 + cmd3

    if plot_FWOA_diff == True:
        print('   - mapping Morph Difference from FWOA outputs as TIFs/PNGs')
        for difftype in diffrastypes.keys():
            rastype = diffrastypes[difftype]
            cmd4 = 'python ICM_morph_differencing.py %s %s %s %s %s %s %s\n' % (s, g_fwa, g_fwoa, ey, ey, rastype, difftype)

            ctrl_str = ctrl_str + cmd4
    
    if plot_IC_FWOA_diff == True:
        print('   - mapping Morph Difference from both Initial Conditions & FWOA at same year outputs as TIFs')
        cmd5 = 'python ICM_morph_differencing_3ras.py %s %s %s %s %s %s %s %s\n' % (s, g_fwa, g_fwoa, g_fwoa, ey, ey_ic, 'lndtyp30', 'lndtypdiff')

        ctrl_str = ctrl_str + cmd5

    # write sbatch file with final list of function calls saved to ctrol_str
    tag8    = 'pp%01d%03d%02d' % (s,g_fwa,y-sy+1)
    sbatch_file_unique = 'S%02d.G%03d.%04d.%s' % (s,g_fwa,y,sbatch_file)
    write_sbatch(sbatch_file_unique,account,email,tag8,ctrl_str,perf)

    cmdstr = ['sbatch', '%s' % sbatch_file_unique]
    cmdout = subprocess.check_output(cmdstr).decode()


if plot_hydro_ts == True:
    print('plotting ICM-Hydro timeseries: S%02d G%03d' % (s,g_fwa) )
    tag8 = 'hyts%01d%03d' % (s,g_fwa)
    ctrl_str = 'python ICM-Hydro_plotting_noCRMS.py %s %s\n' % (s,g_fwa)
    sbatch_file_uniqueH = 'S%02d.G%03d.%04d.hydTS.%s' % (s,g_fwa,y,sbatch_file)
    write_sbatch(sbatch_file_uniqueH,account,email,tag8,ctrl_str,perf)
    cmdstr = ['sbatch', '%s' % sbatch_file_uniqueH]
    cmdout = subprocess.check_output(cmdstr).decode()

if plot_veg_ts == True:
    print('plotting ICM-LAVegMod timeseries: S%02d G%03d' % (s,g_fwa) )
    last_year = 2070
    tag8 = 'vgts%01d%03d' % (s,g_fwa)

    cmd1 = 'python ICM-Veg_timeseries_plotting.py %s %s %s\n' % (s,g_fwa,last_year)
    cmd2 = 'python ICM-Veg_ecoregion_timeseries_plotting.py %s %s %s\n' % (s,g_fwa,last_year)
    ctrl_str = cmd1 + cmd2

    sbatch_file_uniqueV = 'S%02d.G%03d.2070.vegTS.%s' % (s,g_fwa,sbatch_file)
    write_sbatch(sbatch_file_uniqueV,account,email,tag8,ctrl_str,perf)
    cmdstr = ['sbatch', '%s' % sbatch_file_uniqueV]
    cmdout = subprocess.check_output(cmdstr).decode()
                                                                                         
            
