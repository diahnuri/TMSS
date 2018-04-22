from django.shortcuts import render, redirect
from .models import SentimenDB, FormalisasiKataDB, KataFormalDB, StopwordsIDDB
import string, time, random, os, logging, csv, json, requests
from zipfile import ZipFile
import numpy as np
import scipy.special as scp
from io import StringIO, TextIOWrapper, BytesIO
from builtins import str
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from collections import Counter
from preprocess.formalisasi import correction

# Create your views here.
def halamanMuka(request):
    return render(request, 'JST/halamanMuka.html', {})

def inputDataSentimen(request):
    return render(request, 'JST/inputDataSentimen.html', {})

def simpanSentimen(request):
    if request.method == 'POST':
        jenisFile = request.POST["jenisFile"]
        typeFile = (request.FILES['dataset'].name).split('.')[1]
        if (typeFile == 'txt'):
            readers = TextIOWrapper(request.FILES['dataset'].file, encoding='utf-8 ', errors='replace')
        elif (typeFile == 'csv'):
            try:
                text = TextIOWrapper(request.FILES['dataset'].file, encoding='utf-8 ', errors='replace')
                readers = csv.reader(text)
            except:
                text = StringIO(request.FILES['dataset'].file.read().decode())
                readers = csv.reader(text)
        else:
            return render(request, 'JST/inputDataSentimen.html', {})

        if (jenisFile == "positive"):
            sentimens = SentimenDB.objects.filter(sentiLab=1).values_list('kataSentimen', flat=True)
            for reader in readers:
                kata = ''.join(reader)
                #kata = str(reader)
                if kata not in sentimens:
                    priorPos = 0.90
                    priorNeg = 0.05
                    priorNet = 0.05
                    sentiLab = 1
                    sentimen = SentimenDB(kataSentimen=kata, sentiLab=sentiLab, priorPositive=priorPos,
                                          priorNegative=priorNeg, priorNetral=priorNet)
                    sentimen.save()
            return render(request, 'JST/halamanMuka.html', {})
        elif (jenisFile == "negative"):
            #SentimenDB.objects.all().delete()
            sentimenDict = SentimenDB.objects.filter(sentiLab=2).values_list('kataSentimen', flat=True)
            for reader in readers:
                kata = ''.join(reader)
                if kata not in sentimenDict:
                    priorPos = 0.05
                    priorNeg = 0.90
                    priorNet = 0.05
                    sentiLab = 2
                    sentimen = SentimenDB(kataSentimen=kata, sentiLab=sentiLab, priorPositive=priorPos,
                                          priorNegative=priorNeg, priorNetral=priorNet)
                    sentimen.save()
            return render(request, 'JST/halamanMuka.html', {})
        elif (jenisFile == "fileSentimenPrior"):
            sentimenDict = SentimenDB.objects.values_list('kataSentimen', flat=True)
            for reader in readers:
                kata = ''.join(reader)
                baris = kata.split(",")
                kata = baris[0]
                if kata not in sentimenDict:
                    priorPos = float(baris[1])
                    priorNeg = float(baris[2])
                    priorNet = float(baris[3])
                    if (priorPos > priorNeg):
                        if (priorPos > priorNet):
                            sentiLab = 1
                        elif (priorPos < priorNet):
                            sentiLab = -1
                    elif (priorPos < priorNeg):
                        if (priorNeg > priorNet):
                            sentiLab = 2
                        elif (priorNeg < priorNet):
                            sentiLab = -1
                    else:
                        sentiLab = -1

                    sentimen = SentimenDB(kataSentimen=kata, sentiLab=sentiLab, priorPositive=priorPos,
                                          priorNegative=priorNeg, priorNetral=priorNet)
                    sentimen.save()
            return render(request, 'JST/halamanMuka.html', {})

        elif (jenisFile == "sentilab"):
            return render(request, 'JST/inputDataSentimen.html', {})
        else:
            return render(request, 'JST/inputDataSentimen.html', {})
    else:
        return render(request,'JST/halamanMuka.html',{})

def simpanStopwords(request):
    if request.method == 'POST':
        # StopwordsIDDB.objects.all().delete()
        typeFile = (request.FILES['dataset'].name).split('.')[1]
        if (typeFile == 'txt'):
            readers = TextIOWrapper(request.FILES['dataset'].file, encoding='utf-8 ', errors='replace')
        elif (typeFile == 'csv'):
            try:
                text = TextIOWrapper(request.FILES['dataset'].file, encoding='utf-8 ', errors='replace')
                readers = csv.reader(text)
            except:
                text = StringIO(request.FILES['dataset'].file.read().decode())
                readers = csv.reader(text)
        else:
            return render(request, 'JST/inputDataSentimen.html', {})
        for line in readers:
            stopword = StopwordsIDDB(kataStopword=str(''.join(line)))
            stopword.save()
        #logging.warning("Save done")
        return render(request, 'JST/inputDataSentimen.html', {})

    else:
        return render(request, 'JST/inputDataSentimen.html', {})

class document(object):
    def __init__(self):
        self.length = 0
        self.words = {}
        self.priorSentiLabels = {}
        self.docID = ""

