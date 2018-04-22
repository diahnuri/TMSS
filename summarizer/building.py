
# coding: utf-8

# In[1]:

def dataman (path,file):
    import os
    import sqlite3
    import numpy as np
    
    os.chdir(path)
    conn = sqlite3.connect(file)
    c = conn.cursor()
    
    all = c.execute('select * from berita')

    
    items = []
    
    for row in all:
        if len(row[1])<200:
            judul = row [0] 
            print ('panjang konten pada berita dengan judul :', judul, ', tidak melebihi 200 karakter')
        else :
            temp = {
                'judul' : row[0],
                'isi' : row[1]
            }
            items.append(temp)
    
    conn.close()
    return items


# In[2]:

def tokenizer (data):
    from nltk.tokenize import sent_tokenize as sento
    from nltk.tokenize import word_tokenize as worto
    from Sastrawi.Stemmer import StemmerFactory
    from Sastrawi.StopWordRemover import StopWordRemoverFactory
    
    
    stopword_factory = StopWordRemoverFactory.StopWordRemoverFactory()
    stemmer_factory = StemmerFactory.StemmerFactory()
    stopwords = stopword_factory.create_stop_word_remover()
    stemmer = stemmer_factory.create_stemmer()
 
    
    for berita in data:
        berita['tokenized']= {
            'bersih':[]
        }
        isi = berita['isi']
        sentences = sento(isi)
        berita['tokenized']['sentences']=sentences
        
#         kena sastrawi
        lemmasIndo = []
        for kalimat in sentences :
            hasil_stem = stemmer.stem(kalimat)
            hasil_stop = stopwords.remove(hasil_stem)
#             asd = worto(hasil_stop)
            berita['tokenized']['bersih'].append(hasil_stop)
        
    return data


# In[3]:

def wordtoken (data):
    from nltk.tokenize import word_tokenize as worto
    for berita in data:
        berita['wordToken']=[]
        sentences = berita['tokenized']['bersih']
        for kalimat in sentences:
            berita['wordToken'].append(worto(kalimat))
    return data


# In[4]:

def vocabulary_builder (corpus):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.feature_extraction.text import CountVectorizer
    import pickle
    
    
    vectorizer = TfidfVectorizer(analyzer='word', min_df = 0)
    vec_train = vectorizer.fit_transform(corpus)
    
    pickle.dump(vectorizer.vocabulary_,open("vocab.pkl","wb"))
    return


# In[5]:

def tfidf (data):
    from sklearn.feature_extraction.text import TfidfTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
    import pickle
    
    transformer = TfidfTransformer()
    loaded_vec = TfidfVectorizer(analyzer='word', min_df = 0,vocabulary=pickle.load(open("vocab.pkl", "rb")))
    for item in data:
        kalimats = item['tokenized']['bersih']
        tfidf = transformer.fit_transform(loaded_vec.fit_transform(kalimats))
        item['verbose']={
            'tfidf':[]
        }
        item['verbose']['tfidf'].append(tfidf)
    
#     print(tfidf)
    return data


# In[6]:

def f2 (data):
    import numpy as np
    for berita in data:
        panjang = len(berita['tokenized']['bersih'])
        berita['skor']={
            'f2':[]
        }
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
        berita['skor']['f2']= temp
    return data


# In[7]:

def f3 (data):
    for berita in data:
        berita['skor']['f3']=[]
        skors = berita['skor']['f3']
        sentences = berita['tokenized']['bersih']
        len_max = max(len(kalimat.split())for kalimat in sentences)
        for kalimat in sentences:
            skor = len(kalimat.split())/len_max
            skors.append(skor)
            
    return data


# In[8]:

def f1 (data):
    for berita in data:
        tfidf = berita['verbose']['tfidf']
        berita['skor']['f1']=[]
        skorf1 = berita['skor']['f1']
        for sentences in tfidf:
            skorsentences = sentences.toarray()
            for skorkalimat in skorsentences:
                skorf1.append(sum(skorkalimat))
                
    
    return data


# In[9]:

