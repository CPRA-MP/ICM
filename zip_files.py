import subprocess
import os
import sys

s = int(sys.argv[1])
g = int(sys.argv[2])

simdir = '/ocean/projects/bcs200002p/ewhite12/MP2023/ICM_test/S%02d/G%03d' % (s,g)
os.chdir(simdir)

for root, dirs, files in os.walk(simdir, topdown=True):
    for name in files:
        try:
            of = os.path.join(root, name)
            zf = '%s.zip' % of
            print('checking %s for compression.' % of)
            # check for *.out timeseries and do not zip UNLESS they are saved in TempFiles
            if '.out' in of:
                if 'TempFiles' in of:
                    zipcmd = 1#subprocess.call(['zip','-mT', zf, of])

            # check if file is located in specific directories that should not be zipped
            if 'TempFiles/compartment_out' in of:
                _a = 'skip'
            elif 'geomorph/output_qaqc' not in of:
                _ = 'skip'
            elif 'geomorph/output/png' not in of:
                _ = 'skip'
            elif 'veg/coverage_timeseries' not in of:
                zipcmd = 2#subprocess.call(['zip','-mT', zf, of])

        except:
            print('  - failed to zip %s.' % of)


