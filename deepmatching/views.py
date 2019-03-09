# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import time

# Create your views here.

from django.http import HttpResponse,JsonResponse
from deepMatching_framework import deepMatching_framework as dm  

#for updating the processbar.
graph_matching_process = 0

def index(request):
    return render(request,"deepmatching/index.html")

def get_graph_matching_process(request):
    print "process: %d"%graph_matching_process
    return JsonResponse(graph_matching_process,safe=False)

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

    embedding = request.POST.get("embedding")
    embedding = str(embedding.encode("utf-8"))
    print "embedding = %s"%embedding

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
    global graph_matching_process
    back = request.META.get('HTTP_REFERER')
    ret = request.FILES.get('filename1')
    filecontext1 = ""
    filecontext2 = ""
    for chunk in ret.chunks():
            filecontext1 += chunk
    graph_matching_process = 10
    nodes1,edges1,g1 = dm.load_graph_from_edges_string(filecontext1)
    graph_matching_process = 20
    ret = request.FILES.get('filename2')
    for chunk in ret.chunks():
            filecontext2 += chunk
    nodes2,edges2,g2 = dm.load_graph_from_edges_string(filecontext2)
    end = len(nodes1)
    ch = request.POST.get("ch")
    ch = int(ch.encode("utf-8"))
    print "ch = %d"%ch

    embedding = request.POST.get("embedding")
    embedding = str(embedding.encode("utf-8"))
    print "embedding = %s"%embedding

    comm_limit_down = request.POST.get("comm_limit_down")
    comm_limit_down = int(comm_limit_down.encode("utf-8"))
    comm_limit_up = request.POST.get("comm_limit_up")
    comm_limit_up = int(comm_limit_up.encode("utf-8"))
    
    print "community size: %d-%d"%(comm_limit_down,comm_limit_up)

    graph_matching_process = 40
    print "===== DeepMatching: 1. initilizating matching ====="
    init_ms,init_z,init_ec = dm.enbeding_init_matching(g1, g2,embedding = embedding)
    graph_matching_process = 60

    print "===== DeepMatching: 2. Refineing matching ====="
    refine_ms,refine_z,refine_ec,refine_accuracy = dm.refine_matching(init_ms,g1,g2,ch=ch)
    graph_matching_process = 80

    print "===== DeepMatching: 3. Propagation matching ====="
    matched_ms,z_score,ec = dm.propagation_matching(refine_ms,g1,g2)
    graph_matching_process = 100

    return render(request,'deepmatching/graph_matching_post.html',{'end': end,'nodes1':nodes1,'edges1':edges1,'nodes2':nodes2,'edges2':edges2,'back':back,"edges3":matched_ms,"z_score":z_score,"ch":ch,"embedding":embedding})
