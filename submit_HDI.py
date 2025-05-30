def write_sbatch(sbatch_file,account,email,tag8,ctrl_str,perfflag=1):
    if perfflag == 1:
            perfstr = '/usr/bin/time -v '
    else:
        perfstr = ''

    with open(sbatch_file, mode='w') as sbat:
        out = sbat.write('#!/bin/bash\n')
        out = sbat.write('#SBATCH -p RM-shared\n')                              # use RM-shared partition
        out = sbat.write('#SBATCH -t 2:00:00\n')                               # set max simulation limit to 48 hours
        out = sbat.write('#SBATCH -N 1\n')                                      # use only one node
        out = sbat.write('#SBATCH --ntasks-per-node 20\n')                      # use only 20 cores of one node
        out = sbat.write('#SBATCH -J %s\n' % tag8)                              # assign Job Name
        out = sbat.write('#SBATCH -o %s.log\n' % tag8)                          # set name for log file
        out = sbat.write('#SBATCH --mail-user=%s\n' % email)                    # set email address for notifications
        out = sbat.write('#SBATCH --mail-type=begin\n')                         # send email when simulation leaves queue
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
import numpy as np

perf = 0
account = 'bcs200002p'                                                          # XSEDE allocation account
email   = 'henry.mccall@csrsinc.com'                                            # emails for notification on queue
sbatch_file = 'HDI.submit'

curdir = os.getcwd()

s = int(sys.argv[1]) #in put scenerio number
g = int(sys.argv[2]) #input group number
project = sys.argv[3] #input project (ie. MP2023, MP2029, UBDP)

run_folder = f'/ocean/projects/bcs200002p/ewhite12/{project}/ICM/S{s:02d}/G{g:03d}' 
inputs = np.genfromtxt(f'{run_folder}/ICM_control.csv',dtype=str,comments='#',delimiter=',')

start_year = int(inputs[29,1].lstrip().rstrip())
end_year = int(inputs[30,1].lstrip().rstrip())


for year in range(start_year,end_year+1):
        ey  = year - start_year + 1
        cmd1 = 'python HDI_standalone.py %s %s %s %s\n' % (s,g,project,year)
        tag8 = f'HDI{g:03d}{ey:02d}'
        sbatch_file_unique = 'S%02d.G%03d.%02d.%s' % (s,g,ey,sbatch_file)
        write_sbatch(sbatch_file_unique,account,email,tag8,cmd1,perf)
        cmdstr = ['sbatch', '%s' % sbatch_file_unique]
        cmdout = subprocess.check_output(cmdstr).decode()
