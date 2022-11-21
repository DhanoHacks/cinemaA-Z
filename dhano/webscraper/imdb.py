#from .models import MovieData

import pandas as pd
import numpy as np
import requests
from requests import get
from bs4 import BeautifulSoup
from time import sleep
from random import randint

titles = []
years = []
time = []
imdb_ratings = []
genres = []



# Getting English translated titles from the movies
headers = {'Accept-Language': 'en-US, en;q=0.5'}

pages = np.arange(1,2,50)
pages

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
        year = container.h3.find('span', class_='lister-item-year').text
        years.append(year)
        
        # Scraping the movie's length
        runtime = container.find('span', class_='runtime').text if container.p.find('span', class_='runtime') else '-'
        time.append(runtime)

        # Scraping the movie's genre
        genre = container.find('span', class_='genre').text.strip()
        genres.append(genre)

        # Scraping the rating
        imdb = float(container.strong.text)
        imdb_ratings.append(imdb)

        #m = MovieData(name=name,site_link="",rating=imdb,plot="",language=["English",],similar=dict(),
        #year_of_release=int(year),duration=int(runtime),genre=genre.split(", "),cast=dict(),reviews=dict(),platform=["Netflix",])
        #m.save()




movies = pd.DataFrame({'movie':titles,
                       'year':years,
                       'time_minute':time,
                       'genres':genres,
                       'imdb_rating':imdb_ratings})

movies.head()



movies.dtypes



# Cleaning 'year' column
movies['year'] = movies['year'].str.extract('(\d+)').astype(int)
movies.head(3)

# Cleaning 'time_minute' column
movies['time_minute'] = movies['time_minute'].str.extract('(\d+)').astype(int)
movies.head(3)


movies.dtypes



movies



movies.to_csv('movies.csv')


