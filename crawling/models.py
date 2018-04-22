from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Pencarian_Keyword(models.Model):
    url = models.CharField(max_length = 100)
    keyword = models.CharField(max_length = 100)
    
    def __str__(self):
        return self.url

class Hasil_Pencarian_Keyword(models.Model):
    word_result = models.CharField(max_length = 1000)
    
    def __str__(self):
        return self.word_result
    
class Tabel_Berita(models.Model):
    id_berita = models.AutoField(primary_key=True)
    judul_berita = models.CharField(max_length = 500)
    konten_berita = models.TextField(null = True)
    user_id = models.ForeignKey(User, null=True, unique=False)
    
    def __str__(self):
        return self.judul_berita

class Kalimat(models.Model):
    berita = models.ForeignKey(Tabel_Berita, on_delete=models.SET_NULL, null=True)
    kalimat = models.TextField()
    tipe = models.CharField(max_length=10, null=True)
    clean = models.TextField()
    f2 = models.DecimalField(max_digits=5, decimal_places=4)
    f4 = models.DecimalField(max_digits=5, decimal_places=4)
    f5 = models.DecimalField(max_digits=5, decimal_places=4)
    accepted = models.BooleanField(default=False)
    index_kalimat = models.IntegerField()

class Preproses(models.Model):
    berita = models.ForeignKey(Tabel_Berita, on_delete=models.SET_NULL, null=True)
    hasil_proses = models.TextField()
    user_id = models.ForeignKey(User, null=True, unique=False)