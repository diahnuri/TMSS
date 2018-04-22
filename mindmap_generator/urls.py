from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'process/$', views.process_mindmap, name='process_mindmap'),
    url(r'verify-prediction', views.verify, name='verify_prediction'),
    url(r'update-model', views.create_model, name='update_model'),
#     url(r'^simpan_hasil', views.simpan_hasil),
] 