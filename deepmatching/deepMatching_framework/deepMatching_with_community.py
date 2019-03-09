#!/usr/bin/python
import community as cmty
import sys
import numpy as np
import networkx as nx 
import deepMatching_framework as dm_framework
from sklearn.metrics.pairwise import *

def obtain_community_detection_in_graph(G,low_threshold,upper_threshold):
    G_cmty_list = community_best_partition_with_limit(G,upper_threshold) 
    G_new_cmty_list = []
    for cmty in G_cmty_list:
        if len(cmty) > low_threshold:
            G_new_cmty_list.append(cmty)
    return G_new_cmty_list

def community_best_partition_with_limit(G,limit_nodes = 500):
	loop_throd_value = 30
	finished_list = []
	unfinished_list = []
	total_G_nodes_number =  G.number_of_nodes()
	unfinished_list.append(G.nodes())
	#print "community detection with limit[<%d] by using best partition......"%limit_nodes
	sys.stdout.flush()
	last_remain_len = len(unfinished_list) 
	remain_loop_count = 0
	while len(unfinished_list) > 0:
		result_nodes = []
		list_nodes = unfinished_list.pop()
		#create Graph for best partition 
		if len(list_nodes) != total_G_nodes_number:
			subG = G.subgraph(list_nodes)
		else:
			subG = G

		#community detection with best partiton 
		subG_partition = cmty.best_partition(subG)
		#check the number of the nodes in the community
		subG_cmty_lists = []

		for com in set(subG_partition.values()):
			temp = [nodes for nodes in subG_partition.keys() if subG_partition[nodes] == com]
			subG_cmty_lists.append(temp)

		for item in subG_cmty_lists:
			if(len(item) > limit_nodes):
				unfinished_list.append(item)
			else:
				finished_list.append(item)

		#print "the size of finished_list : %d " % len(finished_list)
		sys.stdout.flush()
		#print "the size of unfinished_list : %d " % len(unfinished_list)
		sys.stdout.flush()
		current_remain_len = len(unfinished_list)
		if current_remain_len == last_remain_len:
			remain_loop_count += 1
			if remain_loop_count >= loop_throd_value:
				break
		else:
			remain_loop_count = 0 
			last_remain_len = current_remain_len
	#print "community detection with limit[<%d] by using best partition......OK!!"%limit_nodes
	sys.stdout.flush()
	return finished_list

def graph_matching_for_lage_scale(g1,g2,upper_limit = 1000,down_limit = 100,z_score = 2.0,embedding='DeepWalk',cth = 2):
    print"community size scale: [%d - %d]"%(down_limit,upper_limit)
    print"Z check threshold: %.2f"%(z_score)
    print"consistent edges threshold: %d"%(cth)
    print"Embedding method: %s"%(embedding)
    #1. subgraph matching 
    print "====== step 1: subgraph matching ======" 
    print "====== step 1.1: max connected subgraph matching ======"
    sub_g1 = extract_subgraph(g1)
    sub_g2 = extract_subgraph(g2)
    sub_seeds,sub_pg_z,sub_pg_ec = dm_framework.deepmatching_for_samll_scale(sub_g1,sub_g2)
    G1_init_mapping_seeds = [item[0] for item in sub_seeds]
    G2_init_mapping_seeds = [item[1] for item in sub_seeds]

    #2. community matching
    #2.1 community detection
    print "====== step 1.2: community matching ======" 
    print "====== step 1.2.1: community detection ======"
    G1_community_list = obtain_community_detection_in_graph(g1,down_limit,upper_limit)
    G2_community_list = obtain_community_detection_in_graph(g2,down_limit,upper_limit)

    long_cmty_list,long_G,long_initial_seeds = (G1_community_list,g1,G1_init_mapping_seeds) if len(G1_community_list) >= len(G2_community_list) else (G2_community_list,g2,G2_init_mapping_seeds)
    short_cmty_list,short_G,short_initial_seeds = (G1_community_list,g1,G1_init_mapping_seeds) if len(G1_community_list) < len(G2_community_list) else (G2_community_list,g2,G2_init_mapping_seeds)

    #2.2 community mapping with Z check.
    print "====== step 1.2.2: community mapping ======"
    matched_community_with_z_check,global_community_seeds_list,overlap_list_z_level,community_accuracy_rate,matched_count = community_matching(long_G,short_G,long_cmty_list,short_cmty_list,low_threshold = down_limit,upper_threshold = upper_limit)
    print matched_community_with_z_check

    #3. global seeds merge
    print "====== step 2: global seeds merge ======"

    #4. global propagation
    print "====== step 3: global propagation ======"

