from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from nltk.tokenize import WhitespaceTokenizer
from sklearn import metrics
from sklearn.svm import LinearSVC
import numpy as np
import pickle
import re
import os
import peewee as pw
import requests

model_path = os.path.join(os.path.dirname(__file__), 'model')
dataset_path = os.path.join(os.path.dirname(__file__), 'dataset')
vocab_path = os.path.join(model_path, 'vocab')

def regex_when(berita):
    when_word_list = set(map(lambda x: x.strip('\n') , open(os.path.join(dataset_path, 'kapan_list.txt'), 'r').readlines()))
    expression = re.compile(
        '(' +
        '|'.join(re.escape(item) for item in when_word_list) +
        '|\(\d+\/\d+\/\d+\)' +
        '|\(\d+\/\d+\)' +
        '|(\d{1,2}.\d{2})'
        ')')
    
    when_index = list()
    
    for index, kalimat in enumerate(berita):
        if expression.search(kalimat.lower()):
            when_index.append(index)
    
    return [berita[index] for index in when_index]

def f4_weight(list_sentences):
    f4 = list();
    for index, sentence in enumerate(list_sentences):
        other_sentences = [item for sublist in (list_sentences[:index]+list_sentences[index+1:]) for item in sublist]
        intercept = set(sentence).intersection(other_sentences)
        union = set(sentence).union(other_sentences)
        f4.append(len(intercept) / float(len(union)))
    
    return f4

def f5_weight( list_sentences, title ):
    f5 = list()
    for sentence in list_sentences:
        f5.append(len(set(title).intersection(sentence)) / float(len(set(title).union(sentence))))
    return f5

def f2_weight(list_sentences):
    f2 = list()
    corpus = pickle.load(open(os.path.join(model_path, 'corpus_token.p'), "rb" ))
    corpus_len = len(corpus)
    
    sentences_len = len(list_sentences)
    
    for sentence in list_sentences:
        #panjang setiap kalimat
        sentence_len = len(sentence)
        if(sentence_len == 0):
            continue
        f2_temp = 0
        for token in set(sentence):
            tfi = sentence.count(token)
            sentence_that_contain_word = len(list(filter(lambda sent: token in sent, list_sentences)))
            corpus_that_contain_word = len(list(filter(lambda sent: token in sent, corpus)))
            pkss = sentence_that_contain_word/len(list_sentences)
            pss = sentences_len/corpus_len
            if(corpus_that_contain_word == 0):
                continue
            else:
                pk = corpus_that_contain_word/corpus_len
                f2_temp += tfi*((pkss*pss)/pk)
        f2.append(f2_temp/sentence_len)
        
    return f2

def bow(list_sentences, vocab = 'all'):
    if vocab not in ['all', 'f4', 'f5', 'sum']:
        print('error')
        return
    
    vocab = pickle.load(open(os.path.join(vocab_path, vocab+"_bow_vocab.p"), "rb" ))
    count_vectorizer = CountVectorizer(analyzer = "word", vocabulary=vocab)
    return count_vectorizer.fit_transform([' '.join(sentence) for sentence in list_sentences]).toarray()

def tfidf(list_sentences, vocab = 'all'):
    if vocab not in ['all', 'f4', 'f5', 'sum']:
        print('error')
        return
    
    vocab = pickle.load(open(os.path.join(vocab_path, vocab+"_tfidf_vocab.p"), "rb" ))
    tfidf_vectorizer = TfidfVectorizer(analyzer = "word", vocabulary=vocab)
    return tfidf_vectorizer.fit_transform([' '.join(sentence) for sentence in list_sentences]).toarray()

