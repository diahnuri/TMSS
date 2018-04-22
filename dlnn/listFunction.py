##THIS IS THE CODE OF THE PREDICT TAB

#import library2 yg dibutuhkan
from nltk.tokenize import TweetTokenizer, word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from keras.models import model_from_json
from textblob import TextBlob as tb
#from preprocess.bigram import F_BG
from preprocess.ED_rule import F_EDR, correction_3
#from preprocess.ED import F_ED
import tensorflow as tf
import numpy as np
import pickle
import os

#untuk membaca lokasi file/folder
BASE_DIR = os.path.dirname(__file__)
modelpath = os.path.join(BASE_DIR,'Model') #folder model

##stopword removal bahasa Indonesia
stopwordpath = os.path.join(BASE_DIR,'StopWord.txt')
stopWordIndo = word_tokenize(open(stopwordpath,encoding='utf8').read()) 
##sastrawi prepocess 
stemmer = StemmerFactory().create_stemmer() 
##tweet tokenizer
tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)

##text processing
def prepocess(fileData):
    datas = []
    dataCleaning = tknzr.tokenize(fileData)
    for i in dataCleaning: #stopword removal
        if i not in stopWordIndo:
            datas.append(i)
    doc  = str(tb(' '.join(datas)))
    stemmed_file = stemmer.stem(doc)
    try: 
        doc_clean = F_EDR(stemmed_file) #dengan formalisasi (harus menggunakan internet)
    except:
        doc_clean = correction_3(stemmed_file) #tanpa formalisasi hanya typo correction
    return stemmed_file
        
#Feature Extraction Options
##BAG OF WORD
def bow(dataTest,namefolder):
    #proses prepropcessing + feature selection + transformation (extraction)
    vectorizer = CountVectorizer(decode_error='replace',vocabulary=pickle.load(open(modelpath+'/'+namefolder+'/bow_vocab.pkl', 'rb')))
    bow        = vectorizer.transform(dataTest).todense()
    return bow

##TF biner
def tfBiner(dataTest,namefolder):
    #proses prepropcessing + feature selection + transformation (extraction)
    vectorizer = CountVectorizer(decode_error='replace',binary=True,vocabulary=pickle.load(open(modelpath+'/'+namefolder+'/tfBiner_vocab.pkl', 'rb')))
    tfBiner    = vectorizer.transform(dataTest).todense()
    return tfBiner

##TF-IDF
def tf_idf(dataTest,namefolder):
    #proses prepropcessing + feature selection + transformation (extraction)
    ##TF
    vectorizer = CountVectorizer(decode_error='replace', vocabulary=pickle.load(open(modelpath+'/'+namefolder+'/tf_idf_vocab.pkl', 'rb')))
    TFraw      = vectorizer.fit_transform(dataTest).todense()
    ##IDF
    tfIdf  = TfidfTransformer(norm='l2')
    ##TF-IDF
    tf_idf = tfIdf.fit_transform(TFraw).todense()
    return tf_idf

##n-Gram / bigram
def bigram(dataTest,namefolder):
    #proses prepropcessing + feature selection + transformation (extraction)
    vectorizer = CountVectorizer(decode_error='replace',ngram_range=(2,2),vocabulary=pickle.load(open(modelpath+'/'+namefolder+'/bigram_vocab.pkl', 'rb')))
    bigram    = vectorizer.transform(dataTest).todense()
    return bigram

# load the model from disk
def modelVector(f,opsi,namefolder):
    if (opsi==1): #BOW
        json_file = open(modelpath+'/'+namefolder+'/bow_model.json', 'r')
        loaded_model_json = json_file.read()
        loaded_model = model_from_json(loaded_model_json)
        X_Test = bow(f,namefolder) #deklasrasikan X sesuai fitur
        loaded_model.load_weights(modelpath+'/'+namefolder+'/bow_weight.h5')
    elif(opsi==2): #TF Binary      
        json_file = open(modelpath+'/'+namefolder+'/tfBiner_model.json', 'r')
        loaded_model_json = json_file.read()
        loaded_model = model_from_json(loaded_model_json)
        X_Test = tfBiner(f,namefolder)
        loaded_model.load_weights(modelpath+'/'+namefolder+'/tfBiner_weight.h5')
    elif(opsi==3): #TF-IDF
        json_file = open(modelpath+'/'+namefolder+'/tf_idf_model.json', 'r')
        loaded_model_json = json_file.read()
        loaded_model = model_from_json(loaded_model_json)
        X_Test = tf_idf(f,namefolder)
        loaded_model.load_weights(modelpath+'/'+namefolder+'/tf_idf_weight.h5')
    else: #Bigram 
        json_file = open(modelpath+'/'+namefolder+'/bigram_model.json', 'r')
        loaded_model_json = json_file.read()
        loaded_model = model_from_json(loaded_model_json)
        X_Test = bigram(f,namefolder)
        loaded_model.load_weights(modelpath+'/'+namefolder+'/bigram_weight.h5')
    return X_Test,loaded_model
    
def predict(f,opsi,namefolder):
    clean_text = prepocess(f) #melakukan preprosing teks
    with tf.Session():
        X_Test, loaded_model = modelVector([clean_text],opsi,namefolder) #deklarasikan var X dan model yg digunakan
        result = loaded_model.predict(X_Test)
    #prediksi hasil
    finalResult = result[len(result)-1]
    print(finalResult)
    print('leng:',len(finalResult))
    print(np.argmax(finalResult))
    if (len(finalResult)>1): #jika 3 kelas sentimen
        if (np.argmax(finalResult)>1.9):
            return clean_text, 'Positif'
        elif (np.argmax(finalResult)>0.9):
            return clean_text, 'Netral'
        else:
            return clean_text, 'Negatif'
    else: #jika 2 kelas sentimen
        if(finalResult>[0.5]):
            return clean_text, 'Positif'
        else:
            return clean_text, 'Negatif'