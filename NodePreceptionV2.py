# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:NodePreception.py
@time:2017/3/239:59
@节点过滤算法
"""
import networkx as nx
import random
from collections import defaultdict
import numpy as np
from overlapping_modularity import compute_overlap_modularity_cxm
from overlapping_modularity import  compute_overlap_modularity
from SLPAw import SLPA,SLPAw
import communityLouvain as BGLL


# def node_preception():
def overlappingLPA(ego_minus_ego, ego, max_iteration=100,weighted=False):
    """
    频率最大的标签储存多个的重叠LPA
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
        '遍历每个节点，进行标签传播'
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
        '注意c_n是list，因此一个节点可以同时属于多个标签'
        c_n = ego_minus_ego.node[n]['communities']
        for c in c_n:
            if c in community_to_nodes:
                com = community_to_nodes.get(c)
                com.append(n)
            else:
                nodes = [n, ego]
                community_to_nodes[c] = nodes

    return community_to_nodes

def jaccardSim(list1,list2):
    '''
    计算两个list的jaccard相似度，不考虑邻居的那种
    :param list1:
    :param list2:
    :return:
    '''
    intersect=0
    union=len(list1)
    for i in list2:
        if i in list1:
            intersect+=1
        else:
            union+=1
    res=0
    if union>0: #防止除0
        res=float(intersect)/float(union)
    return res


def runNodePreception(G,simThreshold,slpar=0.3):
    '''
    :param G: 输入的图
    :param simThreshold: 构建新的图的相似度
    :return: 二维数组的社团列表结构
    '''
    '1.初始化社团标号为自己,注意一个点可以属于多个社团'
    for n in G.nodes():
        G.node[n]['communities']=[n]

    '2.找邻居社团，构建超图构成的子图H'
    allSubCommunities=[] ##所有的子社团
    H=nx.Graph() ##重新构建的子图
    subcomid_to_subcom={} ##H中节点的映射到包含的suncommunity
    # subcom_to_suncomid={}
    for ego in G.nodes():
        ego_minus_ego=nx.ego_graph(G,ego,1,center=False) ##不包含ego节点，1跳邻居
        '利用非重叠的BGLL'
        # community_to_nodes=overlappingLPA(ego_minus_ego,ego)
        partition=BGLL.best_partition(ego_minus_ego)
        '将partion换成community'
        community_to_nodes=defaultdict(list)
        for node,comID in partition.items():
            community_to_nodes[comID].append(node)
        '将ego加入每个社团'
        for com in community_to_nodes.values():
            com.append(ego)

        '相同的子社团只允许出现一次'
        for subcom in  community_to_nodes.values():
            sortedCom=tuple(sorted(subcom)) ##先给节点排个序
            if not sortedCom in allSubCommunities:
                '还没有该社团'
                allSubCommunities.append(sortedCom) ##加入一个社团
                id=len(allSubCommunities)-1 ##社团编号
                # subcom_to_suncomid[sortedCom]=id ##subcom社团到id的映射
                subcomid_to_subcom[id]=sortedCom  ##H的id到suncom的映射
                '创造H的节点'
                Hnodes=H.nodes()
                H.add_node(id)
                '创造id与其他节点的边'
                for n in Hnodes:
                    com=allSubCommunities[n]
                    sim=jaccardSim(sortedCom,com)
                    if sim>simThreshold:
                        '边不需要考虑方向'
                        H.add_edge(id,n,weight=sim)
            else:
                '该社团已经有过了'
                continue

    '3:对超图H进行社团搜索'
    hcommunities=SLPAw(H,100,slpar,False)

    '4:后处理，将超图节点还原成原来节点'
    allCommunities=[]
    for hcom in hcommunities.values():
        com=set()
        for hnode in hcom:
           subcom=subcomid_to_subcom[hnode]
           for i in subcom:
               com.add(i)
        sortedtmp=sorted(list(com))
        allCommunities.append(sortedtmp)
    return  allCommunities


