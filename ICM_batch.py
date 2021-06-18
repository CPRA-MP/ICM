def write_sbatch(sbatch_file,account,email,tag,tag8,ctrl_str,ICMpy,perfflag=1):
    if perfflag == 1:
            perfstr = '/usr/bin/time -v '
    else:
        perfstr = ''

    with open(sbatch_file, mode='w') as sbat:
        out = sbat.write('#!/bin/bash\n')
        out = sbat.write('#SBATCH -p RM-shared\n')                              # use RM-shared partition
        out = sbat.write('#SBATCH -t 48:00:00\n')                               # set max simulation limit to 48 hours
        out = sbat.write('#SBATCH -N 1\n')                                      # use only one node
        out = sbat.write('#SBATCH --ntasks-per-node 16\n')                      # use only 32 cores of one node
        out = sbat.write('#SBATCH -J %s\n' % tag8)                              # assign Job Name
        out = sbat.write('#SBATCH -o _%s.log\n' % tag)                          # set name for log file
        out = sbat.write('#SBATCH --mail-user=%s\n' % email)                    # set email address for notifications
        out = sbat.write('#SBATCH --mail-type=begin\n')                         # send email when simulation leaves queue
        out = sbat.write('#SBATCH --mail-type=end\n')                           # send email when simulation finishes
        out = sbat.write('#SBATCH -A %s\n' % account)                           # XSEDE allocation for SU accounting
        out = sbat.write('\n')
        #out = sbat.write('date > run.begin\n')                                 # uncomment if want start datetime to be save to 'run.begin' text file
        out = sbat.write('python ./%s\n' % ctrl_str)                            # set ICM_update_control.py command string
        out = sbat.write('%spython ./%s\n' % (perfstr,ICMpy))                  # set ICM.py executable
        #out = sbat.write('date > run.end\n')                                   # uncomment if want start datetime to be save to 'run.begin' text file
    return()

def hotstart(s,g,cyc_s,cyc0_s=2019):
    # this function will cleanup model output files in order to hotstart the model.
    print('Starting to clean up files to hotstart model in %04d...' % cyc_s)
    days2keep = 0
    for yr in range(cyc0_s,cyc_s):
        if yr in range(1984,4000,4):
            days2keep += 366
        else:
            days2keep += 365
    outfiles = os.listdir('hydro' )
    for orig_outfile in outfiles:
        if orig_outfile.endswith('.out'):
            print(' - cleaning up S%02d G%03d %s' % (s,g,orig_outfile) )
            outfile = 'hydro/%s' % (orig_outfile)
            bkfile = 'hydro/%s.bk' % (orig_outfile)
            os.rename(outfile,bkfile)
            with open(bkfile,mode='r') as orig:
                with open(outfile,mode='w') as new:
                    for day in range(0,days2keep):
                        line2write=orig.readline()
                        w = new.write(line2write)
            os.remove(bkfile)
    for reg in ['ATCH','WLO','CSC','lower_Mississippi']:
        for mod in ['FINE','HYDRO','SAL','SAND','TMP']:
            outdir = 'hydro/%s/%s/output' % (reg,mod)
            outfiles = os.listdir('%s' % outdir)
            for outfile in outfiles:
                try:
                    year = int(outfile.split('.')[0][-4:])
                    if year >= cyc_s:
                        print('removing %s/%s' % (outdir,outfile) )
                        os.remove('%s/%s' % (outdir,outfile) )
                except:
                    a=0
    return()

import subprocess
import os
import sys


s       = 6                                                                     # scenario number as integer
g       = 501                                                                   # model group number as integer
ICMpy   = 'ICM.py'                                                              # ICM control code to use for this simulation (e.g. ICM.py)
perf    = 1                                                                     # turn on (1) or off (0) the verbose 'time' function to report out CPU and memory stats for run
account = 'bcs200002p'                                                          # XSEDE allocation account
email   = 'eric.white@la.gov'                                                   # emails for notification on queue
batlog  = 'sbatch_queue.log'                                                    # log file in main directory that logs queue submissions and job dependencies

