import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axisartist.axislines import Axes
from matplotlib.pyplot import gca
import matplotlib.ticker as mtick
import matplotlib.font_manager as font_manager

from datetime import datetime as dt

ilvf = 'E:/ICM/PDD/benefits/PT_project_data/pt_mv_restoration_project_benefit_G521.csv'
#perf = 'E:/ICM/PDD/mp23_pdd_icm.ecoregion_definition_2022.09.06.csv'
#gpf  = 'E:/ICM/PDD/mp23_group_project_list.csv'

od  = 'E:/ICM/PDD/benefits/PT_project_data'

g_fwoa = 520                                    #500
fwoa_label = 'FWOA'                            #'FWOA'
g2p = [521] #range(690,691)#range(685,690)        #range(655,684)     #range(601,654)
#g_in_IP2 = range(690,691)#range(685,690)   #range(655,684)     #[]


s2p = [7,8]
g2pa = g2p

#for g in g2p:
#    g2pa.append(g)

if len(s2p) == 1:
    tag = 'MP2023_S%02d' % s2p[0]
else:
    tag = 'MP2023'

d2p = {}
proj_eco = {}
group_proj = {}
proj_name = {}
projects = []

#units,unit_conv = 'ACRES',0.000247105         # acres per square meter
units,unit_conv = 'SQ MI',0.00000038610216   # sq miles per square meter



print('Reading in output PDD data')
with open(ilvf,mode='r') as ilv:
    nl = 0
    for line in ilv:
        if nl > 0:
            ls = line.split(',')
            prj = int(ls[0])
            g = int(ls[2])
            s = int(ls[8])
            y = int(ls[9])
            #v = ls[4]
            #e = ls[5]
            a = float(ls[10].strip().strip('"'))
            #d = dt.strptime(ls[7],'%Y-%m-%d %H:%M:%S.%f')
            if g in g2pa:
                if s in s2p:
                    if g not in d2p.keys():
                        d2p[g] = {}
                    if s not in d2p[g].keys():
                        d2p[g][s] = {}
                    if prj not in d2p[g][s].keys():
                        d2p[g][s][prj] = {}
                        projects.append(prj)
                    if y not in d2p[g][s][prj].keys():
                        d2p[g][s][prj][y] = a
        nl += 1

benefit_all   = d2p

#####################################
# PLOTTING SYMBOLOGY                #
#####################################
# FWOA Low Scenario:    #0BA7A0 dotted  - Predict default (RGB 11 167 160) - dotted line
# FWOA High Scenario:   #006B66 dotted  - Predict dark (RGB 0 107 102) - dotted line
# FWA Low Scenario:     #9FCC3B solid   - Take Action default (RGB 159 204 59) - solid line
# FWA High Scenario:    #5E8021 solid   - RGB:  94 128 33 Take Action dark (RGB 159 204 59) - solid line

# assign color, linetype, and labels
s_g_col = {}
s_g_col[7] = {514:'#0BA7A0',516:'#96CC3B',520:'#0BA7A0',521:'#96CC3B'}
s_g_col[8] = {514:'#006B66',516:'#5E8021',520:'#006B66',521:'#5E8021'}

s_g_lty = {}
s_g_lty[7] = {514:'dotted',516:'solid',520:'dotted',521:'solid'}
s_g_lty[8] = {514:'dotted',516:'solid',520:'dotted',521:'solid'}

s_g_lab = {}
s_g_lab[7] = {514:'FWOA Lower\nScenario',516:'FWMP Lower\nScenario',520:'FWOA Lower\nScenario',521:'FWMP Lower\nScenario'}
s_g_lab[8] = {514:'FWOA Lower\nScenario',516:'FWMP Lower\nScenario',520:'FWOA Lower\nScenario',521:'FWMP Lower\nScenario'}




# plot benefits curve for each project - both scenarios on same graph

for g in g2p:
    for p in projects:
        plt.figure(figsize=(3.27,1.8))
        ax = plt.subplot(111)
        # add horizontal grid - with thick line at y=0
        # this needs to be before ax.plot() so that the horizontal grid at y=0 is below data
        ax.grid(True,which='major',axis='y',color='#e0e0db',linewidth=0.15)
        ax.axhline(y=0,color='#e0e0db',linewidth=0.5)
        
        png_pth = '%s/%s_G%03d_project_benefits_%s.png' % (od,tag,g,p)
        png_title = 'PROJECT %s' % (p)
       
#        try:
#            png_title = '%s\n%s' % (png_title,proj_name[p])
#        except:
#            _b = 'not plotting a project - no name to use'
        
        png_foot = ''            

        for s in d2p[g].keys():
            print('Plotting benefit curves: S%02d G%03d - %s' % (s,g,p) )
            years   = benefit_all[g][s][p].keys()
            benefit = []
            for y in years:
                benefit.append(benefit_all[g][s][p][y]*unit_conv)
            #png_foot = '%sLand area built/maintained under S%02d @ year %02d: %0.2f %s;  year %02d: %0.2f %s.\n' % (png_foot,s,years[41],benefit[41],units,years[-1],benefit[-1],units)
            ax.plot(years,benefit,marker='o',markersize=0,linestyle=s_g_lty[s][g],linewidth=1,color=s_g_col[s][g],label=s_g_lab[s][g])

        legend_font = font_manager.FontProperties(family='Franklin Gothic Book', size=6)
        ax.legend(loc='lower center',edgecolor='none',facecolor='none',ncol=2,prop=legend_font)

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
        _a = plt.text(0.05,-0.02,png_foot,fontname='Franklin Gothic Book',fontsize=4,transform=plt.gcf().transFigure)
        plt.tight_layout()        
        plt.savefig(png_pth,dpi=600)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
        plt.close()
        print(png_foot)
            
