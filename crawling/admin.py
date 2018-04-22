from django.contrib import admin
from crawling.models import *
# Register your models here.

class Pencarian_Keyword_Admin(admin.ModelAdmin):
    list_display = ['url', 'keyword']
    list_filter = ()
    search_fields = ['url', 'keyword']
    list_per_page = 25

admin.site.register(Pencarian_Keyword, Pencarian_Keyword_Admin)

class Hasil_Pencarian_Keyword_Admin(admin.ModelAdmin):
    list_display = ['word_result']
    list_filter = ()
    search_fields = ['word_result']
    list_per_page = 25

admin.site.register(Hasil_Pencarian_Keyword, Hasil_Pencarian_Keyword_Admin)

class Tabel_Berita_Admin(admin.ModelAdmin):
    list_display = ['id_berita', 'judul_berita', 'konten_berita']
    list_filter = ()
    search_fields = ['id_berita', 'judul_berita', 'konten_berita']
    list_per_page = 25

admin.site.register(Tabel_Berita, Tabel_Berita_Admin)