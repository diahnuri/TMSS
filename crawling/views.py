from django.shortcuts import render, redirect, HttpResponse
from crawling.forms import *
from crawling.models import Hasil_Pencarian_Keyword, Tabel_Berita
from .tests import *
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
import pandas as pd
from builtins import int
import json
from django_tables2.config import RequestConfig
from django_tables2.export.export import TableExport
from .tables import Berita_Tabel
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from crawling.accessData import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# Create your views here.

# class HomePageView(TemplateView):
#     def get(self, request, **kwargs):
#         return render(request, 'index.html', context=None)

# Login required to the apps
@login_required(login_url=settings.LOGIN_URL)
def homePageView(request):
    if not request.user.is_authenticated():
        return redirect('/login')
    return render(request, 'index.html')

# class CrawlingView(TemplateView):
#     def get(self, request, **kwargs):
#         return render(request, 'crawling.html', context=None)
 
# View crawling page
def crawlingView(request):
    dataset = []
    data = None
    
    #jika ada action import data
    if request.method=='POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        df = pd.read_csv(csv_file)
        for index, row in df.iterrows():
            dataset.append({'judul_berita':row[0], 'konten_berita':row[1]})
        data = json.dumps(dataset)                          
    return render(request, 'crawling.html', {'data':data, 'form_input_berita':FormInputBerita, 'form_crawling_berita':PostForm})

#jika link register diklik memanggil view signup
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Berhasil Mendaftar Silahkan Login!')
            return redirect('/login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
    
def hasil(request):
    keyword1 = request.GET.get('keyword', '')
    jumlah1 = request.GET.get('jumlah', 5)
    situs1 = request.GET.get('situs', '')
    jumlah1 = int(jumlah1)
    get_check = request.GET.get('checkbox1', '0')
    if get_check=='0':
    #check situs apa yang dipilih
        if situs1=='det':
            list_news = scrap_detik(keyword1, jumlah1)
        elif situs1 == 'kom':
            list_news = crawl_kompas(keyword1, jumlah1)
        elif situs1 == 'lip':
            list_news = crawl_liputan6(keyword1, jumlah1)
    elif get_check=='1':
        date_start = request.GET.get('date_start')
        date_end = request.GET.get('date_end')
        if situs1=='det':
            list_news = scrap_detik1(keyword1, jumlah1, date_start, date_end)
        elif situs1 == 'kom':
            list_news = crawl_kompas(keyword1, jumlah1)
        elif situs1 == 'lip':
            list_news = crawl_liputan6(keyword1, jumlah1)
    dump = json.dumps(list_news)
     
    return render(request, 'hasil_keyword.html', {'list_news':list_news, 'dump': dump})

# def upload_file(request):
#     
#     
#     return render(request, 'crawling.html', {'header':header, 'list_csv':list_csv})

def word_summary(request):
    id_user = request.user
    a = getAllData(id_user)    
    return render(request, 'wordcloud_summary.html', {'list_berita_data':a})


def input_berita(request):
    if request.method=='POST':
        form = FormInputBerita(request.POST)
        if form.is_valid():
            judul1 = request.POST['judul_berita']
            konten1 = request.POST['konten_berita']
            user1 = request.user
            saveData(judul1, konten1, user1)
            
            #menampilkan pesan sukses
            messages.success(request, 'Berhasil Tersimpan!')
            return redirect('/crawling')
    else:
        form = FormInputBerita()
    return render(request, 'crawling.html')

def save_crawling(request):
    if request.method=='POST':
        listed = request.POST.get('crawling-data')
        list1 = json.loads(listed)
        for row in list1:
            try:
                judul = row['judul_berita']
                konten = row['konten_berita']
                saveData(judul, konten, request.user)
            except:
                pass
        
        #menampilkan pesan sukses
        messages.success(request, 'Berhasil Tersimpan!')
        return redirect('/crawling')

def pilih_analisis(request):
    if request.method=='POST':
        
        #mengecek analisis mana yang dipilih oleh user
        if 'list-data-mindmap' in request.POST:
            list1 = request.POST.get('list-data-mindmap')
            list2 = json.loads(list1)        
            print(list2)
            return render(request, 'crawling_mindmap.html', {'list_news1':list2})
        elif 'list-data-preprocess' in request.POST:
            list_prep = request.POST.get('list-data-preprocess')
            list_prep1 = json.loads(list_prep)            
            print(list_prep1)
            return render(request, 'crawling_preprocess.html', {'list_news1':list_prep1})
        elif 'list-data-summarizer' in request.POST:
            list_prep1 = request.POST.get('list-data-summarizer')
            list_prep2 = json.loads(list_prep1)            
            print(list_prep2)
            return render(request, 'crawling_summarizer.html', {'list_news1':list_prep2})
    else:
        return render(request, 'crawling.html')

def data_management_view(request):
    table = Berita_Tabel(Tabel_Berita.objects.filter(user_id = request.user))
    RequestConfig(request, paginate={'per_page':10}).configure(table)
    export_format = request.GET.get('_export', None)
    pks = request.GET.getlist('amend')
    
    #mengecek tombol mana yang dipilih user
    if 'delete' in request.GET:
        sel = Tabel_Berita.objects.filter(pk__in = pks)
        sel.delete()
    if 'mind_map' in request.GET:
        maps = Tabel_Berita.objects.filter(pk__in = pks)
        list1 = []
        for row in maps:
            list1.append({'judul_berita':row.judul_berita, 'konten_berita':row.konten_berita})
        return render(request, 'crawling_mindmap.html', {'list_news1':list1})
    if 'summarizer' in request.GET:
        maps = Tabel_Berita.objects.filter(pk__in = pks)
        list1 = []
        for row in maps:
            list1.append({'judul_berita':row.judul_berita, 'konten_berita':row.konten_berita})
        return render(request, 'crawling_summarizer.html', {'list_news1':list1})
    if 'preprocess' in request.GET:
        mapss = Tabel_Berita.objects.filter(pk__in = pks)
        list2 = []
        for row in mapss:
            list2.append({'id_berita':row.id_berita,  'judul_berita':row.judul_berita, 'konten_berita':row.konten_berita})
        return render(request, 'crawling_preprocess.html', {'list_news1':list2})
    if 'word_cloud' in request.GET:
        vis = Tabel_Berita.objects.filter(pk__in = pks)
        viss = []
        for row in vis:
            viss.append({'konten_berita':row.konten_berita})
        return render(request, 'wordcloud_universal.html', {'list_news1':viss})
    selected = Berita_Tabel(Tabel_Berita.objects.filter(pk__in = pks))
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, selected, exclude_columns=('amend', 'user_id', 'id_berita'))
        return exporter.response('table.{}'.format(export_format))
    
    
    return render(request, 'data_management.html', {'table':table})

