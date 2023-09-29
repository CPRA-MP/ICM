import os
import sys
import numpy as np
import datetime as dt
import matplotlib as mp
import matplotlib.pyplot as plt
import matplotlib.dates as mpd

#########################################################################
#          set parameters for this run                                  #
#########################################################################
comp_CRMS_LDEQ_map = r'E:\ICM\calibration_run_files\final\CRMS_LDEQ_ICM_compartment_map.csv'
CRMS_dir = r'E:\CRMS_2006-2019\clean_daily'
LDEQ_dir = r'E:\MP2023\MP2023_observed_data_noCRMS\MP2023_Water_Quality_Data'

scn = 'Hindcast (S00)'
grp = 'Cal-Val (G000)'
file_pre = ''   # prefix for run from file naming convention
start_day = dt.date(2006,1,1)
ICM_Hydro_dir = r'E:\ICM\calibration_run_files\final'
plot_dir = r'%s\plots' % ICM_Hydro_dir
html_dir = r'%s\html' % plot_dir
png_dir = r'%s\png' % plot_dir

types = ['STG','SAL','TRG','TSS']

sources = ['CRMS','CRMS','CRMS','LDEQ']
date_cols = [1,1,1,0]
data_cols = [8,5,(10,11),2]
unit_convs = [0.3048,1,1,1]
units = ['m','ppt','m','mg/L']
y_labels = ['Daily Mean Stage (m, NAVD88)','Daily Mean Salinity (ppt)','Daily Mean Tidal Range (m)','Daily mean TSS (mg/L)']
y_ranges = [ -9999,[0, 36],[0,1.0],-9999 ]

#data type codes
# STG = daily mean stage
#'SAL' = daily mean salinity
#'TRG' = daily mean tidal range
#'TSS' = daily mean total suspended sediment

#CRMS_data_columns: 
#  0 = stationID
#  1 = Date_mm/dd/yyyy
#  2 = mean_salinity_ppt
#  3 = median_salinity_ppt
#  4 = min_salinity_ppt
#  5 = max_salinity_ppt
#  6 = stdev_salinity_ppt
#  7 = ncount_salinity
#  8 = mean_stage_ftNAVD88
#  9 = median_stage_ftNAVD88
# 10 = min_stage_ftNAVD88
# 11 = max_stage_ftNAVD88
# 12 = stdev_stage_ftNAVD88
# 13 = ncount_stage_ftNAVD88

#LDEQ_data_columns: 
#  0 = date
#  1 = time
#  2 = data value
#  3 = units

###########################################################################
# read in links.csv and develop compartment-link-compartment dictionaries #
###########################################################################
links_file = r'%s\links.csv' % ICM_Hydro_dir
all_links = []  # array to store all link IDs
all_comps = []  # array to store all compartment IDs
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

####################################################################
# read in file mapping observed data site to ICM-Hydro compartment #
####################################################################
comp_CRMS = {} # dictionary to store compartments as keys with CRMS site as value
comp_LDEQ = {} # dictionary to store compartments as keys with LDEQ site as value
with open(comp_CRMS_LDEQ_map,mode='r') as ccm:
    nl = 0
    for line in ccm:
        if nl > 0:
            linesplit = line.split(',')
            comp = int(linesplit[0])
            CRMS = linesplit[1].strip('\n')
            LDEQ = linesplit[2].strip('\n')
            comp_CRMS[comp] = CRMS
            comp_LDEQ[comp] = LDEQ
        nl += 1

