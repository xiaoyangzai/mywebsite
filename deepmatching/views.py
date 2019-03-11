# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import time

# Create your views here.

from django.http import HttpResponse,JsonResponse
from deepMatching_framework import deepMatching_framework as dm  
from deepMatching_framework import deepMatching_with_community as dm_wc 

#for updating the processbar.
graph_matching_process = 0
community_matching_process = 0

def index(request):
    return render(request,"deepmatching/index.html")

def get_graph_matching_process(request):
    print "process: %d"%graph_matching_process
    return JsonResponse(graph_matching_process,safe=False)

def get_community_matching_process(request):
    print "process: %d"%community_matching_process
    return JsonResponse(community_matching_process,safe=False)

def community_matching(request):
    return render(request,"deepmatching/community_matching.html")

def graph_matching(request):
    return render(request,"deepmatching/graph_matching.html")

def post_graph_matching(request):
    global graph_matching_process
    graph_matching_process = 0
    back = request.META.get('HTTP_REFERER')
    ret = request.FILES.get('filename1')
    graph_matching_process = 10
    filecontext1 = ""
    filecontext2 = ""
    for chunk in ret.chunks():
            filecontext1 += chunk
    nodes1,edges1,g1 = dm.load_graph_from_edges_string(filecontext1)
    ret = request.FILES.get('filename2')
    for chunk in ret.chunks():
            filecontext2 += chunk
    graph_matching_process = 20
    nodes2,edges2,g2 = dm.load_graph_from_edges_string(filecontext2)
    graph_matching_process = 30
    end = len(nodes1)
    ch = request.POST.get("ch")
    ch = int(ch.encode("utf-8"))
    print "ch = %d"%ch

    #embedding = request.POST.get("embedding")
    #embedding = str(embedding.encode("utf-8"))
    #print "embedding = %s"%embedding
    embedding = "deepwalk"

    print "===== DeepMatching: 1. initilizating matching ====="
    init_ms,init_z,init_ec = dm.enbeding_init_matching(g1, g2,embedding = embedding)
    graph_matching_process = 50

    print "===== DeepMatching: 2. Refineing matching ====="
    refine_ms,refine_z,refine_ec,refine_accuracy = dm.refine_matching(init_ms,g1,g2,ch=ch)
    graph_matching_process = 80
    print "===== DeepMatching: 3. Propagation matching ====="
    matched_ms,z_score,ec = dm.propagation_matching(refine_ms,g1,g2)
    graph_matching_process = 100
    time.sleep(0.5)
    return render(request,'deepmatching/graph_matching_post.html',{'end': end,'nodes1':nodes1,'edges1':edges1,'nodes2':nodes2,'edges2':edges2,'back':back,"edges3":matched_ms,"z_score":z_score,"ch":ch,"embedding":embedding})