def extract_subgraph(G,nodes = 500):
    sub_nodes = []  
    nodes_deg = G.degree()
    nodes_sort = sorted(nodes_deg, key = lambda x:x[1], reverse = True)
    sub_degree = nodes_sort[:nodes]
    #Put the first 500 nodes into 'sub_nodes'
    for item in sub_degree:
        sub_nodes.append(item[0])
    sub_G = G.subgraph(sub_nodes)
    sub_G_max = max(nx.connected_component_subgraphs(sub_G), key=len)
    return sub_G_max

def euclidean_metric(sg1_feature_list,sg2_feature_list):
	'''
	Return euclidean distance of two vectors in matrixes
	
	Parameters
	----------

	sg1_feature_list , sg2_feature_list : List
			consists of features of communities
			[[feature_of_community_1],[feature_of_community_2],...] 
	
	Returns
	-------
	distance[0][0] : float
			euclidean distance of two vectors in matrixes
	'''
	X = [] 
	Y = []
	X.append(sg1_feature_list)
	Y.append(sg2_feature_list)
	distance = euclidean_distances(X,Y) 
	return distance[0][0]

def obtain_degree_extern_cmty(G,nodes_list):
	'''
	Return the number of edges between nodes in 'nodes_list' and rest nodes of G

	Parameters
	----------

	G : networkx graph
			original graph that nodes in 'nodes_list' belongs to
	
	nodes_list : List
			some nodes in nodes of graph G

	Returns
	-------

	degrees_of_nodes : Int
			the number of edges between the nodes in 'nodes_list' and the rest nodes of 'G'  

	'''
	#print "obtain extern degree of cmty"
	degrees_of_nodes = 0
	for node in nodes_list:
			temp = nx.neighbors(G,node)
			for i in temp:
					if i not in nodes_list:
							degrees_of_nodes += 1
	#print "outdegree : %d"%degrees_of_nodes
	#print "obtain extern degree of cmty....ok"
	return degrees_of_nodes

def obtain_degree_inter_cmty(G,nodes_list):
	'''
	Returns the degrees of nodes  in  'nodes_list' and the nodes pairs that have edges between them

	Parameters
	----------

	G : networkx graph
			original networkx which the nodes in 'nodes_list' belong to
	
	nodes_list : List
			A list contians some nodes of graph 'G'
	
	Returns
	-------

	degrees_of_nodes : List
			a list consists of degrees of each nodes in 'nodes_list'
			[[node1,degree],[node2,degree],...]
	
	edges_list : List		
			a list consists of nodes pairs which have an edge between them
			[[node1,node3],[node2,node7],....]
	
	'''
	#print "obtain inter degree of the cmty"
	degrees_of_nodes = [] 
	edges_list = []
	for node in nodes_list:
			temp = nx.neighbors(G,node)
			#internal degree of the node in community
			neighbors_in_cmpty = [i for i in temp if i in nodes_list]
			degrees_of_nodes.append([node,len(neighbors_in_cmpty)])
			for j in neighbors_in_cmpty:
					edges_list.append([node,j])
			#degrees_of_nodes.append(len(temp))
	
	#print "obtain inter degree of the cmty...ok"
	return degrees_of_nodes,edges_list

def obtain_degree_distribution_list(degree_nodes,ceil_value):
	distribution_list = [0 for i in range(ceil_value - 1)] 
	degrees_list = [i[1] for i in degree_nodes]
	have_handle = []
	for i in range(ceil_value - 1):
			if i > degrees_list[0]:
					break
			distribution_list[i] = degrees_list.count(i) 
	return distribution_list

def obtain_between_centrality(G,edges_list):
	'''
	Returns betweenness centrality 

	Parameters
	----------

	G : networkx graph
			original graph that nodes in 'edegs_list' belongs to
	
	edges_list : List
			some nodes pairs which have edges between them
	
	Returns
	-------
	
	bc_list : List
			betweenness centrality list
	
	'''
	#1. creat graph with nodes list
	g = nx.Graph()
	for item in edges_list:
			g.add_edge(item[0],item[1])
	bc = nx.betweenness_centrality(g)
	bc_list = []
	for key in bc:
			bc_list.append(bc[key])
	return bc_list

