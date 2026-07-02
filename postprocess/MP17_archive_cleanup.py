import os
import pathlib
from zipfile import ZipFile
from zipfile import ZIP_DEFLATED

src_pd = 'G:/Recovery Drive 4 - Good Data/ICM_simulations'
arc_pd = 'G:/MP17_archive'

Gs = [1]
Ss = [1,3,4]
Ys = range(1,51)

dir_str = 'G%03d/S%02d/G%03d/geomorph/MPM2017_S%02d_G%03d_C000_U00_V00_SLA_I_%02d_%02d_W_initc.gdb' % (g,s,g,s,g,y,y)
'G%03d/S%02d/G%03d/geomorph/output_%02d' % (g,s,g,s,g,y)
'%s/G%03d/S%02d/G%03d/ewe/AreaAveraged'
'%s/G%03d/S%02d/G%03d/land_area_timeseries_plots' % (arc_pd,g,s,g)


os.mkdir('%s/G%03d' % (arc_pd,g) )
os.mkdir('%s/G%03d/S%02d' % (arc_pd,g,s) )
os.mkdir('%s/G%03d/S%02d/G%03d' % (arc_pd,g,s,g) )
os.mkdir('%s/G%03d/S%02d/G%03d/ewe' % (arc_pd,g,s,g) )
os.mkdir('%s/G%03d/S%02d/G%03d/geomorph' % (arc_pd,g,s,g) )
os.mkdir('%s/G%03d/S%02d/G%03d/hydro' % (arc_pd,g,s,g) )

os.mkdir('%s/G%03d/S%02d/G%03d/hydro' % (arc_pd,g,s,g) )
src_dir = '%s/%s' % (src_pd,dir_str)
arc_dir = '%s/%s' % (arc_pd,dir_str)

directory = pathlib.Path(dir_str)


with ZipFile(arc_dir,mode='w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
	for file_path in directory.rglob("*"):
		archive.write(file_path,arcname=file_path.relative_to(directory))

