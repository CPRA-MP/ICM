#ICM imports
import ICM_Settings as icm

#Python imports
import errno
import numpy as np
import os
import shutil
import sys


#########################################################
##               SET UP ICM-LAVegMod                   ##
#########################################################

def icm_LAVegMod_setup(
                        vegetation_dir,cycle_start_elapsed,cycle_end_elapsed,startyear_cycle,
                        startyear,runprefix,file_prefix_cycle,PerWaterFile,WaveAmplitudeFile,
                        MeanSalinityFile,SummerMeanWaterDepthFile,SummerMeanSalinityFile,
                        SummerMeanTempFile,TreeEstCondFile,AcuteSalFile,HtAbvWaterFile
                       ):

    # change to Veg directory
    os.chdir(vegetation_dir)

    print(' Writing ICM-LAVegMod Configuration file for current cycle for years %02d:%02d'  % (cycle_start_elapsed,cycle_end_elapsed))
    # write csv string of all years included in this LAVegMod run cycle
    yrstr = '%02d' % (cycle_start_elapsed)
    for vy in range(cycle_start_elapsed+1,cycle_end_elapsed+1):
        yrstr = '%s,%02d' % (yrstr,vy)

    # write config file for ICM-LAVegMod given the current years being simulated for model cycle
    # only lines that have dynamic variable names are updated here
    # if not dynamic, original line from lavegmod_proto.config.og will be re-written
    
    
    #TODO Consolidate this section
    #       may be able to remove "dm = " and just use write statements
    #       check if both Height Above Water write statements are needed
    #       check proper value for cycle_start_elapsed from ICM_settings.py
    
    with open('lavegmod_proto.config.og',mode='r') as lvcr:
        with open('lavegmod_proto.config',mode='w') as lvcw:
            for line in lvcr:
                if '=' in line:
                    lvm_var = line.split('=')[0]
                    lvm_val = line.split('=')[1]
                    
                    if lvm_var.strip() == 'StartYear':
                        if startyear_cycle == startyear:
                            dm = lvcw.write('%s= 00\n' % lvm_var )
                        else:
                            dm = lvcw.write('%s= %02d\n' % (lvm_var,cycle_start_elapsed-1) ) # start year should the year which is represented by the initial conditions file
                    
                    elif lvm_var.strip() == 'EndYear':
                        dm = lvcw.write('%s= %02d\n' % (lvm_var,cycle_end_elapsed) )
                    
                    elif lvm_var.strip() == 'NumYears':
                        dm = lvcw.write('%s= %02d\n' % (lvm_var,cycle_end_elapsed-cycle_start_elapsed+1) )
                    
                    elif lvm_var.strip() == 'InitialConditionFile':
                        if startyear_cycle == startyear:
                            dm = lvcw.write(line)
                        else:
                            dm = lvcw.write( '%s= %s_O_%02d_%02d_V_vegty.asc+\n' % (lvm_var,runprefix,cycle_start_elapsed-1,cycle_start_elapsed-1 ) )

                    elif lvm_var.strip() == 'WetlandMorphLandWaterFile':
                        dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,PerWaterFile) )

                    elif lvm_var.strip() == 'WetlandMorphYears':
                        dm = lvcw.write( '%s= %02d:%02d\n' % (lvm_var,cycle_start_elapsed,cycle_end_elapsed) )
                    
                    elif lvm_var.strip() == 'WaveAmplitudeFile':
                        dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,WaveAmplitudeFile) )
                    
                    elif lvm_var.strip() == 'MeanSalinityFile':
                        dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,MeanSalinityFile) )
                    
                    elif lvm_var.strip() == 'SummerMeanWaterDepthFile':
                        dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,SummerMeanWaterDepthFile) )
                    
                    elif lvm_var.strip() == 'SummerMeanSalinityFile':
                        dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,SummerMeanSalinityFile) )
                    
                    elif lvm_var.strip() == 'SummerMeanTempFile':
                        dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,SummerMeanTempFile) )
                    
                    elif lvm_var.strip() == 'TreeEstCondFile':
                        dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,TreeEstCondFile) )

                    elif lvm_var.strip() == 'AcuteSalinityStressFile':
                        dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,AcuteSalFile) )
                    
                    elif lvm_var.strip() == 'BarrierIslandHeightAboveWaterFile':
                        dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,HtAbvWaterFile) )
                    
                    elif lvm_var.strip() == 'HeightAboveWaterFile':
                        dm = lvcw.write( '%s= %s_H_%s\n' % (lvm_var,file_prefix_cycle,HtAbvWaterFile) )

                    elif lvm_var.strip() == 'OutputTemplate':
                        dm = lvcw.write( '%s= %s_O_<YEAR>_<YEAR>_V_vegty.asc+\n' % (lvm_var,runprefix) )
                    
                    elif lvm_var.strip() == 'OutputYears':
                        dm = lvcw.write( '%s= %s\n' % (lvm_var,yrstr) )
                    
                    elif lvm_var.strip() == 'DeadFloatingTemplate':
                        dm = lvcw.write( '%s= %s_O_<YEAR>_<YEAR>_V_deadf.asc\n' % (lvm_var,runprefix) )                    
                    
                    elif lvm_var.strip() == 'DeadFloatingYears':
                        dm = lvcw.write( '%s= %s\n' % (lvm_var,yrstr) )
                    
                    else:           # if line does not include a dynamic field - just re-write the file from the original config file
                        dm = lvcw.write(line)
                else:               # if line does not have an =, it is blank for formatting - re-write the empty line for consistency
                    dm = lvcw.write(line)