# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:Test.py
@time:2017/3/1516:42
"""

################################################
###                  Demon 算法实现
# 采用两阶段聚类算法的合并方式
#2016.2.20
###################################################
import time

import networkx as nx

import LabelPropagation as LPA

#import math
#import DistanceDynamic_V1 as DD
import DrawCommunity
##########################"打印社团"##################
def printcommunities(dict):
    for k,v in dict.items():
        s=''
        for vv in v:
            s=s+str(vv)+" "
        print("label: "+str(k)+" size: "+str(len(v))+" community: "+s )

##################抽取邻居网络###################
def friendNetwork(G,node):
    nodeego = nx.ego_graph(G,node)
    nodeego.remove_node(node)
    return nodeego
##################计算两个社团的不包含比例,若符合参数要求则合并，否则返回none###################
def notIncludeMerge(com1,com2,epsilon):
    if len(com1)<len(com2):#小社团是com1
        count = 0
        notincludepart=[] #存储小社团不在大社团的部分
        for n1 in com1:
            if n1 not in com2:
                count=count+1
                notincludepart.append(n1)
        if count/len(com1)<epsilon:
            for nn in notincludepart:
                com2.append(nn)
            return com2
        else: return None
    else:#小社团是com2
        count = 0
        notincludepart=[] #存储小社团不在大社团的部分
        for n2 in com2:
            if n2 not in com1:
                count=count+1
                notincludepart.append(n2)
        if count/len(com2)<epsilon:
            for nn in notincludepart:
                com1.append(nn)
            return com1
        else: return None


###################DEMON合并社团#####################
def absoluteMerge(communities,com,epsilon):
    idx = len(communities)
    #加入一开始社团为0，直接添加并返回，否则执行后面的合并步骤
    if idx==0:
        communities[idx]=com
        return communities
    #只有一开始社团不为0才执行下面
    mergeflag=False #存储社团com是否发生合并的标志
    for i in range(idx):
        mergeres=notIncludeMerge(communities[i],com,epsilon)
        if mergeres!=None:
            communities[i]=mergeres
            mergeflag=True
    if mergeflag==False:
        communities[idx]=com #还没有被合并过，则添加社团（这里假设community的编号0开始）
    return communities




####################第二阶段：递归合并子社团###############
def cluster(communities,minIC):
    #计算簇内连通性
    EC1={}
    for id,com in communities.items():
        temp=0.0
        for n1 in com:
            for n2 in com:
                if(n1!=n2 and G.has_edge(n1,n2)):
                    temp+=G[n1][n2]['weight']
                if(n1!=n2 and G.has_edge(n2,n1)):
                    temp+=G[n2][n1]['weight']
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
                        if(G.has_edge(n1,n2)):
                            EC=EC+G.edge[n1][n2]['weight']
                        if(G.has_edge(n2,n1)):
                            EC=EC+G.edge[n2][n1]['weight']
                RI=2*EC/(EC1[k1]+EC1[k2])
                RC=(len(com1)+len(com2))*EC/(len(com1)*EC1[com1]+len(com2)*EC1[com2])
                #符合条件进行合并
                if RI*RC>minIC:
                    communities[k1].extend(communities[k2])
                    del communities[k2]
                    end =False
                    break
    #递归合并
    if(end==False):
        cluster(communities,minIC)
    else:
        return communities

####################算法主体###############
def run(G,minIC):
    #算法第一阶段，先求出小社团
    communities = {} #存储ego社团发现的小社团
    comid=0
    for n in G.nodes():
        egon = friendNetwork(G,n)#抽取节点n的邻居网络
        egoncomm = LPA.run(egon) #利用LPA算法获得邻居网络构成的社团
        for com in egoncomm.values():
            com.append(n) #将ego也加入网络中
            communities[comid]=com
            comid=comid+1
             #先存储小社团
    #算法第二阶段，将小社团进行合并
    cluster(communities,minIC)
    return communities


if __name__ == '__main__':
    ###合并参数
    minIC=0.2
    G=nx.Graph()
    ##原来论文小例子
    #G.add_nodes_from([1,2,3,4,5,6,7,8,9,10,1,12,13,14,15,16,17,18,19])
    #G.add_edges_from([(1,2),(2,3),(2,4),(2,6),(3,4),(3,6),(4,5),(4,6),(4,7),(5,6),(7,8),(7,11),(8,11),(8,9),(9,10),(9,11),(10,11),(3,13),(6,14),(9,15),(12,13),(13,14),(14,15),(15,16),(16,17),(17,18),(13,18),(14,18),(14,17),(14,16),(15,17),(17,19)],weight=0)
    #G=nx.karate_club_graph()
    G.add_nodes_from(range(0,13,1))
    # G.add_edges_from([(0,1),(0,4),(0,5),(0,6),(1,2),(1,5),(2,3),(2,5),(3,4),(3,5),(3,6),(4,5),(4,6),(6,7),(6,10),(6,11),(7,8),(7,11),(7,12),(8,9),(8,12),(9,10),(9,12),(9,13),(10,11),(10,12),(11,12)])
    #无向图边的权重默认为1
    G.add_edges_from([(0,1),(0,4),(0,5),(0,6),(1,2),(1,5),(2,3),(2,5),(3,4),(3,5),(3,6),(4,5),(4,6),(6,7),(6,10),(6,11),(7,8),(7,11),(7,12),(8,9),(8,12),(9,10),(9,12),(9,13),(10,11),(10,12),(11,12)],weight=1.0)
    #path="D:\LFR data/20160113\overlap\small\mu"
    #infile=open(path+"/network_mu80_on100_om5.dat")
    #G=nx.read_edgelist(infile,nodetype=int)
    #infile.close()
    start=time.clock()  #计算程序初始运行时间
    communities=run(G,minIC)
    end=time.clock() #程序结尾运行时间
    print("time:%fs"%(end-start)) #程序运行时间

    ######################输出社团#################
 #   outfile=path+"\PDemon\PDmu80"
 #   utility.writedict2file(communityDict,outfile)

    ######################打印社团#################
    printcommunities(communities)
    DrawCommunity.run(G,communities)
    ######################计算NMI#####################
    #读取社团文件
    #infile2 = open(path+"\community_mu0_10.dat",'rb')
    #ground_truth=utility.readcom2dict(infile2)
    #infile2.close()
    #for k,v in communityDict.items():
     #   communityDict[k]=sorted(v)
    #ground_truth=[[1,2,3,4,5,6,7,8,9,11,12,13,14,17,18,20,22],[10,15,16,19,21,23,24,25,26,27,28,29,30,31,32,33,34]] #karate的ground_truth
    #ground_truth={0:[0,1,2,3,4,5,6,7,8,10,11,12,13,16,17,19,21],1:[9,14,15,18,20,22,23,24,25,26,27,28,29,30,31,32,33]} #karate的ground_truth
    #print NMIMeasure.dictNMI(communityDict,ground_truth,len(G.nodes()))