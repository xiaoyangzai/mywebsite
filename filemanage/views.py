# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

def get_filename_list(file_dir):
    file_names = []
    dir_names = []
    for filename in os.listdir(file_dir):
        file_names.append(filename)
    return file_names,dir_names

from django.shortcuts import render
from django.http import HttpResponse,StreamingHttpResponse
import os

# Create your views here.

def index(request):
    return render(request,"filemanage/index.html")

def upload_file_html(request):
    return render(request,"filemanage/upload_file_html.html",{"file_count":0,"file_names":""})

def download_file_html(request):
    file_names,dir_names = get_filename_list(os.getcwd()+"/filemanage/download/") 
    print file_names
    print dir_names
    return render(request,"filemanage/download_file_html.html",{"file_count":len(file_names) + len(dir_names),"file_names":file_names,"dir_names":dir_names})

def download_file(request,file_name):
    def file_iterator(file_name,chunk_size=512):
        print "正在下载",file_name,'**********'
        with open(file_name,'rb') as f:
            if f:
                yield f.read()
                print '下载完成'
            else:
                print '未完成下载'

    the_file_name = os.getcwd() + '/filemanage/download/' + file_name
    print "download " ,the_file_name,"........"
    response = StreamingHttpResponse(file_iterator(the_file_name))

    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachement;filename="{0}"'.format(file_name)
    return response

def upload_file_post(request):
    print "start to upload file...."
    ret = request.FILES.get('filename') 
    destination = open(os.path.join(os.getcwd() + "/filemanage/download",ret.name),'wb+')
    for chunk in ret.chunks():
        destination.write(chunk)
    destination.close()
    return render(request,"filemanage/upload_file_html.html",{"file_count":1,"file_names": ret.name})
