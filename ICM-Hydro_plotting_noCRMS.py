import os
import sys
import math
import numpy as np
import datetime as dt
import matplotlib as mp
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mpd

#########################################################################
#          set parameters for this run                                  #
#########################################################################
scn = 'S07'
grp = 'G500 (FWOA)'
file_pre = 'MP2023_S07_G500_C000_U00_V00_SLA_N_01_52_H_'   # prefix for run from file naming convention
hydro_file_pre = ''
start_day = dt.date(2019,1,1)
spinup_years = 2        # number of spinup years included in run - used to calculate elapsed years for plotting (spinup years will be negative)
plot_as_dates = False   # use calendar dates if set to true - otherwise x-axis will be set to elapsed years
ICM_Hydro_dir = r'/ocean/projects/bcs200002p/ewhite12/ICM/S07/G503/hydro'
plot_dir = r'%s/timeseries' % ICM_Hydro_dir
html_dir = r'%s/html' % plot_dir
png_dir = r'%s/png' % plot_dir
links_file = r'%s/TempFiles/Links_2019.csv' % ICM_Hydro_dir
comp_LW_update_file = r'%s/comp_LW_update.csv' % ICM_Hydro_dir


#data type codes to plot
# STG = daily mean stage
#'SAL' = daily mean salinity
#'TRG' = daily mean tidal range
#'TSS' = daily mean total suspended sediment

types = ['STG','SAL','TRG','TSS']
y_labels = ['Daily Mean Stage (m, NAVD88)','Daily Mean Salinity (ppt)','Daily Mean Tidal Range (m)','Daily mean TSS (mg/L)']


###########################################################################
# read in links.csv and develop compartment-link-compartment dictionaries #
###########################################################################
all_links = []  # array to store all link IDs
all_comps = []  # array to store all compartment IDs
link_types = {} # dictionary to store links as keys with linktype as values
link_comps = {} # dictionary to store links as keys with upstream and downstream compartments as values
comp_links = {} # dictionary to store compartments as keys with all links connected to compartment as values

with open(links_file,mode='r') as lf:
    nl = 0
    for line in lf:
        if nl > 0:
            linesplit = line.split(',')
            link = int(linesplit[0])
            USc = int(linesplit[1])
            DSc = int(linesplit[2])
            lnktyp = int(linesplit[7])
            
            link_types[link] = lnktyp
            link_comps[link] = [USc,DSc]

            try:
                comp_links[USc].append(link)
            except:
                comp_links[USc] = [link]
                
            try:
                comp_links[DSc].append(link)
            except:
                comp_links[DSc] = [link]
            
            if link not in all_links:
                all_links.append(link)
            if USc not in all_comps:
                all_comps.append(USc)
            if DSc not in all_comps:
                all_comps.append(DSc)
            
        nl += 1

#######################################################
# read in ICM_LW_update.csv and set compartment flags #
#######################################################
comp_flags = {}
with open(comp_LW_update_file,mode='r') as lf:
    nl = 0
    for line in lf:
        if nl > 0:
            linesplit = line.split(',')
            compID = int(linesplit[0])
            comptype = linesplit[1]
            if comptype == 'upland areas; non-wetland':
                comp_flags[compID] = 1
            elif comptype == 'modeled as 1D reach':
                comp_flags[compID] = 2 
            else:
                comp_flags[compID] = 0
        nl += 1  

