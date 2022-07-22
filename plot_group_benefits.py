import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime as dt

ilvf = 'E:/ICM/PDD/mp23_pdd_icm.land_veg_2022.07.21.14.52.17.csv'
perf = 'E:/ICM/PDD/mp23_pdd_icm.ecoregion_definition_2022.07.21.15.38.38.csv'
gpf  = 'E:/ICM/PDD/mp23_group_project_list.csv'

od  = 'E:/ICM/PDD/benefits'

g_fwoa = 500
g2p = [607,608,654]#range(601,654)#[651]
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

unit_conv = 0.000247105      # acres per square meter

print('Reading in project-ecoregion lookup table')
with open(perf,mode='r') as p_e:
    nl = 0
    for line in p_e:
        if nl > 0:
            proj = int(line.split(',')[1])
            er   = line.split(',')[2].strip()
            if proj not in proj_eco.keys():
                proj_eco[proj] = []
            proj_eco[proj].append(er)
        nl += 1

print('Reading in model group-project lookup table')
with open(gpf,mode='r') as g_p:
    nl = 0
    for line in g_p:
        if nl > 0:
            group = int(line.split(',')[0][1:4])
            proj  = int(line.split(',')[1])
            name  = line.split(',')[3]
            if group not in group_proj.keys():
                group_proj[group] = []
            group_proj[group].append(proj)
            proj_name[proj] = name
            
        nl += 1

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

for g in g2p:
    for s in d2p[g].keys():
        for p in group_proj[g]:
            print( 'Accumulating benefits to project footprint S%02d G%03d - Project %d' % (s,g,p) )
            for v in d2p[g][s].keys():
                ben[g][s][v][p] = {}
                d2p[g][s][v][p] = {}
                d2p[g_fwoa][s][v][p] = {}
                for y in d2p[g][s][v]['MRP'].keys():
                    if y not in ben[g][s][v][p].keys():
                        ben[g][s][v][p][y] = 0.0
                        d2p[g][s][v][p][y] = 0.0
                        d2p[g_fwoa][s][v][p][y] = 0.0
                    for e in proj_eco[p]:
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
        
        for e in group_proj[g]:
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
        for e in group_proj[g]:             # if only plotting cumulative project benefits, loop over projects instead of ecoregions
            for y in range(minyr,maxyr+1):
                years_all[s][g][e].append(y-2)
                fwoa_land_all[s][g][e].append( unit_conv*(d2p[g_fwoa][s]['LND'][e][y] + d2p[g_fwoa][s]['BRG'][e][y] + d2p[g_fwoa][s]['FLT'][e][y] ) )
                fwa_land_all[s][g][e].append( unit_conv*(d2p[g][s]['LND'][e][y] + d2p[g][s]['BRG'][e][y] + d2p[g][s]['FLT'][e][y] ) )
                benefit_all[s][g][e].append( unit_conv*(ben[g][s]['LND'][e][y] + ben[g][s]['BRG'][e][y] + ben[g][s]['FLT'][e][y] ) )


