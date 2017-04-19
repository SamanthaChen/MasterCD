# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:NMIDealer.py
@time:2017/3/2821:24
"""

inPath = 'L:/CDdata/groundTruthData/LFR/'
dataSize=['large','small']
varType=['varymu','varyom']
varmu=[1,2,3,4,5,6,7,8]
varyom=[2,3,4,5,6,7,8]
rList=[0.1,0.2,0.3]
for size in dataSize:
    print 'size:',size
    for var in varType:
        print 'var:',var
        for r in rList:
            nmipath=inPath+size+'/'+var+'/'+'NMI-'+str(r)+'.txt'
            f=open(nmipath,'r')
            for line in f.readlines():
                print line
            f.close()
