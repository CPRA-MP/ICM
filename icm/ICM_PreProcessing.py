#ICM imports
import ICM_Settings as icm

#Python imports


def ICMyearlyVars(year):
        ## calculate elapsed years of model run
    elapsedyear = year - startyear + 1

    ## assign number of days in each month and length of year
    dom = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

    if year in range(1984,4000,4):
        print(r' Current model year (%s) is a leap year - input timeseries must include leap day' % year)
        ndays = 366
        dom[2] = 29
    else:
        ndays = 365
        dom[2] = 28

    # set year-specific file name prefixes
    file_prefix     = r'%s_N_%02d_%02d' % (runprefix,elapsedyear,elapsedyear)
    file_iprefix    = r'%s_I_%02d_%02d' % (runprefix,elapsedyear,elapsedyear)
    file_oprefix    = r'%s_O_%02d_%02d' % (runprefix,elapsedyear,elapsedyear)
    file_prefix_prv = r'%s_N_%02d_%02d' % (runprefix,elapsedyear-1,elapsedyear-1)

#TODO
    return()

    