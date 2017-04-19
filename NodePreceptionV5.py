# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:NodePreception.py
@time:2017/3/239:59
@节点过滤算法
g改进，添加变色龙算法
给节点排序？？
（2017.3.26）根据ego网络的划分情况，为后面预处理自动筛选标签
"""
import networkx as nx
import random
from collections import defaultdict
import numpy as np
from overlapping_modularity import compute_overlap_modularity_cxm
from overlapping_modularity import  compute_overlap_modularity
from SLPAw import SLPA,SLPAw
import communityLouvain as BGLL
import copy
from math import exp,pow,e
import matplotlib.pyplot as plt


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

def overlappingLPA(ego_minus_ego, ego, max_iteration=100,weighted=False):
    """
    频率最大的标签储存多个的重叠LPA,按顺序遍历
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
        '节点遍历的顺序'
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

def computeCentrilityandSort(G):
    '''
    计算节点中心度
    :param G:
    :return:
    '''

    '计算coreness'
    coreDict=nx.core_number(G)
    '求最大core'
    maxCoreness=max(coreDict.values())
    '计算每个节点的中心度'
    densityDict={}
    densityDict=densityDict.fromkeys(G.nodes(),0.0)
    distanceDict={}
    distanceDict=distanceDict.fromkeys(G.nodes(),0.0)
    totalDict={}
    totalDict=totalDict.fromkeys(G.nodes(),0.0)
    for n in G.nodes():
        mindistance=maxCoreness
        for nei in nx.neighbors(G,n):
            #计算单个邻居贡献的密度
            tmpdensity=0
            if coreDict[nei]!=0:
                tmp=float(maxCoreness)/float(coreDict[nei])
                tmp=pow(tmp,2)
                tmpdensity=pow(e,-tmp)
            densityDict[n]+=tmpdensity
            ##计算邻居中最小的core
            if coreDict[nei]<mindistance:
                mindistance=coreDict[nei]
        distanceDict[n]=mindistance
        totalDict[n]=distanceDict[n]*densityDict[n]
    #按分数排序

    sortedD=sorted(totalDict.items(),key=lambda d:d[1],reverse=True)
    visitedSequence=[val[0] for val in sortedD]
    print '原来的总分：'
    print sortedD
    # print 'density:'
    # print sorted(densityDict.items(),key=lambda  d:d[1],reverse=True)
    # degrees=G.degree(G.nodes())
    # print 'degree:'
    # print sorted(degrees.items(), key=lambda d: d[1], reverse=True)
    # res={}
    # for n in G.nodes():
    #     res[n]=densityDict[n]*degrees[n]
    # print 'res:'
    # print sorted(res.items(),key=lambda  d:d[1],reverse=True)
    return  visitedSequence


def computeCentrilityandSort2(G):
    '''
    计算节点中心度
    :param G:
    :return:
    '''

    '计算coreness'
    coreDict=nx.core_number(G)
    degrees = G.degree(G.nodes())
    '求最大core'
    maxCoreness=max(coreDict.values())
    '计算每个节点的中心度'
    densityDict={}
    densityDict=densityDict.fromkeys(G.nodes(),0.0)
    distanceDict={}
    distanceDict=distanceDict.fromkeys(G.nodes(),0.0)
    totalDict={}
    totalDict=totalDict.fromkeys(G.nodes(),0.0)
    for n in G.nodes():
        mindistance=maxCoreness
        tmpdensity=0
        for nei in nx.neighbors(G,n):
            #计算单个邻居贡献的密度
            tmpdensity+=coreDict[nei]
            ##计算邻居中最小的core
            if coreDict[nei]<mindistance:
                mindistance=coreDict[nei]
        densityDict[n] = float(tmpdensity)/float(degrees[n])
        distanceDict[n]=mindistance
        totalDict[n]=distanceDict[n]*densityDict[n]
    #按分数排序

    sortedD=sorted(totalDict.items(),key=lambda d:d[1],reverse=True)
    visitedSequence=[val[0] for val in sortedD]
    print '原来的总分：'
    print sortedD
    print 'density:'
    print sorted(densityDict.items(),key=lambda  d:d[1],reverse=True)
    print 'distance:'
    print sorted(distanceDict.items(),key=lambda  d:d[1],reverse=True)
    print 'degree:'
    print sorted(degrees.items(), key=lambda d: d[1], reverse=True)
    # res={}
    # for n in G.nodes():
    #     res[n]=densityDict[n]*degrees[n]
    # print 'res:'
    # print sorted(res.items(),key=lambda  d:d[1],reverse=True)
    return  visitedSequence

