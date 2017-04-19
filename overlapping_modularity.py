#coding=utf-8
# 所有的id label都为int

import networkx as nx

class MCommunity:
    '''
    Modularity Community.
    '''
    def __init__(self, label):
        self.label = label
        self.members = list()  # 待确定采用list还是set 假设输入的每个community不包含重复节点

    def add_member(self, member):
        self.members.append(member)

    def get_community_size(self):
        return len(self.members)

    def get_members(self):
        return self.members

    def get_label(self):
        return self.label


class MNode:
    '''
    Modularity Node.
    '''
    def __init__(self, node_id):
        self.id = node_id
        self.neighbors = set()
        self.degree = 0
        self.communities = set()

    def add_neighbor(self, neighbor_id):
        if neighbor_id not in self.neighbors:
            self.degree += 1
            self.neighbors.add(neighbor_id)

    def add_community(self, label):
        self.communities.add(label)

    def get_degree(self):
        return self.degree

    def get_community_num(self):
        return len(self.communities)

    def get_neighbors(self):
        return self.neighbors

    def is_in(self, community_label):
        return community_label in self.communities


def compute_overlap_modularity(node_list, edge_list, community_path):
    '''
    :param node_list: A list of nodes.
    :param edge_list: A list of edges. Every edge is a tuple.
    :param community_path: the community result file path.一行是一个社团
    :return: modularity_value: the modularity value.
    '''
    nodes = dict()
    communities = list()
    node_num = len(node_list)
    nodes_clustered = set()


    '存节点'
    for i in range(0, node_num):
        nodes[node_list[i]] = MNode(node_list[i])
    '存边'
    for edge in edge_list:
        nodes[edge[0]].add_neighbor(edge[1])
        nodes[edge[1]].add_neighbor(edge[0])

    with open(community_path) as f:
        community_label = 0
        for line in f:
            if len(line.strip()) == 0:
                continue
            community = MCommunity(community_label)
            members = [int(node_id) for node_id in line.strip().split(' ')]
            for member in members:
                nodes_clustered.add(member)
            for member in members:
                community.add_member(member)
                nodes[member].add_community(community_label)
            communities.append(community)
            community_label += 1

    free_nodes = set(node_list) - nodes_clustered
    free_community = MCommunity(-1)
    for node_id in free_nodes:
        free_community.add_member(node_id)
        nodes[node_id].add_community(-1)
    communities.append(free_community)

    # compute modularity value
    community_num = len(communities)
    sum_value = 0.0
    for m_community in communities:
        members = m_community.get_members()
        if len(members) == 0:
            continue
        label = m_community.get_label()
        community_size = m_community.get_community_size()
        edge_num = 0
        local_sum = 0.0
        for node_id in members:
            node_degree = nodes[node_id].get_degree()
            if node_degree == 0:  # 孤立节点的贡献度为0
                continue
            node_community_num = nodes[node_id].get_community_num()
            neighbors = nodes[node_id].get_neighbors()
            inward = 0.0
            outward = 0.0
            for neighbor_id in neighbors:
                if nodes[neighbor_id].is_in(label):
                    inward += 1
                    edge_num += 1
                else:
                    outward += 1
            local_sum += (inward - outward) / (node_degree * node_community_num)
        local_sum = local_sum * edge_num / (community_size**2 * (community_size - 1))
        sum_value += local_sum

    return sum_value / community_num


def compute_overlap_modularity_cxm(G,communityList):
    '''
    cxm改变的版本
    :param G: networkX的版本
    :param communityList: 二维数组，一个列表是一个社团
    :return: modularity_value: the modularity value.
    '''
    nodes = dict()
    communities = list()
    nodes_clustered = set()
    node_list=G.nodes()

    '存节点'
    for i in G.nodes():
        nodes[i] = MNode(i)
    '存边'
    for edge in G.edges():
        nodes[edge[0]].add_neighbor(edge[1])
        nodes[edge[1]].add_neighbor(edge[0])

    community_label = 0 ##从0开始设置标签
    for com in communityList:
        community = MCommunity(community_label)
        members = [int(node_id) for node_id in com]
        for member in members:
            nodes_clustered.add(member)
        for member in members:
            community.add_member(member)
            nodes[member].add_community(community_label)
        communities.append(community)
        community_label += 1

    # free_nodes = set(node_list) - nodes_clustered
    # free_community = MCommunity(-1)
    # for node_id in free_nodes:
    #     free_community.add_member(node_id)
    #     nodes[node_id].add_community(-1)
    # communities.append(free_community)

    # compute modularity value
    community_num = len(communities)
    if community_num==0:
        return 0
    sum_value = 0.0
    for m_community in communities:
        members = m_community.get_members()
        if len(members) == 0:
            continue
        label = m_community.get_label()
        community_size = m_community.get_community_size()
        edge_num = 0
        local_sum = 0.0
        for node_id in members:
            node_degree = nodes[node_id].get_degree()
            if node_degree == 0:  # 孤立节点的贡献度为0
                continue
            node_community_num = nodes[node_id].get_community_num()
            neighbors = nodes[node_id].get_neighbors()
            inward = 0.0
            outward = 0.0
            for neighbor_id in neighbors:
                if nodes[neighbor_id].is_in(label):
                    inward += 1
                    edge_num += 1
                else:
                    outward += 1
            local_sum += (inward - outward) / (node_degree * node_community_num)
        local_sum = local_sum * edge_num / (community_size**2 * (community_size - 1))
        sum_value += local_sum


    return sum_value / community_num

'原来版本的'
# node_path = r""
# edge_path = r""
# community_path = r""
# node_list = list()
# edge_list = list()
# with open(node_path) as f:
#     for line in f:
#         if len(line.strip()) == 0:
#             continue
#         values = line.strip().split(',')
#         node_list.append(int(values[0]))
#
# with open(edge_path) as f:
#     for line in f:
#         if len(line.strip()) == 0:
#             continue
#         values = line.strip().split(' ')
#         edge_list.append((int(values[0]), int(values[1])))
#
# modularity_value = compute_overlap_modularity(node_list, edge_list, community_path)
# print(modularity_value)
