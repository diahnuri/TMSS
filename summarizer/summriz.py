
# coding: utf-8

# In[62]:
import os
dir_path = os.path.join(os.path.dirname(__file__))
def dataman (judul,isi):
    
    berita = {
        'judul': judul,
        'konten' : isi,
        'skor' : {
            
        }
    }
    return berita


# In[63]:

def tokenizer (berita):
    
    from nltk.tokenize import sent_tokenize as sento
    from nltk.tokenize import word_tokenize as worto
    from Sastrawi.Stemmer import StemmerFactory
    from Sastrawi.StopWordRemover import StopWordRemoverFactory
    
    
    stopword_factory = StopWordRemoverFactory.StopWordRemoverFactory()
    stemmer_factory = StemmerFactory.StemmerFactory()
    stopwords = stopword_factory.create_stop_word_remover()
    stemmer = stemmer_factory.create_stemmer()
    
    teks = berita['konten']
    title = berita['judul']
    
    temp_title = stemmer.stem(title)
    temp_title = stopwords.remove(temp_title)
    
    berita['judul_bersih'] = temp_title
    berita['kalimat_bersih']=[]
    kalimat_bersih = berita['kalimat_bersih']
    
    sentences = sento(teks)
    berita ['kalimat_asli']=sentences
    
    for kalimat in sentences:
        temp_kalimat = stemmer.stem(kalimat)
        temp_kalimat = stopwords.remove(temp_kalimat)
        kalimat_bersih.append(temp_kalimat)
    
    return berita


# In[64]:

def tfidf (berita):
    
    from sklearn.feature_extraction.text import TfidfTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
    import pickle
    
    transformer = TfidfTransformer()
    loaded_vec = TfidfVectorizer(analyzer='word', min_df = 0,vocabulary=pickle.load(open("vocab_test.pkl", "rb")))
    kalimat = berita['kalimat_bersih']
    tfidf = transformer.fit_transform(loaded_vec.fit_transform(kalimat))
    berita['tfidf']= []
    berita['tfidf'].append(tfidf)
    
    return berita


# In[65]:

def vocabulary_builder (corpus):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.feature_extraction.text import CountVectorizer
    import pickle
    
    
    vectorizer = TfidfVectorizer(analyzer='word', min_df = 0)
    vec_train = vectorizer.fit_transform(corpus)
    
    pickle.dump(vectorizer.vocabulary_, open("vocab_test.pkl","wb"))
    return


# In[66]:

def f1 (berita):

    tfidf = berita['tfidf']
    berita['skor']['f1']=[]
    skorf1 = berita['skor']['f1']
    for sentences in tfidf:
        skorsentences = sentences.toarray()
        for skorkalimat in skorsentences:
            skorf1.append(sum(skorkalimat))

    
    return berita


# In[67]:

def f2 (berita):
    import numpy as np
    panjang = len(berita['kalimat_bersih'])
    berita['skor']['f2']=[]
    temp = np.zeros(panjang)
    skor = 1
    for index, x in np.ndenumerate(temp):
        if skor >0.05:
            temp[index]=skor
            skor = skor-0.2

        elif skor<0.05:
            temp[index]=0
        else:
            temp[index]=0

    temp[len(temp)-1]=1
    berita['skor']['f2']=temp
    return berita


# In[68]:

def f3 (berita):
    
    berita['skor']['f3']=[]
    skors = berita['skor']['f3']
    sentences = berita['kalimat_bersih']
    len_max = max(len(kalimat.split())for kalimat in sentences)
    for kalimat in sentences:
        skor = len(kalimat.split())/len_max
        skors.append(skor)

    return berita


# In[69]:

def f7 (berita):
    import re
    berita['skor']['f7']=[]
    sentences = berita['kalimat_bersih']
    
    skor = berita['skor']['f7']
    for kalimat in sentences:
        if len(kalimat.split()) > 0:
            temp = len(re.findall('([0-9]+)',kalimat))/len(kalimat.split())
            skor.append(temp)
        else:
            skor.append(0)
    return berita


# In[70]:

def f4 (berita):
    from Sastrawi.Stemmer import StemmerFactory
    from Sastrawi.StopWordRemover import StopWordRemoverFactory
    
    import gensim
    from gensim import corpora
    from gensim.corpora.dictionary import Dictionary
    from gensim.models.ldamodel import LdaModel
    from gensim.matutils import cossim as cs
    import os
#     os.chdir('D:/[Projects]/corpus/wiki2')
    
    id2word = Dictionary.load(os.path.join(dir_path, 'wiki_mini.dict'))
    mm_corp = corpora.MmCorpus(os.path.join(dir_path, 'wiki_mini_bow.mm'))
    lda = LdaModel.load(os.path.join(dir_path, 'lda_model_mini_wiki.model'))
    
    
    stopword_factory = StopWordRemoverFactory.StopWordRemoverFactory()
    stemmer_factory = StemmerFactory.StemmerFactory()
    stopwords = stopword_factory.create_stop_word_remover()
    stemmer = stemmer_factory.create_stemmer()
    
    

    judul = stemmer.stem(berita['judul'])
    judul = stopwords.remove(judul)
    bow_judul = id2word.doc2bow(judul.lower().split())
    lda_judul = lda[bow_judul]

    sentences = berita['kalimat_bersih']

    berita ['skor']['f4']=[]
    skor = berita['skor']['f4']

