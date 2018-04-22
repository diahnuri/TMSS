##THIS IS THE CODE OF THE CREATE TAB

#import library2 yg dibutuhkan
import os
import pickle
import numpy as np
import tensorflow as tf
from nltk.tokenize import TweetTokenizer, word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from openpyxl.chart.label import DataLabel
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense
from dlnn.models import *
#from preprocess.bigram import F_BG
from preprocess.ED_rule import F_EDR, correction_3
#from preprocess.ED import F_ED


##deklarasikan file & library yang dibutuhkan
BASE_DIR = os.path.dirname(__file__)
modelpath = os.path.join(BASE_DIR,'Model')

#stopword removal bahasa Indonesia
stopWordIndo = word_tokenize(open(os.path.join(BASE_DIR,'stopword.txt'),encoding="utf8").read()) 
#sastrawi stemming 
stemmer = StemmerFactory().create_stemmer() 
#tweet tokenizer
tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
#load lokasi File data dan label dari data base


##FILEDATA TEST ==> tempat data dan label siap untuk diproses
fileData =[] 
fileLabel =[]
Y = fileLabel

##stemming
def stemming(namefolder):
    loadDataSet = dataSet.objects.filter(topik = namefolder)
    for data in loadDataSet:
        print(data.tweet,data.label)
        try:
            fileData.append(stemmer.stem(F_EDR(data.tweet))) #dengan formalisasi (harus menggunakan internet)
        except:
            fileData.append(stemmer.stem(correction_3(data.tweet))) #tanpa formalisasi hanya typo correction
        fileLabel.append(data.label)
    

##Transformation / Feature Extraction Option
#BAG OF WORD
def bow(namefolder):
    #proses prepropcessing + feature selection + transformation (extraction)
    print(len(fileData),len(fileLabel))
    vectorizer = CountVectorizer(stop_words=frozenset(stopWordIndo),tokenizer=tknzr.tokenize)
    bow        = vectorizer.fit_transform(fileData).todense()
    pickle.dump(vectorizer.vocabulary_, open(modelpath+'/'+namefolder+'/bow_vocab.pkl', 'wb'))#simpan vocabulary dalam bentuk pikle
    return bow, len(vectorizer.vocabulary_)

#TF biner
def tfBiner(namefolder):
    #proses prepropcessing + feature selection + transformation (extraction)
    vectorizer = CountVectorizer(binary=True,stop_words=frozenset(stopWordIndo),tokenizer=tknzr.tokenize)
    tfBiner    = vectorizer.fit_transform(fileData).todense()
    pickle.dump(vectorizer.vocabulary_, open(modelpath+'/'+namefolder+'/tfBiner_vocab.pkl', 'wb'))#simpan vocabulary dalam bentuk pikle
    return tfBiner, len(vectorizer.vocabulary_)

#TF-IDF
def tf_idf(namefolder):
    #proses prepropcessing + feature selection + transformation (extraction)
    ##TF
    vectorizer = CountVectorizer(stop_words=frozenset(stopWordIndo),tokenizer=tknzr.tokenize) 
    TFraw      = vectorizer.fit_transform(fileData).todense()
    ##IDF
    tfIdf  = TfidfTransformer(norm="l2",use_idf=True)
    ##TF-IDF
    tf_idf = tfIdf.fit_transform(TFraw).todense()
    pickle.dump(vectorizer.vocabulary_, open(modelpath+'/'+namefolder+'/tf_idf_vocab.pkl', 'wb'))#simpan vocabulary dalam bentuk pikle
    return tf_idf, len(vectorizer.vocabulary_)

#n-Gram / bigram
def bigram(namefolder):
    #proses prepropcessing + feature selection + transformation (extraction)
    vectorizer = CountVectorizer(ngram_range=(2,2),stop_words=frozenset(stopWordIndo),tokenizer=tknzr.tokenize)
    bigram    = vectorizer.fit_transform(fileData).todense()
    pickle.dump(vectorizer.vocabulary_, open(modelpath+'/'+namefolder+'/bigram_vocab.pkl', 'wb'))#simpan vocabulary dalam bentuk pikle
    return bigram, len(vectorizer.vocabulary_)

