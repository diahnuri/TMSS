'''
Created on Jul 10, 2017

@author: Asus-PC
'''
from bs4 import BeautifulSoup
import urllib
import os
import csv

# key_word1 = 'dki'
url = 'https://search.detik.com/search?query=''&source=dcnav&siteid=2'

    # membuat koneksi ke url 
page= urllib.request.urlopen(url)
html = page.read()
    
    # membaca html
soup = BeautifulSoup(html, "html.parser")
    
    #======================================================================================================================
judul = soup.find_all("div", class_="title")
tanggal = soup.find_all("span", class_="date")
a = len(judul)
    # for i in range(a):
    #     print("title : "+judul[i].text.strip())
    #     konten = judul[i].find_all_next(text=True)
    #     print("Isi : "+konten[3].strip())
    #     print("Tanggal : "+tanggal[i].text.strip())
    #     print()
                
os.chdir("C:/Users/Asus-PC/Desktop/")
    
with open("detik1.csv", "w") as toWrite:
    writer = csv.writer(toWrite, delimiter=",")
    writer.writerow(["Judul", "Konten", "Tanggal"])
    for i in range(a):
        konten = judul[i].find_all_next(text=True)
        writer.writerow([judul[i].text.strip(), konten[3].strip(), tanggal[i].text.strip()])