def computeCentrilityandSort3(G):
    '''
    计算节点中心度
    :param G:
    :return:
    '''
    '计算coreness'
    coreDict=nx.core_number(G)
    degrees = G.degree(G.nodes())
    '求最大core'
    maxCoreness=max(coreDict.values())
    '计算每个节点的中心度'
    densityDict={}
    densityDict=densityDict.fromkeys(G.nodes(),0.0)
    distanceDict={}
    distanceDict=distanceDict.fromkeys(G.nodes(),0.0)
    totalDict={}
    totalDict=totalDict.fromkeys(G.nodes(),0.0)
    for n in G.nodes():
        mindistance=maxCoreness
        tmpdensity=0
        for nei in nx.neighbors(G,n):
            # 计算单个邻居贡献的密度
            '影响范围为邻居度的高斯密度之和'
            tmpdensity = 0
            if coreDict[nei] != 0:
                tmp = float(degrees[n]) / float(degrees[nei])
                tmp = pow(tmp, 2)
                tmpdensity = pow(e, -tmp)
            densityDict[n] += tmpdensity
            ##计算邻居中最小的core
            if coreDict[nei] < mindistance:
                mindistance = coreDict[nei]
        distanceDict[n] = float(mindistance)/float(maxCoreness)
        '传播能力为核值（归一化一下吧）'
        totalDict[n] = (float(coreDict[n])/float(maxCoreness)) * densityDict[n]
    #按分数排序

    sortedD=sorted(totalDict.items(),key=lambda d:d[1],reverse=True)
    visitedSequence=[val[0] for val in sortedD]
    print '原来的总分：'
    print sortedD
    print 'density:'
    print sorted(densityDict.items(),key=lambda  d:d[1],reverse=True)
    print 'distance:'
    print sorted(distanceDict.items(),key=lambda  d:d[1],reverse=True)
    print 'degree:'
    print sorted(degrees.items(), key=lambda d: d[1], reverse=True)
    # res={}
    # for n in G.nodes():
    #     res[n]=densityDict[n]*degrees[n]
    # print 'res:'
    # print sorted(res.items(),key=lambda  d:d[1],reverse=True)
    return  visitedSequence

