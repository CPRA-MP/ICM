import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axisartist.axislines import Axes
from matplotlib.pyplot import gca
import matplotlib.ticker as mtick
import matplotlib.font_manager as font_manager

from datetime import datetime as dt

ilvf = 'E:/ICM/PDD/mp23_pdd_icm.land_veg_2022.11.30.09.58.30.csv'#mp23_pdd_icm.land_veg_2022.09.28.17.48.05.csv'
#perf = 'E:/ICM/PDD/mp23_pdd_icm.ecoregion_definition_2022.09.06.csv'
#gpf  = 'E:/ICM/PDD/mp23_group_project_list.csv'

od  = 'E:/ICM/PDD/benefits/regional'

g_fwoa = 514                                    #500
fwoa_label = 'FWOA'                            #'FWOA'
g2p = [516] #range(690,691)#range(685,690)        #range(655,684)     #range(601,654)
#g_in_IP2 = range(690,691)#range(685,690)   #range(655,684)     #[]

IP2_start = 22
s2p = [7,8]
g2pa = [g_fwoa]
for g in g2p:
    g2pa.append(g)

d2p = {}
dates = {}
proj_eco = {}
group_proj = {}
proj_name = {}

for s in s2p:
    dates[s] = {}
    for g in g2p:
        dates[s][g] = '2022-05-21 18:03:10.466196'

dates[7] = {500:dt.strptime('2022-03-24 11:40:33.841920','%Y-%m-%d %H:%M:%S.%f')}#,608:'2022-03-07 14:20:18.767414'}
dates[8] = {500:dt.strptime('2022-03-24 11:40:33.841920','%Y-%m-%d %H:%M:%S.%f')}#,608:'2022-02-14 22:34:23.855443'}

#units,unit_conv = 'ACRES',0.000247105         # acres per square meter
units,unit_conv = 'SQ MI',0.00000038610216   # sq miles per square meter



print('Reading in output PDD data')
with open(ilvf,mode='r') as ilv:
    nl = 0
    for line in ilv:
        if nl > 0:
            ls = line.split(',')
            g = int(ls[1])
            s = int(ls[2])
            y = int(ls[3])
            v = ls[4]
            e = ls[5]
            a = float(ls[6])
            d = dt.strptime(ls[7],'%Y-%m-%d %H:%M:%S.%f')
            if g in g2pa:
                if s in s2p:
                    if g not in d2p.keys():
                        d2p[g] = {}
                    if s not in d2p[g].keys():
                        d2p[g][s] = {}
                    if v not in d2p[g][s].keys():
                        d2p[g][s][v] = {}
                    if e not in d2p[g][s][v].keys():
                        d2p[g][s][v][e] = {}    
                    if y not in d2p[g][s][v][e].keys():
                        if g == 500:
                            if d == dates[s][g]:
                                d2p[g][s][v][e][y] = a
                        else:
                            if d > dt.strptime('2022-05-20','%Y-%m-%d'):
                                d2p[g][s][v][e][y] = a
        nl += 1


ben = {}
for g in g2p:
    ben[g] = {}
    for s in d2p[g].keys():
        print( 'Calculating benefits for S%02d G%03d' % (s,g) )
        ben[g][s] = {}
        for v in d2p[g][s].keys():
            ben[g][s][v] = {}
            for e in d2p[g][s][v].keys():
                ben[g][s][v][e] = {}
                for y in d2p[g][s][v][e].keys():
                    ben[g][s][v][e][y] = d2p[g][s][v][e][y] - d2p[g_fwoa][s][v][e][y]

regions = {}
regions['CHENIER PLAIN']    = ['SAB','CAL','CHR','MEL']
regions['CENTRAL COAST']    = ['TVB','ATD']
regions['TERREBONNE']       = ['VRT','PEN','WTE','ETB']
regions['BARATARIA']        = ['UBA','MBA','LBAnw','LBAne','LBAsw','LBAse']
regions['PONTCH-BRETON']    = ['MRP','LPO','CHS','UBR','LBR','BFD']

for g in g2p:
    for s in d2p[g].keys():
        for p in regions:
            print( 'Accumulating benefits to project footprint S%02d G%03d - %s' % (s,g,p) )
            for v in d2p[g][s].keys():
                ben[g][s][v][p] = {}
                d2p[g][s][v][p] = {}
                d2p[g_fwoa][s][v][p] = {}
                for y in d2p[g][s][v]['MRP'].keys():
                    if y not in ben[g][s][v][p].keys():
                        ben[g][s][v][p][y] = 0.0
                        d2p[g][s][v][p][y] = 0.0
                        d2p[g_fwoa][s][v][p][y] = 0.0
                    for e in regions[p]:
                        ben[g][s][v][p][y] += ben[g][s][v][e][y]
                        d2p[g][s][v][p][y] += d2p[g][s][v][e][y]
                        d2p[g_fwoa][s][v][p][y] += d2p[g_fwoa][s][v][e][y]

