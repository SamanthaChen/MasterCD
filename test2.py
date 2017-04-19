# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:test2.py
@time:2017/3/2310:15
"""

import networkx as nx
import random


def __overlapping_label_propagation(ego_minus_ego, ego, max_iteration=100,weighted=False):
    """

    :param max_iteration: number of desired iteration for the label propagation
    :param ego_minus_ego: ego network minus its center
    :param ego: ego network center
    """
    t = 0 ##迭代次数

    old_node_to_coms = {}

    while t < max_iteration:
        t += 1

        label_freq = {} ##<标签，频率>
        node_to_coms = {} ##<节点，标签>

        nodes = nx.nodes(ego_minus_ego)
        '随机洗牌节点遍历的顺序'
        random.shuffle(nodes)

        count = -len(nodes)

        for n in nodes:
            n_neighbors = nx.neighbors(ego_minus_ego, n)

            if count == 0:
                t += 1

            # compute the frequency of the labels
            '统计标签频率'
            for nn in n_neighbors:
                '假如节点nn还没有标签，标签为自己'
                communities_nn = [nn] ##邻居标签
                '假如节点nn在之前的迭代中已经出现过标签，采用之前的标签'
                if nn in old_node_to_coms:
                    communities_nn = old_node_to_coms[nn]
                '统计邻居标签频率，分带权重和无权重两种'
                for nn_c in communities_nn:
                    if nn_c in label_freq:
                        v = label_freq.get(nn_c)
                        # case of weighted graph
                        if weighted:
                            label_freq[nn_c] = v + ego_minus_ego.edge[nn][n]['weight']
                        else:
                            label_freq[nn_c] = v + 1
                    else:
                        # case of weighted graph
                        if weighted:
                            label_freq[nn_c] = ego_minus_ego.edge[nn][n]['weight']
                        else:
                            label_freq[nn_c] = 1

            # first run, random choosing of the communities among the neighbors labels
            if t == 1:
                '迭代的第一次，从邻居标签里面随机选择'
                if not len(n_neighbors) == 0:
                    r_label = random.sample(label_freq.keys(), 1)
                    ego_minus_ego.node[n]['communities'] = r_label
                    old_node_to_coms[n] = r_label
                count += 1
                continue
            # choose the majority
            else:
                '迭代的第n次，选择邻居里面标签最大的'
                labels = []
                max_freq = -1

                for l, c in label_freq.items():
                    if c > max_freq:
                        max_freq = c
                        labels = [l]
                    elif c == max_freq:
                        labels.append(l)

                node_to_coms[n] = labels ##第n个节点的标签是邻居中标签最大的
                '还没收敛就继续'
                if not n in old_node_to_coms or not set(node_to_coms[n]) == set(old_node_to_coms[n]):
                    old_node_to_coms[n] = node_to_coms[n]
                    ego_minus_ego.node[n]['communities'] = labels

        t += 1
    '利用ego重构社团'
    # build the communities reintroducing the ego
    community_to_nodes = {}
    for n in nx.nodes(ego_minus_ego):
        '假如没有邻居，标签等于自己'
        if len(nx.neighbors(ego_minus_ego, n)) == 0:
            ego_minus_ego.node[n]['communities'] = [n]

        c_n = ego_minus_ego.node[n]['communities']

        for c in c_n:

            if c in community_to_nodes:
                com = community_to_nodes.get(c)
                com.append(n)
            else:
                nodes = [n, ego]
                community_to_nodes[c] = nodes

    return community_to_nodes

def printNodesFile():
    inpath='L:/CDdata/lfr/'
    sizeList=[5000,10000,50000,100000,150000,200000,250000,300000]
    for size in sizeList:
        filename=inpath+'network_'+str(size)+'.nodes'
        rw=open(filename,'w')
        for i in range(1,size+1):
            rw.write(str(i)+'\n')
        rw.close()




if __name__=='__main__':
    printNodesFile()
    # G=nx.karate_club_graph()
    # ego=0
    # ego_minus_ego=nx.ego_graph(G,ego,1,False)
    # tmp=__overlapping_label_propagation(ego_minus_ego,ego)
    # print tmp
