#Python imports
import subprocess

#ICM imports


def RunSAV(year, sterm, gterm, sav_submit_exe_path):
    try:
        snum = '%s' % int(sterm[1:])
        gnum = '%s' % int(gterm[1:])
        cmdstr = ['python',sav_submit_exe_path,snum,gnum,'%s' % year] 
        subprocess.call(cmdstr)
    except:
        print(' !! Failed to submit SAV for %s' % year)