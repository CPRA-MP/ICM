import os
os.chdir('D:/nov20/adcirc_bcdataForICM_20201102/IPETrainfall')
with open('rainfall_intensity_mm_hr.csv',mode='w') as wf:
    hdr = 'storm,15min_dt'
    for stn in range(1,428):
        hdr = '%s,stn_%04d' % (hdr,stn)
    a=wf.write('%s\n' % hdr)

    for imed in os.listdir():
        if imed.endswith('total.imeds'):
            a = 'skip'
        else:
            if imed.endswith('.imeds'):
                sr = {}
                storm = imed.split('_')[3]
                print('storm:  %s' % storm)
                with open(imed,mode='r') as rf:
                    for line in rf:
                        if line.startswith('HEADER'):
                            a = 'skip'
                        else:
                            if line.startswith('Station'):
                                stn = line.split()[0].split('_')[1]
                                sr[stn] = []
                                print('  station:  %s' % stn)
                            else:
                                sr[stn].append(line.split()[-1])
                for t in range(0,len(sr[stn])):
                    wr = '%s,%s' % (storm,t)
                    for s in range(1,427):
                        val = sr['%s' % s][t]
                        wr = '%s,%s' % (wr,val)
                        a = wf.write('%s\n' % wr)




import os
import netCDF4 as nc
from netCDF4 import Dataset

os.chdir('D:/nov20/adcirc_bcdataForICM_20201102')

nc = Dataset('storm_0038_icm_wse.nc','r')

all_t = []
for t in nc['time_station_0001']:
    all_t.append(t)

# check that all data stations have the same number of timesteps
for s in range(1,428):
    ts = 'time_station_%04d' % s
    n = 0
    for t in nc[ts]:
        n += 1
    if n != len(all_t):
        print('%s has %s timesteps, not the %s that it should!' % (s,n,len(all_t)))

with open('wse.csv',mode='w') as wf:
    hdr = 'storm,elapsed_time_min'
    for stn in range(1,428):
        hdr = '%s,stn_%04d' % (hdr,stn)
    a=wf.write('%s\n' % hdr)

    for ncf in os.listdir():
        if ncf.endswith('wse.nc'):
            nc = Dataset(ncf)
            strm = ncf.split('_')[1]
            print('storm: %s' % strm)
            
            all_t = []
            for t in nc['time_station_0001']:
                all_t.append(t)
            print('  - timesteps: %s' % len(all_t))
            
            t_s_w = {}
            for t in all_t:
                ti = '%d' % t.data
                t_s_w[ti] = []
        
            for s in range(1,428):
                print('   - station: %04d' % s)
                ts = 'time_station_%04d' % s
                ds = 'data_station_%04d' % s
                for i in range(0,len(all_t)):
                    t = '%d' %  nc[ts][i].data
                    ws = '%s' % nc[ds][i].data
                    t_s_w[t].append(ws)

            for t in t_s_w.keys():
                t_elap = (float(t) - float(all_t[0]))/60
                wr = '%s,%s' % (strm,t_elap)
                for sws in t_s_w[t]:
                    wr = '%s,%s' % (wr,sws)
                a=wf.write('%s\n' % wr)



#nc.variables:
#'stationName'
#'time_station_0162'
#'data_station_0162'