def obtain_clustering_coefficient_distribution(cc,each_step = 0.1):
	new_cc = []
	cc_distribution_list = []
	step = [i*each_step for i in range(int(1/each_step + 1))][1:]

	for base in step:
			count = 0
			for item in cc: 
					if item < base and item not in new_cc:
							count += 1 
							new_cc.append(item)
			cc_distribution_list.append(count)
	return cc_distribution_list

def obtain_triangles_count(G,nodes_list=None):
    return nx.triangles(G,nodes_list)

def obtain_clustering_coefficient(G,nodes_list):
	'''
	Returns the clustering coefficient of node in nodes list

	Parameters
	----------

	G : networkx graph
			original graph that nodes in 'nodes_list' belongs to
	
	nodes_list : List
			some nodes in nodes of graph G

	Returns
	-------
	
	cc : List
			centrality list
	'''
	dic_cc = nx.clustering(G,nodes_list)
	cc = []
	for k in dic_cc:
			cc.append(dic_cc[k])
	cc = sorted(cc)
	return cc



def obtain_feature_of_cmty_with_degree_distribution(G,nodes_list,throd,ceil_value):
	'''
	obtain the feature of the community
	Return: the community feature
	Return type: list which consists of:
			1. outdegree of the community
			2. number of nodes
			3. number of edges
			4. maxmiun degree 1th,2th and 3th
			5. average degree of community
			6. midian degree
			7. density of community
			8. triangles number of the maximun degree
			9. modularity

			10. maxmiun bs contained 1th,2th and 3th
			11. average bs
			12. midian bs
			13. average cc
			14. midian cc.
	'''
	features_name_list = ["outdegree","nodes","average degree","midian degree","degree[0 - %d] distribution "%(ceil_value),"density","%d th triangles"%(int(throd*0.75)),"%d th triangles"%(int(throd*0.75)),"average bs","midian bs","%d th cc" % (int(throd * 0.75)),"average cc","midian cc"]
	feature = []	
	#obtain the outdegree of the community
	outdegree = obtain_degree_extern_cmty(G,nodes_list)

	feature.append(outdegree)
	feature.append(len(nodes_list))

	#calculate the degree distribution of the nodes
	degree_nodes,edges = obtain_degree_inter_cmty(G,nodes_list)
	#2.1 calculate the degree distribution of the nodes in the community 
	degree_nodes = sorted(degree_nodes,key=lambda x:x[1],reverse = True)
	degree_list = [item[1] for item in degree_nodes]
	average_degree = float(sum(degree_list))/len(degree_list)		
	#midian_degree = obtain_midian_list(degree_list)
	feature.append(average_degree)
	#feature.append(midian_degree)

	max_nodes_list = []
	for i in range(throd):
			max_nodes_list.append(degree_nodes[i][0])
	
	degree_distribution_list = obtain_degree_distribution_list(degree_nodes[:throd],ceil_value)
	#add the degree distribution to the feature one by one
	for item in degree_distribution_list:
			feature.append(item)

	#2. count the number of edges in community
	degree_list = [item[1] for item in degree_nodes]
	edges_count = sum(degree_list) / 2

	#density of the community
	d = float(2 * edges_count) / (len(nodes_list) *(len(nodes_list) - 1))
	feature.append(d)
	
	#3 calculate the triangles distribution
	triangles_count = obtain_triangles_count(G,max_nodes_list)
	triangles = [[key,triangles_count[key]] for key in triangles_count]
	triangles = sorted(triangles,key=lambda x:x[1],reverse = True)
	triangles_distribution = obtain_degree_distribution_list(triangles,ceil_value)
	for k in triangles_distribution:
			feature.append(k)

	#4.calculate betweenness centrality 
	between_centrality_list = obtain_between_centrality(G,edges)
	between_centrality_list = sorted(between_centrality_list,reverse=True)

	bs_distribution_list = obtain_clustering_coefficient_distribution(between_centrality_list,each_step = 0.001)
	for item in bs_distribution_list:
			feature.append(item)

	#5 calculate clustering coefficients
	cc = obtain_clustering_coefficient(G,max_nodes_list)
	cc_distribution_list = obtain_clustering_coefficient_distribution(cc,0.001)
	for item in cc_distribution_list:
			feature.append(item)
			
	return feature

def normalize_cmty_feature(feature):
	'''
	Return the normalized feature of community
	value = (value - MInVale) / (MaxValue - MinValue)

	Parameters
	----------

	feature : List , elment type: float
			the feature of the community
	
	Returns
	-------

	normalized_feature : List , elment type: float
			Return the feature whose elements is normalized
	'''

	feature = sorted(feature)
	maxvalue = feature[-1]
	minvalue = feature[0]
	temp = maxvalue - minvalue
	for i in range(len(feature)):
			feature[i] = (feature[i] - minvalue) * 1.0 / temp 
	return feature
	
	
