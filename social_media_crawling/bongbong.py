
# coding: utf-8

# In[1]:

def dataManagement (path,fileName):
    import os
    import numpy as np
    import sqlite3
    os.chdir(path)
    conn = sqlite3.connect(fileName)
    c = conn.cursor()
    all = c.execute('select * from tweets')

    benda = {'users':[],'twits':[],'ritwistUsr':[],'ritwits':[],'hashtags':[]}

    for row in all:
        benda['users'].append(row[1])
        benda['twits'].append(row[2])
        benda['ritwistUsr'].append(row[3])
        benda['ritwits'].append(row[4])
        benda['hashtags'].append(row[5])

    return benda


# In[2]:

def preproc (alldats):
#     just importing things
    from Sastrawi.Stemmer import StemmerFactory
    from Sastrawi.StopWordRemover import StopWordRemoverFactory
    import profile
    stopword_factory = StopWordRemoverFactory.StopWordRemoverFactory()
    stemmer_factory = StemmerFactory.StemmerFactory()
    stopwords = stopword_factory.create_stop_word_remover()
    stemmer = stemmer_factory.create_stemmer()
#     sastrawix

    import numpy as np
#     numpysh


# loops
    hasil = np.array([], dtype='<U140')
    dataTwit = np.array(alldats['twits'])
    for index , twit in np.ndenumerate(dataTwit):
        hasil_stem = stemmer.stem(twit)
        hasil_stop = stopwords.remove(hasil_stem)
        hasil = np.insert (hasil,hasil.size,hasil_stop)
    return hasil


# In[3]:

def bagofWords (data,nrange):
    from sklearn.feature_extraction.text import CountVectorizer
    vectorizer = CountVectorizer(binary=True,ngram_range = (nrange,nrange))
    bow = vectorizer.fit_transform(data).todense()
    print ('banyak kata unik dalam seluruh dokumen ', len(vectorizer.vocabulary_))
    return bow;


# #### Testing area

# In[4]:

def mainTotm(alldats):
    from datetime import datetime

    # preprocess
    start = datetime.now()
    preprocessed = preproc (alldats)
    print ('preproc time:',datetime.now()-start)

    # commit preprocessed documents
    alldats['preprocessed'] = preprocessed


    start = datetime.now()
    bow = bagofWords(alldats['preprocessed'],1)
    print ('bag of words assigning time:',datetime.now()-start)

    # commit bag of words
    alldats['bow']=bow
    print(alldats.keys())
