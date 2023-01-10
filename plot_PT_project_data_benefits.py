import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axisartist.axislines import Axes
from matplotlib.pyplot import gca
import matplotlib.ticker as mtick
import matplotlib.font_manager as font_manager

from datetime import datetime as dt
datestr = dt.now()

labels = False       # if set to True, the plots will have title, legend, and axes titles - if set to False, none of these will be included

ilvf = 'E:/ICM/PDD/benefits/PT_project_data/pt_mv_restoration_project_benefit_G521.csv'
#perf = 'E:/ICM/PDD/mp23_pdd_icm.ecoregion_definition_2022.09.06.csv'
#gpf  = 'E:/ICM/PDD/mp23_group_project_list.csv'

od  = 'E:/ICM/PDD/benefits/PT_project_data'
output_summary_file = '%s/PT_project_data_for_factsheets.csv' % od

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
imp_yr = {}

units,unit_conv = 'ACRES',0.000247105         # acres per square meter
#units,unit_conv = 'SQ MI',0.00000038610216   # sq miles per square meter



print('Reading in output PDD data')
with open(ilvf,mode='r') as ilv:
    nl = 0
    for line in ilv:
        if nl > 0:
            ls = line.split(',')
            prj = int(ls[0])
            g = int(ls[2])
            iy = int(ls[3])
            s = int(ls[8])
            y = int(ls[9])
            #v = ls[4]
            #e = ls[5]
            a = float(ls[10].strip().strip('"'))
            #d = dt.strptime(ls[7],'%Y-%m-%d %H:%M:%S.%f')

            # import yearly benefit data for each Group/Scenario/Project
            if g in g2pa:
                if s in s2p:
                    if g not in d2p.keys():
                        d2p[g] = {}
                    if s not in d2p[g].keys():
                        d2p[g][s] = {}
                    if prj not in d2p[g][s].keys():
                        d2p[g][s][prj] = {}
                    if prj not in projects:
                        projects.append(prj)
                    if y not in d2p[g][s][prj].keys():
                        d2p[g][s][prj][y] = a

        # save implementation year of project
            if prj not in imp_yr.keys():
                imp_yr[prj] = iy
                
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
s_g_lab[8] = {514:'FWOA Higher\nScenario',516:'FWMP Higher\nScenario',520:'FWOA Higher\nScenario',521:'FWMP Higher\nScenario'}


with open(output_summary_file,mode='w') as sumfile:
    sumfile.write('ModelGroup,Scenario,ProjectID,MaxAnnualBenefit_acre,MinAnnualBenefit_acre,CumulativeBenefit_acreyears,YearsPositiveBenefit,YearsNegativeBenefit,ImplementationYear,Date,Note\n')

    # plot benefits curve for each project - both scenarios on same graph
    for g in g2p:
        for p in projects:
            plt.figure(figsize=(3.27,1.8))
            ax = plt.subplot(111)
            # add horizontal grid - with thick line at y=0
            # this needs to be before ax.plot() so that the horizontal grid at y=0 is below data
            ax.grid(True,which='major',axis='y',color='#e0e0db',linewidth=0.15)
            ax.axhline(y=0,color='#e0e0db',linewidth=0.5)
            if labels == True:
                unit_tag = ''
            else:
                unit_tag = '%s_' % units
            png_pth = '%s/%s_G%03d_project_benefits_%s%s.png' % (od,tag,g,unit_tag,p)
            png_title = 'PROJECT %s' % (p)
           
    #        try:
    #            png_title = '%s\n%s' % (png_title,proj_name[p])
    #        except:
    #            _b = 'not plotting a project - no name to use'
            
            png_foot = ''            
            warning = ''
            
            for s in d2p[g].keys():
                print('Plotting benefit curves: S%02d G%03d - %s' % (s,g,p) )
                years   = range(1,51)#benefit_all[g][s][p].keys()

                first_year  = min(benefit_all[g][s][p].keys())
                if first_year > imp_yr[p]:
                    warning = 'PT data start year %d != implementation year %d ' % (first_year,imp_yr[p]) 
                    print('WARNING: %s' % warning)
                
                benefit = []
                neg_yrs = 0
                pos_yrs = 0
                nil_yrs = 0
                max_ben = 0
                min_ben = 0
                cum_ben = 0
                
                for y in years:
                    
                    if y >= first_year:#imp_yr[p]:
                        try:
                            benefit_i = benefit_all[g][s][p][y]*unit_conv
                        except:
                            benefit_i = 0.0
                            warning = '%s; missing data for yr %d' % (warning,y)
                        benefit.append(benefit_i)

                        cum_ben += benefit_i
                        # count years with negative benefits
                        if benefit_i < 0:
                            neg_yrs += 1
                        # count years with positive benefits
                        elif benefit_i > 0:
                            pos_yrs += 1
                        # count years(post implementation) with zero benefit
                        else:
                            nil_yrs += 1
                        # save yearly maximum benefit
                        if benefit_i > max_ben:
                            max_ben = benefit_i
                        # save yearly minimum benefit
                        if benefit_i < min_ben:         
                            min_ben = benefit_i
                    else:
                        benefit.append(0.0)
                    
                #png_foot = '%sLand area built/maintained under S%02d @ year %02d: %0.2f %s;  year %02d: %0.2f %s.\n' % (png_foot,s,years[41],benefit[41],units,years[-1],benefit[-1],units)
                ax.plot(years,benefit,marker='o',markersize=0,linestyle=s_g_lty[s][g],linewidth=1,color=s_g_col[s][g],label=s_g_lab[s][g])

                note = warning
                write_string = '%d,%d,%d,%0.0f,%0.0f,%0.0f,%d,%d,%d,%s,%s\n' % (g,s,p,max_ben,min_ben,cum_ben,pos_yrs,neg_yrs,imp_yr[p],datestr,note)
                sumfile.write(write_string)

            legend_font = font_manager.FontProperties(family='Franklin Gothic Book', size=6)
            if labels == True:
                ax.legend(loc='best',edgecolor='none',facecolor='none',ncol=2,prop=legend_font)

            # format axes
            #a = gca()
            ax.tick_params(axis='both', which='major',length=0,labelsize=6)

            # vertical axis
            gca().set_yticklabels(gca().get_yticks(),fontname='Franklin Gothic Book',fontsize=6,color='#8e8e8e')
            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
            if labels == True:
                ax.set_ylabel('PROJECT BENEFIT (FWA-%s), %s' % (fwoa_label,units),fontname='Franklin Gothic Demi', fontsize=6, color='#000000')
            ax.spines['left'].set_color('#e0e0db')

            # horizontal axis
            gca().set_xticklabels(gca().get_yticks(),fontname='Franklin Gothic Book',fontsize=6,color='#8e8e8e')
            ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%d'))
            if labels == True:
                ax.set_xlabel('FWOA YEAR',fontname='Franklin Gothic Demi',fontsize=6,color='#000000')
            ax.spines['bottom'].set_color('#e0e0db')
            
            # remove top and right axes
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            if labels == True:
                ax.set_title(png_title,fontname='Franklin Gothic Demi',fontsize=10,loc='left')
            _a = plt.text(0.05,-0.02,png_foot,fontname='Franklin Gothic Book',fontsize=4,transform=plt.gcf().transFigure)
            plt.tight_layout()        
            plt.savefig(png_pth,dpi=600)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
            plt.close()
            print(png_foot)
            

            
