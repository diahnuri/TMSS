'''
Created on Sep 1, 2017

@author: Asus-PC
'''
import pandas as pd
from crawling.models import Tabel_Berita
import csv

def getAllData(id1):
    list_berita_database = []
    
    #mengambil seluruh berita dari basis data yang dimiliki user
    for berita in Tabel_Berita.objects.filter(user_id = id1):
        list_berita_database.append({'judul_berita':berita.judul_berita, 'konten_berita':berita.konten_berita, 'id_berita':berita.id_berita})
    return list_berita_database

def saveData(judul, konten, id1):
    query = Tabel_Berita(judul_berita=judul, konten_berita = konten, user_id = id1)
    query.save()

def getKontenBerita(id1):
    berita = Tabel_Berita.objects.filter(id_berita=id1)[0]
    konten = berita.konten_berita
    return konten

def exportCsv(list1):
    with open('data_export.csv', 'w', newline='') as toWrite:
        writer = csv.writer(toWrite, delimiter = ",")
        writer.writerow(["Judul", "Konten"])
        for i in list1:
            try:
                writer.writerow([i['judul_berita'], i['konten_berita']])
            except:
                pass

def deleteData(id1):
    berita = Tabel_Berita.objects.filter(id_berita=id1)[0]
    berita.delete()