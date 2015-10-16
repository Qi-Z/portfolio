from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<file_path>.*)/file/$', views.file_detail, name='filedetail'),
    url(r'^(?P<project_name>.*)/$', views.detail, name='detail'),

]
