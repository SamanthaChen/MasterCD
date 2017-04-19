# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:linkDealer.py
@time:2017/3/2914:45
"""
def run1():
    inpath='L:/CDdata/Realdata/Link/'
    dataList = ['karate', 'highschool', 'netsci', 'books', 'dolphins', 'football', 'jazz', 'email', 'lesmis', 'PGP',
                'congress', 'cora', 'citeseer', 'imdb']
    for data in dataList:
        f=open(inpath+data+'_edges.comm2nodes.txt','r')
        w=open(inpath+data+'_res','w')
        lines=f.readlines()
        for line in lines:
            line.strip()
            words=line.split()
            newline=''
            for i in range(1,len(words)):#不考虑第一个
                newline+=words[i]+' '
            w.write(newline+'\n')

if __name__=='__main__':
    # inpath='L:/CDdata/lfrTest/smallmu/'
    # for mu in range(10,90,10):
    #     f=open(inpath+'network_mu'+str(mu)+'_link.txt','r')
    #     print inpath+'network_mu'+str(mu)+'_link.txt'
    #     w=open(inpath+'network_mu'+str(mu)+'_link.res','w')
    #     lines=f.readlines()
    #     for line in lines:
    #         line.strip()
    #         words=line.split()
    #         newline=''
    #         for i in range(1,len(words)):#不考虑第一个
    #             newline+=words[i]+' '
    #         w.write(newline+'\n')

    inpath2 = 'L:/CDdata/lfrTest/smallom/'
    for mu in range(2, 9, 1):
        f = open(inpath2 + 'network_om' + str(mu) + '_link.txt', 'r')
        w = open(inpath2 + 'network_om' + str(mu) + '_link.res', 'w')
        lines = f.readlines()
        for line in lines:
            line.strip()
            words = line.split()
            newline = ''
            for i in range(1, len(words)):  # 不考虑第一个
                newline += words[i] + ' '
            w.write(newline + '\n')
