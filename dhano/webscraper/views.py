from django.shortcuts import render
from django.http import HttpResponse

from .models import MovieData

import pandas as pd
import numpy as np
import requests
from requests import get
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import re

def index(response):
    return HttpResponse("Dhano was here!")

def save(response):
    titles = []
    years = []
    time = []
    imdb_ratings = []
    genres = []



    # Getting English translated titles from the movies
    headers = {'Accept-Language': 'en-US, en;q=0.5'}

    pages = np.arange(1,1001,50)

    # Storing each of the urls of 50 movies 
    for page in pages:
        # Getting the contents from the each url
        page = requests.get('https://www.imdb.com/search/title/?groups=top_1000&start=' + str(page) + '&ref_=adv_nxt', headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        
        # Aiming the part of the html we want to get the information from
        movie_div = soup.find_all('div', class_='lister-item mode-advanced')
        
        # Controling the loop’s rate by pausing the execution of the loop for a specified amount of time
        # Waiting time between requests for a number between 2-10 seconds
        # IMP - this helped us resolve the issue of captcha
        sleep(randint(2,10))
        
        for container in movie_div:
            print(container)
            # Scraping the movie's name
            name = container.h3.a.text
            titles.append(name)
            
            # Scraping the movie's year
            year = int(re.search("[0-9]+",container.h3.find('span', class_='lister-item-year').text).group(0))
            years.append(year)
            
            # Scraping the movie's length
            runtime = int(re.search("[0-9]+",container.find('span', class_='runtime').text).group(0)) if container.p.find('span', class_='runtime') else 0
            time.append(runtime)

            # Scraping the movie's genre
            genre = container.find('span', class_='genre').text.strip()
            genres.append(genre)

            # Scraping the rating
            imdb = float(container.strong.text)
            imdb_ratings.append(imdb)

            m = MovieData(name=name,site_link="",rating=imdb,plot="",language=["English",],similar=dict(),year_of_release=year,duration=runtime,genre=genre.split(", "),cast=dict(),reviews=dict(),platform=["Netflix",])
            m.save()
    return HttpResponse("Finished Scraping")