def predict(berita, f2=list(), f4=list(), f5=list()):
    if(len(f2)<=0):
        f2=f2_weight(berita['token_isi'])
    if(len(f4)<=0):
        f4=f4_weight(berita['token_isi'])
    if(len(f5)<=0):
        f5=f5_weight(berita['token_isi'], berita['token_judul'])
    
    weight = list(map(lambda f2, f4, f5: [f2*30, f4*39, f5*49], f2, f4, f5))
    feature = list(map(lambda t, b, w: np.append(np.append(t, b), w), tfidf(berita['token_isi']), bow(berita['token_isi']), weight))
    clf = pickle.load(open(os.path.join(model_path, "all_btw_model.p"), "rb" ))
    code_prediction = clf.predict(feature)
    
    #labeling stop here
    label_prediction = list()
    for kalimat, prediction in zip(berita['list_isi'], code_prediction):
        label_prediction.append({'kalimat':  kalimat, 'kode': prediction})
        
    return label_prediction

def transform_output(judul, prediction_code, f5):
    prediction = {
        'name': judul,
        'kiri': [
            {'name': 'apa', 'kiri': []},
            {'name': 'dimana', 'kiri': []},
            {'name': 'bagaimana', 'kiri': []}
        ],
        'kanan': [
            {'name': 'kapan', 'kanan': []},
            {'name': 'siapa', 'kanan': []},
            {'name': 'mengapa', 'kanan': []}
        ]
    }
    
    prediction['image'] = get_image(judul)
    
    f5_ = 0
    
    for p, f in zip(prediction_code, f5):
        if(p['kode'][0]):
            if(f>f5_):
                f5_=f
                prediction['kiri'][0]['kiri'].append({'name': p['kalimat']})
        if(p['kode'][1]):
            if(len(prediction['kiri'][1]['kiri'])<=0):
                prediction['kiri'][1]['kiri'].append({'name': p['kalimat']})
        if(p['kode'][2]):
            prediction['kiri'][2]['kiri'].append({'name': p['kalimat']})
        if(p['kode'][3]):
            if(len(prediction['kanan'][0]['kanan'])<=0):
                prediction['kanan'][0]['kanan'].append({'name': p['kalimat']})
        if(p['kode'][4]):
            prediction['kanan'][1]['kanan'].append({'name': p['kalimat']})
        if(p['kode'][5]):
            prediction['kanan'][2]['kanan'].append({'name': p['kalimat']})
    
    return prediction

def get_image(query):
    url = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyBVwRyTou6HPn8M7FBgHEKyR1RPueIR1JM&q='+query+'&cx=002314383508018080868:gavvgjm6yoe&fields=items(title,link,pagemap/cse_image)'
    rqs = requests.get(url).json()
    link_image = rqs['items'][0]['pagemap']['cse_image'][0]['src']
    return link_image

def update_model(corpus_kalimat):
    count_vectorizer = CountVectorizer(analyzer = "word", max_features = 5000)
    kalimat_clean = [kalimat.clean for kalimat in corpus_kalimat]
    bow_train_data_features = count_vectorizer.fit_transform(kalimat_clean)
    
    bow_vocabulary = count_vectorizer.vocabulary_
    pickle.dump(bow_vocabulary, open(os.path.join(vocab_path, "all_bow_vocab.p"), 'wb' ))
    
    tfidf_vectorizer = TfidfVectorizer(analyzer = "word")
    tfidf_train_data_features = tfidf_vectorizer.fit_transform(kalimat_clean)
    
    tfidf_vocabulary = tfidf_vectorizer.vocabulary_
    pickle.dump(tfidf_vocabulary, open(os.path.join(vocab_path, "all_tfidf_vocab.p"), 'wb' ))
    
    # Numpy arrays are easy to work with, so convert the result to an array
    bow_train_data_features = bow_train_data_features.toarray()
    tfidf_train_data_features = tfidf_train_data_features.toarray()

    X = list(map(lambda data_, bow, tfidf: np.append(np.append(tfidf, bow), [data_.f2*30, data_.f4*39, data_.f5*49]), s, bow_train_data_features, tfidf_train_data_features))
    Y = list(map(lambda data_: data_.tipe.split(', '), s))
    
    clf = OneVsRestClassifier(LinearSVC(random_state=0))
    y = MultiLabelBinarizer(classes=classes).fit_transform(Y)
    clf.fit(X, y)
    pickle.dump(clf, open(os.path.join(model_path, "all_btw_model.p"), 'wb' ))