def obtain_cmty_feature_array(G,cmty_list,low_threshold,upper_threshold,feature_method = obtain_feature_of_cmty_with_degree_distribution):
    '''
    Return the features of communities in the 'cmty_list' in graph 'G'
    
    Parameters
    ----------
    
    G : networkx graph
    		original networkx graph
    
    cmty_list : List
    		consists of the communities detected by using detection method in G1 and every community contains some nodes
    [[node1,node3,...],[node2,node5,...],...]		
    
    low_threshold : Int
    		the low threshold of the number of nodes in the eligible community
    upper_threshold : Int
    		the ceil threshold of the number of nodes in the eligible community
    
    Returns:
    --------
    feature : List
    		consists of the features of communities in 'eligible_cmty_list'
    		[[feature_of_community_1],[feature_of_community_2],...] 
    '''		
    #print "obtain cmty feature array"
    feature = [] 
    index = 0 
    for cmty in cmty_list:
        temp = feature_method(G,cmty,low_threshold,upper_threshold)
        temp = normalize_cmty_feature(temp)
        feature.append(temp)
        print"community[%d] features vector: "%index,
        print temp
        index += 1 
    #print "obtain cmty feature array finished"
    return feature

def obtain_score_between_features(long_features_list,short_features_list,method = euclidean_metric):
	'''
	calculate the similarity score between features by algritom specified method

	Parameters
	----------

	sg1_feature_list , sg2_feature_list : List
			consists of features of communities
			[[feature_of_community_1],[feature_of_community_2],...] 
	
	method : pointer
			specified the method to calculate the distance between features of communities

	Returns
	-------
	
	scroe_list : List
			contain the distances between each pairs of features of communities 
			[
					[community_1_of_left_Graph,similiarity_1_with_community_in_right_graph,similiarity_2_with_community_in_right_graph,similiarity_3_with_community_in_right_graph,...]
					[community_2_of_left_Graph,similiarity_1_with_community_in_right_graph,similiarity_2_with_community_in_right_graph,similiarity_3_with_community_in_right_graph,...]
					....
			]
	
	'''
	big_feature_list = long_features_list
	score_list = [[] for i in range(len(big_feature_list))]
	small_feature_list = short_features_list

	for index in range(0,len(big_feature_list)):
			s_feature = big_feature_list[index]
			for d_feature in small_feature_list:
					score = method(s_feature,d_feature)
					score_list[index].append(score)
	return score_list

def calculate_common_nodes_between_cmties(s_nodes_list,d_nodes_list):
	'''
	calculate the number of the nodes existed in both s_nodes_list and d_nodes_list

	Parameters
	----------

	s_nodes_list , d_nodes_list : List
			consists of nodes index
	
	Returns
	-------

	common_nodes_rate : float , less than 1
			the partition of the common nodes in small nodes list

	common_nodes_list : List
			consists of nodes which appear in both 's_nodes_list' and 'd_nodes_list'
			
	'''
	if len(s_nodes_list) == 0 or len(d_nodes_list) == 0:
			return 0
	small_node_list = s_nodes_list if len(s_nodes_list) <= len(d_nodes_list) else d_nodes_list
	big_node_list = s_nodes_list if len(s_nodes_list) > len(d_nodes_list) else d_nodes_list
	common_nodes_list = []
	total_count = len(small_node_list) 
	for node in small_node_list:
			if node in big_node_list:
					common_nodes_list.append(node)
	
	common_count = len(common_nodes_list)
	common_nodes_rate = float(common_count)/total_count 
	return common_nodes_rate, common_nodes_list



