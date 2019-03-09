#!/usr/bin/python
import numpy as np
import time as ti
import networkx as nx
from functools import partial
from scipy.io import loadmat
import matplotlib.pyplot as plt
from cpdcore import DeformableRegistration, RigidRegistration, AffineRegistration
from sklearn.decomposition import PCA
from node2vec import learn_nodevec
import time
from graph_matching import *
import sys
from deepwalk import __main__ as deepwalk
from bimatching.sparse_munkres import munkres
import datetime

def visualize(X, Y, ax=None, words = None):
    pass

def nodes_embedding_deepwalk(G, p=1, q=1, dimensions=128):
    # Extract the features for each node using deepwalk
	print "start transport the graph to deepwalk,edges: %d\tnodes: %d" % (G.number_of_edges(),G.order())

	model = deepwalk.process(G.edges(), dimensions=dimensions, number_walks = 20)
	nodes = [word for word, vcab in model.vocab.iteritems()]
	inds = [vcab.index for word, vcab in model.vocab.iteritems()]
	X = model.syn0[inds]
	return nodes,X

def nodes_embedding(G, p=1, q=1, dimensions=128, embedding='DeepWalk'):
    if embedding == 'LINE' or embedding == 'line':
        nodes,X = nodes_embedding_line(G=G, dimensions=dimensions)
        return nodes,X
    else:
        time_start = datetime.datetime.now()
        if embedding == 'DeepWalk' or embedding == 'deepwalk':
            # Extract the features for each node using deepwalk
            model = deepwalk.process(G.edges(), dimensions=dimensions, number_walks = 30)
        elif embedding == 'Node2Vec' or embedding == 'node2vec':
            # Extract the features for each node using node2vec
            model = learn_nodevec(G, dimensions=dimensions, argp=p, argq=q, num_walks=100)
        time_end = datetime.datetime.now()
        time = (time_end - time_start).seconds
        #print "Embedding time: " + str(time)
        nodes = [word for word, vcab in model.wv.vocab.iteritems()]
        inds = [vcab.index for word, vcab in model.wv.vocab.iteritems()]
        X = model.wv.syn0[inds]
        return nodes,X
 
def bipartite_matching(G1, G2, p=1, q=1, dimensions=128, embedding='DeepWalk'):
    node1, node2, proM = map_prob_maxtrix(G1, G2, p=p, q=q, dimensions=dimensions, embedding=embedding)
    time_start_bi = datetime.datetime.now()
    M, N = proM.shape
    values = [(i, j, 1 - proM[i][j])
              for i in xrange(M)
              for j in xrange(N) if proM[i][j] > 1e-2]
    values_dict = dict(((i, j), v) for i, j, v in values)
    munkres_match = munkres(values)
    matches = []
    for p1, p2 in munkres_match:
        if p1 > len(node1) or p2 > len(node2):
            continue
        else:
            matches.append((int(node1[p1]), int(node2[p2]), 1 - values_dict[(p1,p2)]))
    time_end_bi = datetime.datetime.now()
    time = (time_end_bi - time_start_bi).seconds
    #print "Bipartite_matching time: " + str(time)
    return matches

def map_prob_maxtrix(G1, G2, p=1, q=1, dimensions=128, embedding='DeepWalk'):
    # match the nodes according to the node feature based on Coherent Point Drift
    nodes1, X = nodes_embedding(G1, p = p, q=q, dimensions=dimensions, embedding=embedding)
    nodes2, Y = nodes_embedding(G2, p = p, q=q, dimensions=dimensions, embedding=embedding)
    time_start_cpd = datetime.datetime.now()
    reg = RigidRegistration(Y, X)
    callback = partial(visualize)
    reg.register(callback)
    P = reg.P
    time_end_cpd = datetime.datetime.now()
    time = (time_end_cpd - time_start_cpd).seconds
    #print "CPD time: " + str(time)
    return (nodes1, nodes2, P)