##MODELLING PROCESS
# Save model ke dalam file JSON (serialize model)
def saveModel(model,name,namefolder):
    #simpan model dalam bentuk json11
    model_json = model.to_json()
    with open(modelpath+'/'+namefolder+'/'+name+"_model.json", "w") as json_file:
        json_file.write(model_json)
    #simpan weights dalam bentuk HDF5
    model.save_weights(modelpath+'/'+namefolder+'/'+name+"_weight.h5")
    print("Model tersimpan!")

# DEEP LEARNING NEURAL NETWORK
def DLNN2(X,lengVocab): #modelling 2 kelas sentimen
    #pendeskripsian model
    model = Sequential()
    model.add(Dense(60, input_dim=lengVocab, init='uniform', activation='relu'))
    model.add(Dense(20, init='uniform', activation='relu'))
    model.add(Dense(1, init='uniform', activation='sigmoid'))
    #compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['precision','recall'])#kategori binari
    # pembagian data set untuk verifikasi ==> menjadi 90% data train dan 10% data test
    seed = 8
    np.random.seed(seed) #pembagian secara random
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.1, random_state=seed)
    # fit data ke dalam model
    #model.fit(X_train, y_train, validation_data=(X_test,y_test), nb_epoch=35, batch_size=5)
    model.fit(X, Y, nb_epoch=35, batch_size=5) ##the same train and test/validation data set
    # evaluasi hasil pemodelan
    scores = model.evaluate(X,Y) 
    print("")
    print("%s: %.2f%%" %(model.metrics_names[1], scores[1]*100))
    print("%s: %.2f%%" %(model.metrics_names[2], scores[2]*100))
    print("F1:" , f1(scores[1],scores[2])*100,"%")
    #print(list(zip(model.predict(X_test),y_test))) #menguji prediksi dengan data testing
    return model

def DLNN3(X,lengVocab): #modeling 3 kelas sentimen
    #pendeskripsian model
    Y = np_utils.to_categorical(fileLabel)#label 3 kelas sentimen

    model = Sequential()
    model.add(Dense(75, input_dim=lengVocab, init='normal', activation='relu'))
    model.add(Dense(25, init='normal', activation='relu'))
    model.add(Dense(3, init='normal', activation='sigmoid'))
    # Compile model
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['precision','recall'])
    #Manual verification data set ==> split into 90% for train and 10% for test
    seed = 8
    np.random.seed(seed) #pembagian secara random
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.1, random_state=seed)
    # fit data ke dalam model
    # Fit the model
    #model.fit(X_train, y_train, validation_data=(X_test,y_test), nb_epoch=35, batch_size=5)
    model.fit(X, Y, nb_epoch=35, batch_size=5) ##the same train and test/validation data set
    # evaluate the model
    scores = model.evaluate(X_train,y_train) 
    print("")
    print("%s: %.2f%%" %(model.metrics_names[1], scores[1]*100))
    print("%s: %.2f%%" %(model.metrics_names[2], scores[2]*100))
    print("F1:" , f1(scores[1],scores[2])*100,"%")
    #print(list(zip(model.predict(X),Y))) ##check the predict's answer
    return model

# Fungsi mendapatkan nilai f1
def f1(precision,recall):
    f1 = 2*precision*recall/(precision+recall)
    return f1


#Main Process02
def runMethod(method,feature,name,namefolder):
        X, lengVocab = feature
        saveModel(method(X, lengVocab),name,namefolder)

def runpross(opsi):
    if  (opsi== 2):    
        method = DLNN2
    elif(opsi == 3):
        method = DLNN3
    return method

def call(opsi,namefolder):
    with tf.Session():
        stemming(namefolder)
        method =runpross(opsi)
        runMethod(method,bow(namefolder),'bow',namefolder)
        runMethod(method,tfBiner(namefolder),'tfBiner',namefolder)
        runMethod(method,tf_idf(namefolder),'tf_idf',namefolder)
        runMethod(method,bigram(namefolder),'bigram',namefolder )
        print('finish')