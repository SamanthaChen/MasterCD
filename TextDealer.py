# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:TextDealer.py
@time:2017/3/2320:45
"""
from  collections import defaultdict
def delDupEdge():
    path='L:/CDdata/Realdata/'
    # dataset=['karate','highschool','netsci','books','dolphins','football','jazz','email','adjnoun','lesmis','congress']
    dataset2=['PGP','facebook','amazon']
    dataList3=['cora','citeseer','congress','imdb']
    for data in dataList3:
        f=open(path+data+'_edges','r')
        edges=[]
        for line in f.readlines():
            line=line.strip()
            words=line.split()
            e=tuple(sorted([int(val) for val in words]))
            if not e in edges:
                edges.append(e)
        f.close()
        '输出'
        w=open(path+data+'_edges1','w')
        for e in edges:
            string=str(e[0])+' '+str(e[1])
            w.write(string+'\n')
        w.close()

def adjlist2edgelist():
    inpath='L:/CDdata/Realdata/'
    dataname='citeseer'
    f=open(inpath+dataname+'_graph','r')
    w=open(inpath+dataname+'_edges','w')
    adjList={}
    for line in f.readlines():
        line=line.strip()
        words=line.split()
        adjList[words[0]]=words[1:]
    f.close()
    '排个序吧'

    for n in sorted(adjList.keys()):
        neis=adjList[n]
        for nei in neis:
            line = ''
            line=n+' '+nei+'\n'
            w.write(line)
    w.close()


def delweight():
    inpath='L:/CDdata/Realdata/'
    dataname='imdb'
    f=open(inpath+dataname+'_edges','r')
    w=open(inpath+dataname+'_edges1','w')
    for line in f.readlines():
        line=line.strip()
        words=line.split()
        wline=words[0]+' '+words[1]
        w.write(wline+'\n')
    f.close()
    w.close()


import os
def myrename():
    inpath='L:/CDdata/lfrTest/smallmu/'
    om=5
    on=100
    for mu in range(10,90,10):
        # oldname1=inpath+'network_mu'+str(mu)+'_on'+str(on)+'_om'+str(om)+'.comm2nodes.txt'
        oldname1 = inpath + 'community_mu' + str(mu) + '_on' + str(on) + '_om' + str(om)
        newname1=inpath+'community_mu'+str(mu)+'.txt'
        # print oldname1
        # print newname1
        os.rename(oldname1,newname1)
    #
    #     # oldname2 = inpath + 'network_mu' + str(mu) + '_on'+str(on)+'_om'+str(om)+'_CPM.res'
    #     # newname2 = inpath + 'network_mu' + str(mu) + '_CPM.res'
    #     # # print oldname2
    #     # # print newname2
    #     # os.rename(oldname2, newname2)

    # mu=10
    # for om in range(2,9,1):
    #     # oldname3=inpath+'network_mu'+str(mu)+'_on'+str(on)+'_om'+str(om)+'.comm2nodes.txt'
    #     # newname3=inpath+'network_om'+str(om)+'_link.txt'
    #     oldname3 = inpath + 'community_mu' + str(mu) + '_on' + str(on) + '_om' + str(om)
    #     newname3 = inpath + 'community_om' + str(om) + '.txt'
    #     os.rename(oldname3, newname3)

        # oldname4 = inpath + 'network_mu' + str(mu) + '_on'+str(on)+'_om'+str(om)+'_CPM.res'
        # newname4 = inpath + 'network_om' + str(om) + '_CPM.res'
        # # print oldname2
        # # print newname2
        # os.rename(oldname4, newname4)

if __name__=='__main__':
    myrename()