# distance belum bisa pake JSD karena belum ketemu solusi kalau beda ukuran matrixnya
# possibly karena dictionary LDA masih kecil jadi sedikit

    for kalimat in sentences:
        bow_kalimat = id2word.doc2bow(kalimat.lower().split())
        lda_kalimat = lda[bow_kalimat]
        skor_cs = cs(bow_kalimat,bow_judul)
        skor.append(skor_cs)           

#             print(lda_kalimat)
#             print(lda_judul)
#             print(kalimat)
#             print(judul)            
#             distance = jsd(lda_kalimat,lda_judul)
#             if -1 < distance < 1:
#                 skor.append(distance-1)               
#             else :
#                 skor.append(0)
    return berita


# In[71]:

def f5 (berita):
    
    
    return berita


# In[72]:

def f6 (berita):
    
    
    return berita


# In[73]:

def score_summary (berita):
    import pickle
    
    with open(os.path.join(dir_path, 'hasil.ga'), 'rb') as fp:
        weight = pickle.load(fp)

    f1 = berita['skor']['f1']
    w_f1 = weight[0]
    f2 = berita['skor']['f2']
    f3 = berita['skor']['f3']
    f4 = berita['skor']['f4']
    #     f5 = berita['skor']['f5']
    #     f6 = berita['skor']['f6']
    f7 = berita['skor']['f7']
    kalimat_asli = berita['kalimat_asli']
    berita['compiled_scores'] = []

    #     print(kalimat_asli)

    for index, kalimat in enumerate(kalimat_asli):
        allScore = []
        skor_f1 = f1[index] * w_f1
        allScore.append(skor_f1)
        allScore.append(f2[index] * weight[1])
        allScore.append(f3[index] * weight[2])
        allScore.append(f4[index] * weight[3])
        #         allScore.append(f5[index]*weight[4])
        #         allScore.append(f6[index]*weight[5])
        allScore.append(f7[index] * weight[6])
        berita['compiled_scores'].append([kalimat_asli[index], sum(allScore)])
    berita['compiled_scores'] = sorted(berita['compiled_scores'], key=getKey, reverse=1)

    return berita


# In[79]:

def the_summary (berita,rasio):
    import math
    
    panjang_all = len(berita)
    panjang_summary = float(panjang_all) * float(rasio)
    jumlah_kalimat = math.floor(panjang_summary)
    print(panjang_summary)
    summary = []
    if panjang_summary > panjang_all:
        for asd in berita:
            summary.append(asd[0])
            
    else:
        for index in range(0,(jumlah_kalimat)):
            summary.append(berita[index][0])
#             print (berita[index][0])
    
#     summary = [kalimat for kalimat in summary]
    return summary


# In[80]:

def getKey(item):
    return item[1]


# In[81]:

def mainSummarize(judul,isi,ratio):
    from datetime import datetime
    start = datetime.now()


    berita = dataman (judul, isi)
    berita = tokenizer(berita)
    corpus=[kalimat for kalimat in berita['kalimat_bersih']]
    vocabulary_builder(corpus)
    berita = tfidf(berita)
    berita = f1(berita)
    berita = f2(berita)
    berita = f3(berita)
    berita = f7(berita)
    berita = f4(berita)
#     print(berita['skor'])
    berita = score_summary(berita)
#     print(berita.keys())
#     print(ratio)
    complete = the_summary(berita['compiled_scores'],ratio)
    end = datetime.now() - start
    final_dats = {
        'berita':berita,
        'summary':complete,
        'waktu' : end,
        'rasio' : ratio*100
    }
    
#     print(berita)


    return final_dats


# In[83]:

# judul = 'MK Gelar Sidang Perdana Perppu Ormas yang Digugat HTI'
# isi ='Ketum PD SBY dan Ketum Gerindra Prabowo Subianto menggelar pertemuan di Cikeas. Seperti apa kesepakatannya?Pengawalan seperti apa? SBY menjelaskan salah satu cara pengawalannya adalah apabila yang dilakukan negara sudah tepat sesuai kepentingan rakyat maka akan didukung. Dan sebaliknya jika pemerintah tidak tepat dan menciderai rakyat, maka akan dikritisi, dikoreksi dan ditolak.SBY juga menyatakan ada kesepakatan Gerindra dan PD untuk bekerja sama. Kerjasama seperti apa?' 
# berita = mainSummarize(judul,isi,0.4)
# 
# print(' '.join(berita['summary']))


# In[ ]:



