def write_sbatch(sbatch_file,account,email,tag8,ctrl_str,perfflag=1):
    if perfflag == 1:
            perfstr = '/usr/bin/time -v '
    else:
        perfstr = ''

    with open(sbatch_file, mode='w') as sbat:
        out = sbat.write('#!/bin/bash\n')
        out = sbat.write('#SBATCH -p RM-shared\n')                              # use RM-shared partition
        out = sbat.write('#SBATCH -t 01:30:00\n')                               # set max simulation limit to 48 hours
        out = sbat.write('#SBATCH -N 1\n')                                      # use only one node
        out = sbat.write('#SBATCH --ntasks-per-node 20\n')                      # use only 16 cores of one node
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
g = int(sys.argv[2])
sy = 2019
#years = [2029,2041,2055,2069]
years = range(2019,2071)
years =[]
plot_hydro = True
plot_veg = True

py   = 'postprocess.py'                                                              # ICM control code to use for this simulation (e.g. ICM.py)
perf    = 1                                                                     # turn on (1) or off (0) the verbose 'time' function to report out CPU and memory stats for run
account = 'bcs200002p'                                                          # XSEDE allocation account
email   = 'eric.white@la.gov'                                                   # emails for notification on queue
sbatch_file = 'postprocess.submit'



for y in years:
    print('post-processing: S%02d G%03d - yr %s' % (s,g,y) )
    cmd1      = 'python ICM_tif_mapping.py %s %s %s %s\n' % (s,g,y,sy) 
    cmd2      = 'python ICM_FFIBS_mapping.py %s %s %s %s\n' % (s,g,y,sy) 
    cmd3      = 'python morph_differencing.py %s %s %s 2\n' % (s, g, y-sy+1)
    ctrl_str = cmd1 + cmd2 + cmd3
    
    tag8    = 'pp%01d%03d%02d' % (s,g,y-sy+1) 
    write_sbatch(sbatch_file,account,email,tag8,ctrl_str,perf)
    
    cmdstr = ['sbatch', '%s' % sbatch_file]
    cmdout = subprocess.check_output(cmdstr).decode()

    
if plot_hydro == True:
    print('plotting ICM-Hydro timeseries: S%02d G%03d' % (s,g) )
    tag8 = 'hyts%01d%03d' % (s,g)
    ctrl_str = 'python ICM-Hydro_plotting_noCRMS.py %s %s' % (s,g)
    write_sbatch(sbatch_file,account,email,tag8,ctrl_str,perf)
    cmdstr = ['sbatch', '%s' % sbatch_file]
    cmdout = subprocess.check_output(cmdstr).decode()
    
if plot_veg == True:
    print('plotting ICM-LAVegMod timeseries: S%02d G%03d' % (s,g) )
    last_year = 2070
    tag8 = 'vgts%01d%03d' % (s,g)
    ctrl_str = 'python ICM-Veg_timeseries_plotting.py %s %s %s' % (s,g,last_year)
    write_sbatch(sbatch_file,account,email,tag8,ctrl_str,perf)
    cmdstr = ['sbatch', '%s' % sbatch_file]
    cmdout = subprocess.check_output(cmdstr).decode()