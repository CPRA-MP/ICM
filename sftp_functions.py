
with pysftp.Connection(host,username=un,password=pw,port=pt) as sf:
	for g in range(3,20):
		d = (r'\MP2023\Modeling\ICMv3_simulations\S04\G%03d' % g)
		fols = sf.listdir(d)
		sf.mkdir(r'%s\geomorph' % d)
		for fol in fols:
			o = r'%s\%s' % (d,fol)
			n = r'%s\geomorph\%s' % (d,fol)
			sf.rename(o,n)
			print('renamed G%03d %s' % (g,fol))

sf.mkdir(r'%s\post-processed_outputs\maps' % d)
sf.mkdir(r'%s\post-processed_outputs\QAQC' % d)
sf.mkdir(r'%s\post-processed_outputs\timeseries' % d)
sf.mkdir(r'%s\post-processed_outputs\timeseries\hydro' % d)
sf.mkdir(r'%s\post-processed_outputs\timeseries\land' % d)

			
with pysftp.Connection(host,username=un,password=pw,port=pt) as sf:
	for g in range(1,23):
		o = (r'\MP2023\Modeling\ICMv3_simulations\QAQC_output\G%03d\QAQC_output' % g)
		n = (r'\MP2023\Modeling\ICMv3_simulations\S04\G%03d\post-processed_outputs\QAQC' % g)
		for fol in sf.listdir(o):
			ofol = r'%s\%s' % (o,fol)
			nfol = r'%s\%s' % (n,fol)
			sf.rename(ofol,nfol)
			print('renamed %s' % nfol)
		
with pysftp.Connection(host,username=un,password=pw,port=pt) as sf:
	for g in range(1,20):
		o = r'\MP2023\Modeling\ICMv3_simulations\Sal_Stage_Spreadsheets\2023MP_viewer_S04_Medium_G%03d.xlsx' % g
		n = r'\MP2023\Modeling\ICMv3_simulations\S04\G%03d\post-processed_outputs\timeseries\hydro\\2023MP_viewer_S04_Medium_G%03d.xlsx' % (g,g)
		sf.rename(o,n)
		print('renamed %s' % n)