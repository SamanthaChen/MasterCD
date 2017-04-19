# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:SLPAw.py
@time:2017/3/2322:10
"""
from collections import defaultdict
import networkx as nx
import numpy as np
from overlapping_modularity import compute_overlap_modularity_cxm

def SLPA(G,T,r):
    '''
    SLPA算法实现
    https://github.com/romain-fontugne/slpa_nx/blob/master/slpa.py
    :param G:
    :param T: 最大迭代次数
    :param r: 标签频率控制
    :return:社团{标签：set（节点集合）}（字典结构）
    '''
    ##Stage 1: Initialization
    '步骤1：初始化节点内存'
    memory = {i: {i: 1} for i in G.nodes()}

    '步骤2：传播和监听'
    ##Stage 2: Evolution
    for t in range(T):
        '随机洗牌监听顺序'
        listenersOrder = list(G.nodes()) ##监听顺序
        np.random.shuffle(listenersOrder) ##

        for listener in listenersOrder:
            speakers = G[listener].keys() #speaker是节点listerner邻居
            '没有邻居就继续下一个点'
            if len(speakers) == 0:
                continue

            labels = defaultdict(int)

            for j, speaker in enumerate(speakers):
                '传播规则：'
                # Speaker Rule
                total = float(sum(memory[speaker].values()))
                labels[memory[speaker].keys()[
                    np.random.multinomial(1, [freq / total for freq in memory[speaker].values()]).argmax()]] += 1
            '监听规则：选择最大标签'
            # Listener Rule
            acceptedLabel = max(labels, key=labels.get)
            '更新节点监听的内存'
            # Update listener memory
            if acceptedLabel in memory[listener]:
                memory[listener][acceptedLabel] += 1
            else:
                memory[listener][acceptedLabel] = 1
    '步骤3：后处理，删掉内存中出现频率低的标签'
    ## Stage 3:
    for node, mem in memory.iteritems():
        for label, freq in mem.items():
            if freq / float(T + 1) < r:
                del mem[label]
    '找节点的社团隶属'
    # Find nodes membership
    communities = {}
    for node, mem in memory.iteritems():
        for label in mem.keys():
            if label in communities:
                communities[label].add(node)
            else:
                communities[label] = set([node])
    '删掉嵌套的社团'
    # Remove nested communities
    nestedCommunities = set()
    keys = communities.keys()
    for i, label0 in enumerate(keys[:-1]):
        comm0 = communities[label0]
        for label1 in keys[i + 1:]:
            comm1 = communities[label1]
            if comm0.issubset(comm1):
                nestedCommunities.add(label0)
            elif comm0.issuperset(comm1):
                nestedCommunities.add(label1)

    for comm in nestedCommunities:
        del communities[comm]

    return communities

def SLPAw(G,T,r,weight=False):
    '''
    SLPA算法实现（带权重的）
    https://github.com/romain-fontugne/slpa_nx/blob/master/slpa.py
    :param G:
    :param T: 最大迭代次数
    :param r: 标签频率控制
    :param weight: 是否是加权网络
    :return:社团{标签：set（节点集合）}（字典结构）
    '''
    ##Stage 1: Initialization
    '步骤1：初始化节点内存'
    memory = {i: {i: 1} for i in G.nodes()}

    '步骤2：传播和监听'
    ##Stage 2: Evolution
    for t in range(T):
        '随机洗牌监听顺序'
        listenersOrder = list(G.nodes()) ##监听顺序
        np.random.shuffle(listenersOrder) ##

        for listener in listenersOrder:
            speakers = G[listener].keys() #speaker是节点listerner邻居
            '没有邻居就继续下一个点'
            if len(speakers) == 0:
                continue

            labels = defaultdict(float)

            for j, speaker in enumerate(speakers):
                '传播规则：每个邻居从历史标签里面按照多项式分布的概率选一个标签给节点'

                # Speaker Rule
                total = float(sum(memory[speaker].values())) ##邻居标签出现频率之和
                '加权图（re:2017.3.23）'
                if weight:##加权图加的是权重
                    labels[memory[speaker].keys()[
                        np.random.multinomial(10, [freq / total for freq in memory[speaker].values()]).argmax()]] += G.edge[listener][speaker]['weight']
                else: ##无权图加的是1
                    labels[memory[speaker].keys()[
                        np.random.multinomial(10, [freq / total for freq in memory[speaker].values()]).argmax()]] += 1
            '监听规则：选择邻居中出现次数最多的标签'
            # Listener Rule
            acceptedLabel = max(labels, key=labels.get)


            '更新节点监听的内存'
            # Update listener memory
            if acceptedLabel in memory[listener]:
                memory[listener][acceptedLabel] += 1
            else:
                memory[listener][acceptedLabel] = 1
    '步骤3：后处理，删掉内存中出现频率低的标签'
    ## Stage 3:
    for node, mem in memory.iteritems():
        for label, freq in mem.items():
            if freq / float(T + 1) < r:
                del mem[label]
    '找节点的社团隶属'
    # Find nodes membership
    communities = {}
    for node, mem in memory.iteritems():
        for label in mem.keys():
            if label in communities:
                communities[label].add(node)
            else:
                communities[label] = set([node])
    '删掉嵌套的社团'
    # Remove nested communities
    nestedCommunities = set()
    keys = communities.keys()
    for i, label0 in enumerate(keys[:-1]):
        comm0 = communities[label0]
        for label1 in keys[i + 1:]:
            comm1 = communities[label1]
            if comm0.issubset(comm1):
                nestedCommunities.add(label0)
            elif comm0.issuperset(comm1):
                nestedCommunities.add(label1)

    for comm in nestedCommunities:
        del communities[comm]

    return communities

def SLPAwAuto(G,T,egoLabelsNum,weight=False):
    '''
    SLPA算法实现（带权重的）
    https://github.com/romain-fontugne/slpa_nx/blob/master/slpa.py
    改成根据原来的标签个数来自动确定后处理的r
    :param G:
    :param T: 最大迭代次数
    :param egoLabelsNum: 标签频率控制
    :param weight: 是否是加权网络
    :return:社团{标签：set（节点集合）}（字典结构）
    '''
    ##Stage 1: Initialization
    '步骤1：初始化节点内存'
    memory = {i: {i: 1} for i in G.nodes()}

    '步骤2：传播和监听'
    ##Stage 2: Evolution
    for t in range(T):
        '随机洗牌监听顺序'
        listenersOrder = list(G.nodes()) ##监听顺序
        np.random.shuffle(listenersOrder) ##

        for listener in listenersOrder:
            speakers = G[listener].keys() #speaker是节点listerner邻居
            '没有邻居就继续下一个点'
            if len(speakers) == 0:
                continue

            labels = defaultdict(float)

            for j, speaker in enumerate(speakers):
                '传播规则：每个邻居从历史标签里面按照多项式分布的概率选一个标签给节点'

                # Speaker Rule
                total = float(sum(memory[speaker].values())) ##邻居标签出现频率之和
                '加权图（re:2017.3.23）'
                if weight:##加权图加的是权重
                    labels[memory[speaker].keys()[
                        np.random.multinomial(1, [freq / total for freq in memory[speaker].values()]).argmax()]] += G.edge[listener][speaker]['weight']
                else: ##无权图加的是1
                    labels[memory[speaker].keys()[
                        np.random.multinomial(1, [freq / total for freq in memory[speaker].values()]).argmax()]] += 1
            '监听规则：选择邻居中出现次数最多的标签'
            # Listener Rule
            acceptedLabel = max(labels, key=labels.get)


            '更新节点监听的内存'
            # Update listener memory
            if acceptedLabel in memory[listener]:
                memory[listener][acceptedLabel] += 1
            else:
                memory[listener][acceptedLabel] = 1
    '步骤3：后处理，删掉内存中出现频率低的标签'
    '改成根据egoLabelsNum筛选一定数量的标签（2017.3.26）'
    ## Stage 3:
    for node, mem in memory.iteritems():
        '对于每个节点的内存,按标签频率降序排序'
        sortedmem=sorted(mem.items(),key=lambda d:d[1],reverse=True)
        '删掉后面多余的'
        if len(sortedmem)>egoLabelsNum[node]:
            deletedLabels=[val[0] for val in sortedmem[egoLabelsNum[node]:]]
            for label in deletedLabels:
                    del mem[label]
    '找节点的社团隶属'
    # Find nodes membership
    communities = {}
    for node, mem in memory.iteritems():
        for label in mem.keys():
            if label in communities:
                communities[label].add(node)
            else:
                communities[label] = set([node])
    '删掉嵌套的社团'
    # Remove nested communities
    nestedCommunities = set()
    keys = communities.keys()
    for i, label0 in enumerate(keys[:-1]):
        comm0 = communities[label0]
        for label1 in keys[i + 1:]:
            comm1 = communities[label1]
            if comm0.issubset(comm1):
                nestedCommunities.add(label0)
            elif comm0.issuperset(comm1):
                nestedCommunities.add(label1)

    for comm in nestedCommunities:
        del communities[comm]

    return communities

import communityLouvain as BGLL
def newSLPAwauto(G,T=100):
    egoLabelsNum={}
    egoLabelsNum=egoLabelsNum.fromkeys(G.nodes(),1)
    for ego in G.nodes():
        ego_minus_ego=nx.ego_graph(G,ego,1,False)
        '利用非重叠的BGLL'
        partition = BGLL.best_partition(ego_minus_ego)
        '将partion换成community'
        community_to_nodes = defaultdict(list)
        for node, comID in partition.items():
            community_to_nodes[comID].append(node)
        '将ego加入每个社团'
        for com in community_to_nodes.values():
            com.append(ego)
        '记录ego的标签个数'
        egoLabelsNum[ego] = len(community_to_nodes)
    '再用SLPAwAuto'
    communities=SLPAwAuto(G, T,egoLabelsNum)
    return communities



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
    # G=nx.karate_club_graph()
    # for edge in G.edges():
    #     G.edge[edge[0]][edge[1]]['weight']=1
    # res=SLPA(G,1000,0.3)
    # Qov = compute_overlap_modularity_cxm(G, res.values())
    # print res
    # print Qov

    '读文件'
    inPath='L:/CDdata/Realdata/'
    dataList = ['karate', 'highschool', 'netsci', 'books', 'dolphins', 'football', 'jazz', 'email', 'lesmis', 'PGP',
                'congress', 'cora', 'citeseer', 'imdb']
    dataList2=['cora','citeseer','congress','imdb']
    dataList3=['PGP']
    for dataName in dataList:
        print dataName,'...'
        outpath = inPath + 'SLPA/'+dataName+'_res'
        edgeFile=inPath+dataName+'_edges'
        G = nx.read_edgelist(edgeFile,nodetype=int)
        res=SLPA(G,100,0.1)
        # res=newSLPAwauto(G,100)
        '将结果输出'
        dataWriter(res.values(),outpath)