from django.test import TestCase

from bs4 import BeautifulSoup
import requests, re
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

list_news = []
def scrap_detik_page(url):
    try:
        page = urllib.request.urlopen(url)
        html = page.read()
        soup = BeautifulSoup(html, "html.parser")
        judul = soup.find('a',{'data-title': True})
        judul_berita = judul['data-title']
        konten = soup.find('div',attrs={'id':'detikdetailtext'})
#         konten_berita = konten.text.strip().splitlines()[0]
        konten_berita = konten.get_text()
        lihat_tambahan = konten.find_all("div", class_="lihatjg")
        for row in lihat_tambahan:
            bajug = row.get_text()
            
        

            konten_berita = re.sub(bajug, ' ', konten_berita)
        konten_berita = konten_berita.strip().splitlines()[0]
        konten_berita = re.sub(r'(Foto:.+detikcom)', '', konten_berita)
        return {'judul_berita': judul_berita, 'konten_berita': konten_berita}
    except:
        pass
#     list_berita.append({'judul_berita':judul_berita, 'konten_berita':konten_berita})

def scrap_detik(keyword, jumlah):
    url = 'https://www.detik.com/search/searchall?query='+keyword
    return get_link_detik(url, jumlah, list())

def scrap_detik1(keyword, jumlah, date_start, date_end):
    url = 'https://www.detik.com/search/searchall?query='+keyword+'&sortby=time&fromdatex='+date_start+'&todatex='+date_end
    return get_link_detik(url, jumlah, list()) 

def get_link_detik(url, jumlah, data):
    page = requests.get(url)
    content = page.content
    soup_page = BeautifulSoup(content, 'html.parser')
    for article in soup_page.select('div.list-berita > article'):
        if article.has_attr('class'):
            continue
        berita = scrap_detik_page(article.find('a')['href'])
        data.append(berita) #ganti dengan method scarp halaman berita detik
        if len(data)==jumlah:
            break
    if len(data)<jumlah:
        next_page = soup_page.find('div', class_='paging')
        next_page= next_page.find('a', class_='last')['href']
        return get_link_detik(next_page, jumlah, data)
    else:
        return data

def crawl_kompas(keyword, jumlah, data = list()):
    jum = 0
    driver = webdriver.Chrome()
    driver.get('http://www.kompas.com')
    elem = driver.find_element_by_id('search')
    elem.send_keys(keyword)
    elem.send_keys(Keys.RETURN)
    html = driver.page_source
    soup_page = BeautifulSoup(html, 'html.parser')
    tek = soup_page.findAll('a', attrs={'class':'gs-title'})
    for row in tek:
        berita = scrap_kompas(row['href'])
        data.append(berita)
        jum +=1
        if jum == jumlah:
                return data
    driver.quit()
            
def scrap_kompas(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    soup = BeautifulSoup(html, "html.parser")
    judul = soup.find('h1', class_='read__title')
    judul_berita = judul.text.strip()
    konten = soup.find('div',attrs={'class':'read__content'})
    konten_berita = konten.text.strip()
    return {'judul_berita': judul_berita, 'konten_berita': konten_berita}

def scrap_liputan6_page(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    soup = BeautifulSoup(html, "html.parser")
    judul = soup.find('h1', class_='read-page--header--title')
    judul_berita = judul.text.strip()
    konten = soup.find('div',attrs={'class':'article-content-body__item-content'})
    konten_berita = konten.text.strip()
    return {'judul_berita': judul_berita, 'konten_berita': konten_berita}

def crawl_liputan6(keyword, jumlah, data = list()):
    jum = 0
    driver = webdriver.Chrome()
    driver.get('http://www.liputan6.com')
    elem = driver.find_element_by_id('q')
    elem.send_keys(keyword)
    elem.send_keys(Keys.RETURN)
    html = driver.page_source
    soup_page = BeautifulSoup(html, 'html.parser')
    tek = soup_page.findAll('h4', attrs={'class':'articles--iridescent-list--text-item__title'})
    for div in tek:
        links = div.findAll('a', attrs={'data-template-var':'url'})
        for a in links:
            berita = scrap_liputan6_page(a['href'])
            data.append(berita)
            jum +=1
            if jum == jumlah:
                return data
    driver.quit()