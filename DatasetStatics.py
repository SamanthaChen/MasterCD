# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:DatasetStatics.py
@time:2017/3/2817:22
"""
import networkx as nx
from collections import defaultdict

inPath = 'L:/CDdata/Realdata/'
dataList = ['karate', 'highschool', 'netsci', 'books', 'dolphins', 'football', 'jazz', 'email', 'adjnoun', 'lesmis',
            'congress','PGP', 'facebook', 'amazon']  ##  'PGP','facebook','amazon'
dataList2 = ['PGP', 'facebook', 'amazon']
dataList3=['cora','citeseer','congress','imdb']
outFile=inPath+'dataset_statics.txt'
wf=open(outFile,'w')
wf.write('data\tn\tm\taverD\tmaxd\n')
print 'data\tn\tm\taverD\tmaxd\t\labelnum\n'

for dataName in dataList3:
    # print dataName
    line=''
    edgeFile = inPath + dataName + '_edges'
    G=nx.Graph()
    G = nx.read_edgelist(edgeFile, nodetype=int)
    n=len(G)
    m=len(G.edges())
    degress=nx.degree(G)
    averdegress=float(sum([val for val in degress.values()]))/float(n)
    maxd=max(degress.values())

    '读节点标签'
    labelfile=inPath+dataName+'_nodelabel'
    labelDict = {}
    labelGroup=defaultdict(list)
    lf=open(labelfile,'r')
    for line in lf.readlines():
        line = line.strip()
        line=line.replace(',','\t').replace('and','\t').replace(' ','\t')
        words = line.split()
        labelDict[int(words[0])] = words[1:]  ##属性还是str格式
        for a in words[1:]:
            labelGroup[a].append(int(words[0]))
    lf.close()

    # print 'label number:',len(labelGroup.keys())

    line=dataName+'\t'+str(n)+'\t'+str(m)+'\t'+str(averdegress)+'\t'+str(maxd)+'\t'+str(len(labelGroup.keys()))+'\n'
    print line
    wf.write(line)
wf.close()
