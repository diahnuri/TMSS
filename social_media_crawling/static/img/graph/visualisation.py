from wordcloud import WordCloud
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import os, sqlite3, datetime
from django.core.files import File
from social_media_crawling.models import *
from Sastrawi.Stemmer import StemmerFactory
from Sastrawi.StopWordRemover import StopWordRemoverFactory

stopword_factory = StopWordRemoverFactory.StopWordRemoverFactory()
stemmer_factory = StemmerFactory.StemmerFactory()
stopwords = stopword_factory.create_stop_word_remover()
stemmer = stemmer_factory.create_stemmer()

def visual():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    db_temp = os.path.join(BASE_DIR, 'db.sqlite3')
    my_path = os.path.dirname(__file__)
#     here = os.path.dirname(__file__)
#     os.remove(os.path.join(here,'twitterWordCloud.jpg'))
    f = sqlite3.connect(db_temp)
    cursor = f.cursor()
    a = cursor.execute("SELECT tweet FROM social_media_crawling_TwitterCrawl")

    text = []
    new_text =[]
    plt.ioff()

    
    for row in a:
        text.append(row[0])

    for twit in text:
        new_text.append(stopwords.remove(twit))

    wc = WordCloud(width=1024,height=720,background_color='white').generate(' '.join(new_text))
    fig = plt.figure(figsize=(12, 8), dpi=300)

    plt.imshow(wc)
    plt.axis("off")
    fig.savefig(my_path+'\\twitterWordCloud2.jpg')
    plt.close(fig)
    #create barchart
    a = cursor.execute("SELECT date, count(*)as nilai FROM social_media_crawling_TwitterCrawl group by date")
    date = []
    nilai = []
    for row in a:
        date.append(datetime.datetime.strptime(row[0],"%Y-%m-%d"))
        nilai.append(row[1])
       
    fig,ax = plt.subplots()
    ax.bar(date, nilai, width=0.25)
    ax.xaxis_date()
    
    fig.savefig(my_path+'\\twitterChart3.png')
    plt.close(fig)
    
    #create top user
    listname = []
    i = 0
    a = cursor.execute("SELECT NAME, count(*)As nilai from social_media_crawling_TwitterCrawl group by name order by nilai DESC")
    for row in a:
        listname.append((row[0],int(row[1])))
        i +=1
        if i == 5:
            break
    f.close()
    

    return listname
        
def visual1():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    db_temp = os.path.join(BASE_DIR, 'db.sqlite3')
    my_path = os.path.dirname(__file__)
#     here = os.path.dirname(__file__)
#     os.remove(os.path.join(here,'twitterWordCloud.jpg'))
    f = sqlite3.connect(db_temp)
    cursor = f.cursor()
    a = cursor.execute("SELECT status FROM social_media_crawling_FacebookCrawl")

    text = []
    plt.ioff()
    for row in a:
        text.append(row[0])
         
    wc = WordCloud(background_color='white').generate(' '.join(text))
    fig = plt.figure()
     
    plt.imshow(wc)
    plt.axis("off")
    fig.savefig(my_path+'\\facebookWordCloud2.jpg')
    plt.close(fig)
    #create barchart
#     a = cursor.execute("SELECT date, count(*)as nilai FROM social_media_crawling_TwitterCrawl group by date")
#     date = []
#     nilai = []
#     for row in a:
#         date.append(datetime.datetime.strptime(row[0],"%Y-%m-%d"))
#         nilai.append(row[1])
#        
#     fig,ax = plt.subplots()
#     ax.bar(date, nilai, width=0.25)
#     ax.xaxis_date()
#     
#     fig.savefig(my_path+'\\twitterChart3.png')

    
    #create top user
    listname = []
    i = 0
    a = cursor.execute("SELECT NAME, count(*)As nilai from social_media_crawling_FacebookCrawl group by name order by nilai DESC")
    for row in a:
        listname.append((row[0],int(row[1])))
        i +=1
        if i == 5:
            break
    f.close()
    
    return listname


def visualDS(filter_db,text,dbchoice):
    my_path = os.path.dirname(__file__)
    plt.ioff()
    new_text = []
    for twit in text:
        new_text.append(stopwords.remove(twit))
    wc = WordCloud(width=1024,height=720,background_color='white').generate(' '.join(new_text))
    fig = plt.figure(figsize=(12, 8), dpi=300)
    plt.imshow(wc)
    plt.axis("off")
    fig.savefig(my_path+'\\'+dbchoice+'\\'+filter_db+'.jpg')
    plt.close(fig)