# simple python script to update the ICM_control.csv input file for simulation batching
# call this function with passing in variables to be updated in ICM_control.csv:  
#     $python update_ICM_control.py S06 G501 1 2019 2020 1

# fnc_s = scenario number for use in file naming convention
# fnc_g = model group number for use in file naming convention
# cyc_n = number of current simulation cycle being set up
# cyc_s = calendar year for first year of current simulation cycle
# cyc_s = calendar year for last year of current simulation cycle
# sub_n = column from shallow subsidence input data to be used for scenario

import sys
import os

fnc_s = int(sys.argv[1])
fnc_g = int(sys.argv[2])
cyc_n = int(sys.argv[3])
cyc_s = int(sys.argv[4])
cyc_e = int(sys.argv[5])
sub_n = int(sys.argv[6])

print('\n*****************************************************************')
print('  Updating ICM_control.csv for S%02d G%03d cycle %02d (%04d-%04d).' % (fnc_s,fnc_g,cyc_n,cyc_s,cyc_e) )
print('*****************************************************************\n')


old_ctrl = 'ICM_control_%02d.csv' % (cyc_n-1)
ctrl = 'ICM_control.csv'
os.rename(ctrl,old_ctrl)

with open(old_ctrl, mode='r') as cf:
    with open(ctrl,mode='w') as wf:
        nl = 0
        for line in cf:
            var = line.split(',')[0]
            val = line.split(',')[1]
            nl += 1
            if nl == 25:                                    # sub_n:  update column of shallow subsidence input data to be used for this run
                out = wf.write('%s,%d\n' % (var,sub_n) )
            elif nl == 42:                                 # cyc_n:  update simulation cycle number
                out = wf.write('%s,%d\n' % (var,cyc_n) )
            elif nl == 43:                                  # cyc_s:  update first year of simulation cycle
                out = wf.write('%s,%d\n' % (var,cyc_s) )
            elif nl == 44:                                  # cyc_e:  update end year of simulation cycle 
                out = wf.write('%s,%d\n' % (var,cyc_e) )
            elif nl == 65:                                  # fnc_s:  update scenario number for file naming convention tag 
                out = wf.write('%s,S%02d\n' % (var,fnc_s) )
            elif nl == 66:                                  # fnc_g:  update model group number for file naming convention tag
                out = wf.write('%s,G%03d\n' % (var,fnc_g) )
            else:
                out = wf.write(line)
