from django.shortcuts import render
from .ED_rule import correction_3, bigram_corr5, F_EDR
from .ED import correction_2, bigram_corr4, F_ED
from .bigram import bigram_corr3, bigram_corr4, F_BG
from .formalisasi import correction, correction_2
from preprocess.form import PostForm
from preprocess.form2 import PostForm2
from .tests import getall
# from anaconda_navigator.utils.py3compat import request
from _io import TextIOWrapper, StringIO
from docutils.parsers.rst.directives import encoding
from django.http import HttpResponse
from wsgiref.util import FileWrapper
import csv, os

# Create your views here.
# def index(request):
#     tp = ['Edit Distance + Rule','Formalisasi']
#     input = ''
#     hasil = ''
#     textb = []
#     if request.method=="POST":
#         if 'inputA' in request.POST:
#             PR = request.POST.get("PR")
#             input = request.POST.get('inputtext')
#             hasil = correction_3(input)
#         elif 'inputB' in request.POST:
#             PS = request.POST.get("PS")
#             input = request.POST.get('inputtext')
#             hasil = correction(input)
#     return render(request, 'index_preprocess.html',{'input':input, 'hasil':hasil,'data':tp,'text1':textb})

def index(request):
    input = ''
    hasil = ''
    textb = []
#     hasil1 = bigram_corr5(gettweet())
    situs1 = request.POST.get('method', '')
    if situs1=='EDR':
        input = request.POST.get('inputtext')
        hasil = F_EDR(input)
    elif situs1 == 'ED':
        input = request.POST.get('inputtext')
        hasil = F_ED(input)
    elif situs1 == 'BG':
        input = request.POST.get('inputtext')
        hasil = F_BG(input)
    situs2 = request.POST.getlist('method1')
    if situs2 == 'FR':
        input = request.POST.get('inputtext')
        hasil = correction(input)
#     if 'fromDB' in request.POST:
#         hasil1 = bigram_corr5(gettweet())
    return render(request, 'index_preprocess.html', {'input':input, 'hasil':hasil, 'f':PostForm, 'f2':PostForm2})

def hasilCSV(request):
    if request.method == 'POST':
        name = request.FILES['fileInput'].name
        typeFile = name.split('.')[1]
        if(typeFile == 'txt'):
            reader = TextIOWrapper(request.FILES['fileInput'].file, encoding='utf-8')
        elif(typeFile == 'csv'):
            try:
                text = TextIOWrapper(request.FILES['fileInput'].file, encoding='utf-8')
                reader = csv.reader(text)
            except:
                text = StringIO(request.FILES['fileInput'].file.read().decode())
                reader = csv.reader(text)
        
        arrData = []
        for line in reader:
            line = ''.join(line)
            arrData.append(line)
        
        myfile = StringIO()
        
        metode = request.POST['metode']
        statusFormalisasi = request.POST.get('formalisasi', False)
        if(metode == 'EDR'):
            for line in arrData:
                hasil = F_EDR(line)
                myfile.write(hasil + os.linesep)
        elif(metode == 'ED'):
            for line in arrData:
                hasil = F_ED(line)
                myfile.write(hasil + os.linesep)
        elif(metode == 'BG'):
            for line in arrData:
                hasil = F_BG(line)
                myfile.write(hasil + os.linesep)
        
        myfile.flush()
        myfile.seek(0)
        
        response = HttpResponse(FileWrapper(myfile), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=hasil.csv'
        return response
    else:
        return render(request, 'index_preprocess.html', {})
        
        