for g in g2p:
    for s in d2p[g].keys():
        print( 'Accumulating benefits to coastwide (SLA) for S%02d G%03d' % (s,g) )
        for v in d2p[g][s].keys():
            ben[g][s][v]['SLA'] = {}
            d2p[g][s][v]['SLA'] = {}
            d2p[g_fwoa][s][v]['SLA'] = {}
            for e in d2p[g][s][v].keys():
                for y in d2p[g][s][v][e].keys():
                    if y not in ben[g][s][v]['SLA'].keys():
                        ben[g][s][v]['SLA'][y] = 0.0
                        d2p[g][s][v]['SLA'][y] = 0.0
                        d2p[g_fwoa][s][v]['SLA'][y] = 0.0
                    ben[g][s][v]['SLA'][y] += ben[g][s][v][e][y]
                    d2p[g][s][v]['SLA'][y] += d2p[g][s][v][e][y]
                    d2p[g_fwoa][s][v]['SLA'][y] += d2p[g_fwoa][s][v][e][y]

years_all     = {}
fwoa_land_all = {}
fwa_land_all  = {}
benefit_all   = {}

for s in s2p:
    years_all[s]        = {}
    fwoa_land_all[s]    = {}
    fwa_land_all[s]     = {}
    benefit_all[s]      = {}

for g in g2p:
    for s in d2p[g].keys():
        years_all[s][g]     = {}
        fwoa_land_all[s][g] = {}
        fwa_land_all[s][g]  = {}
        benefit_all[s][g]   = {}
        
        for e in regions.keys():
            years_all[s][g][e]       = []
            fwoa_land_all[s][g][e]   = []
            fwa_land_all[s][g][e]    = []
            benefit_all[s][g][e]     = []
                    
for g in g2p:
    for s in d2p[g].keys():
        print('Prepping ecoregion benefit curves for plotting: S%02d G%03d' % (s,g) )
        minyr = min( d2p[g][s]['LND']['MRP'].keys() )
        maxyr = max( d2p[g][s]['LND']['MRP'].keys() )
        #for e in d2p[g][s]['LND'].keys():   # if looping over ecoregions, this will include project and coastwide cumulative benefit values
        for e in regions:             # if only plotting cumulative project benefits, loop over projects instead of ecoregions
            for y in range(minyr,maxyr+1):
                years_all[s][g][e].append(y-2)
                fwoa_land_all[s][g][e].append( unit_conv*(d2p[g_fwoa][s]['LND'][e][y] + d2p[g_fwoa][s]['BRG'][e][y] + d2p[g_fwoa][s]['FLT'][e][y] ) )
                fwa_land_all[s][g][e].append( unit_conv*(d2p[g][s]['LND'][e][y] + d2p[g][s]['BRG'][e][y] + d2p[g][s]['FLT'][e][y] ) )
                benefit_all[s][g][e].append( unit_conv*(ben[g][s]['LND'][e][y] + ben[g][s]['BRG'][e][y] + ben[g][s]['FLT'][e][y] ) )


#####################################
# PLOTTING SYMBOLOGY                #
#####################################
# FWOA Low Scenario:    #0BA7A0 dotted  - Predict default (RGB 11 167 160) - dotted line
# FWOA High Scenario:   #006B66 dotted  - Predict dark (RGB 0 107 102) - dotted line
# FWA Low Scenario:     #9FCC3B solid   - Take Action default (RGB 159 204 59) - solid line
# FWA High Scenario:    #5E8021 solid   - RGB:  94 128 33 Take Action dark (RGB 159 204 59) - solid line

# assign color, linetype, and labels
s_g_col = {}
s_g_col[7] = {514:'#0BA7A0',516:'#96CC3B'}
s_g_col[8] = {514:'#006B66',516:'#5E8021'}

s_g_lty = {}
s_g_lty[7] = {514:'dotted',516:'solid'}
s_g_lty[8] = {514:'dotted',516:'solid'}

s_g_lab = {}
s_g_lab[7] = {514:'FWOA Lower\nScenario',516:'FWMP Lower\nScenario'}
s_g_lab[8] = {514:'FWOA Higher\nScenario',516:'FWMP Higher\nScenario'}




