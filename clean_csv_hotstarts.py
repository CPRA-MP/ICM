
S = int(sys.argv[1])
G = int(sys.argv[2])


lvfile = './S%02d/G%03d/geomorph/output/MP2023_S%02d_G%03d_C000_U00_V00_SLA_O_01_52_land_veg.csv' % (S,G,S,G)
print('\nchecking for hotstart data in : %s' % lvfile)


with open(lvfile,mode='r') as lvf:
    nrb = 0
    nr = 0
    scenarios   = []
    groups      = []
    codes       = []
    ecoregions  = []
    years       = []
    ecoregion_values = {}
    
    for r in lvf:   # 'prj_no', 'S', 'ICMyear', 'code', 'ecoregion', 'value'
        if nr == 0:
            header = r
        else:
            try:
                g = int(r.split(',')[0].strip()[1:4])
                s = int(r.split(',')[1].strip()[1:3])
                y = int(r.split(',')[2].strip())
                c = r.split(',')[3].strip()
                e = r.split(',')[4].strip()
                v = float(r.split(',')[5].strip())
                
                if s not in ecoregion_values.keys():
                    ecoregion_values[s] = {}
                    scenarios.append(s)
                if g not in ecoregion_values[s].keys():
                    ecoregion_values[s][g] = {}
                    groups.append(g)
                if c not in ecoregion_values[s][g].keys():
                    ecoregion_values[s][g][c] = {}
                    codes.append(c)
                if e not in ecoregion_values[s][g][c].keys():
                    ecoregion_values[s][g][c][e] = {}
                    ecoregions.append(g)
                if y not in ecoregion_values[s][g][c][e].keys()
                    ecoregion_values[s][g][c][er][y] = []
                    years.append(y)
                    
                ecoregion_values[s][g][c][er][y].append(v)

            except:
                nrb += 1
                badrows.append(nr)
        nr += 1
    if nrb > 0:
        print(' Failed to parse %d rows in %s. Check lines:' % (nrb,lvfile))
        print(badrows)

hotstart = False
for s in scenarios:
    for g in groups:
        for c in codes:
            for e in ecoregions:
                for y in years:
                    repeats  = len(ecoregion_values[s][g][c][er][y])
                    if repeats > 1:
                        hotstart = True

if hotstart == True:
    print('found multiple values for at least one year - indicating run was hotstarted.')
    orig = lvfile
    back = '%s.old' % orig
    print('copying original file with new *.old extension.')
    os.rename(orig,back)
    print('writing new file using only the last instance of each year with repeated data.')
    
    with open(lvfile,mode='w') as lvf_new:
        lvf_new.write(header):
        for s in scenarios:
            for g in groups:
                for c in codes:
                    for e in ecoregions:
                        for y in years:
                            val2write = ecoregion_values[s][g][c][er][y][-1]    # pulls only the last value for any given year and ignores earlier values
                            lvf_new.write('G%03d,S%02d,%02d,%s,%s,%s\n' % (g,s,y,c,e,val2write) )
else:
    print('did not find any repeat/hotstarted data.')


