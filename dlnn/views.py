#import library2 yg dibutuhkan
from django.shortcuts import render, render_to_response, redirect
from urllib.request import HTTPRedirectHandler
from django.http import JsonResponse
from textblob import TextBlob as tb
from _io import TextIOWrapper
from dlnn.listFunction import *
from .listFunction2 import *
from .models import *
from .tests import * 
import json


#Create your views here.
def index(request):
    Topik = listfolder() #topik yang ada disimpan dalam bentuk folder-folder ==> filebased
    FeatX = ['1  Bag of Word','2  TF Binary','3  TF-IDF','4  Bigram'] #pilihan fitur extrac
    kelasSentimen = ['2 Kelas Sentimen - (positif atau negatif)','3 Kelas Sentimen - (positif, negatif, atau netral)'] #pilihan jumlah kelas sentimen
    tabledata = ''
    prediction = ''
    data = ''
    IA = ''
    topik = ''
    if request.method=="POST":
        if 'input' in request.POST:            
            tabledata = []
            topik = request.POST.get("topik")
            FE = request.POST.get("FE")
            IA = request.POST.get("inputArea")
            print(topik, FE, IA)
            if IA == "": #kalau menginput dengan file (multi input)
                inputFile = request.FILES["inputDataTest"]
                loadfile = TextIOWrapper(inputFile.file,encoding='utf-8')
                datatemp = []
                for i in loadfile:
                    datatemp.append(i)
                for i in datatemp:
                    prepros, prediction = predict(i,int(FE),topik) #memanggil fungsi predict dari listFunction
                    tabledata.append({
                        'input': i,
                        'prepros': prepros,
                        'prediction': prediction,
                        'confirm': True
                        })
                data = json.dumps(tabledata) #memasukan ke tabel hasil
            else: #kalau menginput dengan text area (1 input)
                prepros, prediction = predict(IA,int(FE),topik)#memanggil fungsi predict dari listFunction
                tabledata.append({
                    'input': IA,
                    'prepros': prepros,
                    'prediction': prediction,
                    'confirm': True
                    })
                data = json.dumps(tabledata) #memasukan ke tabel hasil
        
        if 'create' in request.POST and request.FILES: #memproses pembuatan model
            topik = request.POST.get('inputTopik') #judul topik
            KS = request.POST.get('KS') #banyaknya Kelas Sentimen
            dataS = request.FILES['inputData'] #dataset yg digunakan
            label = request.FILES['inputLabel'] #label yg digunakan
            
            createfiletemp(dataS,label,topik) #memanggil fungsi dari tsts untuk menginput dataset ke database
            crfolder(topik) #membuat folder topik
            call(int(KS),topik) #memanggil fungsi call untuk membuat model dari listfinction2
            q = kelasData(topik=topik, kategori=KS)
            q.save()
    return render(request, "index_dlnnFinal.html",{'selected_topic': topik,'data':FeatX,'sent':predict, 'IA':IA, 'hasil':data,'topik':Topik, 'kelasSentimen':kelasSentimen})

def verif(request):
    data = ''
    if request.method=="POST":
        data = request.POST.get('data')
        Topik = request.POST.get('topik')
        confirmedData = json.loads(data)
        for cd in confirmedData:
            if(cd['confirm']):
                label_data = 1 if cd['prediction'] == 'Positif' else 0
                q=dataSet(tweet=cd['input'],label=label_data,topik=Topik)
                q.save()
    return JsonResponse(data, safe=False)

def updatemodel(request): #melakukan remodeling ketika dipencet tombol remodeling
    if request.method=="POST":
        Topik = request.POST.get('topik')
        q = kelasData.objects.filter(topik=Topik)
        
        print(q[0].kategori,Topik)
        call(int(q[0].kategori),Topik)
    return JsonResponse("SAVED", safe=False)

def visualization(request): #terkoneksi ke visualisasi wordclouds wmss
    wordClouds = []
    if request.method=="POST":
        dataT = request.POST.get('data')
        loadData = json.loads(dataT)
        for row in loadData:
            wordClouds.append(row['prepros'])
        words = str(tb(' '.join(wordClouds)))
        print(":",words)
        list2 = []
        list2.append({'konten_berita':words})
    return render(request, "wordcloud_universal.html",{'list_news1':list2})

def lihatDB (request): #mengecek isi data base
    dataSet1 = dataSet.objects.all() 
    return render(request,"lookDB.html",{'data':dataSet1,})  