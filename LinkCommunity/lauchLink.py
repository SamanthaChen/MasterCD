# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:lauchLink.py
@time:2017/3/2914:24
"""
import sys, os
from copy import copy
from operator import itemgetter
from heapq import heappush, heappop
from collections import defaultdict
from itertools import combinations, chain # requires python 2.6+
from optparse import OptionParser
from link_clustering import *

threshold = 0.5
is_weighted = False
dendro_flag = False
delimiter=' '
basename=''

print "# loading network from edgelist..."
basename = os.path.splitext(args[0])[0]
if is_weighted:
    adj, edges, ij2wij = read_edgelist_weighted(args[0], delimiter=delimiter)
else:
    adj, edges = read_edgelist_unweighted(args[0], delimiter=delimiter)

# run the method:
if threshold is not None:
    if is_weighted:
        edge2cid, D_thr = HLC(adj, edges).single_linkage(threshold, w=ij2wij)
    else:
        edge2cid, D_thr = HLC(adj, edges).single_linkage(threshold)
    print "# D_thr = %f" % D_thr
    write_edge2cid(edge2cid, "%s_thrS%f_thrD%f" % (basename, threshold, D_thr), delimiter=delimiter)
else:
    if is_weighted:
        edge2cid, S_max, D_max, list_D = HLC(adj, edges).single_linkage(w=ij2wij)
    else:
        if dendro_flag:
            edge2cid, S_max, D_max, list_D, orig_cid2edge, linkage = HLC(adj, edges).single_linkage(
                dendro_flag=dendro_flag)
            write_dendro("%s_dendro" % basename, orig_cid2edge, linkage)
        else:
            edge2cid, S_max, D_max, list_D = HLC(adj, edges).single_linkage()

    f = open("%s_thr_D.txt" % basename, 'w')
    for s, D in list_D:
        print >> f, s, D
    f.close()
    print "# D_max = %f\n# S_max = %f" % (D_max, S_max)
    write_edge2cid(edge2cid, "%s_maxS%f_maxD%f" % (basename, S_max, D_max), delimiter=delimiter)