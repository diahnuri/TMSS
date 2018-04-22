from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^summary/$', views.index),
    url(r'^asem/', views.kampung),
    url(r'summarized', views.ringkasan),
    url(r'kentung_test', views.ayam),
    url(r'ringkas', views.summary_only)
] 