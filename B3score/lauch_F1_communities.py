# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:lauch_F1_communities.py
@time:2017/3/2714:01
"""
from F1_communities import  *
args = parser.parse_args()

def run(community,groundtruth,plotPic=False):
    fc = F1_communities(community, groundtruth)
    prl_list = None
    try:
        prl_list = fc.get_precision_recall()
    except Exception:
        '将文件转换为社团'
        fc.convert_coms(groundtruth)
        fc = F1_communities(community, "%s_r" % groundtruth)
        prl_list = fc.get_precision_recall()

    mean, std, mx, mn, mode = fc.get_f1(prl_list)
    'Node Coverage ，Ground Truth Communities，Identified Communities ，'
    coverage, gt_coms, id_coms, ratio_coms, node_coverage, redundancy = fc.get_partition_stats()

    quality = fc.get_quality(mean, coverage, redundancy)

    # print "          Partition Info          "
    # print "Ground Truth Communities : %d" % gt_coms
    # print "Identified Communities   : %d" % id_coms
    # print "Community Ratio          : %.3f" % ratio_coms
    # print "Ground Truth Matched     : %.3f" % coverage
    # print "Node Coverage            : %.3f" % node_coverage
    # print "-----------------------------------"
    # print "      Matching Quality (F1)        "
    # print "Min    : %.3f" % mn
    # print "Max    : %.3f" % mx
    # print "Mode   : %.3f" % mode
    # print "Avg    : %.3f" % mean
    # print "Std    : %.3f" % std
    # print "-----------------------------------"
    # print "          Overall Quality          "
    print "Quality: %.3f" % quality
    print "-----------------------------------"

    '画图'
    if plotPic is not False:
        fc.plot(prl_list, max_points=args.maxpts, title=args.title, fileout=args.outfile)
        print "-----------------------------------"

if __name__=='__main__':
    run()