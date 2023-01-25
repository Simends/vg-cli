#!/usr/bin/python
import sys
import time
import json
import requests
from bs4 import BeautifulSoup

SCRAPE_INTERVAL = 10

printed_articles = []

def getArticles():
    url = "https://www.vg.no"
    data = requests.get(url).text
    soup = BeautifulSoup(data, "html.parser")
    articles = soup.find_all("article", class_="article-extract")
    return articles

def getUrl(article):
    return article.find_all("a")[0].get('href')

def getArticlePage(url):
    data = requests.get(url).text
    soup = BeautifulSoup(data, "html.parser")
    article = soup.find_all("div", id="main")
    return article

def getTrackingData(article):
    tr_data_json = article.find_all("script", class_="tracking-data")[0].getText()
    return json.loads(tr_data_json)

def getId(tracking_data):
    return tracking_data['articleId']

def getTitle(tracking_data):
    return tracking_data['teaserText'].replace("\n", " ")

def trimDateString(date_string):
    return date_string.replace("T", " ").replace("Z", "")

def getPublicationDateFromArticlePage(article_page):
    try:
        return article_page[0].find_all("time", itemprop="datePublished")[0].get('datetime')
    except IndexError:
        return ""

def getPublicationDateFromFrontPage(tracking_data):
    try:
        return tracking_data['changes']['firstPublished']
    except TypeError:
        return ""

def getPublicationDate(tracking_data, article_page_url):
    publication_date = getPublicationDateFromFrontPage(tracking_data)
    if publication_date != "":
        return trimDateString(publication_date)
    article_page = getArticlePage(article_page_url)
    publication_date = getPublicationDateFromArticlePage(article_page)
    if publication_date != "":
        return trimDateString(publication_date)
    return "                   "

def createArticlesList():
    articles = getArticles()
    article_list = ""
    for article in articles:
        tracking_data = getTrackingData(article)
        id = getId(tracking_data)
        if id in printed_articles:
            continue
        title = getTitle(tracking_data)
        article_page_url = getUrl(article)
        publication_date = getPublicationDate(tracking_data, article_page_url)
        if article_list != "":
            article_list += "\n"
        article_list += publication_date + " " + title
        printed_articles.append(id)
    return article_list
    
def sortStringList(list):
    splitted_list = list.split('\n')
    splitted_list.sort()
    return '\n'.join(splitted_list)

def main(_):
    while True:
        article_list = createArticlesList()
        if article_list != "":
            print(sortStringList(article_list))
        time.sleep(SCRAPE_INTERVAL)

if __name__ == "__main__":
    main(sys.argv[1:])
