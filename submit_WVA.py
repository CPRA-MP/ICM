def write_sbatch(sbatch_file,account,email,tag8,ctrl_str,perfflag=1):
    if perfflag == 1:
            perfstr = '/usr/bin/time -v '
    else:
        perfstr = ''

    with open(sbatch_file, mode='w') as sbat:
        out = sbat.write('#!/bin/bash\n')
        out = sbat.write('#SBATCH -p RM-shared\n')                              # use RM-shared partition
        out = sbat.write('#SBATCH -t 12:00:00\n')                               # set max simulation limit to 48 hours
        out = sbat.write('#SBATCH -N 1\n')                                      # use only one node
        out = sbat.write('#SBATCH --ntasks-per-node 20\n')                      # use only 20 cores of one node
        out = sbat.write('#SBATCH -J %s\n' % tag8)                              # assign Job Name
        out = sbat.write('#SBATCH -o %s.log\n' % tag8)                          # set name for log file
        out = sbat.write('#SBATCH --mail-user=%s\n' % email)                    # set email address for notifications
        #out = sbat.write('#SBATCH --mail-type=begin\n')                         # send email when simulation leaves queue
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
import numpy as np

#to run command: sumbit_WVA.py S% G%%%

s = int(sys.argv[1])
g_fwa = int(sys.argv[2])
project = sys.argv[3]

perf = 0
account = 'bcs200002p'                                                          # XSEDE allocation account
email   = 'henry.mccall@csrsinc.com'                                            # emails for notification on queue
sbatch_file = 'wva.submit'

#curdir = os.getcwd()
HSIcontol = os.path.normpath('/ocean/projects/bcs200002p/ewhite12/%s/ICM/S0%s/G%s/ICM_HSI_control.csv' % (project,s,g_fwa))
#HSIcontol = os.path.normpath('%s/S0%s/G%s/ICM_HSI_control.csv' % (curdir,s,g_fwa)) #Test String

inputs = np.genfromtxt(HSIcontol,dtype=str,comments='#',delimiter=',')

startyear = int(inputs[29,1].lstrip().rstrip())
endyear = int(inputs[30,1].lstrip().rstrip())


for year in range(startyear, endyear+1):
    # for xyz in range (0,4): #test String
    #     listyears = [2020, 2030, 2040, 2050] #For Testing
    #     year = listyears[xyz] #For Testing
    ey = year-startyear+1
    cmd1 = 'python ICM_WVA_standalone.py %s %s %s %s\n' % (s,g_fwa,year, project)

    #os.chdir('%s/S%02d/G%03d' % (curdir, s, g_fwa))

    tag8    = 'wva4%01d%03d%02d' % (s,g_fwa,ey)
    sbatch_file_unique = 'S%02d.G%03d.%04d.%s' % (s,g_fwa,year,sbatch_file)
    write_sbatch(sbatch_file_unique,account,email,tag8,cmd1,perf)

    cmdstr = ['sbatch', '%s' % sbatch_file_unique]
    cmdout = subprocess.check_output(cmdstr).decode()