def runNPChameleon(G, chamelonAlpha=0.1, slpar=0.3):
    '''
    :param G: 输入的图
    :param simThreshold: 构建新的图的相似度
    :return: 二维数组的社团列表结构
    '''
    '1.初始化社团标号为自己,注意一个点可以属于多个社团'
    for n in G.nodes():
        G.node[n]['communities'] = [n]

    '2.找邻居社团，构建超图构成的子图H'
    allSubCommunities = []  ##所有的子社团
    H = nx.Graph()  ##重新构建的子图
    subcomid_to_subcom = {}  ##H中节点的映射到包含的suncommunity
    subcom_to_suncomid = {}
    for ego in G.nodes():
        ego_minus_ego = nx.ego_graph(G, ego, 1, center=False)  ##不包含ego节点，1跳邻居
        '重叠LPA算法找ego网络的社团'
        # community_to_nodes=overlappingLPA(ego_minus_ego,ego)

        'splaw找'
        community_to_nodes = SLPA(ego_minus_ego, 100, slpar)
        '将ego加入所有的subcomunity里面'
        for com in community_to_nodes.values():
            com.add(ego)

        '相同的子社团只允许出现一次'
        for subcom in community_to_nodes.values():
            sortedCom = tuple(sorted(subcom))  ##先给节点排个序
            if not sortedCom in allSubCommunities:
                '还没有该社团'
                allSubCommunities.append(sortedCom)  ##加入一个社团
            else:
                '该社团已经有过了'
                continue
    coms={}
    for i in range(len(allSubCommunities)):
        coms[i]=allSubCommunities[i]
    '3:对超图H进行社团搜索'
    communities=chameleonMerge(coms,chamelonAlpha,G)
    print communities


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

def chameleonMerge(communities,minIC,G,weight=False):
    '''
    两阶段聚类
    :param communities:  字典格式
    :param minIC:
    :return:
    '''
    #计算簇内连通性
    EC1={}
    for id,com in communities.items():
        temp=0.0
        for n1 in com:
            for n2 in com:
                if (n1!=n2 and G.has_edge(n1,n2)):
                    if weight:
                        temp+=G.edge[n1][n2]['weight']
                    else:
                        temp+=1

        EC1[id]=temp
    #设置结束flag
    end = True
    #计算簇之间连通性
    for k1,com1 in communities.items():
        for k2,com2 in communities.items():
            if(com1!=com2):
                #分别计算RI，CI
                EC=0.0
                RI=0.0
                SEC=0.0
                RC=0.0
                #计算权重之和EC
                for n1 in com1:
                    for n2 in com2:
                        if (n1 != n2 and G.has_edge(n1, n2)):
                            if weight:
                                EC += G.edge[n1][n2]['weight']
                            else:
                                EC += 1
                RI=0
                if (EC1[k1]+EC1[k2])>0:
                    RI=2*EC/(EC1[k1]+EC1[k2])
                RC=0
                if (len(com1)*EC1[com1]+len(com2)*EC1[com2])>0:
                    RC=(len(com1)+len(com2))*EC/(len(com1)*EC1[com1]+len(com2)*EC1[com2])
                #符合条件进行合并
                if RI*RC>minIC:
                    communities[k1].extend(communities[k2])
                    del communities[k2]
                    end =False
                    break
    #递归合并
    if(end==False):
        chameleonMerge(communities,minIC,G,weight)
    else:
        return communities




if __name__=='__main__':
    # G=nx.karate_club_graph()
    # runNPChameleon(G)
    # for edge in G.edges():
    #     G.edge[edge[0]][edge[1]]['weight']=1
    # res=SLPA(G,1000,0.3)
    # Qov = compute_overlap_modularity_cxm(G, res.values())
    # print res
    # print Qov
    '读文件'
    sim=0.05 ###超图的相似度超多少才有边
    inPath='L:/CDdata/Realdata/'
    dataList=['karate','highschool','netsci','books','dolphins','football','jazz','email','adjnoun','lesmis','congress'] ##  'PGP','facebook','amazon'
    for dataName in dataList:
        outpath = inPath + 'NPV2/'+dataName+'_res'
        edgeFile=inPath+dataName+'_edges1'
        G = nx.read_edgelist(edgeFile,nodetype=int)
        res=runNodePreception(G,sim)
        '将结果输出'
        dataWriter(res,outpath)
        # print res
        Qov=compute_overlap_modularity_cxm(G,res)
        print Qov




