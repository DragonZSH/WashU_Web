from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^deviceadd/$', views.device_add, name='device_add'),
    url(r'^devicedelete/$', views.device_delete, name='device_delete'),
    url(r'^devicedeploy/$', views.device_deploy, name='device_deploy'),
    url(r'^getswitchport/$', views.get_connected_switchport, name='get_connected_switchport'),
    url(r'^getclientdetails/$', views.get_client_details, name='get_client_details'),
    url(r'^calcpath/$', views.calc_path, name='calc_path'),
    url(r'^calcpathris/$', views.calc_path_ris, name='calc_path_ris'),
    url(r'^ipsearch/$', views.ipsearch, name='ipsearch'),
    url(r'^noaccess/$', views.noaccess, name='noaccess'),
    url(r'^mygroups/$', views.mygroups, name='mygroups'),
]
