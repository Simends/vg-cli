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

def getTrackingData(article):
    tr_data_json = article.find_all("script", class_="tracking-data")[0].getText()
    return json.loads(tr_data_json)

def getId(tracking_data):
    return tracking_data['articleId']

def getTitle(tracking_data):
    return tracking_data['teaserText'].replace("\n", " ")

def getPublicationDate(tracking_data):
    try:
        publication_date = tracking_data['changes']['firstPublished']
        return publication_date.replace("T", " ").replace("Z", "")
    except TypeError:
        return "                   "

def main(_):
    while True:
        articles = getArticles()
        for article in articles:
            tracking_data = getTrackingData(article)
            id = getId(tracking_data)
            if id in printed_articles:
                continue
            publication_date = getPublicationDate(tracking_data)
            title = getTitle(tracking_data)
            print(publication_date + " " + title)
            printed_articles.append(id)
        time.sleep(SCRAPE_INTERVAL)

if __name__ == "__main__":
    main(sys.argv[1:])