def obtain_community_matched_pairs(long_G,long_cmty_list,short_G,short_cmty_list,score_list,long_features_list,short_features_list,throd_value = 0.75):
	'''		
	calculate the accuracy rate of matching communities between graphes

	Parameters
	----------

	SG1 ,SG2 : networkx graph
			original netwrokx graph
	SG1_new_cmty , SG2_new_cmty : List
			the communities list of the SG1 graph and SG2 graph
	
	scroe_list : List
			contain the distances between each pairs of features of communities 
			[
					[community_1_of_left_Graph,similiarity_1_with_community_in_right_graph,similiarity_2_with_community_in_right_graph,similiarity_3_with_community_in_right_graph,...]
					[community_2_of_left_Graph,similiarity_1_with_community_in_right_graph,similiarity_2_with_community_in_right_graph,similiarity_3_with_community_in_right_graph,...]
					....
			]
	
	SG1_feature,SG2_feature : List
			consists of features of communities
			[[feature_of_community_1],[feature_of_community_2],...] 
	
	throd_value : float
			the threshold of accuracy rate of the nodes between the matched communities 
			
	Returns
	-------

	accuracy_rate : float
			the accuracy rate of the matched communities

	big_G : networkx graph
			the number of communities in this graph is greater

	samll_G : networkx graph
			the number of communities in this graph is smaller 

	big_new_cmty : List
			the communities list in 'big_G'

	small_new_cmty : List
			the communities list in 'small_G'
	
	matched_index : List
			contains the pairs index of communities. 
			The left index of pairs is the community from the big_G graph 
			The right index of pairs is the community from the small_G graph 

	return the result of the matched communities index
	'''
	matched_count = 0
	unmatched_count = 0
	matched_index = []

	big_new_cmty,big_G = long_cmty_list,long_G 
	small_new_cmty,small_G = short_cmty_list,short_G 
	big_feature = long_features_list 
	small_feature = short_features_list 

	overlap_list = []

	loop_count = len(big_new_cmty)	

	small_cmty_count = len(small_new_cmty)
	have_matched_big_new_cmty = {} 
	for i in range(0,loop_count):
		#print "**************************************************************"
		#obtain the similarity list of ith community with all of the other community
		similarity_list =[(index,score_list[i][index]) for index in range(0,small_cmty_count)]
		#sort the similiarity of ith community such that obtain the most similar one
		similarity_list = sorted(similarity_list,key=lambda x:x[1])
		
		#print "%d pairs have been matched!!" % len(have_matched_big_new_cmty)			 
		if len(have_matched_big_new_cmty) == small_cmty_count:
				break

		#print "cmty: %d" % i
		#print "similarity list: ",
		#print similarity_list

		while len(similarity_list) > 0:
				#obtain the similiarity list of the best one similiaried with the ith cmty from big community list
				best_score = similarity_list[0][1]
				C_index = similarity_list[0][0]
				#print "best score: %.5f" % best_score
				#print "C index: %d"% C_index

				similarity_list.pop(0)
				#obtain the community which is most similar to the community specified by C_index
				dest_similarity_list = []		
				dest_cmty_index = 0
				for item in score_list:
						#if dest_cmty_index had matched before
						if dest_cmty_index in have_matched_big_new_cmty.keys() and have_matched_big_new_cmty[dest_cmty_index] != C_index:
								dest_cmty_index += 1
								continue
						dest_similarity_list.append(item[C_index])
						dest_cmty_index += 1

				dest_similarity_list = sorted(dest_similarity_list)
				#print dest_similarity_list
				if best_score > dest_similarity_list[0]:
						continue;
				break
		#no matched if length of the similiarity list is zero,guasee the firsted matched community is the best one
		if len(similarity_list) == 0:
				unmatched_count += 1
				continue
		#print "best candidate: %d" % C_index
		temp_rate,common_nodes_list = calculate_common_nodes_between_cmties(big_new_cmty[i],small_new_cmty[C_index]) 

		#add the index of big cmty 
		have_matched_big_new_cmty[i] = C_index
		matched_index.append([i,C_index,len(common_nodes_list),temp_rate])
		#print "overlap rate: %.4f" % temp_rate
		overlap_list.append(temp_rate)
		if temp_rate >= throd_value:
				#print "mapping successful!"
				matched_count += 1
		else:
				#print "mapping failed"
				unmatched_count += 1
		print "matched count: %d" % matched_count
		print "unmatched count: %d" % unmatched_count
	accuracy_rate = 0
	if len(matched_index) > 0: 
		accuracy_rate = float(matched_count)/len(matched_index)
	#print "total count: %d" % len(matched_index) 
	#print "accuracy rate: %.5f" % accuracy_rate
	return accuracy_rate,overlap_list,matched_index


