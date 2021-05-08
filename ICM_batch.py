import subprocess, os

def write_sbatch(sbatch_file,account,email,tag,tag8,py):
    with open(sbatch_file, mode='w') as sbat:
        sbat.write('#!/bin/bash\n')
        sbat.write('#SBATCH -p RM-shared\n')                            # use RM-shared partition
        sbat.write('#SBATCH -t 48:00:00\n')
        sbat.write('#SBATCH -N 1\n')                                    # use only one node
        sbat.write('#SBATCH --ntasks-per-node 32\n')                    # use only 32 cores of one node
        sbat.write('#SBATCH -J %s\n' % tag8)                             # assign Job Name
        sbat.write('#SBATCH -o _%s.log\n' % tag)                        # set name for log file
        sbat.write('#SBATCH --mail-user=%s\n' % email)
        sbat.write('#SBATCH --mail-type=begin\n')
        sbat.write('#SBATCH --mail-type=end\n')
        sbat.write('#SBATCH -A %s\n' % account)
        sbat.write('\n')
        #sbat.write('date > run.begin\n')
        sbat.write('/usr/bin/time -v python ./%s\n' % py)               # set python executable
        #sbat.write('date > run.end\n')
    return()

years = range(2019,2071)
for year in years:
    ey = year - years[0] + 1                                            # elapsed year

    account = 'bcs200002p'
    email =   'eric.white@la.gov'
    tag =     'S06_G502_%02d' % ey
    tag8 =    'S6G502%02d' % ey                                         #SLURM job names on Bridges only allow for 8 characters
    py =      'S06_G502_ICM.py'
    
    sbatch_file = '%s.submit' % tag
    write_sbatch(sbatch_file,account,email,tag,tag8,py)

    if ey == 1:
        #cmd = 'sbatch %s' % sbatch_file                                 # command string to submit first job without any dependencies
        cmd = ['sbatch', '%s' % sbatch_file]
    else:
        #cmd = 'sbatch --depend=afterok:%s %s' % (jobnum, sbatch_file)   # command string to submit job that is dependenent on previous year job finishing successfully
        cmd = ['sbatch','--depend=afterok:%s' % jobnum,'%s' % sbatch_file]

#    status, jobnum_string = subprocess.getstatusoutput(cmd)             # submit job and save job number
    try:
        jobnum_string = subprocess.check_output(cmd).decode()
        status = 0
    except:
        status = 1 
    
    jobnum = jobnum_string.split()[-1]

    if (status == 0 ):
        print('%s is job: %s' % (sbatch_file,jobnum) )
    else:
        print('%s failed to submit. Fix.')
        break
