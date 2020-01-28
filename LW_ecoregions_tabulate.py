import numpy as np

scenarios = ['S04']
runs = ['G314','G314a','G314b','G314c','G314d']

erall = ['AVT','LTB','UBA','BFD','UPO','LPO','MEL','LBA','BRT','CAS','WCR','ECR','LPObi','BRTbi','BFDbi','LTBbi','LBAbi']
erout = ['AVT','LTB','UBA','BFD','UPO','LPO','MEL','LBA','BRT','CAS','WCR','ECR']

save_dir = r'D:\ICM\summary_outputs'
model_dir = r'D:\ICM'
run_pre = 'MPM2017'
years = range(1,51,1)

for s in scenarios:
	for g in runs:
                # sumcsv is the combined output file
		sumcsv = r'%s\%s_%s_%s_C000_U00_V00_SLA_O_01_50_W_LandAreaEcoregions.csv' % (save_dir,run_pre,s,g)
		lfd = {}
		wd = {}
		for er in erall:
			lfd[er] = {}
			wd[er] = {}
		for y in years:
			print ('formatting %s %s, year %02d' % (s,g,y))
			for er in erall:
				lfd[er][y] = 0.0
				wd[er][y] = 0.0
			
			lwfcsv = r'%s\%s\%s\geomorph\output_%02d\Deliverables\%s_%s_%s_C000_U00_V00_SLA_N_%02d_%02d_W_LWFzn.csv' % (model_dir,run_pre,s,g,y,s,g,y,y)
			
			lwf = np.genfromtxt(lwfcsv,skip_header=1,delimiter=',',dtype='str')
			for row in lwf:
				eri = row[0][0:3]
				L = float(row[1]) + float(row[3])
				W = float(row[2])
				try:
					lfd[eri][y] += L
					wd[eri][y] += W
				except:
					dump = 'ecoregion not a key'
				
		with open(sumcsv,mode='wt') as outf:
			print ('writing %s' % sumcsv)
			header = 'year'
			for er in erout:
				header = '%s,%s_land_area_m2,%s_water_area_m2' % (header,er,er)
			outf.write('%s\n' % header)
			for y in years:
				writeline = '%s' % y
				for er in erout:
					writeline = '%s,%s,%s'  % (writeline,lfd[er][y],wd[er][y])
				outf.write('%s\n' % writeline)
			
				
				
				
			
			
