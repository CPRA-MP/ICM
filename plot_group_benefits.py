import numpy as np
import matplotlib.pyplot as plt

ilvf = 'C:/Users/EricPad/Desktop/may_2022/mp23_pdd_icm.land_veg_2022.03.24.11.44.32.csv'
od  = 'C:/Users/EricPad/Desktop/may_2022/te110'

g_fwoa = 500
g2p = [608]
s2p = [7,8]
g2pa = [g_fwoa]+g2p
d2p = {}

dates = {}
dates[7] = {500:'2022-03-24 11:40:33.841920',608:'2022-03-07 14:20:18.767414'}
dates[8] = {500:'2022-03-24 11:40:33.841920',608:'2022-02-14 22:34:23.855443'}
    
unit_conv = 0.000247105      # acres per square meter

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
            d = ls[7]
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
                        if d == dates[s][g]:
                            d2p[g][s][v][e][y] = a
        nl += 1

ben = {}
for g in g2p:
    ben[g] = {}
    for s in d2p[g].keys():
        ben[g][s] = {}
        for v in d2p[g][s].keys():
            ben[g][s][v] = {}
            for e in d2p[g][s][v].keys():
                ben[g][s][v][e] = {}
                for y in d2p[g][s][v][e].keys():
                    ben[g][s][v][e][y] = d2p[g][s][v][e][y] - d2p[g_fwoa][s][v][e][y]
                    
for g in g2p:
    for s in d2p[g].keys():
        miny = min( d2p[g][s]['LND']['MRP'].keys() )
        maxy = max( d2p[g][s]['LND']['MRP'].keys() )
        for e in d2p[g][s]['LND'].keys():
            years       = []
            fwoa_land   = []
            fwa_land    = []
            benefit     = []
            for y in range(miny,maxy+1):
                years.append(y-2)
                fwoa_land.append( unit_conv*(d2p[g_fwoa][s]['LND'][e][y] + d2p[g_fwoa][s]['BRG'][e][y] + d2p[g_fwoa][s]['FLT'][e][y] ) )
                fwa_land.append( unit_conv*(d2p[g][s]['LND'][e][y] + d2p[g][s]['BRG'][e][y] + d2p[g][s]['FLT'][e][y] ) )
                benefit.append( unit_conv*(ben[g][s]['LND'][e][y] + ben[g][s]['BRG'][e][y] + ben[g][s]['FLT'][e][y] ) )
        
        # plot FWA and FWOA on same graph
            png_pth = '%s/MP2023_S%02d_G%03d_land_area_%s.png' % (od,s,g,e)
            png_title = 'Land Area - Draft 2023 MP ICM Simulations - S%02d - G%03d - %s' % (s,g,e)
            fig,ax = plt.subplots(figsize=(6,4))
            ax.plot(years,fwoa_land,marker='o',markersize=0,linestyle='solid',linewidth=1,color='black',label='FWOA - G%03d' % g_fwoa)
            ax.plot(years,fwa_land,marker='o',markersize=0,linestyle='solid',linewidth=1,color='red',label='FWA - G%03d' % g)
            ax.tick_params(axis='both', which='major', labelsize='x-small')
            ax.set_xlabel('FWOA Year',fontsize='small')    
            ax.set_ylabel('Land area in ecoregion, acres',fontsize='x-small')
            ax.legend(loc='upper right',edgecolor='none',facecolor='none')
            ax.grid(True,which='both',axis='both',color='silver',linewidth=0.25) 
            ax.set_title(png_title,fontsize='small')              
            plt.savefig(png_pth,dpi=600)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
            plt.close()
            
        # plot benefits curve    
            png_pth = '%s/MP2023_S%02d_G%03d_project_benefits_%s.png' % (od,s,g,e)
            png_title = 'Project Benefits - Draft 2023 MP ICM Simulations - S%02d - G%03d - %s' % (s,g,e)
            fig,ax = plt.subplots(figsize=(6,4))
            ax.plot(years,benefit,marker='o',markersize=0,linestyle='solid',linewidth=1,color='red',label='FWA - FWOA (benefit)')
            ax.tick_params(axis='both', which='major', labelsize='x-small')
            ax.set_xlabel('FWOA Year',fontsize='x-small')
            ax.set_ylabel('Project Benefit (FWA - FWOA), acres',fontsize='x-small')
            #ax.legend(loc='upper right',edgecolor='none',facecolor='none')
            ax.grid(True,which='both',axis='both',color='silver',linewidth=0.25) 
            ax.set_title(png_title,fontsize='small')              
            plt.savefig(png_pth,dpi=600)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
            plt.close()
            
                            
# ModelGroup,Scenario,Year_ICM,VegetationCode,Ecoregion,Area_m2,Date,Year_FWOA,Note