for nt in range(0,len(types)):
    source = sources[nt]
    out_type = types[nt]
    date_col = date_cols[nt]
    data_col = data_cols[nt]
    unit_conv = unit_convs[nt]
    unit = units[nt]
    y_txt = y_labels[nt]
    y_range = y_ranges[nt]


    csv_fpath = r'%s\MP2023_stats_%s.csv' % (plot_dir,out_type)

    if os.path.exists (plot_dir) == False:
        os.mkdir(plot_dir)
    if os.path.exists (html_dir) == False:
        os.mkdir(html_dir)
    if os.path.exists (png_dir) == False:
        os.mkdir(png_dir)
    if os.path.exists (r'%s\%s' % (png_dir,out_type)) == False:
        os.mkdir(r'%s\%s' % (png_dir,out_type))
    
    # read in model output data
    h_out_file = r'%s\%s%s.out' % (ICM_Hydro_dir,file_pre,out_type)
    print(' reading in %s' % h_out_file)
    h_out = np.genfromtxt(h_out_file,skip_header=0,delimiter=',') # for 2017 ICM formatting of stg.out
    ndays, ncomps = h_out.shape
    
    # if ncomps != len(all_comps):
        # sys.exit(' data check shows that Hydro output does not have same number of outputs as input links file\nAborting plotting script.')
    
    model_dates = [start_day + dt.timedelta(days=x) for x in range(0, ndays)]
    model_dates_plt = mpd.date2num(model_dates) # matplotlib date object
    
    # open output csv where statistics will be saved
    with open(csv_fpath,mode='w') as outfile:
        _ = outfile.write('ICM_Hydro_comp,site,Obs Mean(%s), Obs StDv (%s), Model Mean (%s), Model StDv (%s),Bias (%s),RMSE (%s),R-sq,NSE,RMSE bias corrected(%s),NSE bias corrected\n' % (unit,unit,unit,unit,unit,unit,unit))
        nc = 0
        for c in range(0,ncomps):
            nc += 1
            comp = c+1
            print(r' compartment %04d - %d/%d - %0.1f%%' %(comp,nc,ncomps,100*nc/ncomps))
        
            png_fname = 'ICM-Hydro_comp%04d_%s.png' % (comp,out_type)
            png_fpath = r'%s\%s\%s' % (png_dir,out_type,png_fname)
            
            model_label = 'ICM-Hydro comp %04d' % (comp)
            model_vals = []
            for d in range(0,ndays):
                model_vals.append(float(h_out[d][c]))
            
            try:
                # empty lists that will include timeseries of observed data
                obs_dates = []
                obs_vals = []
        
                # set file name based on data source
                if source == 'CRMS':
                    site = comp_CRMS[comp]
                    dt_delim = '/'      # CRMS file date format is M/D/Y
                    print ('  - corresponding CRMS site is %s' % site)
                    csvf = r'%s\%s_daily_English.csv' % (CRMS_dir,site)
                elif source == 'LDEQ':
                    site = comp_LDEQ[comp]
                    dt_delim = '/'      # CRMS file date format is M/D/Y
                    print ('  - corresponding LDEQ site is %s' % site)
                    csvf = r'%s\%s\%s_%s.csv' % (LDEQ_dir,out_type,site,out_type)
                
                # read in observed data
                if out_type == 'TRG':
                    # tidal range calculations need to read in date, min stage, and max stage for the day
                    import_cols = [date_col,data_col[0],data_col[1]]
                    f = np.genfromtxt(csvf,dtype=(str,str),skip_header=1,usecols=import_cols,delimiter=',')
                    
                    for row in f:
                        if row[1] != 'na':          # if have min stage data for day
                            if row[2] != 'na':      # and have max stage data for day
                                odate = dt.date(int(row[0].split(dt_delim)[2]),int(row[0].split(dt_delim)[0]),int(row[0].split(dt_delim)[1]))
                                wsmin = float(row[1])*unit_conv
                                wsmax = float(row[2])*unit_conv
                                oval = wsmax - wsmin
                                # append observed data and date of observation into lists that will be plotted
                                obs_dates.append(odate)
                                obs_vals.append(oval)
                else:
                    import_cols = [date_col,data_col]
                    f = np.genfromtxt(csvf,dtype=(str,str),skip_header=1,usecols=import_cols,delimiter=',')
                    for row in f:
                        if row[1] != 'na':          # if have data for day
                            odate = dt.date(int(row[0].split(dt_delim)[2]),int(row[0].split(dt_delim)[0]),int(row[0].split(dt_delim)[1]))
                            oval = float(row[1])*unit_conv
                            # append observed data and date of observation into lists that will be plotted
                            obs_dates.append(odate)
                            obs_vals.append(oval)
                
                # convert list of observation dates into a matplotlib date object
                obs_dates_plt = mpd.date2num(obs_dates)
                # compartment had observed data, so set plot_obs and calc_stats flags to 1
                plot_obs= 1
                calc_stats = 1
            except:
                # failed to find 
                plot_obs = 0
                calc_stats = 0
                print ('  - no corresponding observed data site')
            
            if calc_stats == 1:
                
                paired_data = {}
                paired_data['obs'] = {}
                paired_data['mod'] = {}
                
                for date in obs_dates_plt:
                    if date in model_dates_plt:
                        obs_index = np.where(obs_dates_plt == date)[0][0]
                        mod_index = np.where(model_dates_plt == date)[0][0]
                        paired_data['obs'][date] = obs_vals[obs_index]
                        paired_data['mod'][date] = model_vals[mod_index]
                
                # calculate descriptive statistics using numpy
                paired_dates = paired_data['obs'].keys()
                
                n_paired = len(paired_dates)
                obs_mean = np.mean(np.fromiter(paired_data['obs'].values(),dtype=float))
                obs_stdv = np.std(np.fromiter(paired_data['obs'].values(),dtype=float))
                mod_mean = np.mean(np.fromiter(paired_data['mod'].values(),dtype=float))
                mod_stdv = np.std(np.fromiter(paired_data['mod'].values(),dtype=float))
            
                # bias (bias, pbias (0 - 1) )
                bias = mod_mean - obs_mean
                pbias = bias/obs_mean
                
                # calculate performance statistics using equations in Meselhe & Rodrigue (2013), Nash & Sutcliffe (1970)
                PRn  = 0    # summation term for numerator of Pearson correlation coefficient (r)
                PRdm = 0    # summation term for model component of denominator of Pearson correlation coefficient (r)
                PRdo = 0    # summation term for observation component of denominator of Pearson correlation coefficient (r)
                NSEn = 0    # summation term for numerator of Nash Sutcliffe Model Efficiency (NSE) - also the numerator for root mean squared error (RMSE)
                NSEd = 0    # summation term for denominator of Nash Sutcliffe Model Efficiency (NSE)
                RMSEd = 0   # summation term for denominator of root mean squared error (RMSE)
                PRn_bc  = 0 # summation term for numerator of bias-corrected Pearson correlation coefficient (r) 
                PRdm_bc = 0 # summation term for model component of denominator of bias-corrected Pearson correlation coefficient (r)
                NSEn_bc = 0 # summation term for numerator of bias-corrected Nash Sutcliffe Model Efficiency (NSE) - also the numerator for root mean squared error (RMSE)
                                
                for date in paired_data['obs'].keys():
                    # shortened variable names
                    oi = paired_data['obs'][date]
                    om = obs_mean
                    mi = paired_data['mod'][date]
                    mm = mod_mean
                    # bias correct model values
                    mi_bc = mi - bias
                    mm_bc = mm - bias
                    
                    
                    # calculate summmations used for Pearson Correlation Cofficient (r)
                    PRn  += (mi-mm)*(oi-om)
                    PRdm += (mi-mm)**2
                    PRdo += (oi-om)**2
                    # calculate bias-corrected version
                    PRn_bc  += (mi_bc-mm_bc)*(oi-om)
                    PRdm_bc += (mi_bc-mm_bc)**2

                
                    # calculate summmations used for Nash Sutcliffe Model Efficiency (NSE)
                    NSEn += (oi-mi)**2
                    NSEd += (oi-om)**2
                    # calculate bias-corrected version
                    NSEn_bc += (oi-mi_bc)**2
                    
                    # calculate summation used in root mean squared error (RMSE)
                    RMSEd += oi
                
                try:
                    # Pearson Correlation Cofficient (r) (0 - 1)
                    r = PRn / (PRdm**0.5 * PRdo**0.5)
                    r_sq = r**2
                    r_bc = PRn_bc / (PRdm_bc**0.5 * PRdo**0.5)
                    r_sq_bc = r_bc**2
                    
                    # Nash-Sutcliffe Efficiency (NSE) (-inf - 1)
                    NSE = 1 - NSEn / NSEd
                    NSE_bc = 1 - NSEn_bc / NSEd
                    
                    # Root Mean Squared Error (RMSE) - not normalized
                    RMSE = (NSEn / n_paired)**0.5
                    RMSE_bc = (NSEn_bc / n_paired)**0.5
                    
                    # Root Mean Squared Error - Normalized
                    RMSEnorm = RMSE/obs_mean
                    RMSEnorm_bc = RMSE_bc/obs_mean
                    
                    stats_text = 'Obs mean = %0.03f %s\nObs stdv = = %0.03f %s\nBias = %0.03f %s\nR-sq = %0.3f\nRMSE = %0.03f (bc = %0.3f)\nNSE  = %0.3f (bc = %0.3f)' % (obs_mean,unit,obs_stdv,unit,bias,unit,r_sq,RMSE,RMSE_bc,NSE,NSE_bc)
                    _ = outfile.write('%d,%s,%0.03f,%0.03f,%0.03f,%0.03f,%0.03f,%0.03f,%0.3f,%0.3f,%0.3f,%0.3f\n' % (comp,site,obs_mean,obs_stdv,mod_mean,mod_stdv,bias,RMSE,r_sq,NSE,RMSE_bc,NSE_bc))
                
                except:
                    r = 'na'
                    r_sq = 'na'
                    bias = 'na'
                    NSE = 'na'
                    RMSE = 'na'
                    RMSEnorm = 'na'
                    stats_text = 'Bias = NA\nRMSE = NA\nR-sq = NA\nNSE  = NA'
                    _ = outfile.write('%d,%s,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA\n'  % (comp,site) )
                
                stats_text_prop = dict(boxstyle='round', facecolor='white')
                
            fig = plt.figure()
            ax = fig.add_subplot(111,facecolor='whitesmoke')
            # plot model data
            ax.plot_date(model_dates_plt,model_vals,marker='o',markersize=0,linestyle='solid',linewidth=1,color='black',label=model_label)
            
            # add observed data to plot (if available)
            if plot_obs == 1:
                ax.plot_date(obs_dates_plt,obs_vals,marker='o',markersize=1,linestyle='solid',linewidth=0,color='red',label=site)
            
            
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
            ax.set_xlabel(x_txt)    
        
            # format Y-axis
            if y_range != -9999:
                ax.set_ylim(y_range)
            ax.set_ylabel(y_txt)
        
            # add legend
            ax.legend(loc='upper right',edgecolor='none',facecolor='none')
        
            # add grid 
            ax.grid(True,which='both',axis='x',color='silver',linewidth=0.5)
    
            if calc_stats == 1:         # add text box with statistics
                ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=8, verticalalignment='top', bbox=stats_text_prop)
    
            plt.savefig(png_fpath)
            plt.close() 


    #############################################################################################################
    # build html pages for each compartment with stage and salinity plots and links to neighboring compartments #
    #############################################################################################################
for comp in range(1,ncomps+1):
    html_fname = 'ICM-Hydro_comp%04d.html' % comp # this must match html writing script lower that maps to connected compartments
    html_file = r'%s\%s' % (html_dir,html_fname)

    png_fname = 'ICM-Hydro_comp%04d_%s.png' % (comp,out_type)
    png_fpath = r'%s\%s\%s' % (png_dir,out_type,png_fname)
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
                        hf.write(' <a href="..\html\ICM-Hydro_comp%04d.html"> Compartment %04d via Link %04d </a>  <br>' % (cnct_comp,cnct_comp,link))
        except:
            _ = 'no links for compartment'
        hf.write(' </body>')  
        hf.write('</html>')
        
 
