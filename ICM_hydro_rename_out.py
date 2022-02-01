import sys
import os

s = int(sys.argv[1
g = int(sys.argv[2])
c = 0
u = 0
v = 0
r = 'SLA'

out_fol = 'S%02d/G%03d/hydro' % (s,g)

for out in os.listdir(out_fol):
    if out.endswith('.out'):
        out1 = '%s/%s' % (out_fol,out)
        out2 = '%s/MP2023_S%02d_G%03d_C%03d_U%02d_V%02d_%r_O_01_52_H_%s' % (out_fol,s,g,c,u,v,r,out)
        if out.startswith('MP2023'):
            print('%s already exists - skipping rename' % out1)
        else:
            os.rename(out1,out2)

