#!/usr/bin/python

import networkx as nx
from networkx.readwrite import json_graph

def load_graph(graph_edges):
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
    return nodes_degree,graph.edges()


def main():
    #g = load_graph(edges)
    g = nx.karate_club_graph()

if __name__ == "__main__":
    main()