def f7 (data):
    import re
    for berita in data:
        sentences = berita['tokenized']['bersih']
        berita['skor']['f7']=[]
        skor = berita['skor']['f7']
        for kalimat in sentences:
            if len(kalimat.split()) > 0:
                temp = len(re.findall('([0-9]+)',kalimat))/len(kalimat.split())
                skor.append(temp)
            else:
                skor.append(0)
    return data


# In[10]:

def latentDir ():
#     ini cuman intuk tes bisa masuk sini apa engga LDA modelnya
    import gensim
    from gensim import corpora
    from gensim.corpora.dictionary import Dictionary
    from gensim.models.ldamodel import LdaModel
    import os
    os.chdir('D:/[Projects]/corpus/wiki2')
    mm_corp = corpora.MmCorpus('./LDA/wiki_mini_bow.mm')
    id2word = Dictionary.load('./LDA/wiki_mini.dict')
    lda = LdaModel.load('./LDA/lda_model_mini_wiki.model')
    
    if lda != None :
        print('Model LDA berhasil di load')
    else :
        print('model LDA gagal di load')
    return


# In[11]:

def f4 (data):
    from Sastrawi.Stemmer import StemmerFactory
    from Sastrawi.StopWordRemover import StopWordRemoverFactory
    
    import gensim
    from gensim import corpora
    from gensim.corpora.dictionary import Dictionary
    from gensim.models.ldamodel import LdaModel
    from gensim.matutils import cossim as cs
    import os
    os.chdir('D:/[Projects]/corpus/wiki2')
    mm_corp = corpora.MmCorpus('./LDA/wiki_mini_bow.mm')
    id2word = Dictionary.load('./LDA/wiki_mini.dict')
    lda = LdaModel.load('./LDA/lda_model_mini_wiki.model')
    
    
    stopword_factory = StopWordRemoverFactory.StopWordRemoverFactory()
    stemmer_factory = StemmerFactory.StemmerFactory()
    stopwords = stopword_factory.create_stop_word_remover()
    stemmer = stemmer_factory.create_stemmer()
    
    
    for berita in data:
        judul = stemmer.stem(berita['judul'])
        judul = stopwords.remove(judul)
        bow_judul = id2word.doc2bow(judul.lower().split())
        lda_judul = lda[bow_judul]
        
        sentences = berita['tokenized']['bersih']
        
        berita ['skor']['f4']=[]
        skor = berita['skor']['f4']
#         loop tiap kalimat kasih lda dan distance


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
        return data


# In[12]:

def jsd(x,y):
    import numpy as np
    #Jensen-shannon divergence
    import warnings
    warnings.filterwarnings("ignore", category = RuntimeWarning)
    x = np.array(x)
    y = np.array(y)
    d1 = x*np.log2(2*x/(x+y))
    d2 = y*np.log2(2*y/(x+y))
    d1[np.isnan(d1)] = 0
    d2[np.isnan(d2)] = 0
    d = 0.5*np.sum(d1+d2)    
    return d


# In[13]:

def GeneticAlg  (data):
    import random
    from deap import base, creator, tools, algorithms
    
    return


# ## Testing Area

# In[14]:

def main_summirze_build (path,file):


    latentDir()
    alldats = dataman(path,file)
    alldats = tokenizer(alldats)
    # # for item in tokened :
    # #     print (item['tokenized']['bersih'])
    allKalimats=[kalimat for berita in alldats for kalimat in berita['tokenized']['bersih']]
    vocabulary_builder(allKalimats)
    alldats = tfidf(alldats)
    alldats = f2(alldats)
    alldats = f3(alldats)
    alldats = f1(alldats)
    alldats = f7(alldats)
    alldats = wordtoken(alldats)
    return alldats
    


# In[15]:

path = 'D:/[Projects]/corpus'
file = 'berits.sqlite'
final_shet = main_summirze_build(path,file)


# In[16]:

# for item in alldats:
#     for i in item['verbose']['tfidf']:
#         print(i.toarray())
#         print('---------------------------------')
# for berita in alldats:
#     print(berita['skor']['f7'])

