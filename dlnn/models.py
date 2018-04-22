from django.db import models

# Create your models here.
##Tabel 01    
class dataSet(models.Model):
    tweet = models.CharField(max_length = 150)
    label = models.CharField(max_length = 20)
    topik = models.CharField(max_length = 30)
##Tabel 02
class kelasData(models.Model):
    topik = models.CharField(max_length = 30)
    kategori = models.CharField(max_length = 1)