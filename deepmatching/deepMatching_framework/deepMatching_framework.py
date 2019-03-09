#!/usr/bin/python
import math
import sys
import numpy as np
import deepMatching as dm
import refinement as rf
import networkx as nx
import random as rd

def load_graph_from_edges_string(graph_edges):
    lines = graph_edges.strip().split('\n')
    graph = nx.Graph()
    for line in lines:
        line = line.split(' ')
        if graph.has_edge(int(line[0]) + 1,int(line[1]) + 1) == False and  graph.has_edge(int(line[1]) + 1,int(line[0]) + 1) == False:
            graph.add_node(int(line[0])+1,name=line[0])
            graph.add_node(int(line[1])+1,name=line[1])
            graph.add_edge(int(line[0]) + 1,int(line[1]) + 1)
    nodes_degree = []
    for node in graph.nodes():
        nodes_degree.append((node,graph.degree(node)))
    return nodes_degree,graph.edges(),graph


def load_graph_from_edges_file(edges_file,comment = '#',delimiter=' '):
    sf = open(edges_file)
    lines = sf.readlines()
    re_count = 0
    G = nx.Graph()
    for line in lines:
        if comment in line:
            continue
        line = line.strip().split(delimiter)
        
        if G.has_edge(int(line[0]) + 1,int(line[1]) + 1) == False and G.has_edge(int(line[1]) + 1,int(line[0]) + 1) == False:
            G.add_edge(int(line[0])+1,int(line[1]) + 1)
    sf.close()
    return G 


def maximum_consistency_matches(matches, G1, G2, nodenum_limit=7, cth = 2.0):
    '''
    Extract a sublist of matches in order to maximize the consistency between the two subgraphs. The two subgraphs 
    are extracted from the two matching graphs according to the sublist of matches. The consistency between two 
    graphs is defined as the ratio of the number of consistent edges between the two graphs over the maximun number 
    of edges of the two graphs. 
    :param matches: A list of tuple (v_i, u_i), where v_i \in G_1, u_i \in G_2
    :param G1: the matching graph
    :param G2: the matching graph
    :param nodenum_limit: The minimum number of nodes in each subgraph. 
    :param cth: The consistency threshold, a consistency below this threshold suggests a failed matching. 
    :return: A sublist of matches. An empty list represents a failed matching. 
    '''
    mcdeg = match_consistent_degree(matches, G1, G2)
    seeds = []
    for match, deg in mcdeg.items():
        if deg > cth:
            seeds.append(match)
    if len(seeds) < nodenum_limit:
        seeds = []
    return seeds

def match_consistent_degree(matches, G1, G2):
    '''
    Calculate the consistent degree for each match in matches, the consistent degree is define the number of 
    consistent edges connected to the matching node in each graph.
    :param matches: A list of tuple (v_i, u_i), where v_i \in G_1, u_i \in G_2
    :param G1: the matching graph
    :param G2: the matching graph
    :return: A dict, where the keys are the matches, the values are the consistent degree defined above
    '''
    cedges = consistent_edges(matches, G1, G2)
    mcdeg = {}
    for G1_edge, G2_edge in cedges.items():
        mcdeg[(G1_edge[0], G2_edge[0])] = mcdeg.get((G1_edge[0], G2_edge[0]), 0) + 1
        mcdeg[(G1_edge[1], G2_edge[1])] = mcdeg.get((G1_edge[1], G2_edge[1]), 0) + 1
    return mcdeg



def mapping_consistency(matches, G1, G2):
    nodes1 = [item[0] for item in matches]
    nodes2 = [item[1] for item in matches]
    subG1 = G1.subgraph(nodes1)
    subG2 = G2.subgraph(nodes2)
    cedges = consistent_edges(matches, G1, G2)
    return graph_consistency(cedges, subG1, subG2)

def random_mapping_parameters_estimate(G1, G2,nodes1,nodes2):
    edge_consistency_list = []
    random_number = len(nodes1) if len(nodes1) <= len(nodes2) else len(nodes2) 

    for i in range(100):
        rd.shuffle(nodes1)
        rd.shuffle(nodes2)
        matches = [(nodes1[j], nodes2[j]) for j in range(random_number)]
        edge_consistency_list.append(mapping_consistency(matches, G1, G2))
    edge_consistency_list = np.array(edge_consistency_list)
    return (np.mean(edge_consistency_list), np.std(edge_consistency_list))



