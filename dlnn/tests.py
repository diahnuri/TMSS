from django.core.files.uploadedfile import TemporaryUploadedFile
from django.test import TestCase
from dlnn.models import *
import pandas as pd
import numpy as np
import sqlite3
import os

# Create your tests here.

BASE_DIR = os.path.dirname(__file__)
Modelfolder = os.path.join(BASE_DIR,'Model')

def crfolder(f):
    folder = os.path.join(Modelfolder,f)
    os.makedirs(folder)
    return folder
    
def listfolder():
    list = os.listdir(Modelfolder)
    print(list)
    return list

def createfiletemp(f, g ,topik):
    dbsave = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dbsave = os.path.join(dbsave, 'db.sqlite3')
    conn = sqlite3.connect(dbsave)
    cursor = conn.cursor()
    data = []
    label = []
    data1=[]
    for chunk in f.chunks():
        data.append(chunk)
       
    for a in data:
        data1.append(a.decode('utf-8'))

    for chunk2 in g.chunks():
        label.append(chunk2)
        #tal.write(str(chunk2))
    label1 = []
    for a in label:
        label1.append(a.decode('utf-8')) 
            
    data=[]
    for a in data1:
        la = a.split('\r\n')
        for list in la:
            data.append(list)
    print(data)
    label = []
    for a in label1:
        la = a.split('\r\n')
        for list in la:
            label.append(list)     

    print(label)
    print(len(data)-1)
    for c in range(len(data)-1):
        print(c)
        a = data[c]
        b = label[c]
        print(label[c])
        cursor.execute("insert into dlnn_dataSet(tweet,label,topik) values (?, ?, ?);", (a,b,topik))
        conn.commit()    
    print('finish')

def savemodeldb(f,g):
    dbsave = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dbsave = os.path.join(dbsave, 'db.sqlite3')
    conn = sqlite3.connect(dbsave)
    cursor = conn.cursor()
    
    data = []
    label = []
    b = open(createfiletemp(f).temporary_file_path())
    print(b)
    for a in b:
        data.append(a)
    c = open(createfiletemp(g).temporary_file_path()).read()
    for a in c:
        label.append(a)
    fulldata = list(zip(data,label))
    for a in fulldata:
        cursor.execute("insert into dlnn_dataSet(tweet,label) values (?, ?);", (a[0],a[1]))