import sys
import numpy as np
import subprocess

split_file = True
if split_file == True:
    os.chdir(r'H:\Shared\Planning and Research\Plan Development Section\Master Plan\2023 Master Plan Update\Modeling\Risk Modeling')
    data = np.genfromtxt('depths_g500_for_cpra_2022-03-10.csv',delimiter=',',skip_header=1)

    scenarios = []
    years = []
    returns = []

    for row in data:
        s = row[0]
        y = row[1]
        ri = row[3]
    
        if s not in scenarios:
            scenarios.append(s)
        if y not in years:
            years.append(y)
        if ri not in returns:
            returns.append(ri)
        
    for S in scenarios:
        for RI in returns:
            for Y in years:
                a = outfile = 'MP2023_S%02d_G500_C000_U00_V00_SLA_O_%02d_%02d_CLARA_%0.1f_aep_depths.csv' % (S,Y,Y,100/RI)
                print('prepping %s' % outfile)
                
                with open(outfile,mode='w') as of:
                    a = of.write('landscape_scenario_id,year,point_id,return_period,depth_10,depth_50,depth_90\n')
                    for row in data:
                        s = row[0]
                        y = row[1]
                        ri = row[3]

                        if s == S:
                            if y == Y:
                                if ri == RI:
                                    writeline = row[0]
                                    for nc in range(1,len(row)):
                                        val = row[nc]
                                        writeline = '%s,%s' % (writeline,val)
                                    a = of.write('%s\n' % writeline)



#os.chdir(r'H:\Shared\Planning and Research\Plan Development Section\Master Plan\2023 Master Plan Update\Modeling\Risk Modeling')

S   = int(sys.argv[1])
G   = int(sys.argv[2])
Y   = int(sys.argv[3])
RI  = int(sys.argv[4])
CB  = int(sys.argv[5])       # 10, 50, 90

build_xyz  = True
build_tif  = True
delete_xyz = False
build_csvs = False

print('processing CLARA outputs for: S%02d G%03d - yr %02d - %02d-th percentile - %0.1f percent AEP' % (S,G,Y,CB,100/RI) )

cbi = {10:5,50:6,90:7}      # column number of CLARA output data file that corresponds to flood depth of confidence bound 10, 50, or 90
dc = cbi[CB]            # column of input file that corresponds to depth at confidence interval assigned in CB

clara_grid_xyz = 'grid/MP2023_CLARA_grid_pt_index_2023_v05.xyz'

clara_outs = 'outputs/depths_ft_g500_for_cpra_2022-03-10.csv'

xyz_outfile =  'outputs/xyz/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_%02d_%02d_CLARA_%0.1f_aep_depths_ft.xyz' % (S,G,Y,Y,100/RI)
tif_outfile =  'outputs/tif/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_%02d_%02d_CLARA_%0.1f_aep_depths_ft.tif' % (S,G,Y,Y,100/RI)

print('reading in output data from %s' % clara_outs)
data = np.genfromtxt(clara_outs,delimiter=',',skip_header=1)

if build_xyz == True:
    print('mapping CLARA outputs to %s' % xyz_outfile )
    pid_val = {}            # initialize empty dictionary where key will be CLARA grid ID, and value will be assigned from output file
    for row in data:
        s   = row[0]
        yr  = row[1]
        pid = row[2]
        ri  = row[3]
        val  = row[dc]
        if s == S:
            if yr == Y:
                if ri == RI:
                        pid_val[pid] = val
    with open(xyz_outfile,mode='w') as xyz_out:
        with open(clara_grid_xyz,mode='r') as xyz_in:
            for row in xyz_in:
                vals = row.split()
                x = float(vals[0])
                y = float(vals[1])
                pid = int(vals[2])
                try:
                    val = pid_val[pid]
                except:
                    val = -9999
                w = xyz_out.write('%s %s %s\n' % (x,y,val) )

if build_tif == True:
    print('converting XYZ output to %s' % tif_outfile)
    gtcmd = ['gdal_translate',xyz_outfile,tif_outfile]
    gtrun = subprocess.call(gtcmd)

if delete_xyz == True:
    print('deleting %s' % xyz_outfile)
    rmcmd = ['rm', xyz_outfile]
    rmcmd = subprocess.call(rmcmd)

if build_csvs ==  True:
    scenarios = []
    years = []
    returns = []

    for row in data:
        s = row[0]
        y = row[1]
        ri = row[3]
    
        if s not in scenarios:
            scenarios.append(s)
        if y not in years:
            years.append(y)
        if ri not in returns:
            returns.append(ri)
        
    for S in scenarios:
        for RI in returns:
            for Y in years:
                outfile = 'outputs/csv/MP2023_S%02d_G500_C000_U00_V00_SLA_O_%02d_%02d_CLARA_%0.1f_aep_depths_ft.csv' % (S,Y,Y,100/RI)
                print('prepping %s' % outfile)
            
                with open(outfile,mode='w') as of:
                    a = of.write('landscape_scenario_id,year,point_id,return_period,depth_10,depth_50,depth_90\n')
                    for row in data:
                        s = row[0]
                        y = row[1]
                        ri = row[3]

                        if s == S:
                            if y == Y:
                                if ri == RI:
                                    writeline = row[0]
                                    for nc in range(1,len(row)):
                                        val = row[nc]
                                        writeline = '%s,%s' % (writeline,val)
                                    a = of.write('%s\n' % writeline)