def community_matching(long_G,short_G,long_cmty_list,short_cmty_list,low_threshold = 50,upper_threshold = 1000,method = euclidean_metric,z_threashold = 2.0):
    '''
    Return the matched pairs of communities from the 'G1' and 'G2' and calculate the matching accuracy rate between the communities detected by the method specified by 'detect_methond'	
    
    Parameters
    ----------
    G1,G2 : networkx graph
    		original networkx graph
    
    low_threshold : int
    		the minimum number of nodes in a community
    
    upper_threshold : int
    		the minimum number of nodes in a community
    
    method : pointer
    		point the  function of calculating distance bewteen communities' features
    
    detect_method : pointer
    		point the  function of detecting tht communities in graphes 
    
    Returns
    -------
    
    rate : float	
    	the accuracy rate of matched pairs of communities
    
    left_Graph,right_Graph : networkx graph
    	specified which graph the left communities or right communities in 'matched_index'		belong to 
    				example: matched_index = [[1,3],[5,6],...]. the community of index 1 is in left_Graph and the community of index 3 is in right_Graph 
    
    		left_cmty_list,right_cmty_list : List
    				consist of the communities in left Graph and right Graph
    				[[community_1],[community_2],....]
    		
    		matched_index : List
    				consists of matched index of communities between the left Graph and right Graph
    				[[1,3],[4,5],...]
    
    		scroe_list : List
    				contain the distances between each pairs of features of communities 
    				[
    						[community_1_of_left_Graph,similiarity_1_with_community_in_right_graph,similiarity_2_with_community_in_right_graph,similiarity_3_with_community_in_right_graph,...]
    						[community_2_of_left_Graph,similiarity_1_with_community_in_right_graph,similiarity_2_with_community_in_right_graph,similiarity_3_with_community_in_right_graph,...]
    						....
    				]
    		
    '''
    #1. Extract the features of community based on their attributes.
    print"***** Community mapping: 1. extract features of community. *****"
    long_cmty_features = obtain_cmty_feature_array(long_G,long_cmty_list,low_threshold,upper_threshold)
    short_cmty_features = obtain_cmty_feature_array(short_G,short_cmty_list,low_threshold,upper_threshold)

    #2. Calculate the distance among the communities as the similarity.
    print"***** Community mapping: 2. Calculate the similarity between communities. *****"
    score_list_between_community_features = obtain_score_between_features(long_cmty_features,short_cmty_features,method = method)

    #3. Mapping the community based the similarity between them. 
    print "***** Community mapping: 3. Initial mapping  between communities. *****"
    accuracy_rate,overlap_list,matched_index = obtain_community_matched_pairs(long_G,long_cmty_list,short_G,short_cmty_list,score_list_between_community_features,long_cmty_features,short_cmty_features,throd_value = 0.5)
  
    #4. Refine the result of community mapping with Z check.
    print "***** Community mapping: 4. refine mapping  between communities. *****"
    z_score_list = []
    crebiliable_matched_index = []
    global_seeds_of_nodes_list = []
    matched_communities_with_z_check = []
    overlap_list_z_level = []
    matched_count_z_level = 0
     
    for item in matched_index:
        long_cmty_index = item[0] 
        short_cmty_index = item[1] 
        #4.1 Constuct the subgrpahs with nodes in the matched community pairs. 
        sub_G1 = long_G.subgraph(long_cmty_list[long_cmty_index])
        sub_G2 = short_G.subgraph(short_cmty_list[short_cmty_index])
        
        #4.2 Employ DeepMatching framework between the subgraphs. 
        community_seeds,community_z_score,community_ec = dm_framework.deepmatching_for_samll_scale(sub_G1,sub_G2) 
        print "community[%d] vs community[%d] z_score: %.2f"%(long_cmty_index,short_cmty_index,community_z_score)
        if community_z_score > z_threashold:
        	matched_communities_with_z_check.append([long_cmty_index,short_cmty_index,community_z_score])
        	overlap_list_z_level.append(item[3])
        
        	if item[3] > 0.5:
        		matched_count_z_level += 1
        	for i in community_seeds:
        		global_seeds_of_nodes_list.append(i)
    
    print "refine matched community count: %d" % matched_count_z_level
    community_matched_accuracy_z_level = 0
    if len(matched_communities_with_z_check) > 0:
    	community_matched_accuracy_z_level = float(matched_count_z_level) / len(matched_communities_with_z_check)
    
    return matched_communities_with_z_check,global_seeds_of_nodes_list,overlap_list_z_level,community_matched_accuracy_z_level,matched_count_z_level


def main():
    g1 = dm_framework.load_graph_from_edges_file(sys.argv[1])  
    g2 = dm_framework.load_graph_from_edges_file(sys.argv[2])  
    graph_matching_for_lage_scale(g1,g2,upper_limit = 1000,down_limit= 100)

if __name__ == "__main__":
    main()