def runOrderedNodePreceptionAutoslpar(G,simThreshold):
    '''
    有访问顺序，改成自动筛选slpa的r值？？？？
    :param G: 输入的图
    :param simThreshold: 构建新的图的相似度
    :return: 二维数组的社团列表结构
    '''
    '1.初始化社团标号为自己,注意一个点可以属于多个社团'
    for n in G.nodes():
        G.node[n]['communities']=[n]

    '2.给节点排序'
    #按节点的度降序排序
    # visitedSequece=sorted(G.nodes(),key=lambda n:G.degree(n),reverse=True)
    #按节点核值排序
    # coreDict = nx.core_number(G)
    # print coreDict
    # visitedSequece = [t[0] for t in sorted(coreDict.items(),key=lambda d:d[1],reverse=True)]
    # print visitedSequece


    visitedSequece=computeCentrilityandSort3(G)
    #存储节点是否该访问的标志
    visiteFlag={}
    for n in G.nodes():
        visiteFlag[n]=False #所有节点初始化
    '初始化'
    allSubCommunities=[] ##所有的子社团
    H=nx.Graph() ##重新构建的子图
    subcomid_to_subcom={} ##H中节点的映射到包含的suncommunity
    # subcom_to_suncomid={}
    '3.找邻居社团，构建超图构成的子图H'
    '记录本来ego的邻居赋予它的标签个数'
    egoLabelsNum={}
    egoLabelsNum=egoLabelsNum.fromkeys(G.nodes(),1)
    for ego in visitedSequece:
        if(visiteFlag[ego]==False):
            ego_minus_ego=nx.ego_graph(G,ego,1,center=False) ##不包含ego节点，1跳邻居
            '访问标志'
            for n in ego_minus_ego:
                visiteFlag[n]=True
            visiteFlag[ego]=True

            '重叠LPA'
            # community_to_nodes=overlappingLPA(ego_minus_ego,ego)

            '利用非重叠的BGLL'
            partition=BGLL.best_partition(ego_minus_ego)
            '将partion换成community'
            community_to_nodes=defaultdict(list)
            for node,comID in partition.items():
                community_to_nodes[comID].append(node)
            '将ego加入每个社团'
            for com in community_to_nodes.values():
                com.append(ego)
            '记录ego的标签个数'
            egoLabelsNum[ego]=len(community_to_nodes)
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
        else:
            continue

    '3:对超图H进行社团搜索'
    hcommunities=SLPAw(H,100,egoLabelsNum,True)

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


def runNPChameleon(G, chamelonAlpha=0.03, slpar=0.3):
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
        coms[i]=list(allSubCommunities[i])
    '3:对超图H进行社团搜索'
    communities=chameleonMerge(coms,chamelonAlpha,G)
    print communities
    return communities

def hopSortDemon(G,epsilon):
    degrees=nx.degree(G)
    # visitedSequece = computeCentrilityandSort(G)
    sortedDegree=sorted(degrees.items(),key=lambda d:d[1],reverse=True)
    visitedSequece=[val[0] for val in sortedDegree]
    # 存储节点是否该访问的标志
    visiteFlag = {}
    for n in G.nodes():
        visiteFlag[n] = False  # 所有节点初始化
    '找邻居社团，构建超图构成的子图H'
    allCommunities={}
    for ego in visitedSequece:
        if (visiteFlag[ego] == False):
            ego_minus_ego = nx.ego_graph(G, ego, 1, center=False)  ##不包含ego节点，1跳邻居
            '访问标志'
            for n in ego_minus_ego:
                visiteFlag[n] = True
            visiteFlag[ego] = True

            '重叠LPA'
            community_to_nodes=overlappingLPA(ego_minus_ego,ego)

            '合并'
            for id1,com1 in community_to_nodes.items():
                allCommunities=absoluteMerge(allCommunities,id1,com1,epsilon)
    return allCommunities


def absoluteMerge(allcommunities, id1, com1, epsilon):
    if len(allcommunities)==0:
        allcommunities[id1] = com1
        return allcommunities
    if sorted(com1) in allcommunities.values():
        return allcommunities
    else:
        for id2,com2 in allcommunities.items():
            union=None
            '计算相似度'
            if shareRate(com2, com1) >= epsilon:
                tmpset=set(com1)
                for n in com2:
                    tmpset.add(n)
                tmpset=list(tmpset)
                tmpset=sorted(tmpset)
                union=tmpset
                allcommunities[id2]=union
            if union is None:
                allcommunities[id1]=com1
        return allcommunities






def shareRate(list1, list2):
    res = 0.0
    len1 = len(list1)
    len2 = len(list2)
    if (len1 < len2):
        count = 0
        for i in list1:
            for j in list2:
                if j == i:
                    count += 1
        if count > 0:
            res = float(count) / float(len1)
    else:
        count = 0
        for i in list1:
            for j in list2:
                if j == i:
                    count += 1
        if count > 0:
            res = float(count) / float(len2)
    return res


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

