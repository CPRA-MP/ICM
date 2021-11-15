from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pkg_resources as pr


scens2update = [7,8]    # [0]
groups2update = [500]       # [0]
years2update = range(1,53)  # [2018]

codes2update = ['LND','WAT','FLT','FOR','FRM','INM','BRM','SAM','BRG','UPL']
eco2update = ['ATD','BFD','CAL','CHR','CHS','ETB','LBAne','LBAnw','LBAse','LBAsw','LBO','LBR','LPO','MBA','MEL','MRP','PEN','SAB','TVB','UBA','UBR','UVR','VRT','WTE','EBbi','WBbi','TEbi']
eco2bi ={ 'CHSbi':'EBbi','LBRbi':'EBbi', 'LBAnebi':'WBbi','LBAsebi':'WBbi','LBAswbi':'WBbi','ETBbi':'TEbi','WTEbi':'TEbi' }
eco3skip = ['ATB']

eco2plot = eco2update
codes2plot = {}
codes2plot['FOR'] = [ 51/255,   100/255,      0/255,1]
codes2plot['FRM'] = [102/255,   204/255,      0/255,1]
codes2plot['INM'] = [255/255,   255/255,      0/255,1]
codes2plot['BRM'] = [255/255,   160/255,      0/255,1]
codes2plot['SAM'] = [255/255,     0/255,      0/255,1]
codes2plot['BRG'] = [175/255,   140/255,      0/255,1]
codes2plot['FLT'] = [255/255,    198/255,    255/255,1]
codes2plot['UPL'] = [128/255,   128/255,    128/255,1]
codes2plot['WAT'] = [  0/255,     0/255,    255/255,1]

plotOrder = ['SAM','BRM','INM','FRM','FOR','FLT','BRG','UPL']#,'WAT']

years2plot = []
for y in years2update:
    if y <= 2:
        years2plot.append(y-3)
    else:
        years2plot.append(y-2)


d = {}
for S in scens2update:
    d[S] = {}
    for G in groups2update:
        d[S][G] = {}
        for Y in years2update:
            d[S][G][Y] = {}
            for C in codes2update:
                d[S][G][Y][C] = {}
                for E in eco2update:
                    d[S][G][Y][C][E] = 0
             

# land_veg columns [data format]:
#       ModelGroup [%03d]
#       Scenario [%02d]
#       Year_ICM [%d]
#       VegetationCode [%s - max length of 3]
#       Ecoregion [%s]
#       Area_m2 [%d or %f]
#       Date [%s (MM-DD-YYYY )]
#       Year_FWOA [%d]
#       Note [%s]

datestr = dt.now()

for S in scens2update:
    for G in groups2update:
        if G == 0:
            lvfile =  'MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_00_00_land_veg.csv' % (S,G)
        else:
            lvfile = './S%02d/G%03d/geomorph/output/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_01_52_land_veg.csv' % (S,G,S,G)
           # lvfile = 'MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_01_52_land_veg.csv' % (S,G)
        print('\nreading output data from: %s' % lvfile)
        with open(lvfile,mode='r') as lvf:
            badrows = []
            nrb = 0
            nr = 0
            for r in lvf:   # 'prj_no', 'S', 'ICMyear', 'code', 'ecoregion', 'value'
                nr += 1
                try:
                    g = int(r.split(',')[0].strip()[1:4])
                    s = int(r.split(',')[1].strip()[1:3])
                    y = int(r.split(',')[2].strip())
                    c = r.split(',')[3].strip()
                    e = r.split(',')[4].strip()
                    v = float(r.split(',')[5].strip())
                    if e in eco2bi.keys():
                        er = eco2bi[e]
                    else:
                        er = e
                    if er in eco2update:
                        if s == S:
                            if g == G:
                                if c in codes2update:
                                    d[s][g][y][c][er] += v
                except:
                    nrb += 1
                    badrows.append(nr)
            if nrb > 0:
                print(' Failed to parse %d rows in %s. Check lines:' % (nrb,lvfile))
                print(badrows)



for S in scens2update:
    for G in groups2update:
        veg_dir = r'./S%02d/G%03d/veg' % (S,G)
        outdir = '%s/coverage_timeseries/ecoregion' % veg_dir
        spinup_years = 2
        for E in eco2plot:
            print('plotting ecoregion outputs for: S%02d G%03d %s' % (S,G,E))
            png_file = '%s/MP2023_S%02d_G%03d_C000_U00_V00_%s_O_01_52_V_vgtyp.png' % (outdir,S,G,E)
            #png_file = 'MP2023_S%02d_G%03d_C000_U00_V00_%s_O_02_52_V_vgtyp.png' % (S,G,E)
            x_txt = 'FWOA Year'
            y_txt = 'Area (sq km)'
            title = 'Land cover by habitat type for ecoregion: %s - Run: S%02d G%03d' % (E,S,G)

            fig, ax = plt.subplots()
            bot_array = np.zeros([len(years2update)])
            for C in plotOrder:
                array2plot = []
                for Y in years2update:
                    array2plot.append( d[S][G][Y][C][E]/(1000**2) )     # convert from square meters to square km

                ax.bar( years2plot,array2plot,width=0.75,bottom=bot_array,color=codes2plot[C],label=C )
                bot_array = bot_array + np.array(array2plot)


            
            plt.legend(ncol=round((len(plotOrder)+1)/2),fontsize='small',bbox_to_anchor=(0.5,-0.15), loc='upper center', borderaxespad=0.00,frameon=False)
            plt.xlabel(x_txt)   
            plt.ylabel(y_txt)
            plt.title(title)

            plt.axvline(x=0,linewidth=0.75,color='black')

            plt_v = pr.get_distribution('matplotlib').version.split('.')
            if int(plt_v[0]) >= 3:
                if int(plt_v[1]) >= 1:
                    plt_secondary = True
                else:
                    plt_secondary = False
            
            if plt_secondary == True:
                def sqkm_to_acre1K(x):
                    return x*0.247105381467
    
                def acre1K_to_sqkm(x):
                    return x/4.0468564224

                secax_y = ax.secondary_yaxis('right', functions=(sqkm_to_acre1K, acre1K_to_sqkm))
                secax_y.set_ylabel('Area (1000 acres)',rotation=270,labelpad=12.0)


            plt.savefig(png_file,bbox_inches='tight')
                
                
            plt.close()
            
