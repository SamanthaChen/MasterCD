# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:test3.py
@time:2017/3/2313:15
"""
import communityLouvain as cd
import networkx as nx
import matplotlib.pyplot as plt
import random
from collections import defaultdict
from overlapping_modularity  import  compute_overlap_modularity_cxm

#better with karate_graph() as defined in networkx example.
#erdos renyi don't have true community structure
G = nx.karate_club_graph()

#first compute the best partitio
partition = cd.best_partition(G)

#drawing
size = float(len(set(partition.values())))
pos = nx.spring_layout(G)
count = 0.
for com in set(partition.values()) :
    count = count + 1.
    list_nodes = [nodes for nodes in partition.keys()
                                if partition[nodes] == com]
    c = [random.random()] * len(list_nodes)  # random color...
    nx.draw_networkx_nodes(G, pos, list_nodes, alpha=0.5,vmin=0.0,vmax=1.0,
                                node_color =c)


nx.draw_networkx_edges(G,pos, alpha=0.5,width=1,label=True,)
nx.draw_networkx_labels(G,pos,font_size=12)
plt.show()

# 'partition变成社团'
# communityDict=defaultdict(list)
# for node,comId in partition.items():
#     communityDict[comId].append(node)
# Qov=compute_overlap_modularity_cxm(G,communityDict.values())
# print Qov



