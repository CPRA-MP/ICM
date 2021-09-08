import matplotlib.pyplot as plt
import numpy as np

outdir = r'C:\Eric\git\ICM'
data_file = r'C:\Eric\git\ICM\ICM_output_to_PT_20161202_G300_land_veg.csv'

data_in = np.genfromtxt(data_file,skip_header=1,delimiter=',',dtype='str')

print(' - reading in data from %s' % data_file)

# columns in ecoregion output tables formatted for PT:
#   Project number
#   Scenario
#   Year
#   Ecoregion
#   Variable type code
#   Area of variable in ecoregion (sq. meters)

# variable type codes in ecoregion output tables formatted for PT:
#   LND = land
#   WAT = water
#   BLH = bottomland hardwood forest
#   SWA = swamp forest
#   FRM = fresh marsh - attached
#   INM = intermediate marsh
#   BMH = brackish marsh
#   SAM = saline marsh 
#   UPL = upland/developed
#   BRG = bareground
#   FLT = flotant fresh marsh

# Read ecoregion summary data tables into nested dictionaries of timeseries arrays
# keys for nested dictionaries are:
#   P = project number
#   S = scenario
#   E = ecoregion
#   H = habitat type
#   each PSEH combination will have a value that is a timeseries array

years = []
PSEHts = {}

for row in data_in:
    prj = row[0]
    s = row[1]
    yr = int(row[2])
    hab = row[3]
    eco = row[4]
    area = float(row[5])
    
    
    # build new nested dictionaries if a new project, scenario, ecoregion, or habitat type is found
    # the year and timeseries arrays will be ordered by the order of the input file...if not chronological in the input file, these arrays will be out of order
    # can fix this by adding one more layer to the dictionary that uses year as one more key...but this will complicate plotting functions below  
    # ignore for now since all PT formatted files are chronologically structured
    
    # append year to timeseries dt array
    if yr not in years:
        years.append(yr)
    
    if prj not in PSEHts.keys():
        PSEHts[prj] = {}
    
    if s not in PSEHts[prj].keys():
        PSEHts[prj][s] = {}
    
    if eco not in PSEHts[prj][s].keys():
        PSEHts[prj][s][eco] = {}
    
    if hab not in PSEHts[prj][s][eco].keys():
        PSEHts[prj][s][eco][hab] = []
    
    PSEHts[prj][s][eco][hab].append(area)

for S in ['S01','S04','S03']:
    for P in ['G300_FWOA_v3']:
        ecoregions = PSEHts[P][S].keys()
        for er in ecoregions:
            print(' - plotting %s %s %s' % (S,P,er) )

            #saline marsh
            bar0 = PSEHts[P][S][er]['SAM']
            legtxt0 = 'Saline marsh'
            col0 = 'red'
            
            #brackish
            bar1 = PSEHts[P][S][er]['BMH']
            legtxt1 = 'Brackish marsh'
            col1 = 'orange'
            
            #inter
            bar2 = PSEHts[P][S][er]['INM']
            legtxt2 = 'Intermediate marsh'
            col2 = 'yellow'
            
            #fresh
            bar3 = PSEHts[P][S][er]['FRM']
            legtxt3 = 'Fresh marsh - attached'
            col3 = 'limegreen'
            
            #flotant
            bar4 = np.array(PSEHts[P][S][er]['FRM'])-np.array(PSEHts[P][S][er]['FRM']) #placeholder for floating marsh - currently setting to zero
            legtxt4 = 'Fresh marsh - floating'
            col4 = 'plum'
            
            #swamp forest
            bar5 = PSEHts[P][S][er]['SWA']
            legtxt5 = 'Swamp forest'
            col5 = 'forestgreen'
            
            #bottomland hardwood forest
            bar6 = PSEHts[P][S][er]['BLH']
            legtxt6 = 'Bottomland hardwood forest'
            col6 = 'darkolivegreen'
            
            #bareground
            bar7 = PSEHts[P][S][er]['BRG']
            legtxt7 = 'Unvegetated bareground'
            col7 = 'tan'
            
            #upland/notmod
            bar8 = PSEHts[P][S][er]['UPL']
            legtxt8 = 'Upland or developed'
            col8 = 'lightgrey'
            
            #calculate vertical offset for each variable in a stacked barplot
            bot1 = np.array(bar0)
            bot2 = np.array(bot1) + np.array(bar1)
            bot3 = np.array(bot2) + np.array(bar2)
            bot4 = np.array(bot3) + np.array(bar3)
            bot5 = np.array(bot4) + np.array(bar4)
            bot6 = np.array(bot5) + np.array(bar5)
            bot7 = np.array(bot6) + np.array(bar6)
            bot8 = np.array(bot7) + np.array(bar7)
            
            #set column width
            wid = 4
            

            pbar0 = plt.bar(years,bar0,width=wid,label=legtxt0,color=col0)
            pbar1 = plt.bar(years,bar1,width=wid,label=legtxt1,color=col1, bottom=bot1)
            pbar2 = plt.bar(years,bar2,width=wid,label=legtxt2,color=col2, bottom=bot2)
            pbar3 = plt.bar(years,bar3,width=wid,label=legtxt3,color=col3, bottom=bot3)
            pbar4 = plt.bar(years,bar4,width=wid,label=legtxt4,color=col4, bottom=bot4)
            pbar5 = plt.bar(years,bar5,width=wid,label=legtxt5,color=col5, bottom=bot5)
            pbar6 = plt.bar(years,bar6,width=wid,label=legtxt6,color=col6, bottom=bot6)
            pbar7 = plt.bar(years,bar7,width=wid,label=legtxt7,color=col7, bottom=bot7)
            pbar8 = plt.bar(years,bar8,width=wid,label=legtxt8,color=col8, bottom=bot8)
            
            #set axes and chart titles
            x_txt = 'Year'
            y_txt = 'Habitat Coverage, sq. meters'
            title_txt = 'Habitat Coverage:  %s - %s - %s' % (S,P,er)
            
            plt.legend(ncol=3,fontsize='small',bbox_to_anchor=(0.5,-0.2), loc='upper center', borderaxespad=0.00)
            plt.ylabel(y_txt)
            plt.xlabel(x_txt)
            plt.title(title_txt)
            plt.tight_layout()
            
            plt.savefig(r'%s\%s_%s_habitat_timeseries_%s.png' % (outdir,S,P,er) ) 
            plt.close()