shsub_col = {'S06':1,'S07':1,'S08':2,'S09':2}                                   # column of shallow subsidence input table to be used for each scenario (set in ICM_control.csv)
                                                                                # input shallow subsidence table : ./geomorph/ecoregion_shallow_subsidence_mm.csv
                                                                                # column 1: 25th percentile shallow subsidence for ecoregion
                                                                                # column 2: 50th percentile shallow subsidence for ecoregion
                                                                                # column 3: 75th percentile shallow subsidence for ecoregion

cyc0_s = 2019                                                                   # initial model year for all cycles - this must be equal to the starting year of the *.out files generated by ICM_Hydro
cycles = {}
cycles[ 1] = [2019,2020]
cycles[ 2] = [2021,2025]
cycles[ 3] = [2026,2030]
cycles[ 4] = [2031,2035]
cycles[ 5] = [2036,2040]
cycles[ 6] = [2041,2045]
cycles[ 7] = [2046,2050]
cycles[ 8] = [2051,2055]
cycles[ 9] = [2056,2060]
cycles[10] = [2061,2065]
cycles[11] = [2066,2070]

check = input('\n You are trying to submit %d cycles for S%02d G%03d. Is that right? [y]es or [n]o?\n' % (len(cycles.keys()),s,g) )
if check == 'y':
    print (' Thanks for confirming. Moving on with batch submittal.\n\n')
else:
    sys.exit('Glad we asked. Exiting now so you can get thing straightened out.\n')

hstxt = ''                                                                  # string that will report out whether current cycle is a hotstart or not
prv_jobnum = -9999                                                          # flag for previous job number - will not be re-set until after first job in batch is successfully submitted

for cyc_n in sorted(cycles.keys()):
    cyc_s = cycles[cyc_n][0]                                                    # starting year for cycle
    cyc_e = cycles[cyc_n][1]                                                    # ending year for cycle

    tag         = 'S%02d_G%03d_cyc%02d' % (s,g,cyc_n)
    tag8        = '%d.%3d.%02d'         % (s,g,cyc_n)                           # SLURM job names on Bridges only allow for 8 characters
    sbatch_file = '%s.submit' % tag
    sub_n       = shsub_col['S%02d' % s]
    ctrl_str    = 'ICM_control_update.py %s %s %d %04d %04d %d' % (s, g, cyc_n, cyc_s, cyc_e, sub_n) 
    

    
    if cyc_n == min(cycles.keys()):                                             # check if job for cycle should be dependent on previous cycle or not
        if cyc_s != cyc0_s:                                                     # check if hotstarting
            print('\n\nStarting year of first cycle is set to %04d, not %04d.\n' % (cyc_s,cyc0_s) )
            hs = input('Do you want to hotstart the model in %04d? [y]es or [n]o?\n' % cyc_s)
            if hs == 'y':
                print('\nAlright. Hotstarting in %04d.' % cyc_s)  
                hstxt = '  Hotstarting the model in %04d.' % cyc_s
                hotstart(cyc_s,cyc0_s)
            else:
                sys.exit('\nUnderstood. Clean up your input settings and start again. Exiting now.\n\n')
                
        cmdstr = ['sbatch', '%s' % sbatch_file]
    else:
        cmdstr = ['sbatch','--depend=afterok:%s' % prv_jobnum,'%s' % sbatch_file]
    
    # write batch file that will be submitted to SLURM queue with sbatch
    write_sbatch(sbatch_file,account,email,tag,tag8,ctrl_str,ICMpy,perf)

    # submit job using subprocess and save JobID
    # on Bridges2 a successful sbatch call returns a a JobID as a string message:
    #
    # $ sbatch S06_G502.submit
    # Submitted batch job 1134247
    try:
        jobnum_string = subprocess.check_output(cmdstr).decode()
        status = 0
    except:
        status = 1 
    
    jobnum = jobnum_string.split()[-1]

    if (status == 0 ):
        print('%s is job: %s' % (tag,jobnum) )
        with open(batlog,mode='a') as qlog:
            if prv_jobnum == -9999:
                qlog.write('%s (%04d-%04d) is job %s and has no job dependencies.%s\n' % (tag,cyc_s,cyc_e,jobnum,hstxt) )
            else:
                qlog.write('%s (%04d-%04d) is job %s and depends on job %s finishing successfully.%s\n' % (tag,cyc_s,cyc_e,jobnum,prv_jobnum,hstxt) )
    else:
        print('%s failed to submit. Fix.' % tag)
        break
    
    prv_jobnum = jobnum    
