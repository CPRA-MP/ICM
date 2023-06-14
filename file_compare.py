import sys
import numpy as np

fp1 = sys.argv[1]
fp2 = sys.argv[2]

n1 = 0
n2 = 0

f1 = np.genfromtxt(fp1,dtype='str',delimiter='123456789')
n1 = len(f1)
        
f2 = np.genfromtxt(fp2,dtype='str',delimiter='123456789')
n2 = len(f2)

if n1 == n2:
    print('Both files are same length: %d lines.' % n1)
    print('Comparing files line-by-line.')
    b1 = []
    b2 =[]
    
    for r in range(0,n1):
        l1 = f1[r]
        l2 = f2[r]
        
        if l1 != l2:
            b1.append('line %d: %s' % (r+1,l1))
            b2.append('line %d: %s' % (r+1,l2))

    if len(b1) > 0:
        print('Files are of same length, but are not identical.')
        print('%d lines do not match, out of %d total lines.' % (len(b1),n1))

        print('\nFirst lines that do not match:')
        print(b1[0])
        print(b2[0])
        
        
    else:
        print('Files are identical. Congratulations.')


else:
    print('Files are not the same length:')
    print('    %s has %d lines' % (fp1,n1))
    print('    %s has %d lines' % (fp2,n2))
    print('Exiting now.')    
 