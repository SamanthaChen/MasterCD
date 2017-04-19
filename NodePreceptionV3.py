# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:NodePreception.py
@time:2017/3/239:59
@节点过滤算法
g改进，添加变色龙算法
给节点排序？？
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
from math import exp


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
def computeCentrilityandSort(G):
    '''
    计算节点中心度
    :param G:
    :return:
    '''
    G=nx.Graph()
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
                tmpdensity=pow(exp,-pow((float(maxCoreness)/float(coreDict[nei])),2))
            densityDict[n]+=tmpdensity
            ##计算邻居中最小的core
            if coreDict[nei]<mindistance:
                mindistance=coreDict[nei]
        distanceDict[n]=mindistance
        totalDict[n]=distanceDict[n]*densityDict[n]
    #按分数排序




def runNodePreception(G,simThreshold,slpar=0.3):
    '''
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


    visitedSequece=computeCentrilityandSort(G)
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
    for ego in visitedSequece:
        if(visiteFlag[ego]==False):
            ego_minus_ego=nx.ego_graph(G,ego,1,center=False) ##不包含ego节点，1跳邻居
            '访问标志'
            for n in ego_minus_ego:
                visiteFlag[n]=True
            visiteFlag[ego]=True
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
        else:
            continue

    '3:对超图H进行社团搜索'
    hcommunities=SLPAw(H,100,slpar,True)

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
    sim=0.05 ###超图的相似度超多少才有边
    inPath='L:/CDdata/Realdata/'
    dataList=['karate','highschool','netsci','books','dolphins','football','jazz','email','adjnoun','lesmis','congress'] ##  'PGP','facebook','amazon'
    for dataName in dataList:
        outpath = inPath + 'NPV2/'+dataName+'_res'
        edgeFile=inPath+dataName+'_edges'
        G = nx.read_edgelist(edgeFile,nodetype=int)
        # res=runNodePreception(G,sim)
        res = runNPChameleon(G)
        '将结果输出'
        dataWriter(res.values(),outpath)
        # print res
        Qov=compute_overlap_modularity_cxm(G,res.values())
        print Qov




