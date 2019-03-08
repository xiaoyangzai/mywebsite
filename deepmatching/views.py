# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from deepMatching_framework import deepMatching_framework as dm  

def index(request):
    return render(request,"deepmatching/index.html")

def community_matching(request):
    return render(request,"deepmatching/community_matching.html")

def graph_matching(request):
    return render(request,"deepmatching/graph_matching.html")

def post_graph_matching(request):
    back = request.META.get('HTTP_REFERER')
    ret = request.FILES.get('filename1')
    filecontext1 = ""
    filecontext2 = ""
    for chunk in ret.chunks():
            filecontext1 += chunk
    nodes1,edges1,g1 = dm.load_graph_from_edges_string(filecontext1)
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
    matched_ms,z_score,ec = dm.deepmatching_for_samll_scale(g1,g2,ch,embedding) 
    return render(request,'deepmatching/graph_matching_post.html',{'end': end,'nodes1':nodes1,'edges1':edges1,'nodes2':nodes2,'edges2':edges2,'back':back,"edges3":matched_ms,"z_score":z_score,"ch":ch,"embedding":embedding})

def post_community_matching(request):
    back = request.META.get('HTTP_REFERER')
    ret = request.FILES.get('filename1')
    filecontext1 = ""
    filecontext2 = ""
    for chunk in ret.chunks():
            filecontext1 += chunk
    nodes1,edges1,g1 = dm.load_graph_from_edges_string(filecontext1)
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

    matched_ms,z_score,ec = dm.deepmatching_for_samll_scale(g1,g2,ch,embedding) 
    return render(request,'deepmatching/graph_matching_post.html',{'end': end,'nodes1':nodes1,'edges1':edges1,'nodes2':nodes2,'edges2':edges2,'back':back,"edges3":matched_ms,"z_score":z_score,"ch":ch,"embedding":embedding})