# plot land area curves for each project - FWA and FWOA on same graph
for g in g2p:
    for s in d2p[g].keys():
        for e in group_proj[g]:             # if only plotting cumulative project benefits, loop over projects 
            print('Plotting land area curves: S%02d G%03d - %s' % (s,g,e) )
            years     = years_all[s][g][e]
            fwoa_land = fwoa_land_all[s][g][e]
            fwa_land  = fwa_land_all[s][g][e]
            png_pth   = '%s/MP2023_S%02d_G%03d_land_area_%s.png' % (od,s,g,e)
            png_title = 'Land Area - Draft 2023 MP ICM Simulations - S%02d - G%03d - %s' % (s,g,e)
            png_foot = 'Ecoregions in project footprint:'
            for ec in proj_eco[e]:
                png_foot = '%s %s' % (png_foot,ec)
            try:
                png_title = '%s\n%s' % (png_title,proj_name[e])
            except:
                _b = 'not plotting a project - no name to use'
            fig,ax = plt.subplots(figsize=(6,4))
            _a = ax.plot(years,fwoa_land,marker='o',markersize=0,linestyle='solid',linewidth=1,color='black',label='FWOA - G%03d' % g_fwoa)
            _a = ax.plot(years,fwa_land,marker='o',markersize=0,linestyle='solid',linewidth=1,color='red',label='FWA - G%03d' % g)
            _a = ax.tick_params(axis='both', which='major', labelsize='x-small')
            _a = ax.set_xlabel('FWOA Year',fontsize='small')    
            _a = ax.set_ylabel('Land area, acres',fontsize='x-small')
            _a = ax.legend(loc='upper right',edgecolor='none',facecolor='none',fontsize='x-small')
            _a = ax.grid(True,which='both',axis='both',color='silver',linewidth=0.25) 
            _a = ax.set_title(png_title,fontsize='small')
            _a = plt.text(0.05,0.02,png_foot,fontsize=6,transform=plt.gcf().transFigure)
            _a = plt.tight_layout()
            _a = plt.savefig(png_pth,dpi=600)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
            _a = plt.close()

# plot benefits curve for each project - both scenarios on same graph
col = {7:'black',8:'red'}
for g in g2p:
    for e in group_proj[g]:             # if only plotting cumulative project benefits, loop over projects 
        fig,ax = plt.subplots(figsize=(6,4))
        png_pth = '%s/MP2023_G%03d_project_benefits_%s.png' % (od,g,e)
        png_title = 'Project Benefits (FWA-FWOA) - Draft 2023 MP ICM Simulations - G%03d - %s' % (g,e)
        try:
            png_title = '%s\n%s' % (png_title,proj_name[e])
        except:
            _b = 'not plotting a project - no name to use'
        png_foot = 'Ecoregions in project footprint:'
        for ec in proj_eco[e]:
            png_foot = '%s %s' % (png_foot,ec)
            
        for s in d2p[g].keys():
            print('Plotting benefit curves: S%02d G%03d - %s' % (s,g,e) )
            years   = years_all[s][g][e]
            benefit = benefit_all[s][g][e]
            _a      = ax.plot(years,benefit,marker='o',markersize=0,linestyle='solid',linewidth=1,color=col[s],label='S%02d' % s)
        
        _a = ax.tick_params(axis='both', which='major', labelsize='x-small')
        _a = ax.set_xlabel('FWOA Year',fontsize='x-small')
        _a = ax.set_ylabel('Project Benefit (FWA - FWOA), acres',fontsize='x-small')
        ax.legend(loc='upper left',edgecolor='none',facecolor='none',fontsize='x-small')
        _a = ax.grid(True,which='both',axis='both',color='silver',linewidth=0.25) 
        _a = ax.set_title(png_title,fontsize='small')
        _a = plt.text(0.05,0.02,png_foot,fontsize=6,transform=plt.gcf().transFigure)
        _a = plt.tight_layout()        
        _a = plt.savefig(png_pth,dpi=600)                       # 1800 dpi is hi-res but does not quite show each 30-m pixel. Anything higher requires more RAM than default allocations on PSC's RM-shared and RM-small partitions
        _a = plt.close()

        
###############################################################################################
##########          Sample code to get color names from Hex code                     ##########
###############################################################################################
#hex2use = '#FF0000'
#for named_color in matplotlib.colors.get_named_colors_mapping().keys():
#	hex = matplotlib.colors.get_named_colors_mapping()[named_color]
#    if hex == hex2use:
#		color2use = named_color
#
## get RGB values as tuple from named hex
#matplotlib.colors.hex2color(hex2use) 
#        
## get RGBA values as tuple from named color
#matplotlib.colors.to_rgba(color2use)
#
## get RGBA values as an array from named color
#matplotlib.colors.to_rgba_array(color2use)