class dataset(object):
    def __init__(self):
        self.word2atr = {}
        self.sentiLex = {}
        self.freqWord = {}
        self.id2word = {}
        self.pdocs = {}

        self.numDocs = 0
        self.aveDocLength = 0.0000  # average document length
        self.vocabSize = 0
        self.corpusSize = 0
        self.numVocabs = 0
        self.maxLength = 0

        self.labeledPositiveWords = []
        self.labeledNegativeWords = []

        self.arrData = []

    def sentiFile(self, statusFSL, positiveMI=None, negativeMI=None):
        if(statusFSL == True):
            sentimen = SentimenDB.objects.values_list('kataSentimen', 'sentiLab', 'priorNetral', 'priorPositive', 'priorNegative')
            for senti in sentimen:
                #Recoding label sentimen dari DB model dimana 1:positive, 2:negative -> 1:positive, 0:negatitve
                if(str(senti[1]) == '2'):
                    label = 0
                elif(str(senti[1]) == '1'):
                    label = 1
                self.sentiLex[senti[0]] = [label, [float(senti[2]), float(senti[3]), float(senti[4])]]
        if(positiveMI != None):
            for kata in positiveMI:
                self.sentiLex[str(kata)] = [1, [0.05, 0.90, 0.05]]
        if(negativeMI != None):
            for kata in negativeMI:
                self.sentiLex[str(kata)] = [0, [0.05, 0.05, 0.05]]
        #sentimenDB = self.sentiLex
        return self.sentiLex

    def tokenisasi(self, teks):
        dataAwal = self.sentiLex.keys()
        arrNegasi = ['tidak', 'bukan', 'jangan', 'tak']
        kalimat = teks.lower()
        arrUji = kalimat.split()
        setBigram = False
        setBigramNegasi = False
        arrHasil = []
        for i in range(0, len(arrUji)):
            if(setBigram == True):
                setBigram = False
                pass
            elif(setBigramNegasi == True):
                setBigramNegasi = False
                pass
            else:
                if(i < (len(arrUji) - 1)):
                    kataAwal = arrUji[i]
                    kataAkhir = arrUji[i+1]
                    kataGabungan = kataAwal + " " + kataAkhir
                    if kataAwal in arrNegasi:
                        if(i < (len(arrUji) - 2)):
                            cekKata = arrUji[i+1] +" "+ arrUji[i+2]
                            if(cekKata in dataAwal):
                                token = kataAwal + " " + cekKata
                                arrHasil.append(token)
                                setBigram = True
                                setBigramNegasi = True
                        else:
                            token = kataGabungan
                            arrHasil.append(token)
                            setBigram = True
                    elif kataGabungan in dataAwal:
                        token = kataGabungan
                        arrHasil.append(token)
                        setBigram = True
                    elif kataAwal in dataAwal:
                        token = kataAwal
                        arrHasil.append(token)
                    else:
                        token = kataAwal
                        arrHasil.append(token)
                else:
                    token = arrUji[i]
                    arrHasil.append(token)
        # print(arrHasil)
        return arrHasil
        
    def readDataStream(self, arrData, statusStopwords, filtered):
        # Inisialisasi kata negasi
        daftarNegasi = ['tidak', 'bukan', 'tak', 'jangan']
        # idWord = self.pdataset.pdocs[d].words[t]
        # teks = self.id2word[idWord]
        # kata = teks.split()
        # if(len(kata) == 3):
        #     cekKata = 
        # elif (len(kata) == 2):
        #     pass
        # else:
        #     pass
        stopwords = StopwordsIDDB.objects.values_list('kataStopword', flat=True)
        stopwords = list(stopwords)
        filteredLimit = filtered

        # arrKataSebelum = []
        # arrKataTokenisasi = []

        #Menghapus sentiment lexicon yang ada di stopwords
        for kata in self.sentiLex.keys():
            try:
                stopwords.remove(kata)
            except ValueError:
                continue
                

        #Untuk menghitung frekuensi kemunculan kata untuk Model Prior Filtered Subjectivity Lexicon
        # self.freqWord['lorem'] = 0 #untuk mencegah genap
        for baris in arrData:
            # arrKataSebelum.append(len(baris.split()))
            line = self.tokenisasi(baris)
            barisLength = len(line)
            for i in range(0, barisLength):
                if line[i] not in self.freqWord.keys():
                    self.freqWord[str(line[i])] = 1
                else:
                    self.freqWord[str(line[i])] += 1
        #Proses membaca corpus dengan keterangan lexicon
        idx = 0
        
        for baris in arrData:
            #logging.warning(str(baris))
            self.pdoc = document()
            line = self.tokenisasi(baris)
            #print(line)
            # arrKataTokenisasi.append(len(line))
            

            #Checking stopwords
            if(statusStopwords == True):
                lineTemp = []
                for stopword in stopwords:
                    while True:
                        try:
                            line.remove(stopword)
                            lineTemp.append(stopword)
                        except ValueError:
                            break
                if(len(line) == 0):
                    line = lineTemp

            
            # if(len(line) % 2 == 0):
            #     line.append('lorem')
            docLength = len(line)

            if (docLength > self.maxLength):
                self.maxLength = docLength

            if (docLength > 0):
                self.arrData.append(baris)
                self.corpusSize += docLength
                #self.pdoc.length = docLength
                self.pdoc.docID = ("doc" + str(self.numDocs))
                self.pdoc.length = docLength
                self.numDocs += 1
                # Generate ID for tokens in the corpus, assign with voabulary id
                for k in range(0, docLength):
                    priorSenti = -1
                    if (line[k] not in self.word2atr.keys()):
                        if(self.freqWord[str(line[k])] > filteredLimit):
                            if (line[k] in self.sentiLex.keys()):
                                #print(str(line[k])+" - "+str(self.sentiLex[str(line[k])][0]))
                                self.word2atr[str(line[k])] = [self.numVocabs, self.sentiLex[str(line[k])][0],
                                                               self.sentiLex[str(line[k])][1]]
                                self.pdoc.words[k] = self.numVocabs                                     
                                self.pdoc.priorSentiLabels[k] = self.word2atr[str(line[k])][1]
                                #print(str(line[k]) + " - " +str(self.word2atr[str(line[k])][1]))

                                if(self.word2atr[str(line[k])][1] == 1):
                                    self.labeledPositiveWords.append(str(line[k]))
                                elif(self.word2atr[str(line[k])][1] == 0):
                                    self.labeledNegativeWords.append(str(line[k]))

                                self.id2word[self.numVocabs] = str(line[k])


                                self.numVocabs += 1
                            else:
                                # Memberikan label sentimen untuk kata negasi
                                arrKata = line[k].split()
                                if arrKata[0] in daftarNegasi:
                                    kataAkhir = ""
                                    if(len(arrKata) == 2):
                                        kataAkhir = arrKata[1]
                                    elif(len(arrKata) == 3):
                                        kataAkhir = arrKata[1] +" "+arrKata[2]

                                    if (kataAkhir in self.sentiLex.keys()):
                                        # print("Uji coba : "+kataAkhir)
                                        label = self.sentiLex[str(kataAkhir)][0]
                                        # print(str(label))
                                        if(label == 1):
                                            priorSenti = 0
                                        elif(label == 0):
                                            priorSenti = 1
                                #print(str(line[k])+" - "+ str(priorSenti))
                                #Akhir kasus untuk kata negasi
                                self.word2atr[str(line[k])] = [self.numVocabs, priorSenti, [1, 1, 1]]
                                self.pdoc.words[k] = self.numVocabs
                                self.pdoc.priorSentiLabels[k] = priorSenti

                                self.id2word[self.numVocabs] = str(line[k])

                                self.numVocabs += 1
                        else:
                            self.word2atr[str(line[k])] = [self.numVocabs, priorSenti, [1, 1, 1]]
                            self.pdoc.words[k] = self.numVocabs
                            self.pdoc.priorSentiLabels[k] = priorSenti

                            self.id2word[self.numVocabs] = str(line[k])

                            self.numVocabs += 1
                    else:
                        self.pdoc.words[k] = self.word2atr[str(line[k])][0]
                        self.pdoc.priorSentiLabels[k] = self.word2atr[str(line[k])][1]

            self.pdocs[idx] = self.pdoc
            idx += 1

        self.vocabSize = len(self.word2atr)
        self.aveDocLength = self.corpusSize / self.numDocs
        # for i in range(0, len(arrKataSebelum)):
        #     print(str(i)+" adalah "+str(arrKataSebelum[i])+" - "+str(arrKataTokenisasi[i]))