for nt in range(0,len(types)):
    out_type = types[nt]
    y_txt = y_labels[nt]


    if os.path.exists (plot_dir) == False:
        os.mkdir(plot_dir)
    if os.path.exists (html_dir) == False:
        os.mkdir(html_dir)
    if os.path.exists (png_dir) == False:
        os.mkdir(png_dir)
    if os.path.exists (r'%s/%s' % (png_dir,out_type)) == False:
        os.mkdir(r'%s/%s' % (png_dir,out_type))
    
    # read in model output data
    h_out_file = r'%s/%s%s.out' % (ICM_Hydro_dir,hydro_file_pre,out_type)
    print(' reading in %s' % h_out_file)
    h_out = np.genfromtxt(h_out_file,skip_header=0,delimiter=',')
    ndays, ncomps = h_out.shape
    
    model_dates = [start_day + dt.timedelta(days=x) for x in range(0, ndays)]
    model_dates_plt = mpd.date2num(model_dates) # matplotlib date object
    elapsed_years = []

    for d in model_dates:
        doy = d.timetuple().tm_yday     # convert dt.date to a timetuple that is day-of-year
        if d.year in range(2000,4000,4):
            diy = 366.0
        else:
            diy = 365.0
        elapsed_years.append( (doy/diy)-spinup_years+d.year - start_day.year )
    
    if ndays/365 <= 2:      # if data is no more than 2 years in length put tick marks at months and labels every year
        dtick = 1./12.
        dlabel = 1
    elif ndays/365 < 10:    # if data is more than 2 years but less than 10 put tick marks at quarters and labels every year
        dtick = 0.25
        dlabel = 1
    else:                   # if data is more than 10 years, put tick marks every year & labels every 5 years
        dtick = 1
        dlabel = 5
        
    x_axis_ticks = np.arange( 0-spinup_years,math.ceil(elapsed_years[-1]), dtick )
    x_axis_labels = [0-spinup_years]
    for ey in np.arange( 0,math.ceil(elapsed_years[-1])+1, dlabel):
        x_axis_labels.append(ey)
    x_range = [0-spinup_years, math.ceil(elapsed_years[-1])+1]
    
    nc = 0
    for c in range(0,ncomps):
        nc += 1
        comp = c+1
        print(r' compartment %04d - %d/%d - %0.1f%%' %(comp,nc,ncomps,100*nc/ncomps))
    
        png_fname = '%s_comp%04d_%s.png' % (file_pre,comp,out_type)
        png_fpath = r'%s/%s/%s' % (png_dir,out_type,png_fname)
        
        model_label = 'ICM-Hydro comp %04d - %s - %s' % (comp, scn, grp)
        model_vals = []
        for d in range(0,ndays):
            model_vals.append(float(h_out[d][c]))
        
    
        fig = plt.figure(figsize=(20,4))
        ax = fig.add_subplot(111,facecolor='whitesmoke')
        
        if plot_as_dates == True:
            # plot model data as calendar date on x-axis
            ax.plot_date(model_dates_plt,model_vals,marker='o',markersize=0,linestyle='solid',linewidth=1,color='black',label=model_label)
            # format X-axis
            x_range = [model_dates[0],model_dates[-1]]
            ax.set_xlim(x_range)
            ax.xaxis.set_major_locator(mpd.YearLocator())
            if ndays/365 <= 2:      # if data is no more than 2 years in length put tick marks at months
                ax.xaxis.set_minor_locator(mpd.MonthLocator())
                ax.xaxis.set_major_formatter(mpd.DateFormatter('%Y'))
            elif ndays/365 < 10:    # if data is more than 2 years but less than 10 put tick marks at quarters
                ax.xaxis.set_minor_locator(mpd.MonthLocator((1,4,7,10)))
                ax.xaxis.set_major_formatter(mpd.DateFormatter('%Y'))
            else:
                ax.xaxis.set_major_formatter(mpd.DateFormatter('%y'))
            x_txt = r'Year'
        else:
            # plot model data as elapsed years
            ax.plot(elapsed_years,model_vals,marker='o',markersize=0,linestyle='solid',linewidth=1,color='black',label=model_label)
            ax.set_xlim(x_range)
            ax.xaxis.set_major_locator(ticker.FixedLocator(x_axis_labels))
            ax.xaxis.set_minor_locator(ticker.FixedLocator(x_axis_ticks))
            ax.xaxis.grid(True, which='major')
            x_txt = r'Model Year'

        # format X-axis
        ax.set_xlabel(x_txt)    
    
        # format Y-axis
        if out_type == 'SAL':
            y_range = [0.,36.]
        else:
            y_range = [math.floor(min(model_vals)),math.ceil(max(model_vals))]
        
        ax.set_ylim(y_range)
        
        ax.set_ylabel(y_txt)
        
        
    
        # add legend
        ax.legend(loc='upper right',edgecolor='none',facecolor='whitesmoke')
    
        # add grid 
        ax.grid(True,which='major',axis='both',color='silver',linewidth=0.5) 
        if out_type == 'STG':
              ax.axhline(0, color='black',linewidth=0.5) # horizontal lines at 0 
        
        # add watermark text
        if comp_flags[comp] == 1:
            comp_flag_text = 'Compartment is upland tributary area for water volume only - DO NOT USE DATA'
        elif comp_flags[comp] == 2:
            comp_flag_text = 'Compartment is modeled with the 1D reach code - DO NOT USE THIS DATA - REFER TO 1D OUTPUT TIMESERIES'
        else:
            comp_flag_text = '-9999'
        
        if comp_flag_text != '-9999':
            ax.text(0.5, 0.5, comp_flag_text, verticalalignment='center', horizontalalignment='center', transform=ax.transAxes, color='red', size='large',weight='heavy',bbox={'facecolor': 'white', 'pad': 2})
        
        plt.savefig(png_fpath)
        plt.close() 


    #############################################################################################################
    # build html pages for each compartment with stage and salinity plots and links to neighboring compartments #
    #############################################################################################################