# plot land area curves for each project - FWA and FWOA on same graph
for g in g2p:
    for e in regions.keys():             # if only plotting cumulative project benefits, loop over projects 
        print('Plotting land area curves: S%02d G%03d - %s' % (s,g,e) )
        
        plt.figure(figsize=(3.27,1.8))
        ax = plt.subplot(111)
        # add horizontal grid - with thick line at y=0
        # this needs to be before ax.plot() so that the horizontal grid at y=0 is below data
        ax.grid(True,which='major',axis='y',color='#e0e0db',linewidth=0.15)
        ax.axhline(y=0,color='#e0e0db',linewidth=0.5)
    

        png_pth   = '%s/MP2023_G%03d_land_area_%s.png' % (od,g,e)
        png_title = 'LAND AREA - %s' % (e)

        png_foot = 'Ecoregions in region:'
        for ec in regions[e]:
            png_foot = '%s %s' % (png_foot,ec)
        try:
            png_title = '%s\n%s' % (png_title,proj_name[e])
        except:
            _b = 'not plotting a project - no name to use'

        for s in d2p[g].keys():
            years     = years_all[s][g][e]
            fwoa_land = fwoa_land_all[s][g][e]
            fwa_land  = fwa_land_all[s][g][e]


            ax.plot(years,fwoa_land,marker='o',markersize=0,linestyle=s_g_lty[s][g_fwoa],linewidth=1,color=s_g_col[s][g_fwoa],label=s_g_lab[s][g_fwoa] )
            ax.plot(years,fwa_land,marker='o',markersize=0,linestyle=s_g_lty[s][g],linewidth=1,color=s_g_col[s][g],label=s_g_lab[s][g] )


        legend_font = font_manager.FontProperties(family='Franklin Gothic Book', size=6)
        ax.legend(loc='bottom left',edgecolor='none',facecolor='none',ncol=2,prop=legend_font)

        # format axes
        #a = gca()
        ax.tick_params(axis='both', which='major',length=0,labelsize=6)

        # vertical axis
        gca().set_yticklabels(gca().get_yticks(),fontname='Franklin Gothic Book',fontsize=6,color='#8e8e8e')
        ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
        ax.set_ylabel('LAND AREA, %s' % units, fontname='Franklin Gothic Demi', fontsize=6, color='#000000')
        ax.spines['left'].set_color('#e0e0db')

        # horizontal axis
        gca().set_xticklabels(gca().get_yticks(),fontname='Franklin Gothic Book',fontsize=6,color='#8e8e8e')
        ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
        ax.set_xlabel('FWOA YEAR',fontname='Franklin Gothic Demi',fontsize=6,color='#000000')
        ax.spines['bottom'].set_color('#e0e0db')
    
        # remove top and right axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.set_title(png_title,fontname='Franklin Gothic Demi',fontsize=10,loc='left')
        #_a = plt.text(0.05,0.0,png_foot,fontname='Franklin Gothic Demi',fontsize=6,transform=plt.gcf().transFigure)
        plt.tight_layout()        
        plt.savefig(png_pth,dpi=600)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
        plt.close()
            



# plot benefits curve for each project - both scenarios on same graph

for g in g2p:
    for e in regions:
        plt.figure(figsize=(3.27,1.8))
        ax = plt.subplot(111)
        # add horizontal grid - with thick line at y=0
        # this needs to be before ax.plot() so that the horizontal grid at y=0 is below data
        ax.grid(True,which='major',axis='y',color='#e0e0db',linewidth=0.15)
        ax.axhline(y=0,color='#e0e0db',linewidth=0.5)
        
        png_pth = '%s/MP2023_G%03d_project_benefits_%s.png' % (od,g,e)
        png_title = 'MASTER PLAN BENEFITS - %s' % (e)
        try:
            png_title = '%s\n%s' % (png_title,proj_name[e])
        except:
            _b = 'not plotting a project - no name to use'
        
        png_foot = ''            

        for s in d2p[g].keys():
            print('Plotting benefit curves: S%02d G%03d - %s' % (s,g,e) )
            years   = years_all[s][g][e]
            benefit = benefit_all[s][g][e]
            png_foot = '%sLand area built/maintained under S%02d @ year %02d: %0.2f %s;  year %02d: %0.2f %s.\n' % (png_foot,s,years[21],benefit[21],units,years[-1],benefit[-1],units)
            ax.plot(years,benefit,marker='o',markersize=0,linestyle=s_g_lty[s][g],linewidth=1,color=s_g_col[s][g],label=s_g_lab[s][g])

        legend_font = font_manager.FontProperties(family='Franklin Gothic Book', size=6)
        ax.legend(loc='upper left',edgecolor='none',facecolor='none',ncol=2,prop=legend_font)

        # format axes
        #a = gca()
        ax.tick_params(axis='both', which='major',length=0,labelsize=6)

        # vertical axis
        gca().set_yticklabels(gca().get_yticks(),fontname='Franklin Gothic Book',fontsize=6,color='#8e8e8e')
        ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
        ax.set_ylabel('PROJECT BENEFIT (FWA-%s), %s' % (fwoa_label,units),fontname='Franklin Gothic Demi', fontsize=6, color='#000000')
        ax.spines['left'].set_color('#e0e0db')

        # horizontal axis
        gca().set_xticklabels(gca().get_yticks(),fontname='Franklin Gothic Book',fontsize=6,color='#8e8e8e')
        ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
        ax.set_xlabel('FWOA YEAR',fontname='Franklin Gothic Demi',fontsize=6,color='#000000')
        ax.spines['bottom'].set_color('#e0e0db')
        
        # remove top and right axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.set_title(png_title,fontname='Franklin Gothic Demi',fontsize=10,loc='left')
        #_a = plt.text(0.05,0.0,png_foot,fontname='Franklin Gothic Demi',fontsize=6,transform=plt.gcf().transFigure)
        plt.tight_layout()        
        plt.savefig(png_pth,dpi=600)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
        plt.close()
            
