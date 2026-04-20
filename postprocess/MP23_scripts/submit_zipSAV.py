
def write_sbatch(sbatch_file,account,email,tag8,ctrl_str,perfflag=1):
    if perfflag == 1:
            perfstr = '/usr/bin/time -v '
    else:
        perfstr = ''

    with open(sbatch_file, mode='w') as sbat:
        out = sbat.write('#!/bin/bash\n')
        out = sbat.write('#SBATCH -p RM-shared\n')                              # use RM-shared partition
        out = sbat.write('#SBATCH -t 00:20:00\n')                               # set max simulation limit to 48 hours
#        out = sbat.write('#SBATCH -N 1\n')                                      # use only one node
#        out = sbat.write('#SBATCH --ntasks-per-node 20\n')                      # use only 20 cores of one node
        out = sbat.write('#SBATCH -J %s\n' % tag8)                              # assign Job Name
#        out = sbat.write('#SBATCH -o %s.log\n' % tag8)                          # set name for log file
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
sav_yr = int(sys.argv[3])
sy = 2019
elapsedyear = sav_yr - sy + 1
pd = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM'

perf    = 0                                                                     # turn on (1) or off (0) the verbose 'time' function to report out CPU and memory stats for run
account = 'bcs200002p'                                                          # XSEDE allocation account
email   = 'eric.white@la.gov'                                                   # emails for notification on queue
sbatch_file = 'SAV_zip.submit'


mpterm = 'MP2023'
sterm = 'S%02d' % s
gterm = 'G%03d' % g
cterm = 'C000'
uterm = 'U00'
vterm = 'V00'
rterm = 'SLA'


runprefix = '%s_%s_%s_%s_%s_%s_%s' % (mpterm,sterm,gterm,cterm,uterm,vterm,rterm)
file_oprefix    = '%s_O_%02d_%02d' % (runprefix,elapsedyear,elapsedyear)
sav_file_no_ext = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM/%s/%s/geomorph/output/%s_W_SAV' % (sterm,gterm,file_oprefix)

SAVcsv = '%s.csv' % sav_file_no_ext 
SAVasc = '%s.asc' % sav_file_no_ext
SAVxyz = '%s_prob.xyz' % sav_file_no_ext

SAVxyz_zip = '%s.zip' % SAVxyz
SAVcsv_zip = '%s.zip' % SAVcsv

ctrl_str = 'zip -mT %s %s \nzip -mT %s %s \n' % (SAVxyz_zip,SAVxyz,SAVcsv_zip,SAVcsv)

tag8    = 'zi%01d%03d%02d' % (s,g,elapsedyear) 
write_sbatch(sbatch_file,account,email,tag8,ctrl_str,perf)
cmdstr = ['sbatch', '%s' % sbatch_file]
cmdout = subprocess.check_output(cmdstr).decode()
