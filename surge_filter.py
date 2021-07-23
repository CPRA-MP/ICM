import numpy as np

dates = np.genfromtxt('D:/ICM/S06/G502/hydro/surge.csv',delimiter=',',skip_header=1,usecols=[0],dtype=str)
s = np.genfromtxt('D:/ICM/S06/G502/hydro/surge.csv',delimiter=',',skip_header=1,usecols=range(1,23))
mx = np.max(s[0:140255],axis=0)
pks = {}
for yr in range(2019,2071):
    pks[yr] = {}
    pks[yr][8] = []
    pks[yr][10] = []
    for c in range(0,22):
        pks[yr][8].append(0)
        pks[yr][10].append(0)

r = 0
for d in s:
    yr = int(dates[r][0:4])
    mon = int(dates[r][4:6])
    
    if mon in [8,10]:
        c=0
    
        for g in d:
            if g >= mx[c]:
                pks[yr][mon][c] = max( g, pks[yr][mon][c] )
        c+=1
    r+=1

with open('D:/ICM/S06/surge_filtered_new.csv',mode='w') as so:
    r = 0
    for d in s:
        c=0
        
        lineout = dates[r]
        
        yr = int(dates[r][0:4])
        mon = int(dates[r][4:6])

        for g in d:
            if mon in [8,10]:
                if pks[yr][mon][c] > mx[c]:
                    if g > 0.5:
                        val = mx[c]*g/pks[yr][mon][c]
                    else:
                        val = g
                else:
                    val = g
            else:
                val = g
            lineout = '%s,%s' % (lineout,val)
            c+=1
        
        out = so.write('%s\n' % lineout)
        
        r+=1