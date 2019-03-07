# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
import graph_matching as gm 

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
    nodes1,edges1 = gm.load_graph(filecontext1)
    ret = request.FILES.get('filename2')
    for chunk in ret.chunks():
            filecontext2 += chunk
    nodes2,edges2 = gm.load_graph(filecontext2)
    end = len(nodes1)
    edges3 = [(0,34),(1,25),(3,20)]
    z_score = request.POST.get("zscore")
    comm_limit_down = request.POST.get("comm_limit_down")
    comm_limit_up = request.POST.get("comm_limit_up")
    print "z_score = ",z_score
    return render(request,'deepmatching/graph_matching_post.html',{'end': end,'nodes1':nodes1,'edges1':edges1,'nodes2':nodes2,'edges2':edges2,'back':back,"edges3":edges3})

def post_community_matching(request):
    back = request.META.get('HTTP_REFERER')
    ret = request.FILES.get('filename1')
    filecontext1 = ""
    filecontext2 = ""
    for chunk in ret.chunks():
            filecontext1 += chunk
    nodes1,edges1 = gm.load_graph(filecontext1)
    ret = request.FILES.get('filename2')
    for chunk in ret.chunks():
            filecontext2 += chunk
    nodes2,edges2 = gm.load_graph(filecontext2)
    end = len(nodes1)
    edges3 = [(0,34),(1,25),(3,20)]
    z_score = request.POST.get("zscore")
    comm_limit_down = request.POST.get("comm_limit_down")
    comm_limit_up = request.POST.get("comm_limit_up")
    print "z_score = ",z_score
    return render(request,'deepmatching/community_matching_post.html',{'end': end,'nodes1':nodes1,'edges1':edges1,'nodes2':nodes2,'edges2':edges2,'back':back,"edges3":edges3})
#return HttpResponse("zsocre: " + str(z_score) + "community szie :" + str(comm_limit_down) +"-" +str(comm_limit_up))