def consistent_edges(matches, G1, G2):
    '''
    Extract all the consistent edge between the two matching graphs based on the matches
    :param matches: A list of tuple (v_i, u_i), where v_i \in G_1, u_i \in G_2
    :param G1: the matching graph
    :param G2: the matching graph
    :return: A dict, where the keys are the consistent edges in G_1, the values are the consistent edges in G_2
    '''
    # matchmapping = dict([(string.atoi(match[0]), string.atoi(match[1])) for match in matches])
    matchmapping = dict([(match[0], match[1]) for match in matches])
    cedges = {}
    for edge in G1.edges():
        # print edge, (matchmapping.get(edge[0], -1), matchmapping.get(edge[1], -1))
        if G2.has_edge(matchmapping.get(edge[0], -1), matchmapping.get(edge[1], -1)):
            cedges[edge] = (matchmapping.get(edge[0]), matchmapping.get(edge[1]))
    return cedges



def graph_consistency(consistent_edges, G1, G2):
    '''
    Calculate the consistency between two graphs
    :param consistent_edges: A dict, composed of the consistent edges
    :param G1: the matching graph
    :param G2: the matching graph
    :return: the consistency, a float value between 0.0 to 1.0. 
    '''
    G1_size = G1.size()
    G2_size = G2.size()
    if G1_size == 0 or G2_size ==0:
        return 0.0
    consistent_edge_count = 0.0
    for edge in G1.edges():
        if edge in consistent_edges or (edge[1], edge[0]) in consistent_edges:
            consistent_edge_count += 1.0
    return consistent_edge_count*1.0/max(G2_size, G1_size)

def mapping_credibility(matches, G1, G2):
    nodes1 = [item[0] for item in matches]
    nodes2 = [item[1] for item  in matches]
    subG1 = G1.subgraph(nodes1)
    subG2 = G2.subgraph(nodes2)
    seed_edge_consistency = mapping_consistency(matches, subG1, subG2)
    m, s = random_mapping_parameters_estimate(subG1, subG2,nodes1,nodes2)
    # print 'mean, std', m, s
    cred = 0
    if s > 0:
        cred = (seed_edge_consistency - m) / s
    # print 'Credibility:', cred
    return cred


def enbeding_init_matching(G1, G2,matched_dic = None,embedding='DeepWalk'):
    count = 0
    matches = dm.bipartite_matching(G1, G2,dimensions=100,embedding=embedding)
    if matched_dic == None: 
        for match in matches:
            if match[0] == match[1]:
                count += 1
    else:
        for match in matches:
            if match[0] not in matched_dic:
                continue
            if matched_dic[match[0]] == match[1]:
                count += 1
    z = mapping_credibility(matches, G1, G2)
    edge_consistency = mapping_consistency(matches, G1, G2)
    return matches,z,edge_consistency

def refine_matching(init_matched_ms,G1,G2,ch = 2.0):
    matches_ms = maximum_consistency_matches(init_matched_ms, G1, G2,cth=ch)
    edge_consistency = mapping_consistency(matches_ms, G1, G2)
    #print "edge consistency:", edge_consistency
    z = mapping_credibility(matches_ms, G1, G2)
    #print "initial seeds cre: %f"%z
    count = 0
    for match in matches_ms:
        if match[0] == match[1]:
            count += 1
    accuracy = 0
    if len(matches_ms) != 0 and count != 0:
        accuracy = float(count)/len(matches_ms)
    return matches_ms, z,edge_consistency,accuracy

def propagation_matching(matched_ms,G1,G2):
    refine_match_nodes,refine_real_matched_nodes_count,refine_rate = rf.match_propagation(matched_ms,G1,G2)
    edge_consistency = mapping_consistency(refine_match_nodes, G1, G2)
    pz = mapping_credibility(refine_match_nodes, G1, G2)
    return refine_match_nodes,pz,edge_consistency

def deepmatching_for_samll_scale(g1,g2,ch=2,embedding = 'DeepWalk'):
    #g1 = load_graph_from_edges_file(g1)
    #g2 = load_graph_from_edges_file(g2)
    print "===== DeepMatching: 1. initilizating matching ====="
    #initilzation mapping
    init_ms,init_z,init_ec = enbeding_init_matching(g1, g2,embedding = embedding)

    print "===== DeepMatching: 2. Refineing matching ====="
    #refine mapping
    refine_ms,refine_z,refine_ec,refine_accuracy = refine_matching(init_ms,g1,g2,ch=ch)

    print "===== DeepMatching: 3. Propagation matching ====="
    #propagation mapping
    pg_ms,pg_z,pg_ec = propagation_matching(refine_ms,g1,g2)
    return pg_ms,pg_z,pg_ec
    

def main():
    if len(sys.argv) < 2:
        print "usage: ./deepmatching_for_small_scale.py [graph1 file] [graph2 file]"
        return

    ms,z,ec = deepmatching_for_samll_scale(sys.argv[1],sys.argv[2],embedding='DeepWalk')

    print "matched nodes:"
    print ms
    print "z score:",z
    print "edge consistency:",ec

if __name__ == "__main__":
    main()
