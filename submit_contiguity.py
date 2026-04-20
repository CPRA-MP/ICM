import subprocess, os, sys

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
        #sbat.write('module purge\n')
        #sbat.write('module load python/3.8.6\n')
        #sbat.write('\n')

        #out = sbat.write('date > run.begin\n')      
        out = sbat.write('module load anaconda3\n')
        out = sbat.write('source activate ICMv2023\n')        # uncomment if want start datetime to be save to 'run.begin' text file
        out = sbat.write('%s%s' % (perfstr, ctrl_str))                          # set call python script being submitted
        #out = sbat.write('date > run.end\n')                                   # uncomment if want start datetime to be save to 'run.begin' text file
    return()


s = int(sys.argv[1])
g = int(sys.argv[2])
y = int(sys.argv[3])

perf    = 0                                                                     # turn on (1) or off (0) the verbose 'time' function to report out CPU and memory stats for run
account = 'bcs200002p'                                                          # XSEDE allocation account
email   = ''                                                   # emails for notification on queue
#tag8 = 'contiguity%d%3d%2d' % (s,g,y)
tag8 = f'contiguity{s}{g:03}{y:02}'

ctrl_str = 'python contiguity.py  %s %s %s\n' % (s,g,y)
sbatch_file = 'S%02d.G%03d.y%04d.contig.submit' % (s,g,y)
write_sbatch(sbatch_file,account,email,tag8,ctrl_str,perf)
cmdstr = ['sbatch', '%s' % sbatch_file]
cmdout = subprocess.check_output(cmdstr).decode()