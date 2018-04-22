from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from crawling.models import Tabel_Berita, Kalimat
from crawling.forms import *
import json
import time

from .preprocess import initialize_berita
from .process import *

def index(request):
    return render(request, 'index-mindmap.html')

def process_mindmap(request):
    if request.method == 'POST':
        list_data = request.POST.get('list-data', 0)
        
        if list_data == 0:
            out_vis, out_konf = create_label_mindmap(request.POST.get('judul_berita'), request.POST.get('konten_berita'))
            output_visualisasi = [out_vis]
            output_konfirmasi = [out_konf]
        
        else:
            list_data = json.loads(list_data)
            print(list_data)
            output_visualisasi = list()
            output_konfirmasi = list()
            for berita in list_data:
                out_vis, out_konf = create_label_mindmap(berita['judul_berita'], berita['konten_berita'])
                output_visualisasi.append(out_vis)
                output_konfirmasi.append(out_konf)
        
        return render(request, 'mindmap.html', {'prediction': json.dumps(output_visualisasi), 'confirmation': json.dumps(output_konfirmasi), 'range': range(len(output_visualisasi))})
    else:
        return redirect('/mindmap/')
    
def create_model(request):
    all = Kalimat.objects.filter(Q(f2__gt=0.0) | Q(f4__gt=0.0) | Q(f5__gt=0.0)).exclude(Q(tipe__isnull=True) | Q(tipe__exact=''))
    update_model(all)
    return JsonResponse({'status': 'success'})
    
def create_label_mindmap(judul, konten, id=''):
    process_berita = initialize_berita(judul, konten)
    f2 = f2_weight(process_berita['token_isi'])
    f4 = f4_weight(process_berita['token_judul'])
    f5 = f5_weight(process_berita['token_isi'], process_berita['token_judul'])
    
    prediction = predict(process_berita, f2, f4, f5)
    hasil_prediksi = list()
    for i, (p, k, t, f2_, f4_, f5_) in enumerate(zip(prediction, process_berita['list_isi'], process_berita['token_isi'], f2, f4, f5)):
        kode = p['kode']
        hasil_prediksi.append({
            'kalimat' : k,
            'clean' : ' '.join(t),
            'f2' : f2_,
            'f4' : f4_,
            'f5' : f5_,
            'index_kalimat' : i+1,
            'prediction': {
                'apa': True if p['kode'][0] else False,
                'dimana': True if p['kode'][1] else False,
                'bagaimana': True if p['kode'][2] else False,
                'kapan': True if p['kode'][3] else False,
                'siapa': True if p['kode'][4] else False,
                'mengapa': True if p['kode'][5] else False
            }
        })
    
    transformed_output = transform_output(judul, prediction, f5)
    
    return transformed_output, hasil_prediksi
    
def verify(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        id = request.POST.get('id_berita', 0)

        id = id if id !=0 else int(round(time.time() * 1000))

        confirmationData = json.loads(data)
        for kalimat in confirmationData:
            tipe = list()
            if(kalimat['prediction']['apa']):
                tipe.append('apa')
            if(kalimat['prediction']['dimana']):
                tipe.append('dimana')
            if(kalimat['prediction']['bagaimana']):
                tipe.append('bagaimana')
            if(kalimat['prediction']['kapan']):
                tipe.append('kapan')
            if(kalimat['prediction']['siapa']):
                tipe.append('siapa')
            if(kalimat['prediction']['mengapa']):
                tipe.append('mengapa')
                
            tipe = ', '.join(tipe)

            Kalimat.objects.create(
                kalimat = kalimat['kalimat'],
                clean = kalimat['clean'],
                f2 = kalimat['f2'],
                f4 = kalimat['f4'],
                f5 = kalimat['f5'],
                tipe = tipe,
                index_kalimat = kalimat['index_kalimat'],
                berita_id = id
            )

        return JsonResponse({'status': 'success'})
    
def process_mindmap1(request):
    if request.method == 'POST':
        judul = request.POST.get('judul_berita', None)
        konten = request.POST.get('konten_berita', None)
        if request.POST.get('list_berita', 0) == 0:
            output = [create_label_mindmap(judul, konten)]
        
        else:
            return JsonResponse('kjhkjhk')
        
        return render(request, 'mindmap.html', {'prediction': json.dumps(output), 'range': range(len(output))})
    else:
        return HttpResponse(4)

    