class modelJST(object):
    def __init__(self, alpha, beta, gamma, topics, name, statusStopwords, statusFSL, filtered, iterasi, positiveMI=None, negativeMI=None):
        if(positiveMI == None and negativeMI == None):
            self.word2atr = {}
            self.sentiLex = {}
            self.id2word = {}
            self.arrData = []

            self.numTopics = topics
            self.rangeSentiLabs = 2
            self.vocabSize = 0
            self.numDocs = 0
            self.corpusSize = 0
            self.aveDocLength = 0

            self.niters = iterasi  # 1000
            self.liter = 0
            self.savestep = 200  # 200
            self.twords = 20
            self.updateParaStep = 40  # 40

            self.alpha = alpha
            self.beta = beta
            self.gamma = gamma
            self.name = name
            self.statusStopwords = statusStopwords
            self.statusFSL = statusFSL
            self.filtered = filtered

            self.positiveMI = None
            self.negativeMI = None
        elif(positiveMI != None and negativeMI != None):
            self.word2atr = {}
            self.sentiLex = {}
            self.id2word = {}
            self.arrData = []

            self.numTopics = topics
            self.rangeSentiLabs = 2
            self.vocabSize = 0
            self.numDocs = 0
            self.corpusSize = 0
            self.aveDocLength = 0

            self.niters = iterasi  # 1000
            self.liter = 0
            self.savestep = 200  # 200
            self.twords = 20
            self.updateParaStep = 40  # 40

            self.alpha = alpha
            self.beta = beta
            self.gamma = gamma
            self.name = name
            self.statusStopwords = statusStopwords
            self.statusFSL = statusFSL
            self.filtered = filtered

            self.positiveMI = positiveMI
            self.negativeMI = negativeMI

    def execute_model(self, arrData):
        start = time.time()
        # definisi model dataset dari kelas dataset
        self.pdataset = dataset()
        # Mengeluarkan file berisi prior sentimen dari database
        self.sentiLex = self.pdataset.sentiFile(self.statusFSL, self.positiveMI, self.negativeMI)
        # Membuat dataset dengan masukkan array
        self.pdataset.readDataStream(arrData, self.statusStopwords, self.filtered)

        # Memanggil kamus kata dengan attribut dan kta dgn id
        self.word2atr = self.pdataset.word2atr
        self.id2word = self.pdataset.id2word
        self.arrData = self.pdataset.arrData

        for id in self.id2word.keys():
            print("Kata : "+ str(self.id2word[int(id)]))

        # Proses pemanggilan awal
        self.initializing_parameter()

        # Proses estimasi awal
        self.initializing_estimasi()

        # Proses estimasi
        self.estimasi_model()

        end = time.time()
        self.processTime = end - start

        # if (arrLabel == None):
        #     start = time.time()
        #     # definisi model dataset dari kelas dataset
        #     self.pdataset = dataset()
        #     # Mengeluarkan file berisi prior sentimen dari database
        #     self.sentiLex = self.pdataset.sentiFile(self.positiveMI, self.negativeMI)
        #     # Membuat dataset dengan masukkan array
        #     self.pdataset.readDataStream(arrData, self.statusStopwords, self.filtered)
        #
        #     # Memanggil kamus kata dengan attribut dan kta dgn id
        #     self.word2atr = self.pdataset.word2atr
        #     self.id2word = self.pdataset.id2word
        #
        #     # Proses pemanggilan awal
        #     self.initializing_parameter()
        #
        #     # Proses estimasi awal
        #     self.initializing_estimasi()
        #
        #     # Proses estimasi
        #     self.estimasi_model()

        #     myfile = StringIO()
        #     myfile.write("Nilai alpha : " + str(self.alpha) + os.linesep)
        #     myfile.write("Nilai beta : " + str(self.beta) + os.linesep)
        #     myfile.write("Nilai gamma : " + str(self.gamma) + os.linesep)
        #     myfile.write("Document mean : " + str(self.aveDocLength) + os.linesep)
        #     myfile.write("Filtered Subjectivity Lexicon : "+str(self.filtered)+os.linesep)
        #     myfile.write("Stopwords : "+str(self.statusStopwords)+os.linesep)
        #     myfile.write("Iterasi : " + str(self.niters) + os.linesep)
        #     myfile.write("Update iterasi : " + str(self.savestep))
        #     myfile.write(os.linesep)
        #
        #     for d in range(0, self.numDocs):
        #         myfile.write("dokumen ke : " + str(d) + os.linesep)
        #         # myfile.write("Gammasum dokumen ke " + str(d) +" : " + str(self.gammaSum_d[d]))
        #         myfile.write(str(self.pdataset.pdocs[d].length) + os.linesep)
        #         myfile.write("Sentimen Netral : " + str(self.pi_dl[d][0]) + os.linesep)
        #         myfile.write("Sentimen Positive : " + str(self.pi_dl[d][1]) + os.linesep)
        #         myfile.write("Sentimen Negative : " + str(self.pi_dl[d][2]) + os.linesep)
        #         # for l in range(0, self.rangeSentiLabs):
        #         #    myfile.write("Nilai dari alphaSUm : "+ str(self.alphaSum_l[l])+ os.linesep)
        #         myfile.write(os.linesep)
        #     end3 = time.time()
        #     myfile.write(str(end3 - start))
        #     myfile.flush()
        #     myfile.seek(0)
        #
        #     response = HttpResponse(FileWrapper(myfile), content_type='text/csv')
        #     response['Content-Disposition'] = 'attachment; filename=JST.txt'
        #     return response
        # else:
        #     start = time.time()
        #     arrLabel = arrLabel
        #     akurasi = 0
        #     numDoc = 0
        #     # definisi model dataset dari kelas dataset
        #     self.pdataset = dataset()
        #     # Mengeluarkan file berisi prior sentimen dari database
        #     self.sentiLex = self.pdataset.sentiFile()
        #     # Membuat dataset dengan masukkan array
        #     self.pdataset.readDataStream(arrData, self.statusStopwords, self.filtered)
        #
        #     # Memanggil kamus kata dengan attribut dan kta dgn id
        #     self.word2atr = self.pdataset.word2atr
        #     self.id2word = self.pdataset.id2word
        #
        #     # Proses pemanggilan awal
        #     self.initializing_parameter()
        #
        #     # Proses estimasi awal
        #     self.initializing_estimasi()
        #
        #     # Proses estimasi
        #     self.estimasi_model()
        #
        #     myfile = StringIO()
        #
        #     myfile.write("Jenis : "+str(self.name)+os.linesep)
        #     myfile.write("Nilai alpha : " + str(self.alpha) + os.linesep)
        #     myfile.write("Nilai beta : " + str(self.beta) + os.linesep)
        #     myfile.write("Nilai gamma : " + str(self.gamma) + os.linesep)
        #     myfile.write("Filtered Subjectivity Lexicon : " + str(self.filtered) + os.linesep)
        #     myfile.write("Stopwords : " + str(self.statusStopwords) + os.linesep)
        #     myfile.write("Document mean : " + str(self.aveDocLength) + os.linesep)
        #     myfile.write("Banyak kata berlabel : " + str(self.labelPrior) + os.linesep)
        #     myfile.write("Banyak jenis kata (formalisasi) : " + str(len(self.word2atr)) + os.linesep)
        #     myfile.write("Banyak dokumen : " + str(self.numDocs) + os.linesep)
        #     myfile.write(os.linesep)
        #
        #     for z in range(0, self.numTopics):
        #         myfile.write("Alpha untuk topik ke - " + str(z) + " : " + str(self.alpha_temp[z]) + os.linesep)
        #     myfile.write("Alpha total : " + str(self.alphaSum_l[1]) + os.linesep)
        #     myfile.write(os.linesep)
        #
        #     outRange = 0
        #
        #     for d in range(0, self.numDocs):
        #         myfile.write("dokumen ke : " + str(d) + os.linesep)
        #         # myfile.write("Gammasum dokumen ke " + str(d) +" : " + str(self.gammaSum_d[d]))
        #         myfile.write(str(self.pdataset.pdocs[d].length) + os.linesep)
        #         myfile.write("Sentimen Netral : " + str(self.pi_dl[d][0]) + os.linesep)
        #         myfile.write("Sentimen Positive : " + str(self.pi_dl[d][1]) + os.linesep)
        #         myfile.write("Sentimen Negative : " + str(self.pi_dl[d][2]) + os.linesep)
        #
        #         if (self.pi_dl[d][1] > self.pi_dl[d][2] and self.pi_dl[d][1] > self.pi_dl[d][0]):
        #             label = 1
        #             numDoc += 1
        #         elif(self.pi_dl[d][1] > self.pi_dl[d][2]):
        #             label = 1
        #             numDoc += 1
        #             outRange += 1
        #         elif(self.pi_dl[d][2] > self.pi_dl[d][1] and self.pi_dl[d][2] > self.pi_dl[d][0]):
        #             label = 0
        #             numDoc += 1
        #         elif(self.pi_dl[d][2] > self.pi_dl[d][1]):
        #             label = 0
        #             numDoc += 1
        #             outRange += 1
        #         else:
        #             label = 0
        #             numDoc += 1
        #             outRange += 1
        #
        #         if (label == arrLabel[d]):
        #             akurasi += 1
        #         # for l in range(0, self.rangeSentiLabs):
        #         #    myfile.write("Nilai dari alphaSUm : "+ str(self.alphaSum_l[l])+ os.linesep)
        #         myfile.write(os.linesep)
        #     myfile.write("Akurasi terhadap label : " + str(akurasi / numDoc) + os.linesep)
        #     myfile.write("Lari dari acuan pelabelan : " + str(outRange) + os.linesep)
        #     end3 = time.time()
        #     myfile.write("Waktu proses : " + str(end3 - start))
        #     myfile.flush()
        #     myfile.seek(0)
        #
        #     response = HttpResponse(FileWrapper(myfile), content_type='text/csv')
        #     response['Content-Disposition'] = 'attachment; filename=JST.txt'
        #     return response

    def initializing_parameter(self):
        self.numDocs = self.pdataset.numDocs
        self.vocabSize = self.pdataset.vocabSize
        self.corpusSize = self.pdataset.corpusSize
        self.aveDocLength = self.pdataset.aveDocLength

        # Membentuk model masing - masing fungsi
        self.nd = np.zeros((self.numDocs))
        self.ndl = np.zeros((self.numDocs, self.rangeSentiLabs))
        self.ndlz = np.zeros((self.numDocs, self.rangeSentiLabs, self.numTopics))
        self.nlzw = np.zeros((self.rangeSentiLabs, self.numTopics, self.vocabSize))
        self.nlz = np.zeros((self.rangeSentiLabs, self.numTopics))

        # Posterior terhadap peluang dari masing2 dokumen
        self.p = np.zeros((self.rangeSentiLabs, self.numTopics))

        # Memodelkan paramater
        self.pi_dl = np.zeros((self.numDocs, self.rangeSentiLabs))
        self.theta_dlz = np.zeros((self.numDocs, self.rangeSentiLabs, self.numTopics))
        self.phi_lzw = np.zeros((self.rangeSentiLabs, self.numTopics, self.vocabSize))

        # Menginisiasikan nilai alpha
        if (self.alpha <= 0):
            self.alpha = (self.aveDocLength) / (self.rangeSentiLabs * self.numTopics)

        # Mengisikan nilai alpha ke model paramter
        self.alpha_lz = np.empty((self.rangeSentiLabs, self.numTopics))
        self.alpha_lz.fill(self.alpha)

        self.alphaSum_l = np.zeros((self.rangeSentiLabs))

        for l in range(0, self.rangeSentiLabs):
            for z in range(0, self.numTopics):
                self.alphaSum_l[l] += self.alpha_lz[l][z]

        # Menginisiasikan nilai betha
        if (self.beta <= 0.0):
            self.beta = 0.01

        self.beta_lzw = np.empty((self.rangeSentiLabs, self.numTopics, self.vocabSize))
        self.beta_lzw.fill(self.beta)

        self.betaSum_lz = np.zeros((self.rangeSentiLabs, self.numTopics))

        # Menginisisikan nilai gamma
        if (self.gamma <= 0):
            self.gamma = (self.aveDocLength) / self.rangeSentiLabs

        self.gamma_dl = np.empty((self.numDocs, self.rangeSentiLabs))
        self.gamma_dl.fill(self.gamma)

        self.gammaSum_d = np.zeros((self.numDocs))
        for d in range(0, self.numDocs):
            for l in range(0, self.rangeSentiLabs):
                self.gammaSum_d[d] += self.gamma_dl[d][l]

        # Mentransformasi kata2 terhadap label sentimen masing2
        self.lambda_lw = np.ones((self.rangeSentiLabs, self.vocabSize))

        for word in self.sentiLex.keys():
            for j in range(0, self.rangeSentiLabs):
                if (word in self.word2atr.keys()):
                    self.lambda_lw[j][self.word2atr[str(word)][0]] = self.sentiLex[str(word)][1][j]

        for l in range(0, self.rangeSentiLabs):
            for z in range(0, self.numTopics):
                for r in range(0, self.vocabSize):
                    self.beta_lzw[l][z][r] = self.beta_lzw[l][z][r] * self.lambda_lw[l][r]
                    self.betaSum_lz[l][z] += self.beta_lzw[l][z][r]
                #logging.warning("Nilai beta awal label ke "+str(l)+" topik ke "+str(z)+" : "+str(self.betaSum_lz[l][z]))

    def initializing_estimasi(self):
        # Menginisialisasikan topik ke setiap dokumen
        self.z = np.empty((self.numDocs, self.pdataset.maxLength))
        self.z.fill(0)

        # Menginisalisasikan label ke setiap dokumen
        self.l = np.empty((self.numDocs, self.pdataset.maxLength))
        self.l.fill(0)
        self.labelPrior = 0
        for d in range(0, self.numDocs):
            docLength = self.pdataset.pdocs[d].length
            for t in range(0, docLength):
                if (self.pdataset.pdocs[d].priorSentiLabels[t] > -1):
                    # Memasukkan label sentimen dari prior ke model
                    sentiLab = self.pdataset.pdocs[d].priorSentiLabels[t]
                    self.labelPrior += 1
                else:
                    # bila kata tidak memiliki prior dari database dan untuk bigram dan negasi bigram
                    sentiLab = int(round(random.uniform(0, 1) * self.rangeSentiLabs))
                    if (sentiLab == self.rangeSentiLabs):
                        sentiLab = round(sentiLab - 1)

                self.l[d][t] = int(round(sentiLab))

                # Meninisialisasikan topik secara random
                topic = int(round(random.uniform(0, 1) * self.numTopics))
                if (topic == self.numTopics): topic = (topic - 1)
                self.z[d][t] = int(round(topic))

                # model count assignment
                self.nd[d] += 1
                self.ndl[d][sentiLab] += 1
                self.ndlz[d][sentiLab][topic] += 1
                self.nlzw[sentiLab][topic][self.pdataset.pdocs[d].words[t]] += 1
                self.nlz[sentiLab][topic] += 1

    def estimasi_model(self):
        self.countUpdateParameter = 0
        for self.liter in range(0, self.niters):
            #logging.warning("iterasi ke : "+str(self.liter))
            for m in range(0, self.numDocs):
                for n in range(0, self.pdataset.pdocs[m].length):
                    sentiLab = int(round(self.l[m][n]))
                    topic = int(round(self.z[m][n]))

                    # Mengoptimasi topik dan label dari kata
                    sentiLab, topic = self.sampling(m, n, sentiLab, topic)

                    self.l[m][n] = int(round(sentiLab))
                    self.z[m][n] = int(round(topic))
            if((self.liter % 10) == 0):
                logging.warning(
                    "Nilai peluang untuk label ke " + str(0) +" iterasi ke " + str(self.liter) + " : " +str(
                        self.p[0][0]))
                logging.warning(
                    "Nilai peluang untuk label ke " + str(1) + " iterasi ke " + str(self.liter) + " : " + str(
                        self.p[1][0]))
                # logging.warning(
                #     "Nilai peluang untuk label ke " + str(2) + " iterasi ke " + str(self.liter) + " : " + str(
                #         self.p[2][0]))
                logging.warning(' ')

            if (self.updateParaStep > 0 and self.liter % self.updateParaStep == 0):
                self.update_Parameters()

            if (self.savestep > 0 and self.liter % self.savestep == 0):
                if (self.liter == self.niters): break

                # print("Saving the model at iteratiot '%d' \n" % self.liter)
                self.compute_pi_dl()
                self.compute_theta_dlz()
                self.compute_phi_lzw()

        self.compute_pi_dl()
        self.compute_theta_dlz()
        self.compute_phi_lzw()

    def compute_pi_dl(self):
        for d in range(0, self.numDocs):
            for l in range(0, self.rangeSentiLabs):
                self.pi_dl[d][l] = (self.ndl[d][l] + self.gamma_dl[d][l]) / (self.nd[d] + self.gammaSum_d[d])

    def compute_theta_dlz(self):
        for d in range(0, self.numDocs):
            for l in range(0, self.rangeSentiLabs):
                for z in range(0, self.numTopics):
                    self.theta_dlz[d][l][z] = (self.ndlz[d][l][z] + self.alpha_lz[l][z]) / (self.ndl[d][l] + self.alphaSum_l[l])

    def compute_phi_lzw(self):
        for l in range(0, self.rangeSentiLabs):
            for z in range(0, self.numTopics):
                for r in range(0, self.vocabSize):
                    self.phi_lzw[l][z][r] = (self.nlzw[l][z][r] + self.beta_lzw[l][z][r]) / (self.nlz[l][z] + self.betaSum_lz[l][z])

    def sampling(self, m, n, sentiLab, topic):
        w = self.pdataset.pdocs[m].words[n]
        sentiLab = int(round(sentiLab))
        topic = int(round(topic))

        self.nd[m] -= 1
        self.ndl[m][sentiLab] -= 1
        self.ndlz[m][sentiLab][topic] -= 1
        self.nlzw[sentiLab][topic][w] -= 1
        self.nlz[sentiLab][topic] -= 1

        # do multinomial sampling via cumulative method
        for l in range(0, self.rangeSentiLabs):
            for k in range(0, self.numTopics):
                self.p[l][k] = ((self.nlzw[l][k][w] + self.beta_lzw[l][k][w]) / (self.nlz[l][k] + self.betaSum_lz[l][k])) * \
                               ((self.ndlz[m][l][k] + self.alpha_lz[l][k]) / (self.ndl[m][l] + self.alphaSum_l[l])) * \
                               ((self.ndl[m][l] + self.gamma_dl[m][l]) / (self.nd[m] + self.gammaSum_d[m]))
                #logging.warning("Nilai peluang untuk label ke "+str(l)+" iterasi ke "+str(self.liter)+" : "+str(self.p[l][k]))

        # accumulate multinomial parameters
        for l in range(0, self.rangeSentiLabs):
            for z in range(0, self.numTopics):
                if (z == 0):
                    if (l == 0):
                        continue
                    else:
                        self.p[l][z] += self.p[l - 1][self.numTopics - 1]  # accumulate the sum of the previous array
                else:
                    self.p[l][z] += self.p[l][z - 1]

        # probability normalization
        u = random.uniform(0, 1) * self.p[self.rangeSentiLabs - 1][self.numTopics - 1]

        # sample sentiment label l, where l \in [0, S-1]
        loopBreak = False
        for sentiLab in range(0, self.rangeSentiLabs):
            for topic in range(0, self.numTopics):
                if (self.p[sentiLab][topic] > u):
                    loopBreak = True
                    break
            if (loopBreak == True):
                break

        if (sentiLab == self.rangeSentiLabs): sentiLab = int(round(self.rangeSentiLabs - 1))
        if (topic == self.numTopics): topic = int(round(self.numTopics - 1))

        # add estiamted 'z' and 'l' to count variable
        self.nd[m] += 1
        self.ndl[m][sentiLab] += 1
        self.ndlz[m][sentiLab][topic] += 1
        self.nlzw[sentiLab][topic][self.pdataset.pdocs[m].words[n]] += 1
        self.nlz[sentiLab][topic] += 1

        return sentiLab, topic

    def update_Parameters(self):
        self.data = np.zeros((self.numTopics, self.numDocs))
        self.alpha_temp = np.zeros((self.numTopics))
        # self.nanCondions = False
        # update alpha
        for l in range(0, self.rangeSentiLabs):
            for z in range(0, self.numTopics):
                for d in range(0, self.numDocs):
                    self.data[z][d] = self.ndlz[d][l][z]

            for z in range(0, self.numTopics):
                self.alpha_temp[z] = self.alpha_lz[l][z]

            self.polya_fit_simple(self.data, self.alpha_temp, self.numTopics, self.numDocs)

            # update alpha
            self.alphaSum_l[l] = 0.0
            for z in range(0, self.numTopics):
                self.alpha_lz[l][z] = self.alpha_temp[z]
                self.alphaSum_l[l] += self.alpha_lz[l][z]

    def polya_fit_simple(self, data, alpha, numTopics, numDocs):
        K = numTopics
        nSample = numDocs
        polya_iter = 100000
        sat_state = False
        # mp.dps = 8

        old_alpha = np.zeros((K))
        data_row_sum = np.zeros((nSample))

        for i in range(0, nSample):
            for k in range(0, K):
                # data_row_sum[i] +=  mp.mpf(data[k][i])
                data_row_sum[i] += data[k][i]

        for i in range(0, polya_iter):
            sum_alpha_old = 0.0

            for k in range(0, K):
                old_alpha[k] = alpha[k]
            for k in range(0, K):
                sum_alpha_old += old_alpha[k]

            for k in range(0, K):
                sum_g = 0.0
                sum_h = 0.0

                for j in range(0, nSample):
                    sum_g += scp.digamma(data[k][j] + old_alpha[k])
                    sum_h += scp.digamma(data_row_sum[j] + sum_alpha_old)

                # alpha[k] = mp.mpf(old_alpha[k]*mp.mpf(sum_g - (nSample*self.digamma(old_alpha[k])))/mp.mpf(sum_h - (nSample*self.digamma(sum_alpha_old))))
                alpha[k] = (old_alpha[k] * (sum_g - (nSample * scp.digamma(old_alpha[k]))) / (
                sum_h - (nSample * scp.digamma(sum_alpha_old))))
                self.alpha_temp[k] = alpha[k]

            for j in range(0, K):
                if ((np.fabs(alpha[j]) - old_alpha[j]) > 0.000001):
                    break
                if (j == K - 1):
                    sat_state = True

            if (sat_state == True):
                break