def chameleonMerge(subcommunities,minIC,G,weight=False):
    '''
    两阶段聚类
    :param communities:  字典格式
    :param minIC:最小的连通阈值
    :return:
    '''
    #计算簇内连通性
    ECInner={}
    for id,com in subcommunities.items():
        temp=0.0
        for n1 in com:
            for n2 in com:
                if (n1!=n2 and G.has_edge(n1,n2)):
                    if weight:
                        temp+=G.edge[n1][n2]['weight']
                    else:
                        temp+=1

        ECInner[id]=temp
    #设置结束flag
    end = True
    #计算簇之间连通性
    #为了防止删除错误，做一个拷贝
    subcommunitiesCopy=copy.deepcopy(subcommunities)
    allCommunities={}
    for comID,com in subcommunitiesCopy.items():
        allCommunities=mymerge(allCommunities,comID,com,minIC,ECInner,weight,G)
    return allCommunities


def mymerge(allCommunities,comID,com,minIC,ECInner,weight,G):
    '合并社团'
    if sorted(com) in allCommunities.values():
        return allCommunities
    else:
        inserted=False
        for testID,testcom in allCommunities.items():
            '计算是否能合并'
            union=None
            ECouter=0
            # 计算权重之和EC
            for n1 in testcom:
                for n2 in com:
                    if (n1 != n2 and G.has_edge(n1, n2)):
                        if weight:
                            ECouter+= G.edge[n1][n2]['weight']
                        else:
                            ECouter += 1
            #计算相对近似行
            RI = 0
            if (ECInner[comID] + ECInner[testID]) > 0:
                RI = 2 * ECouter / (ECInner[comID] + ECInner[testID])
            RC = 0
            if (len(com) * ECInner[comID] + len(testcom) * ECInner[testID]) > 0:
                RC = (len(com) + len(testcom)) * ECouter / (len(com) * ECInner[comID] + len(testcom) * ECInner[testID])
            # 符合条件进行合并
            if RI * RC > minIC:
                tmp=set()
                for n in com:
                    tmp.add(n)
                for n in testcom:
                    tmp.add(n)
                union=sorted(list(tmp))
                ##合并完更新簇连通性
                RItmp=ECInner[testID]
                RItmp+=ECInner[comID]
                for n1 in com:
                    for n2 in testcom:
                        if (n1 != n2 and G.has_edge(n1, n2)):
                            if weight:
                                RItmp += G.edge[n1][n2]['weight']
                            else:
                                RItmp += 1
                ECInner[comID]=RItmp
            if union is not None:
                allCommunities.pop(testID)
                allCommunities[comID]=union
                inserted=True
                break
        #假如没有合并，将原来社团之间放到结果中
        if not inserted:
            allCommunities[comID]=com
        return allCommunities


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
    sim=0.08###超图的相似度超多少才有边
    inPath='L:/CDdata/Realdata/'
    dataList=['karate','highschool','netsci','books','dolphins','football','jazz','email','adjnoun','lesmis','congress'] ##  'PGP','facebook','amazon'
    dataList2=['PGP','facebook','amazon']
    for dataName in dataList:
        print dataName
        outpath = inPath + 'demon/'+dataName+'_res'
        edgeFile=inPath+dataName+'_edges'
        G = nx.read_edgelist(edgeFile,nodetype=int)
        '传统的'
        # res=runOrderedNodePreception(G,sim,slpar=0.5)
        'demon'
        res=hopSortDemon(G,0.6)
    #     '变色龙'
    #     # res = runNPChameleon(G)
    #     '将结果输出'
        dataWriter(res.values(),outpath)
        # print res
        Qov=compute_overlap_modularity_cxm(G,res.values())
        print Qov


    # G=nx.karate_club_graph()
    # l=computeCentrilityandSort3(G)
    # '画图'
    # pos=nx.spring_layout(G)
    # for i in range(len(l)):
    #     c=i
    #     nx.draw_networkx_nodes(G, pos, [l[i]], node_color=c,alpha=0.5,vmin=0.0,vmax=1.0)
    # nx.draw_networkx_edges(G, pos,width=1,alpha=0.5)
    # nx.draw_networkx_labels(G,pos,font_size=12)
    # plt.show()





