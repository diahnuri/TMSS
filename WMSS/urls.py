"""WMSS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from crawling import views
from mindmap_generator import views as views_mindmap
from dlnn import views as views_dlnn

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.homePageView, name='homePageView'),
    url(r'^crawling/$', views.crawlingView, name='crawlingView'),
    url(r'^data_management/$', views.data_management_view, name='data_management_view'),
    url(r'^crawling/hasil_keyword/', views.hasil, name='hasil'),
    url(r'^crawling/word_summary/$', views.word_summary, name='word_summary'),
    url(r'^crawling/input_berita/$', views.input_berita, name='input_berita'),
    url(r'^crawling/word_summary/berita/$', views.get_berita, name='get_berita'),
    url(r'^crawling/print_analisis/$', views.print_analisis, name='print_analisis'),
    url(r'^mindmap/', include('mindmap_generator.urls')),
    url(r'^crawling/save_crawling/', views.save_crawling, name='save_crawling'),
    url(r'^crawling/pilih_analisis/', views.pilih_analisis, name='pilih_analisis'),
    url(r'^social_media_crawling/', include('social_media_crawling.urls')),
    url(r'^preprocess/', include('preprocess.urls', namespace='prepros')),
    url(r'^summarizer/', include('summarizer.urls')),
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^logout/', views.logout_view, name='logout_view'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^jst/', include('jst.urls', namespace='JST')),
    url(r'^dlnn/$', views_dlnn.index, name="dlnn_index"),
    url(r'^dlnn/verification/', views_dlnn.verif, name="dlnn_verif"),
    url(r'^dlnn/update_model/', views_dlnn.updatemodel, name="dlnn_update_model"),
    url(r'^dlnn/visualisasi/', views_dlnn.visualization, name="dlnn_visualisasi"),
    url(r'^lookdb/', views_dlnn.lihatDB, name="dlnn_index")
]