def inputDataFormalisasi(request):
    if request.method == 'POST':
        #cek koneksi formalisasi
        koneksi = cekKoneksi()

        arrKataFormal = KataFormalDB.objects.values_list('kataFormal', flat=True)
        arrFormalisasi = FormalisasiKataDB.objects.values_list('kataInformal', flat=True)
        arrSentimen = SentimenDB.objects.values_list('kataSentimen', flat=True)

        arrData = []
        arrData.extend(arrKataFormal)
        arrData.extend(arrFormalisasi)
        arrData.extend(arrSentimen)
        arrData = list(set(arrData))
        dictKata = {}

        #file = request.FILES['dataset']
        #file.open()
        remove = string.punctuation
        remove = remove.replace("#","")
        remove = remove.replace("@","")

        #for line in file:
        #    line = str(line)
        #    line = line[2:-5]
        #    line = ''.join(line)
        typeFile = (request.FILES['dataset'].name).split('.')[1]
        if (typeFile == 'txt'):
            readers = TextIOWrapper(request.FILES['dataset'].file, encoding='utf-8 ', errors='replace')
        elif (typeFile == 'csv'):
            try:
                text = TextIOWrapper(request.FILES['dataset'].file, encoding='utf-8 ', errors='replace')
                readers = csv.reader(text)
            except:
                text = StringIO(request.FILES['dataset'].file.read().decode())
                readers = csv.reader(text)
        else:
            return render(request, 'JST/inputDataSentimen.html', {})
        dfjKata = {}
        numDocs = 0
        arrCorpus = []
        for reader in readers:
            kalimat = ''.join(reader)
            line = kalimat.translate(str.maketrans('', '', remove)).lower()
            arrCorpus.append(line)

        arrJSONFormalisasi = []
        #if(koneksi):
        #   for kalimat in arrCorpus:
        #        formalisasiKateglo = {}
        #        formalisasiKateglo['input'] = kalimat
        #        formalisasiKateglo['output'] = correction(kalimat)
        #        arrJSONFormalisasi.append(formalisasiKateglo)
        jsonFormalisasi = json.dumps(arrJSONFormalisasi)

        for line in arrCorpus:
            baris = line.split()
            if(len(baris) > 0):
                numDocs += 1
                #Untuk Unigram
                for kata in baris:
                    if kata not in arrData:
                        if kata not in dictKata.keys():
                            dictKata[kata] = 1
                            dfjKata[kata] = 0
                        else:
                            dictKata[kata] += 1
                # Untuk Bigram
                # for i in range(0, len(baris) - 1):
                #     kata = str(''.join(baris[i] + " " + baris[i+1]))
                #     if kata not in arrData:
                #         if kata not in dictKata.keys():
                #             dictKata[kata] = 1
                #             dfjKata[kata] = 0
                #         else:
                #             dictKata[kata] += 1

        # for reader in readers:
        #     kata = ''.join(reader)
        #     line = kata.translate(str.maketrans('', '', remove)).lower()
        #     baris = line.split()
        #     if(len(baris) > 0):
        #         for i in range(0, len(baris)-1):
        #             kata = baris[i] + " " + baris[i+1]
        #             if kata not in arrData:
        #                 if kata not in dictKata.keys():
        #                     dictKata[kata] = 1
        #                     dfjKata[kata] = 0
        #                 else:
        #                     dictKata[kata] += 1

        for reader in arrCorpus:
            baris = reader.split()
            # if(len(baris)>0):
            #     for i in range(0, len(baris) - 1):
            #         kata = str(''.join(baris[i] + " " + baris[i+1]))
            #         baris.append(kata)
            #Menghitung dfj
            for kata in dictKata.keys():
                if kata in baris:
                    if(dfjKata[kata] == 0):
                        dfjKata[kata] = 1
                    else:
                        dfjKata[kata] += 1

        #Inisialisasi dan hitung tf-idf
        tfidfKata = {}

        for kata in dictKata.keys():
            #logging.warning(kata)
            if(dfjKata[kata] == numDocs):
                n = 0
            else:
                n = 1
            tfidfKata[kata] = dictKata[kata] * np.log(numDocs/(dfjKata[kata]))
            #logging.warning(str(kata) +" : "+str(tfidfKata[kata]))

        #arrKata = sorted(dictKata, key=dictKata.__getitem__, reverse=True)
        arrKata = sorted(tfidfKata, key=tfidfKata.__getitem__, reverse=True)

        w = 0
        dictKata = {}
        for kata in arrKata:
            dictKata[w] = kata
            w += 1

        arrKataFormalizationed = []
        arrKataNonFormalizationed = []
        for kata in arrKata:
            data = {}
            data['input'] = kata
            data['output'] = correction(kata)
            if(data['input'] == data['output']):
                arrKataNonFormalizationed.append(kata)
            else:
                arrKataFormalizationed.append(data)
        #Catch error
        #if not arrKataFormalizationed:
        #    arrKataNonFormalizationed.append('Lala')
        jsonFormalized = json.dumps(arrKataFormalizationed)
        jsonNonFormalized = json.dumps(arrKataNonFormalizationed)

        batasKata = int(request.POST['vocabSize'])
        if(w > batasKata):
            w = batasKata

        return render(request, 'JST/formalisasiKata.html', {'dickKata': dictKata, 'arrData': arrData, 
                                                            'vocabSize': w,
                                                            'jsonFormalisasi': jsonFormalisasi,
                                                            'jsonFormalized': jsonFormalized,
                                                            'jsonNonFormalized': jsonNonFormalized,
                                                            })
    else:
        return render(request, 'JST/inputDataFormalisasi.html',{})

