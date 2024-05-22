#Python imports
import os
import sys

#ICM imports
import ICM_Settings as icm


def RunLAVegMod(year, vegetation_dir, startyear, elapsed_hotstart, 
                VegConfigFile
                ):

    #########################################################
    ##                RUN VEGETATION MODEL                 ##
    #########################################################
    os.chdir(vegetation_dir)

    #TODO assuming that model_v3 exists and will be available 
    import model_v3

    if year == startyear + elapsed_hotstart:
        print ('\n--------------------------------------------------')
        print ('        CONFIGURING VEGETATION MODEL')
        print ('----------------------------------------------------')
        sys.path.append(vegetation_dir)

        LAVegMod = model_v3.Model()
        veg_config = LAVegMod.config(VegConfigFile)


    veg_run = LAVegMod.step()