def post_community_matching(request):
    global community_matching_process
    community_matching_process = 0
    back = request.META.get('HTTP_REFERER')
    ret = request.FILES.get('filename1')
    filecontext1 = ""
    filecontext2 = ""
    for chunk in ret.chunks():
            filecontext1 += chunk
    community_matching_process = 10
    nodes1,edges1,g1 = dm.load_graph_from_edges_string(filecontext1)
    ret = request.FILES.get('filename2')
    for chunk in ret.chunks():
            filecontext2 += chunk
    nodes2,edges2,g2 = dm.load_graph_from_edges_string(filecontext2)
    end = len(nodes1)
    ch = request.POST.get("ch")
    ch = int(ch.encode("utf-8"))
    print "ch = %d"%ch

    community_matching_process = 15
    #embedding = request.POST.get("embedding")
    #embedding = str(embedding.encode("utf-8"))
    #print "embedding = %s"%embedding
    embedding = "deepwalk"

    comm_limit_down = request.POST.get("comm_limit_down")
    comm_limit_down = int(comm_limit_down.encode("utf-8"))
    comm_limit_up = request.POST.get("comm_limit_up")
    comm_limit_up = int(comm_limit_up.encode("utf-8"))
    print "community size: %d-%d"%(comm_limit_down,comm_limit_up)
    community_matching_process = 20
    time.sleep(0.1)

    #1. subgraph matching 
    print "====== step 1: subgraph matching ======" 
    print "====== step 1.1: max connected subgraph matching ======"

    #2. community matching
    #2.1 community detection
    print "====== step 1.2: community matching ======" 
    print "====== step 1.2.1: community detection ======"
    G1_community_list = dm_wc.obtain_community_detection_in_graph(g1,comm_limit_down,comm_limit_up)
    community_matching_process = 25
    G2_community_list = dm_wc.obtain_community_detection_in_graph(g2,comm_limit_down,comm_limit_up)
    community_matching_process = 30
    long_cmty_list,long_G,long_edges = (G1_community_list,g1,edges1) if len(G1_community_list) >= len(G2_community_list) else (G2_community_list,g2,edges2)
    short_cmty_list,short_G,short_edges = (G1_community_list,g1,edges1) if len(G1_community_list) < len(G2_community_list) else (G2_community_list,g2,edges2)

    #2.2 community mapping with Z check.
    print "====== step 1.2.2: community mapping ======"
    matched_community_with_z_check,global_community_seeds_list,overlap_list_z_level,community_accuracy_rate,matched_count,long_cmty_features,short_cmty_features = dm_wc.community_matching(long_G,short_G,long_cmty_list,short_cmty_list,low_threshold = comm_limit_down,upper_threshold = comm_limit_up)
    print "Community matched nodes pairs number: %d"%(len(global_community_seeds_list)) 
    community_matching_process = 70
    #3. construct the data for HTML
    #3.1 matched_nodes = [(node_id,nodel_label,title,group,shape,size)]
    #3.2 unmatched_nodes = [(node_id,nodel_label,title,group,shape,size)]
    number_nodes_of_long_graph= len(long_G.nodes())
    number_nodes_of_short_graph= len(short_G.nodes())
    number_edges_of_short_graph= len(short_edges)
    number_edges_of_long_graph= len(long_edges)
    number_of_credible_matched_communities = len(matched_community_with_z_check)
    long_cmty_indexs = [i for i in range(len(long_cmty_list))]
    short_cmty_indexs = [i for i in range(len(short_cmty_list))]
    nodes_of_matched_community = []
    edges_between_matched_community = []
    long_unmatched_cmty_index = [i for i in range(len(long_cmty_list))]
    short_unmatched_cmty_index = [i for i in range(len(short_cmty_list))]
    tmp_index= 0
    for item in matched_community_with_z_check:
        long_nodes_degree = []
        short_nodes_degree = []
        if long_G == g1:
            long_nodes_degree = [[i,"%d"%i,"Node id: %d<br>Degree: %d<br> Community id: %d"%(i,long_G.degree(i),tmp_index),tmp_index,"dot","{size: 150}",long_G.degree(i) * 20] for i in long_cmty_list[item[0]]]
            short_nodes_degree = [[i+number_nodes_of_long_graph,"%d"%(i),"Node id: %d<br>Degree: %d<br> Community id: %d"%(i,short_G.degree(i),tmp_index),tmp_index,"diamond","{size: 150}",short_G.degree(i) * 20] for i in short_cmty_list[item[1]]]
        else:
            long_nodes_degree = [[i + number_nodes_of_short_graph,"%d"%i,"Node id: %d<br>Degree: %d<br> Community id: %d"%(i,long_G.degree(i),tmp_index),tmp_index,"diamond","{size: 150}",long_G.degree(i)*20] for i in long_cmty_list[item[0]]]
            short_nodes_degree = [[i,"%d"%i,"Node id: %d<br>Degree: %d<br> Community id: %d"%(i,short_G.degree(i),tmp_index),tmp_index,"dot","{size: 150}",short_G.degree(i) * 20] for i in short_cmty_list[item[1]]]

        long_nodes_degree.sort(key=lambda x:x[-1])
        long_nodes_degree.reverse()
        long_unmatched_cmty_index.remove(item[0])

        short_nodes_degree.sort(key=lambda x:x[-1])
        short_nodes_degree.reverse()
        short_unmatched_cmty_index.remove(item[1])
        edges_between_matched_community.append([long_nodes_degree[0][0],short_nodes_degree[0][0]])

        if long_G == g1:
            long_nodes_degree[0][2] = "Node id: %d<br>Degree: %d<br> Community id:%d<br> feature1: %.2f<br>feature2: %.2f"%(long_nodes_degree[0][0],long_nodes_degree[0][-1]/20,long_nodes_degree[0][3],long_cmty_features[item[0]][0],long_cmty_features[item[0]][1]) 
            short_nodes_degree[0][2] = "Node id: %d<br>Degree: %d<br> Community id:%d<br> feature1: %.2f<br>feature2: %.2f"%(short_nodes_degree[0][0] - number_nodes_of_long_graph,short_nodes_degree[0][-1]/20,short_nodes_degree[0][3],short_cmty_features[item[1]][0],short_cmty_features[item[1]][1]) 
        else:
            long_nodes_degree[0][2] = "Node id: %d<br>Degree: %d<br> Community id:%d<br> feature1: %.2f<br>feature2: %.2f"%(long_nodes_degree[0][0] - number_nodes_of_short_graph,long_nodes_degree[0][-1]/20,long_nodes_degree[0][3],long_cmty_features[item[0]][0],long_cmty_features[item[0]][1]) 
            short_nodes_degree[0][2] = "Node id: %d<br>Degree: %d<br> Community id:%d<br> feature1: %.2f<br>feature2: %.2f"%(short_nodes_degree[0][0],short_nodes_degree[0][-1]/20,short_nodes_degree[0][3],short_cmty_features[item[1]][0],short_cmty_features[item[1]][1]) 
        #set the title of the node whose degree is the greatest in community.
        nodes_of_matched_community.extend(long_nodes_degree)
        nodes_of_matched_community.extend(short_nodes_degree)
        tmp_index += 1

    community_matching_process = 80
    nodes_of_unmatched_community = [] 
    number_community_of_short_graph = len(short_cmty_list)
    number_community_of_long_graph = len(long_cmty_list)
    long_tmp_index = tmp_index 
    short_tmp_index = tmp_index 
    for item in long_unmatched_cmty_index:
        long_nodes_degree = []
        if long_G == g1:
            long_nodes_degree = [[i,"%d"%i,"Node id: %d <br>Degree: %d<br> Community id: %d"%(i,long_G.degree(i),long_tmp_index),long_tmp_index,"dot","{size: 150}",long_G.degree(i) * 20] for i in long_cmty_list[item]]
        else:
            long_nodes_degree = [[i + number_nodes_of_short_graph,"%d"%i,"Node id: %d <br> Degree: %d <br> Community id: %d"%(i,long_G.degree(i),long_tmp_index),long_tmp_index + number_community_of_short_graph,"diamond","{size: 150}",long_G.degree(i)*20] for i in long_cmty_list[item]]

        long_nodes_degree.sort(key=lambda x:x[1])
        long_nodes_degree.reverse()

        if long_G == g1:
            long_nodes_degree[0][2] = "Node id: %d<br>Degree: %d <br> Community id:%d<br> feature1: %.2f <br>feature2: %.2f"%(long_nodes_degree[0][0],long_nodes_degree[0][-1]/20,long_nodes_degree[0][3],long_cmty_features[item][0],long_cmty_features[item][1]) 
        else:
            long_nodes_degree[0][2] = "Node id: %d <br>Degree: %d<br> Community id:%d<br> feature1: %.2f<br>feature2: %.2f"%(long_nodes_degree[0][0] - number_nodes_of_short_graph,long_nodes_degree[0][-1]/20,long_nodes_degree[0][3],long_cmty_features[item][0],long_cmty_features[item][1]) 

        nodes_of_unmatched_community.extend(long_nodes_degree)
        long_tmp_index += 1

    community_matching_process = 90
    short_unmatched_cmty = []
    for item in short_unmatched_cmty_index:
        short_nodes_degree = []
        if long_G == g1:
            short_nodes_degree = [[i+number_nodes_of_long_graph,"%d"%(i),"Node id: %d'<br>'Degree: %d'<br>' Community id: %d"%(i,short_G.degree(i),short_tmp_index),short_tmp_index + number_community_of_long_graph,"diamond","{size: 150}",short_G.degree(i) * 20] for i in short_cmty_list[item]]
        else:
            short_nodes_degree = [[i,"%d"%i,"Node id: %d'<br>'Degree: %d'<br>' Community id: %d"%(i,short_G.degree(i),short_tmp_index),short_tmp_index,"dot","{size: 150}",short_G.degree(i) * 20] for i in short_cmty_list[item]]

        short_nodes_degree.sort(key=lambda x:x[1])
        short_nodes_degree.reverse()

        if long_G == g1:
            short_nodes_degree[0][2] = "Node id: %d'<br>'Degree: %d'<br>' Community id:%d'<br>' feature1: %.2f'<br>'feature2: %.2f"%(short_nodes_degree[0][0] - number_nodes_of_long_graph,short_nodes_degree[0][-1]/20,short_nodes_degree[0][3],short_cmty_features[item][0],short_cmty_features[item][1]) 
        else:
            short_nodes_degree[0][2] = "Node id: %d'<br>'Degree: %d'<br>' Community id:%d'<br>' feature1: %.2f'<br>'feature2: %.2f"%(short_nodes_degree[0][0],short_nodes_degree[0][-1]/20,short_nodes_degree[0][3],short_cmty_features[item][0],short_cmty_features[item][1]) 

        nodes_of_unmatched_community.extend(short_nodes_degree)
        short_tmp_index += 1

    #construct edges
    all_edges_final = []
    if long_G == g1:
        all_edges_final.extend(long_edges) 
        for edge in short_edges:
            all_edges_final.append((edge[0] + number_nodes_of_long_graph,edge[1] + number_nodes_of_long_graph))
    else:
        all_edges_final.extend(short_edges) 
        for edge in long_edges:
            all_edges_final.append((edge[0] + number_nodes_of_short_graph,edge[1] + number_nodes_of_short_graph))

    community_matching_process = 100
    legend1 = 0
    legend1 = 0
    legend1 = number_nodes_of_long_graph + number_nodes_of_short_graph + 1
    legend2 = number_nodes_of_long_graph + number_nodes_of_short_graph + 2
    graph_order = 0
    if long_G == g1:
        graph_order = 1 

    return render(request,'deepmatching/community_matching_post.html',{'nodes_of_matched_community':nodes_of_matched_community,'nodes_of_unmatched_community':nodes_of_unmatched_community,'edges_between_matched_community': edges_between_matched_community,'all_edges_final':all_edges_final,"legend1":legend1,"legend2":legend2,"graph_order":graph_order})