def simpanFormalisasiKata(request):
    if request.method == 'POST':
        vocabSize = int(request.POST['vocabSize'])
        for x in range(0,vocabSize):
            x = '_'+str(x)
            kataInformal = 'kataInformal'+x
            kataFormal = 'kataFormal'+x
            kataInformal = request.POST[kataInformal]
            kataFormal = request.POST[kataFormal]

            if (kataFormal != ""):
                form = FormalisasiKataDB(kataInformal=kataInformal, kataFormal=kataFormal)
                form.save()
            else:
                form = KataFormalDB(kataFormal=kataInformal)
                form.save()

        return redirect('JST:halamanMuka')
    else:
        return redirect('JST:inputData')

def previewMI(request):
    if request.POST:
        # arrKataFormal = KataFormalDB.objects.values_list('kataFormal', flat=True)
        # arrFormalisasi = FormalisasiKataDB.objects.values_list('kataInformal', flat=True)
        # arrSentimen = SentimenDB.objects.values_list('kataSentimen', flat=True)
        #
        # arrData = []
        # arrData.extend(arrKataFormal)
        # arrData.extend(arrFormalisasi)
        # arrData.extend(arrSentimen)
        # arrData = list(set(arrData))

        # arrData = []
        arrStopwords = StopwordsIDDB.objects.values_list('kataStopword', flat=True)
        # arrData.extend(arrStopwords)

        # dictKata = {}
        remove = string.punctuation
        remove = remove.replace("#", "")
        remove = remove.replace("@", "")

        name = request.FILES['dataset'].name
        typeFile = name.split('.')[1]
        if (typeFile == 'txt'):
            readers = TextIOWrapper(request.FILES['dataset'].file, encoding='utf-8 ', errors='replace')
        elif (typeFile == 'csv'):
            try:
                text = TextIOWrapper(request.FILES['dataset'].file, encoding='utf-8 ', errors='replace')
                readers = csv.reader(text)
            except:
                text = StringIO(request.FILES['dataset'].file.read().decode())
                readers = csv.reader(text)
        else:
            return render(request, 'JST/inputDataSentimen.html', {})

        dictKata = {} #berisi TF dari masing2 kata
        indexDoc = 0
        dictData = {} #berisi raw dokumen
        dfjKata = {} #berisi banyak dokumen yang memuat suatu kata
        arrCorpus =[] #array menyimpan file dari memori
        numDocs = 0

        #Memindahkan file dari memory ke array
        for reader in readers:
            kalimat = ''.join(reader)
            #kalimat = kalimat.translate(str.maketrans('', '', remove)).lower()
            arrCorpus.append(kalimat)
            numDocs += 1

        #Buat data untuk MI dan Formalisasi database
        arrDataMI = []
        formalisasi = FormalisasiKataDB.objects.values_list('kataInformal', 'kataFormal')
        kataFormalisasi = {}
        for i in range(0, len(formalisasi)):
            kataFormalisasi[str(formalisasi[i][0])] = str(formalisasi[i][1])

        #Menyimpan data mentahan dan formalisasi untuk ektraksi MI
        for reader in arrCorpus:
            #reader = ''.join(reader)
            line = str(reader).lower()
            baris = line.split()

            if (len(baris) > 0):
                dictData[indexDoc] = line
                indexDoc += 1

            if (len(baris) > 0):
                kalimat = ""
                for x in range(0, len(baris)):
                    if baris[x] in kataFormalisasi.keys():
                        baris[x] = kataFormalisasi[baris[x]]
                    kalimat = kalimat + " " + baris[x]
                arrDataMI.append(kalimat)

        #Hitung TF dari masing2 kata
        for line in arrDataMI:
            line = line.translate(str.maketrans('', '', remove)).lower()
            baris = line.split()
            if (len(baris) > 0):
                #TF untuk unigram
                for kata in baris:
                    if kata not in dictKata.keys():
                        dictKata[kata] = 1
                        dfjKata[kata] = 0
                    else:
                        dictKata[kata] += 1
                #TF untuk bigram
                for i in range(0, (len(baris) - 1)):
                    kata = baris[i] + " " + baris[i + 1]
                    if kata not in dictKata.keys():
                        dictKata[kata] = 1
                        dfjKata[kata] = 0
                    else:
                        dictKata[kata] += 1

        for line in arrDataMI:
            line = line.translate(str.maketrans('', '', remove)).lower()
            baris = line.split()
            if (len(baris) > 0):
                for i in range(0, len(baris) - 1):
                    kata = str(''.join(baris[i] + " " + baris[i + 1]))
                    baris.append(kata)
            # Menghitung dfj
            for kata in dictKata.keys():
                if kata in baris:
                    if (dfjKata[kata] == 0):
                        dfjKata[kata] = 1
                    else:
                        dfjKata[kata] += 1

        # Inisialisasi dan hitung tf-idf
        tfidfKata = {}

        # Cek stopwords
        stopwords = request.POST['stopwords']
        if (stopwords == 'yes'):
            for kata in arrStopwords:
                if kata in dictKata.keys():
                    # logging.warning(str(kata))
                    del dictKata[kata]

        for kata in dictKata.keys():
            # logging.warning(kata)
            if (dfjKata[kata] == numDocs):
                n = 0
            else:
                n = 1
            tfidfKata[kata] = dictKata[kata] * np.log(numDocs / (dfjKata[kata] + n))
            # logging.warning(str(kata) +" : "+str(tfidfKata[kata]))

        # arrKata = sorted(dictKata, key=dictKata.__getitem__, reverse=True)
        arrKata = sorted(tfidfKata, key=tfidfKata.__getitem__, reverse=True)

        # file.close()
        #arrKata = sorted(dictKata, key=dictKata.__getitem__, reverse=True)

        w = 0
        kata = {}
        for word in arrKata:
            kata[w] = word
            w += 1
        vocabSize = int(request.POST['vocabSize'])
        if (w > vocabSize):
            w = vocabSize

        #logging.warning(str(kata[0]))
        kalimat = str(kata[0])
        for i in range(1, w):
            kalimat = kalimat +","+kata[i]

        statusMI = request.POST['statusMI']
        if(statusMI == 'yes'):
            statusMI = True
        else:
            statusMI = False

        return render(request, 'JST/previewMI.html', {'dictData': dictData, 'kata': kata, 'jarak': range(0, w),
                                                     'kalimat': kalimat, 'lenCorpus' : indexDoc, 'name': name,
                                                     'statusMI': statusMI})
    else:
        return render(request, 'JST/inputDataMI.html', {})