for c in range(0,ncomps):
    comp = c+1
    html_fname = 'ICM-Hydro_comp%04d.html' % comp # this must match html writing script lower that maps to connected compartments
    html_file = r'%s/%s' % (html_dir,html_fname)

    with open(html_file,mode='w') as hf:
        hf.write('<html>')
        hf.write(' <head>')
        hf.write('   <p style ="font-size:24;font-style:;font-weight:bold" align="center">%s - %s<br>Compartment %04d</p>' % (scn,grp,comp))
        hf.write(' </head>')
        hf.write(' <body>')
        hf.write(' <p><img src="..\png\STG\ICM-Hydro_comp%04d_STG.png" " align ="top"> <img src="..\png\TRG\ICM-Hydro_comp%04d_TRG.png" align ="top"></p>' % (comp,comp))
        hf.write(' <p><img src="..\png\SAL\ICM-Hydro_comp%04d_SAL.png" " align ="top"> <img src="..\png\TSS\ICM-Hydro_comp%04d_TSS.png" align ="top"></p>' % (comp,comp))
        hf.write(' <p style ="font-size:18;font-style:;font-weight:bold" align="left">Next Sequential ICM-Hydro Compartments:</p>')
        
        if comp != 1:
            hf.write('<a href="..\html\ICM-Hydro_comp%04d.html"> Previous: Compartment %04d </a>  <br>' % (comp-1,comp-1)) 
        else:
            hf.write(' <a> Previous: n/a </a>  <br>' )
        if comp != ncomps:
            hf.write(' <a href="..\html\ICM-Hydro_comp%04d.html"> Next: Compartment %04d </a>  <br>' % (comp+1,comp+1))
        else:
            hf.write(' <a> Next: n/a </a>  <br>' )
        hf.write(' <p style ="font-size:18;font-style:;font-weight:bold" align="left">Neighboring ICM-Hydro Compartments:</p>')
        try:
            for link in comp_links[comp]:           # loop through all  links connecting to compartment
                for cnct_comp in link_comps[link]:  # find compartments that are connected via link
                    if cnct_comp != comp:           # link will have two compartments - one that is current compartment and one that is the connected compartment
                        if link_types[link] < 0:
                            link_inactive = ' - Link is deactivated (LinkType<0)'
                        else:
                            link_inactive = ''
                        hf.write(' <a href="..\html\ICM-Hydro_comp%04d.html"> Compartment %04d via Link %04d %s</a>  <br>' % (cnct_comp,cnct_comp,link,link_inactive))
        except:
            _ = 'no links for compartment'
        hf.write(' </body>')  
        hf.write('</html>')
        
 
