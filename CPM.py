# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:CPM.py
@time:2017/3/2616:11
"""
import networkx as nx


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



inPath = 'L:/CDdata/Realdata/'
dataList = ['karate', 'highschool', 'netsci', 'books', 'dolphins', 'football', 'jazz', 'email', 'adjnoun', 'lesmis',
            'congress']  ##  'PGP','facebook','amazon'
dataList2 = ['PGP', 'facebook', 'amazon']
dataList3 = ['karate', 'highschool', 'netsci', 'books', 'dolphins', 'football', 'jazz', 'email', 'lesmis', 'PGP',
             'cora', 'citeseer']  # 'imdb'
for dataName in dataList3:
    print dataName
    outpath = inPath + 'CPM/' + dataName + '_res'
    edgeFile = inPath + dataName + '_edges'
    G = nx.read_edgelist(edgeFile, nodetype=int)
    '传统的'
    k=6
    coms = list(nx.k_clique_communities(G, k))
    dataWriter(coms, outpath)