def prosesMI(request):
    if request.method == 'POST':
        formalisasi = FormalisasiKataDB.objects.values_list('kataInformal', 'kataFormal')
        kataFormalisasi = {}
        for i in range(0, len(formalisasi)):
            kataFormalisasi[str(formalisasi[i][0])] = str(formalisasi[i][1])

        remove = string.punctuation
        remove = remove.replace("#", "")
        remove = remove.replace("@", "")
        remove = remove.replace(",", "")
        # print(remove)

        #Membuat lisr memuat kata2 MI Positive
        positiveMI = request.POST['positiveMI'].translate(str.maketrans('', '', remove)).lower()
        positiveMIFormalisasi = []
        positiveMIArr = positiveMI.split(',')
        for kata in positiveMIArr:
            katas = kata.split()
            kataBaru = ""
            for i in range(0, len(katas)):
                if katas[i] in kataFormalisasi.keys():
                    katas[i] = kataFormalisasi[katas[i]]
                    if (i == 0):
                        kataBaru = str(katas[i])
                    else:
                        kataBaru = str(kataBaru) +" "+str(katas[i])
                else:
                    if (i == 0):
                        kataBaru = str(katas[0])
                    else:
                        kataBaru = str(kataBaru) +" "+str(katas[i])
            positiveMIFormalisasi.append(kataBaru)


        #Membuat list yang memuat kata2 MI Negative
        negativeMI = request.POST['negativeMI'].translate(str.maketrans('', '', remove)).lower()
        negativeMIFormalisasi = []
        negativeMIArr = negativeMI.split(',')
        for kata in negativeMIArr:
            katas = kata.split()
            kataBaru = ""
            for i in range(0, len(katas)):
                if katas[i] in kataFormalisasi.keys():
                    katas[i] = kataFormalisasi[katas[i]]
                    if (i == 0):
                        kataBaru = str(katas[i])
                    else:
                        kataBaru = str(kataBaru) +" "+str(katas[i])
                else:
                    if (i == 0):
                        kataBaru = str(katas[0])
                    else:
                        kataBaru = str(kataBaru) +" "+str(katas[i])
            negativeMIFormalisasi.append(kataBaru)

        #Membuat list yang memuat dokumen2 dari corpus
        arrData = []
        arrDataRaw = []
        lenCorpus = int(request.POST['lenCorpus'])
        logging.warning(str(lenCorpus))
        #numRaw = 0
        #numProcess = 0
        for i in range(0, lenCorpus):
            kalimat = "kalimat_"+str(i)
            kalimat = request.POST[kalimat]
            kata = kalimat.translate(str.maketrans('', '', remove)).lower()
            baris = kata.split()
            if (len(baris) > 0):
                arrDataRaw.append(kalimat)
                #numRaw += 1
                # proses Formalisasi
                kalimatBaru = ""
                for x in range(0, len(baris)):
                    if baris[x] in kataFormalisasi.keys():
                        baris[x] = kataFormalisasi[baris[x]]
                    kalimatBaru = kalimatBaru + " " + baris[x]
                arrData.append(kalimatBaru)
                #numProcess += 1
        #logging.warning("Jumlah data awal : "+str(numRaw))
        #logging.warning("Jumlah data hasil proses : "+str(numProcess))
        # Memberikan nilai untuk hyperparameter dari User atau otomatis
        if (request.POST['alpha'] == ""):
            alpha = -1
        else:
            alpha = float(request.POST['alpha'])

        if (request.POST['beta'] == ""):
            beta = -1
        else:
            beta = float(request.POST['beta'])

        if (request.POST['gamma'] == ""):
            gamma = -1
        else:
            gamma = float(request.POST['gamma'])

        if(request.POST['topics'] == ""):
            topics = 1
        else:
            topics = int(request.POST['topics'])

        if(request.POST['iterasi'] == ""):
            iterasi = 1000
        else:
            iterasi = int(request.POST['iterasi'])

        # Cek stopwords
        stopwords = request.POST['stopwords']
        if (stopwords == 'yes'):
            statusStopwords = True
        else:
            statusStopwords = False

        statusLexicon = request.POST['FSL']
        if (statusLexicon == 'none'):
            statusFSL = False
            if (request.POST['filtered'] == ""):
                filtered = 0
            else:
                filtered = int(request.POST['filtered'])
        elif (statusLexicon == 'full'):
            statusFSL = True
            filtered = 0
        else:
            statusFSL = True
            if (request.POST['filtered'] == ""):
                filtered = 0
            else:
                filtered = int(request.POST['filtered'])

        # Mencari status dari file label untuk pengujian prior
        cekLabel = request.FILES.get('label', False)
        if (cekLabel != False):
            typeFile = (request.FILES['label'].name).split('.')[1]
            if (typeFile == 'txt'):
                labels = TextIOWrapper(request.FILES['label'].file, encoding='utf-8 ', errors='replace')
            elif (typeFile == 'csv'):
                try:
                    text = TextIOWrapper(request.FILES['label'].file, encoding='utf-8 ', errors='replace')
                    labels = csv.reader(text)
                except:
                    text = StringIO(request.FILES['dataset'].file.read().decode())
                    labels = csv.reader(text)
            else:
                return render(request, 'JST/inputDataMI.html', {})

            dictLabel = {}
            for key, label in enumerate(labels):
                label = int(''.join(label))
                dictLabel[key] = int(label)

            if (len(dictLabel) != len(arrData)):
                return render(request, 'JST/inputDataMI.html', {})

        #Lakukan Proses utuk MI
        simulationIteration = int(request.POST['iterasiSimulasi'])

        positiveTopics = []
        negativeTopics = []

        pi_dli = np.zeros((len(arrData), 2, simulationIteration))

        vocabSize = 0
        corpusSize = 0 #banyak kata dalam suatu corpus
        corpusLength = 0 #banyak dokumen dalam suatu corpus
        priorLabeled = 0
        aveDocSize = 0.0

        kataPositive = []
        kataNegative = []
        kalimatHasil = []

        waktuSimulasi = {}
        hyperparametersSimulasi = {}
        hyperparameter = ""
        dataSimulasi = []

        # Mengekstrak topic words untuk tiap label sentimen
        pengaliPeluang = [10000, 9000, 8000, 7000, 6000, 5000, 4000, 3000, 2500, 2000, 1500, 1200,
                          1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]
        kali = 0

        for i in range(0, simulationIteration):
            positiveSimulasi = {}
            negativeSimulasi = {}
            name = "JST MI Simulation : %s " % str(simulationIteration)
            jst = modelJST(alpha, beta, gamma, topics, name, statusStopwords, statusFSL, filtered, iterasi,
                           positiveMIFormalisasi, negativeMIFormalisasi)
            jst.execute_model(arrData)
            waktuSimulasi[i] = jst.processTime
            hyperparametersSimulasi[i] = str(round(jst.alpha, 4)) + " * " + \
                                         str(round(jst.beta, 4)) + " * " + \
                                         str(round(jst.gamma, 4))
            for d in range(0, jst.numDocs):
                for l in range(0, jst.rangeSentiLabs):
                    pi_dli[d][l][i] = jst.pi_dl[d][l]

            if(i == 0):
                kalimatHasil = jst.arrData
                hyperparameter = str(jst.alpha) + ", " + str(jst.beta) + "," + str(jst.gamma)
                vocabSize = jst.vocabSize
                corpusSize = jst.corpusSize
                priorLabeled = jst.labelPrior
                aveDocSize = jst.aveDocLength
                kataPositive = jst.pdataset.labeledPositiveWords
                kataNegative = jst.pdataset.labeledNegativeWords
                corpusLength = jst.numDocs


            # JSON untuk topik positive
            for z in range(0, topics):

                words_probs = {}
                for w in range(0, vocabSize):
                    words_probs[w] = [w, jst.phi_lzw[1][z][w]]
                topicsWords = sorted(words_probs.items(), key=lambda item: item[1][1], reverse=True)

                for pengali in pengaliPeluang:
                    if (topicsWords[0][1][1] * pengali < 90):
                        kali = pengali
                        break

                positiveTopic = []
                for i in range(0, 40):
                    positiveTopic.append([jst.id2word[topicsWords[i][1][0]], int(round(topicsWords[i][1][1] * kali))])
                positiveSimulasi[z] = positiveTopic
            positiveTopics.append(positiveSimulasi)

            # JSON untuk topik negative
            for z in range(0, topics):
                words_probs = {}
                for w in range(0, vocabSize):
                    words_probs[w] = [w, jst.phi_lzw[0][z][w]]
                topicsWords = sorted(words_probs.items(), key=lambda item: item[1][1], reverse=True)

                for pengali in pengaliPeluang:
                    if (topicsWords[0][1][1] * pengali < 90):
                        kali = pengali
                        break

                negativeTopic = []
                for i in range(0, 40):
                    negativeTopic.append([jst.id2word[topicsWords[i][1][0]], int(round(topicsWords[i][1][1] * kali))])
                negativeSimulasi[z] = negativeTopic
            negativeTopics.append(negativeSimulasi)


        #Membuat JSON unutk hasil peluang sentimen tiap dokumen dalam tiap simulasi
        for d in range(0, corpusLength):
            data = {}
            data['kalimat'] = kalimatHasil[d]
            for i in range(0, simulationIteration):
                data['positive_'+str(i)] = pi_dli[d][1][i]
                data['negative_'+str(i)] = pi_dli[d][0][i]
                if(pi_dli[d][1][i] > pi_dli[d][0][i]):
                    label = 1
                elif(pi_dli[d][1][i] < pi_dli[d][0][i]):
                    label = 2
                else:
                    label = 0
                data['hasil_'+str(i)] = label
            dataSimulasi.append(data)
        jsonSimulasi = json.dumps(dataSimulasi)

        #Membuat ringkasan label sentimen
        sentimenSimulasi = []
        for i in range(0, simulationIteration):
            sentimenLabel = []
            for d in range(0, corpusLength):
                if (pi_dli[d][1][i] > pi_dli[d][0][i]):
                    label = 'positive'
                elif (pi_dli[d][1][i] < pi_dli[d][0][i]):
                    label = 'negative'
                else:
                    label = 'netral'
                sentimenLabel.append(label)
                sentimenLabel.append('total')
            sentimenTest = Counter(sentimenLabel)
            sentimenSimulasi.append(sentimenTest)
        jsonSentimen = json.dumps(sentimenSimulasi)
        jsonPositive = json.dumps(positiveTopics)
        jsonNegative = json.dumps(negativeTopics)


        if(cekLabel == False):
            name = "JST MI tanpa label Simulation : %s " % str(simulationIteration)
            #Membuat json untuk review simulasi
            arrReviewSimulasi = []
            for i in range(0, simulationIteration):
                arrRStemp = {}
                arrRStemp['waktu'] = waktuSimulasi[i]
                arrRStemp['hyperparameter'] = hyperparametersSimulasi[i]
                arrRStemp['positive'] = round(
                    (sentimenSimulasi[i]['positive']/sentimenSimulasi[i]['total']) * 100, 2)
                arrRStemp['negative'] = round(
                    (sentimenSimulasi[i]['negative'] / sentimenSimulasi[i]['total']) * 100, 2)
                arrRStemp['objektif'] = round(
                    (sentimenSimulasi[i]['netral'] / sentimenSimulasi[i]['total']) * 100, 2)
                arrReviewSimulasi.append(arrRStemp)
            jsonReviewSimulasi = json.dumps(arrReviewSimulasi)

            return render(request, 'JST/HasilJSTSimulasi.html', {'corpusLength': corpusLength,
                                                                 'name': name,
                                                                 'stopwordsStatus': statusStopwords,
                                                                 'lexiconStatus': statusLexicon + " (" + str(
                                                                     filtered) + ")",
                                                                 'hyperparameters': hyperparameter,
                                                                 'vocabSize': vocabSize,
                                                                 'corpusSize': corpusSize,
                                                                 'aveDocSize': aveDocSize,
                                                                 'priorLabeled': priorLabeled,
                                                                 'topics': topics,
                                                                 'iterasiGibbs': iterasi,
                                                                 'kataPositive': kataPositive,
                                                                 'kataNegative': kataNegative,
                                                                 'jsonSimulasi': jsonSimulasi,
                                                                 'iterasiSimulasi': simulationIteration,
                                                                 'jsonPositive': jsonPositive,
                                                                 'jsonNegative': jsonNegative,
                                                                 'jsonSentimen': jsonSentimen,
                                                                 'jsonReviewSimulasi': jsonReviewSimulasi,
                                                                 })
        else:
            name = "JST MI dengan label Simulation : %s " % str(simulationIteration)
            #Membuat pengukuran terhadap akurasi
            akurasiSimulasi = {}
            for i in range(0, simulationIteration):
                sumDocLabel = 0
                sumDocAkurasi = 0
                for d in range(0, len(arrData)):
                    if (pi_dli[d][1][i] > pi_dli[d][0][i]):
                        sentiLab = 1
                        sumDocLabel += 1
                    elif (pi_dli[d][1][i] < pi_dli[d][0][i]):
                        sentiLab = 2
                        sumDocLabel += 1
                    else:
                        sentiLab = -1

                    if (str(sentiLab) == str(dictLabel[i])):
                        sumDocAkurasi += 1
                akurasiSimulasi[i] = round((sumDocAkurasi / sumDocLabel) * 100, 2)

            #membuat json untuk review simulasi dengan nilai akurasi labelnya
            arrReviewSimulasi = []
            for i in range(0, simulationIteration):
                arrRStemp = {}
                arrRStemp['waktu'] = waktuSimulasi[i]
                arrRStemp['hyperparameter'] = hyperparametersSimulasi[i]
                arrRStemp['positive'] = round(
                    (sentimenSimulasi[i]['positive'] / sentimenSimulasi[i]['total']) * 100, 2)
                arrRStemp['negative'] = round(
                    (sentimenSimulasi[i]['negative'] / sentimenSimulasi[i]['total']) * 100, 2)
                arrRStemp['objektif'] = round(
                    (sentimenSimulasi[i]['netral'] / sentimenSimulasi[i]['total']) * 100, 2)
                arrRStemp['akurasi'] = akurasiSimulasi[i]
                arrReviewSimulasi.append(arrRStemp)
            jsonReviewSimulasi = json.dumps(arrReviewSimulasi)
            return render(request, 'JST/HasilJSTSimulasi.html', {'corpusLength': corpusLength,
                                                                 'name': name,
                                                                 'stopwordsStatus': statusStopwords,
                                                                 'lexiconStatus': statusLexicon + " (" + str(
                                                                     filtered) + ")",
                                                                 'dictLabel': dictLabel,
                                                                 'hyperparameters': hyperparameter,
                                                                 'vocabSize': vocabSize,
                                                                 'corpusSize': corpusSize,
                                                                 'aveDocSize': aveDocSize,
                                                                 'priorLabeled': priorLabeled,
                                                                 'iterasiSimulasi': simulationIteration,
                                                                 'topics': topics,
                                                                 'iterasiGibbs': iterasi,
                                                                 'kataPositive': kataPositive,
                                                                 'kataNegative': kataNegative,
                                                                 'jsonSimulasi': jsonSimulasi,
                                                                 'jsonPositive': jsonPositive,
                                                                 'jsonNegative': jsonNegative,
                                                                 'jsonSentimen': jsonSentimen,
                                                                 'jsonReviewSimulasi': jsonReviewSimulasi,
                                                                 })

