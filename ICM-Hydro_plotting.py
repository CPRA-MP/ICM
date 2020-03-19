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
comp_CRMS_map = r'E:\ICM\CRMS_ICM_compartment_map.csv'
scn = 'High Scenario (S00)'
grp = 'FWOA (G000)'
file_pre = ''	# prefix for run from file naming convention
start_day = dt.date(2006,1,1)
ICM_Hydro_dir = r'E:\ICM\ICM_hydro_CP'
out_type = 'STG'	# STG = daily mean stage
					#'SAL' = daily mean salinity
					#'TRG' = daily mean tidal range
CRMS_dir = r'E:\CRMS\clean_daily'
CRMS_date_col = 1
CRMS_column = 5 	#  0 = stationID
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
unit_conv = 0.3048
plot_dir = r'%s\plots' % ICM_Hydro_dir
html_dir = r'%s\html' % plot_dir
png_dir = r'%s\png' % plot_dir
y_txt = r'Daily Mean Salinity (ppt)'
y_range = [0, 36]
y_txt = r'Daily Mean Stage (m, NAVD88)'
y_range = [-2.0, 2.0]

if os.path.exists (plot_dir) == False:
	os.mkdir(plot_dir)
if os.path.exists (html_dir) == False:
	os.mkdir(html_dir)
if os.path.exists (png_dir) == False:
	os.mkdir(png_dir)
if os.path.exists (r'%s\%s' % (png_dir,out_type)) == False:
	os.mkdir(r'%s\%s' % (png_dir,out_type))

###########################################################################
# read in links.csv and develop compartment-link-compartment dictionaries #
###########################################################################
links_file = r'%s\links.csv' % ICM_Hydro_dir
all_links = []	# array to store all link IDs
all_comps = []	# array to store all compartment IDs
link_comps = {}	# dictionary to store links as keys with upstream and downstream compartments as values
comp_links = {}	# dictionary to store compartments as keys with all links connected to compartment as values

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

#####################################################
# read in model output and plot alongside CRMS data #
#####################################################
comp_CRMS = {} # dictionary to store compartments as keys with CRMS site as value
with open(comp_CRMS_map,mode='r') as ccm:
	nl = 0
	for line in ccm:
		if nl > 0:
			linesplit = line.split(',')
			comp = int(linesplit[0])
			CRMS = linesplit[1].strip('\n')
			comp_CRMS[comp] = CRMS
		nl += 1

h_out_file = r'%s\%s%s.out' % (ICM_Hydro_dir,file_pre,out_type)
print(' reading in %s' % h_out_file)
h_out = np.genfromtxt(h_out_file,skip_header=0,delimiter=',') # for 2017 ICM formatting of stg.out
ndays, ncomps = h_out.shape

# if ncomps != len(all_comps):
	# sys.exit(' data check shows that Hydro output does not have same number of outputs as input links file\nAborting plotting script.')

model_dates = [start_day + dt.timedelta(days=x) for x in range(0, ndays)]
model_dates_plt = mpd.date2num(model_dates) # matplotlib date object

nc = 0
for c in range(0,ncomps):
	nc += 1
	comp = c+1
	print(r' compartment %04d - %d/%d - %0.1f%%' %(comp,nc,ncomps,100*nc/ncomps))
	
	png_fname = 'ICM-Hydro_comp%04d_%s.png' % (comp,out_type)
	png_fpath = r'%s\%s\%s' % (png_dir,out_type,png_fname)
	
	html_fname = 'ICM-Hydro_comp%04d.html' % comp # this must match html writing script lower that maps to connected compartments
	html_file = r'%s\%s' % (html_dir,html_fname)

	model_vals = []
	for d in range(0,ndays):
		model_vals.append(float(h_out[d][c]))
	
	try:
		CRMSsite = comp_CRMS[comp]
		print ('  - corresponding CRMS site is %s' % CRMSsite)
		CRMS_dates = []
		CRMS_vals = []
		CRMS_file = r'%s_daily_English.csv' % CRMSsite
		csvf = r'%s\%s' % (CRMS_dir,CRMS_file)
		f=np.genfromtxt(csvf,dtype=(str,str),skip_header=1,usecols=[CRMS_date_col,CRMS_column],delimiter=',')
		for row in f:
			if row[1] != 'na':
				CRMS_dates.append(dt.date(int(row[0].split('/')[2]),int(row[0].split('/')[0]),int(row[0].split('/')[1])))
				CRMS_vals.append(float(row[1])*unit_conv)
		CRMS_dates_plt = mpd.date2num(CRMS_dates)
		plot_CRMS = 1
	except:
		plot_CRMS = 0
		print ('  - no corresponding CRMS site')
	
	
	x_range = [model_dates[0],model_dates[-1]]
	x_txt = r'Year'
	model_label = 'ICM-Hydro comp %04d' % (comp)
	
	fig = plt.figure()
	#fig.suptitle(plot_title)
	ax = fig.add_subplot(111,facecolor='whitesmoke')
	ax.set_ylabel(y_txt)
	ax.set_xlabel(x_txt)
	ax.plot_date(model_dates_plt,model_vals,marker='o',markersize=0,linestyle='solid',linewidth=1,color='black',label=model_label)
	if plot_CRMS == 1:
		ax.plot_date(CRMS_dates_plt,CRMS_vals,marker='o',markersize=1,linestyle='solid',linewidth=0,color='red',label=CRMSsite)
	ax.legend(loc='upper right',edgecolor='none',facecolor='none')
	ax.set_ylim(y_range)
	ax.set_xlim(x_range)
	ax.xaxis.set_major_locator(mpd.YearLocator())
	if ndays/365 <= 2: 		# if data is no more than 2 years in length put tick marks at months
		ax.xaxis.set_minor_locator(mpd.MonthLocator())
		ax.xaxis.set_major_formatter(mpd.DateFormatter('%Y'))
	elif ndays/365 < 10:	# if data is more than 2 years but less than 10 put tick marks at quarters
		ax.xaxis.set_minor_locator(mpd.MonthLocator((1,4,7,10)))
		ax.xaxis.set_major_formatter(mpd.DateFormatter('%Y'))
	else:
		ax.xaxis.set_major_formatter(mpd.DateFormatter('%y'))
		
	ax.grid(True,which='both',axis='x',color='silver',linewidth=0.5) 
	plt.savefig(png_fpath)
	plt.close()	


	#############################################################################################################
	# build html pages for each compartment with stage and salinity plots and links to neighboring compartments #
	#############################################################################################################
	
	with open(html_file,mode='w') as hf:
		hf.write('<html>')
		hf.write(' <head>')
		hf.write('   <p style ="font-size:24;font-style:;font-weight:bold" align="center">%s - %s<br>Compartment %04d</p>' % (scn,grp,comp))
		hf.write(' </head>')
		hf.write(' <body>')
		hf.write(' <p><img src="..\png\%s\%s" align ="top"> <img src="..\png\%s\%s" align ="top"></p>' % (out_type,png_fname,out_type,png_fname))
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
			for link in comp_links[comp]:			# loop through all  links connecting to compartment
				for cnct_comp in link_comps[link]:	# find compartments that are connected via link
					if cnct_comp != comp:			# link will have two compartments - one that is current compartment and one that is the connected compartment
						hf.write(' <a href="..\html\ICM-Hydro_comp%04d.html"> Compartment %04d via Link %04d </a>  <br>' % (cnct_comp,cnct_comp,link))
		except:
			_ = 'no links for compartment'
		hf.write(' </body>')  
		hf.write('</html>')
		
 
