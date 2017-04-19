#coding=utf-8
import networkx as nx
import matplotlib.pyplot as plt
import Demon as D
import Demonhopsort as DhopSort
import sys

# G = nx.Graph()
# # file = open(sys.argv[1], "r")
# file = open('D:\Developer\javaworkspace\DEMON\input\Real Data\karate_edges', "r")
#
# for row in file:
#     part = row.strip().split()
#     G.add_edge(int(part[0]), int(part[1]))
# G=nx.karate_club_graph()

# pos=nx.spring_layout(G)
# nx.draw_networkx_nodes(G, pos, alpha=0.7,vmin=0.0,vmax=1.0)
# nx.draw_networkx_edges(G, pos,alpha=0.3)
# nx.draw_networkx_labels(G,pos)
# plt.axis("off")
# plt.show()

# Example use of DEMON. Parameter discussed in the paper.
# CD = D.Demon()
#self, G, epsilon=0.25, weighted=False, min_community_size=3
# CD.execute(G,0.1,False,2)
from collections import defaultdict
from NodePreceptionV5 import dataWriter

if __name__=='__main__':

    # G=nx.karate_club_graph()
    # res=runNPChameleon(G)
    # Qov=compute_overlap_modularity_cxm(G,res.values())
    # print Qov
    # for edge in G.edges():
    #     G.edge[edge[0]][edge[1]]['weight']=1
    # res=SLPA(G,1000,0.3)
    # Qov = compute_overlap_modularity_cxm(G, res.values())
    # print res
    # print Qov
    '读文件'
    inPath='L:/CDdata/Realdata/'
    # dataList=['karate','highschool','netsci','books','dolphins','football','jazz','email','adjnoun','lesmis','congress'] ##  'PGP','facebook','amazon'
    dataList2=['PGP','facebook','amazon']
    dataList = ['karate', 'highschool', 'netsci', 'books', 'dolphins', 'football', 'jazz', 'email', 'lesmis', 'PGP',
                'congress', 'cora', 'citeseer']
    for dataName in dataList:
        print dataName
        outpath = inPath + 'demon/'+dataName+'_res'
        edgeFile=inPath+dataName+'_edges'
        G = nx.read_edgelist(edgeFile,nodetype=int)
        '传统的'
        # res=runOrderedNodePreception(G,sim,slpar=0.5)
        'demon'
        CD = D.Demon()
        CD2=DhopSort.Demonhopsort()
        communities=CD.execute(G, 1.0, False, 2)
        allcommunities=[]
        for t in communities:
            allcommunities.append(list(t))
        print allcommunities

    #     '将结果输出'
    #     allCommunities=defaultdict(list)
    #     for node in G.nodes():
    #         labels=G.node[node]['communities']
    #         for label in labels:
    #             allCommunities[label].append(node)
        dataWriter(allcommunities,outpath)
