from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$',views.index,name='index'),
    url(r'^graph_matching/post_graph_matching/$',views.post_graph_matching,name='graph_matching_post'),
    url('^graph_matching/$',views.graph_matching,name='graph_matching'),
    url(r'^community_matching/post_community_matching/$',views.post_community_matching,name='community_matching_post'),
    url('^community_matching/$',views.community_matching,name='community_matching'),
]
