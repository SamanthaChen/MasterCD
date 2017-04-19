# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:LFRNMI.py
@time:2017/3/2620:27
"""
from  NodePreceptionV4 import runOrderedNodePreception
import networkx as nx
from collections import defaultdict

def dataWriter(communityList,outpath):
    '''

    :param communityList 二维数组:
    :return:
    '''
    outfile=open(outpath,'w')
    for com in communityList:
        string=''
        for n in com:
            string+=str(n)+' '
        outfile.write(string+'\n')
    outfile.close()




if __name__=='__main__':
    '读文件'
    sim = 0.08  ###超图的相似度超多少才有边
    inPath = 'L:/CDdata/groundTruthData/LFR/'
    dataSize=['large','small']
    varType=['varymu','varyom']
    varmu=[1,2,3,4,5,6,7,8]
    varyom=[2,3,4,5,6,7,8]
    for size in dataSize:
        if size=='small':
            fixon=100
        else:
            fixon=500
        print 'size:',size
        for var in varType:
            print 'var:',var
            if var=='varymu':
                for mu in varmu:
                    networkpath=inPath+size+'/'+var+'/'+'network_mu'+str(mu)+'0_on'+str(fixon)+'_om5.dat'
                    G = nx.read_edgelist(networkpath, nodetype=int)
                    '传统的'
                    res = runOrderedNodePreception(G, sim, slpar=0.5)
                    outpath=inPath+size+'/'+var+'/'+'NPcluster_network_mu'+str(mu)+'0_on'+str(fixon)+'_om5.dat'
                    dataWriter(res, outpath)

            if var=='varyom':
                for om in varyom:
                    networkpath = inPath + size + '/' + var + '/' + 'network_mu10_on'+str(fixon)+'_om'+str(om)+'.dat'
                    G = nx.read_edgelist(networkpath, nodetype=int)
                    '传统的'
                    res = runOrderedNodePreception(G, sim, slpar=0.5)
                    outpath = inPath + size + '/' + var + '/' + 'NPcluster_network_mu10_on'+str(fixon)+'_om'+str(om)+'.dat'
                    dataWriter(res, outpath)

