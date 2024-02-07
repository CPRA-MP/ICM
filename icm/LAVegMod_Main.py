#ICM imports
import ICM_Settings as icm

#Python imports
import os
import sys

def RunLAVegMod(year):

    #########################################################
    ##                RUN VEGETATION MODEL                 ##
    #########################################################
    os.chdir(vegetation_dir)

    if year == startyear + elapsed_hotstart:
        print ('\n--------------------------------------------------')
        print ('        CONFIGURING VEGETATION MODEL')
        print ('----------------------------------------------------')
        sys.path.append(vegetation_dir)
        #TODO assuming that model_v3 exists and will be available 
        import model_v3
        LAVegMod = model_v3.Model()
        veg_config = LAVegMod.config(VegConfigFile)


    veg_run = LAVegMod.step()