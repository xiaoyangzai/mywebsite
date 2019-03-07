from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',views.index,name='filemanage_index'),
    url(r'^upload_file_post$',views.upload_file_post,name="upload_post"),
    url(r'^upload_file_html$',views.upload_file_html,name="upload_html"),
    url(r'^download_file_html$',views.download_file_html,name="download_html"),
    url(r'^download_file/(?P<file_name>.*)/$',views.download_file,name="download_file"),
]
