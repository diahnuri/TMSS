from django.shortcuts import render
from .forms import *
from .summriz import *
from django.template.context_processors import request
# Create your views here.
def index(request):
    hasil = {}
    if request.method == "POST":
        form = FormInputBerita(request.POST)
        if form.is_valid():
            judul = request.POST.get('judul_berita')
            isi = request.POST.get('konten_berita')
            ratio = request.POST.get('rasio')
            print (judul, isi, ratio)
            #hasil = mainSummarize(judul, isi, ratio)
            return render(request, "index.html",{'form_input_berita':FormInputBerita, 'hasil':hasil})
    else:
        return render(request, 'summarizer.html',{'form_input_berita':FormInputBerita})

def kampung (request):
    form = FormInputBerita(request.POST)
    judul = request.POST.get('judul_berita')
    isi = request.POST.get('konten_berita')
    print(judul)
    return render(request, 'asem.html',{'form_input_berita':FormInputBerita})

def ringkasan(request):
    hasil = None
    if request.method == "POST":
        form = FormInputBerita(request.POST)
        if form.is_valid():
            judul = request.POST.get('judul_berita')
            isi = request.POST.get('konten_berita')
            ratio = float(request.POST.get('rasio'))
            print (judul, isi, ratio)
            hasil = mainSummarize(judul, isi, ratio)
            return render(request, "summary.html",{'form_input_berita':FormInputBerita, 'hasil':hasil})
    else:
        return render(request, 'summarizer.html',{'form_input_berita':FormInputBerita})


def summary_only(request):
    hasil = None
    if request.method == "POST":
        form = FormInputBerita(request.POST)
        if form.is_valid():
            judul = request.POST.get('judul_berita')
            isi = request.POST.get('konten_berita')
            ratio = float(request.POST.get('rasio'))
            print(judul, isi, ratio)
            hasil = mainSummarize(judul, isi, ratio)
            return render(request, "hasil_summary.html", {'form_input_berita': FormInputBerita, 'hasil': hasil})
    else:
        return render(request, 'summarizer.html', {'form_input_berita': FormInputBerita})

def ayam(request):
    return render(request,'hasil_summary.html')
