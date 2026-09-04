import shutil
import os
import zipfile


par = 'G:/Recovery Drive 4 - Good Data/ICM_simulations'
parz = 'G:/MP17_archive'
os.chdir(par)
logfile = '%s/MP17_archive.log'



Gs = os.listdir(par)

for g in Gs:
    if g[0] == 'G':
        for s in ['S01','S03','S04']:
            sub = '%s/%s/%s' % (g,s,g)

            dirs2zip = []
            dirs2zip.append('land_area_timeseries')
            dirs2zip.append('QAQC_output')
            dirs2zip.append('ewe/EwEOutput/AreaAveraged')
            dirs2zip.append('geomorph/WM_StaticData.gdb')
            for y in range(1,51):
                dirs2zip.append('geomorph/output_%02d' % y )
                dirs2zip.append('geomorph/MPM2017_%s_%s_C000_U00_V00_SLA_I_%02d_%02d_W_initc.gdb' % (s,g,y,y) )
            dirs2zip.append('hydro/output_timeseries')


            files2zip = []
            for bi in ['ST73124','ST73126','ST73129','ST73131','ST73139','ST73141']:
                for y in range(1,51):
                    files2zip.append('bimode/%s/profile%04d' % (bi,y) )
            files2zip.append('ICM.py')
            files2zip.append('ICM_control.csv')
            files2zip.append('geomorph/input_params.csv')
            files2zip.append('geomorph/WM.py')
            files2zip.append('geomorph/EH_Area_Outside_LWextent.csv')
            files2zip.append('geomorph/Veg_Reclass.csv')
            files2zip.append('veg/MPM2017_%s_%s_C000_U00_V00_SLA_O_01_50_V_vegty.asc+' % (s,g))
            files2zip.append('veg/lavegmod_proto.config')


            # build empty directory trees to hold zipped archives
            for bi in ['ST73124','ST73126','ST73129','ST73131','ST73139','ST73141']:
                os.makedirs('%s/%s/bimode/%s' % (parz,sub,bi),exist_ok=True )
            os.makedirs('%s/%s/ewe'% (parz,sub),exist_ok=True )
            os.makedirs('%s/%s/geomorph'% (parz,sub),exist_ok=True )
            os.makedirs('%s/%s/hydro'% (parz,sub),exist_ok=True )
            os.makedirs('%s/%s/veg'% (parz,sub),exist_ok=True )
                
            for f2z in files2zip:
                print('archiving %s' % f2z)
                try:
                    zip_success = 0  
                    orig = '%s/%s/%s' % (par,sub,f2z)
                    arc = '%s/%s/%s.zip' % (parz,sub,f2z)
                    with zipfile.ZipFile(arc,mode='w',compression=zipfile.ZIP_STORED) as farc:
                        farc.write(orig)
                    zip_success = 1  
                    if zip_success = 1:
                        try:
                            del_success = 0
                            os.remove(orig)
                            del_success = 1
                        except:
                            del_success = 0
                except:
                    zip_success = 0

                with open(logfile,mode='a') as log:
                    log.write('%s,%s,%d,%d\n' % (orig,arc,zip_success,del_success)

            for d2z in dirs2zip:
                print('archiving %s' % d2z)
                try:
                    zip_success = 0 
                    orig = '%s/%s/%s' % (par,sub,d2z)
                    arc = '%s/%s/%s' % (parz,sub,d2z)
                    shutil.make_archive(arc,'zip',orig)
                    zip_success = 1  
                    if zip_success = 1:
                        try:
                            del_success = 0
                            shutil.rmtree(orig)
                            del_success = 1
                        except:
                            del_success = 0
                except:
                    zip_success = 0
                with open(logfile,mode='a') as log:
                    log.write('%s,%s,%d,%d\n' % (orig,arc,zip_success,del_success)