def inputDataPelabelan(request):
    if request.method == 'POST':
        dictKalimat = {}
        name = request.FILES['dataset'].name
        typeFile = (request.FILES['dataset'].name).split('.')[1]
        if (typeFile == 'txt'):
            readers = TextIOWrapper(request.FILES['dataset'].file, encoding='utf-8 ', errors='replace')
        elif (typeFile == 'csv'):
            try:
                text = TextIOWrapper(request.FILES['dataset'].file, encoding='utf-8 ', errors='replace')
                readers = csv.reader(text)
            except:
                text = StringIO(request.FILES['dataset'].file.read().decode())
                readers = csv.reader(text)
        else:
            return render(request, 'JST/inputDataPelabelan.html', {})

        for key, reader in enumerate(readers):
            reader = ''.join(reader)
            dictKalimat[key] = reader
        corpusLength = len(dictKalimat)
        return render(request, 'JST/previewPelabelan.html', {'dictKalimat': dictKalimat,
                                                             'range': range(0, corpusLength),
                                                             'corpusLength': corpusLength,
                                                             'name': name})
    else:
        return render(request, 'JST/inputDataPelabelan.html', {})

def simpanPelabelan(request):
    sizeArrData = request.POST['corpusLength']
    sizeArrData = int(sizeArrData)

    unduhFile = request.POST['unduhFile']
    unduhFile = str(unduhFile)
    dataKalimat = {}
    dataLabel = {}

    if (unduhFile == 'dataset'):
        for i in range(0, sizeArrData):
            status = 'status_' + str(i)
            status = request.POST[status]
            if (status == 'spam'):
                pass
            else:
                kalimat = 'kalimat_' + str(i)
                kalimat = request.POST[kalimat]
                dataKalimat[i] = kalimat

        Kalimat = StringIO()
        for key in dataKalimat.keys():
            Kalimat.write(dataKalimat[key] + os.linesep)
        # Kalimat.write(str(countData))

        Kalimat.flush()
        Kalimat.seek(0)
        response = HttpResponse(FileWrapper(Kalimat), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=kalimat.csv'
        return response
    elif(unduhFile == 'label'):
        for i in range(0, sizeArrData):
            status = 'status_' + str(i)
            status = request.POST[status]
            if (status == 'spam'):
                pass
            elif (status == 'positive'):
                dataLabel[i] = 1
            elif (status == 'negative'):
                dataLabel[i] = 0
            elif (status == 'netral'):
                dataLabel[i] = -1

        Label = StringIO()
        for key in dataLabel.keys():
            Label.write(str(dataLabel[key]) + os.linesep)
        # Label.write(str(countData))

        Label.flush()
        Label.seek(0)
        response = HttpResponse(FileWrapper(Label), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Label.txt'
        return response
    elif(unduhFile == 'full'):
        #spam = []
        # buffer1 = StringIO()
        # kalimat = csv.writer(buffer1, quoting=csv.QUOTE_NONE)

        # buffer2 = StringIO()
        # label = csv.writer(buffer2, quoting=csv.QUOTE_NONE)

        # buffer3 = StringIO()
        # spam = csv.writer(buffer3, quoting=csv.QUOTE_NONE)

        # arrKalimat = []
        # arrLabel =[]
        # arrSpam = []

        spam = StringIO()
        label = StringIO()
        kalimat = StringIO()

        for i in range(0, sizeArrData):
            status = 'status_' + str(i)
            status = request.POST[status]
            if (status == 'spam'):
                teks = request.POST['kalimat_'+str(i)]
                if(len(teks.split()) > 0):
                    spam.write(teks + os.linesep)

                # arrSpam.append(str(teks))
            elif(status == 'positive'):
                senLabel = 1
                teks = request.POST['kalimat_'+str(i)]
                label.write(str(senLabel) + os.linesep)
                kalimat.write(teks + os.linesep)

                # arrLabel.append(str(senLabel))
                # arrKalimat.append(str(teks))
            elif(status == 'negative'):
                senLabel = 2
                teks = request.POST['kalimat_' + str(i)]
                label.write(str(senLabel) + os.linesep)
                kalimat.write(teks + os.linesep)

                # arrLabel.append(str(senLabel))
                # arrKalimat.append(str(teks))
            elif(status == 'netral'):
                senLabel = -1
                teks = request.POST['kalimat_' + str(i)]
                label.write(str(senLabel) + os.linesep)
                kalimat.write(teks + os.linesep)

                # arrLabel.append(str(senLabel))
                # arrKalimat.append(str(teks))

        # label.writerows(arrLabel)
        # kalimat.writerows(arrKalimat)
        # spam.writerows(arrSpam)

        outfile = BytesIO()
        zip = ZipFile(outfile, 'w')

        # buffer1.flush()
        # buffer2.flush()
        # buffer3.flush()
        #
        # buffer1.seek(0)
        # buffer2.seek(0)
        # buffer3.seek(0)

        spam.flush()
        spam.seek(0)

        label.flush()
        label.seek(0)

        kalimat.flush()
        kalimat.seek(0)

        zip.writestr("label.csv", label.getvalue())
        zip.writestr("kalimat.csv", kalimat.getvalue())
        zip.writestr("spam.csv", spam.getvalue())

        #fix for linux zip files
        for file in zip.filelist:
            file.create_system = 0

        zip.close()

        response = HttpResponse(outfile.getvalue(), content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=hasil.zip'

        return response

def cekKoneksi():
    try:
        url = 'http://kateglo.com'
        requests.get(url)
        logging.warning("Koneksi sukses")
        return True
    except requests.ConnectionError:
        return False


