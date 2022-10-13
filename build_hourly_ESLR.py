import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mpd
import datetime as dt
import sys

s = int(sys.argv[1])#8
ESLR_column = int(sys.argv[2])#16


folder =        'H:/Shared/Planning and Research/Plan Development Section/Master Plan/2023 Master Plan Update/Modeling'
tidal_file =    'Preprocessed_Data/MP2023_2010_tidal_WSE.csv'
ESLR_file  =    'Scenarios/SL Data Aug 2021/SL_Interpolated Hourly_Considered and Comparison_10272021.csv'



file2write =    '%s/Preprocessed_Data/Scenario_ESLR/S%02d_TideData.csv' % (folder,s)
png2write =     '%s/Preprocessed_Data/Scenario_ESLR/S%02d_TideData.png' % (folder,s)

# read in hourly tidal data for a given year
print('reading in hourly tidal data for representative year from %s'  % tidal_file)
tidal = np.genfromtxt('%s/%s' % (folder,tidal_file), skip_header = 1, delimiter=',',dtype=str)
tidal_mdh = {}

for row in tidal:
    timedate =  row[1]
    data =      row[2:]
    md =        timedate[4:8]               # MMDD
    h =         timedate[9:11]              # HH
    mdh = '%s%s' % (md,h)

    tidal_mdh[mdh] = data
    

# check if given year has leap day data, if not, repeat Feb 28 for leap day
print('checking for leap day data')
if '022901' not in tidal_mdh.keys():
    for h in range(0,25):
        mdh = '0229%02d' % h
        mdh2fill = '0228%02d' % h
        try:            # using try/except here to cover cases for both midnight as 00:00 and 24:00
            tidal_mdh[mdh] = tidal_mdh[mdh2fill]
        except:
            _ = 'mdh2fill not in tidal_mdh'
        
# read in 50 year timeseries ESLR curves
print('reading in ESLR curves')
eslr = np.genfromtxt('%s/%s' % (folder,ESLR_file), skip_header = 1, delimiter=',',usecols=[0,ESLR_column],dtype=str)
ESLRyr50 = float(eslr[-1][1])

tide2plot = []
eslr2plot = []
dates2plot = []
nhours = 0
startday = dt.datetime.strptime(eslr[0][0],'%m/%d/%Y %H:%M')

print('writing output file: %s' % file2write)
with open(file2write,mode='w') as outfile:
    outfile.write('ESLR=%0.2fm by 2070 - Date Time,ICM Tide Gage 1 - NOAA 8735180 Dauphin Island Mobile Bay AL (adjusted by x amplify),ICM Tide Gage 2 - NOAA 8760922 Pilots Station East Southwest Pass LA,ICM Tide Gage 3 - NOAA 8761724 Grand Isle LA,ICM Tide Gage 4 - USGS 073813498 Caillou Bay LA-zwRev,ICM Tide Gage 5 - NOAA 8768094 Calcasieu Pass LA,ICM Tide Gage 6 - NOAA 8770570 Sabine Pass TX\n' % ESLRyr50)
    for row in eslr:
        nhours += 1
        timedate = row[0]
        m = int(timedate.split('/')[0])
        d = int(timedate.split('/')[1])
        y = int(timedate.split('/')[2].split(' ')[0])
        h = int(timedate.split(' ')[1].split(':')[0])
        mdh = '%02d%02d%02d' % (m,d,h)
        eslr_val = float(row[1])
    
        tidal_data = tidal_mdh[mdh]
        line2write = '%04d%02d%02d %02d:00:00' % (y,m,d,h)

        for gage_val in tidal_data:
            mwl =  float(gage_val) + eslr_val
            line2write = '%s,%0.6f' % (line2write,mwl)
            
        outfile.write('%s\n' % line2write)
        
        
        tide2plot.append( float(tidal_data[4]) + eslr_val )
        eslr2plot.append( eslr_val )


print('reading in historic water levels for plotting')
obs_file   =    '%s/Model Improvements/Model Inputs/Datasets/tidal/MP2023_NOAA_8768094_CalcasieuPass_20200521.csv' % folder
observed = np.genfromtxt(obs_file,skip_header = 3,delimiter=',',usecols=[3,4,-4],dtype=str)
obs_dates = []
obs_tide2plot = []
for row in observed:
    datetime = '%s %s' % (row[0],row[1])
    wsel = float(row[2])
    obs_dates.append(dt.datetime.strptime(datetime,'%m/%d/%Y %H:%M'))
    obs_tide2plot.append(wsel)


print('plotting output file: %s' % png2write)        
png_title = 'ICM Tide Gage 5 - NOAA 8768094 Calcasieu Pass LA - S%02d Tidal Boundary' % (s)


dates2plot = mpd.date2num([startday + dt.timedelta(hours=x) for x in range(0, nhours)])# matplotlib date object
obs_dates2plot = mpd.date2num(obs_dates)
fig,ax = plt.subplots(figsize=(12,4))
_a = ax.plot_date(obs_dates2plot,obs_tide2plot,marker='o',markersize=0,linestyle='solid',linewidth=0.25,color='black',label='Observed Tidal Levels - Calcasieu Pass - NOAA 8768094 - 8.6 mm/yr subsidence removed from signal')
_a = ax.plot_date(dates2plot,tide2plot,marker='o',markersize=0,linestyle='solid',linewidth=0.25,color='grey',label='S%02d Future Scenario Tidal Boundary' % s)
_a = ax.plot_date(dates2plot,eslr2plot,marker='o',markersize=0,linestyle='solid',linewidth=2,color='red',label='S%02d Assumed ESLR' % s)
_a = ax.tick_params(axis='both', which='major', labelsize='x-small')
_a = ax.set_ylim([-1,2])
_a = ax.set_xlabel('Year',fontsize='small')    
_a = ax.set_ylabel('Water Level, m NAVD88',fontsize='x-small')
_a = ax.legend(loc='upper left',edgecolor='none',facecolor='none',fontsize='x-small')
_a = ax.grid(True,which='both',axis='both',color='silver',linewidth=0.25) 
_a = ax.set_title(png_title,fontsize='small')
_a = plt.tight_layout()
_a = plt.savefig(png2write)#,dpi=600)
_a = plt.close()