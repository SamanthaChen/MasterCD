# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:QulitiesTextDealer.py
@time:2017/4/717:53
"""
def printAllQulities():
    algo='SLPA'
    infile='L:/Cddata/RealData/'+algo+'/Qulities.txt'
    rf=open(infile,'r')
    allLines=rf.readlines()
    lineNum=0
    allList={}
    for lineNum in range(0,len(allLines),13):
        '数据行'
        dataline=allLines[lineNum]
        dataline=dataline.replace('*','').replace('=','\t')
        dataParts=dataline.strip().split('\t')
        data=dataParts[-1]
        allList[data]={} ##二维列表
        '后面各种参数行'
        for count in range(1,13):
            Qline=allLines[lineNum+count]
            Qline=Qline.replace(' ','').replace(',','').replace('=','\t')
            # print Qline
            QParts=Qline.strip().split('\t')
            # print QParts
            allList[data][QParts[0]]=float(QParts[-1])

    "一个参数一个参数打印"
    dataList=['karate','highschool','netsci','books','dolphins','football','jazz','email','lesmis','PGP','congress','cora','citeseer','imdb']
    Qlist=['Q','NQ','Qds','intraEdges','intraDensity','contraction','interEdges','expansion','conductance','fitness','modularityDegree','QovL']
    for Q in Qlist:
        print 'Q:',Q
        for data in dataList:
            print data,'\t',allList[data][Q]
        print '\n\n'


def printQds(algo):
    # algo = 'SLPA'
    infile = 'L:/Cddata/RealData/' + algo + '/Qulities_6.txt'
    rf = open(infile, 'r')
    allLines = rf.readlines()
    lineNum = 0
    allList = {}
    for lineNum in range(0, len(allLines), 13):
        '数据行'
        dataline = allLines[lineNum]
        dataline = dataline.replace('*', '').replace('=', '\t')
        dataParts = dataline.strip().split('\t')
        data = dataParts[-1]
        allList[data] = {}  ##二维列表
        '后面各种参数行'
        for count in range(1, 13):
            Qline = allLines[lineNum + count]
            Qline = Qline.replace(' ', '').replace(',', '').replace('=', '\t')
            # print Qline
            QParts = Qline.strip().split('\t')
            # print QParts
            allList[data][QParts[0]] = float(QParts[-1])

    "一个参数一个参数打印"
    dataList = ['karate', 'highschool', 'netsci', 'books', 'dolphins', 'football', 'jazz', 'email', 'lesmis', 'PGP',
                'congress', 'cora', 'citeseer']#'imdb'
    dataList2=['karate', 'highschool', 'netsci', 'books', 'dolphins', 'football', 'jazz', 'email', 'lesmis']
    dataList3 = ['karate', 'highschool', 'netsci', 'books', 'dolphins', 'football', 'jazz', 'email', 'lesmis', 'PGP',
                 'cora', 'citeseer']  # 'imdb'
    Qlist = ['Q', 'NQ', 'Qds', 'intraEdges', 'intraDensity', 'contraction', 'interEdges', 'expansion', 'conductance',
             'fitness', 'modularityDegree', 'QovL']


    print 'Qds:\n'
    for data in dataList3:
        print data, '\t', allList[data]['Qds']
    print '\n\n'

import os,sys
def slpaDealer():
    '''
    重命名
    :return:
    '''
    inpath='L:/CDdata/Realdata/SLPA/'
    dataList = ['karate', 'highschool', 'netsci', 'books', 'dolphins', 'football', 'jazz', 'email', 'lesmis', 'PGP',
                'congress', 'cora', 'citeseer']
    r=0.01
    for data in dataList:
        infile=inpath+'SLPAw_'+data+'_edges_run1_r'+str(r)+'_v3_T100.icpm'
        outfile=inpath+data+'_res0'
        os.rename(infile,outfile)

if __name__=='__main__':
    printQds('CPM')
    # slpaDealer()