def get_berita(request):
    id2 = request.GET.get('id')
    konten1 = getKontenBerita(id2)
    return JsonResponse({'konten': konten1})

def print_analisis(request):
    listt = []
    judul = request.POST.get('judul_berita')
    konten = request.POST.get('konten_berita')
    listt.append({'judul_berita':judul, 'konten_berita':konten.replace('"', '')})
    print('-----------------------------------')
    print(listt)
    #mengecek analisis mana yang dipilih user
    if 'mindmap-analysis' in request.POST:
        return render(request, 'crawling_mindmap.html', {'list_news1':listt})
    elif 'summarizer-analysis' in request.POST:
        return render(request, 'crawling_summarizer.html', {'list_news1':listt})
    elif 'wordcloud-analysis' in request.POST:
        return render(request, 'wordcloud_universal.html', {'list_news1':listt})

def login_view(request):
    if request.POST:
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        
        #mengecek username dan password, jika tidak memberi pesan eror
        if user is not None:
            
            #mengecek apakah user ada di basis data
            try:
                login(request, user)
            except:
                messages.add_message(request, messages.INFO, 'Akun ini belum ada')
            return redirect('/')            
        else:
            messages.add_message(request, messages.INFO, 'Username atau password Anda salah')                     
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/login/')

def data_management_view1(request):
    id_user = request.user
    a = getAllData(id_user)
    if request.method=='POST':
        check = request.POST.getlist('check')
        if 'delete' in request.POST:            
            for row in check:
                sel = Tabel_Berita.objects.filter(id_berita = row)
                sel.delete()
            return redirect('/data_management1/')
        if 'mind_map' in request.POST:            
            list1 = []
            for row in check:
                maps = Tabel_Berita.objects.filter(id_berita=row)[0]              
                list1.append({'judul_berita':maps.judul_berita, 'konten_berita':maps.konten_berita})
            return render(request, 'crawling_mindmap.html', {'list_news1':list1})
        if 'summarizer' in request.POST:
            list1 = []
            for row in check:
                maps = Tabel_Berita.objects.filter(id_berita=row)[0]
                list1.append({'judul_berita':maps.judul_berita, 'konten_berita':maps.konten_berita})
            return render(request, 'crawling_summarizer.html', {'list_news1':list1})
        if 'preprocess' in request.POST:
            list2 = []
            for row in check:
                mapss =  Tabel_Berita.objects.filter(id_berita = row)[0]
                list2.append({'id_berita':row, 'judul_berita':mapss.judul_berita, 'konten_berita':mapss.konten_berita})
            return render(request, 'crawling_preprocess.html', {'list_news1':list2})
        if 'word_cloud' in request.POST:             
            viss = []
            for row in check:
                vis = Tabel_Berita.objects.filter(id_berita = row)[0]
                remope = vis.konten_berita
                remope1 = remope.replace('"', '')
                viss.append({'konten_berita':remope1})
            return render(request, 'wordcloud_universal.html', {'list_news1':viss})
        if '_export' in request.POST:
            list1 = []
            for row in check:
                exp = Tabel_Berita.objects.filter(id_berita = row)[0]
                list1.append({'judul_berita':exp.judul_berita, 'konten_berita':exp.konten_berita})
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="exported_data.csv"'
        
            writer = csv.writer(response)
            writer.writerow(["Judul", "Konten"])
            for i in list1:
                try:
                    writer.writerow([i['judul_berita'], i['konten_berita']])
                except:
                    pass       
            return response
    return render(request, 'data_management2.html', {'list1':a})

def test_1(request):
    id_user = request.user
    q = getAllData(id_user)
 
    data = request.GET.get('data[]')
  
    paginator = Paginator(q, 10)
 
    sort = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')
    limit = int(request.GET.get('limit'))
    offset = int(request.GET.get('offset'))
 
    if order == 'asc':
        q = q.order_by(sort)
    else:
        q = q.order_by('-' + sort)
 
    paginator = Paginator(q, limit)
    page = int(offset / limit) + 1
    
    try:
        docs = paginator.page(page)
    except PageNotAnInteger:
        docs = paginator.page(1)
    except EmptyPage:
        docs = paginator.page(paginator.num_pages)
 
    docs_dict = {
        'total': paginator.count,
        'rows': [{'id': doc.id,
                  'judul_berita': doc.judul_berita,
                  'konten_berita':doc.konten_berita
                  } for doc in docs]
    }
    
    return JsonResponse(docs_dict)