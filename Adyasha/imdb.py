import pandas as pd
import numpy as np
import requests
from requests import get
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import re

titles = []
years = []
time = []
imdb_ratings = []
genres = []
plots = []
casts = []
images = []
movieurls = []


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

        # Scraping the plot
        plot = container.find_all('p', class_='text-muted')[1].text.lstrip().rstrip()
        plots.append(plot)

        # Scraping the cast
        castlist = container.find_all('a')
        stars = []
        for cast in castlist[13:len(castlist)-1]:

            stars.append(cast.text)
        casts.append(stars)

        #Scraping the image url
        imageurl = re.findall("https:.*\.jpg", str(container))
        images.append(imageurl)
        
        #Getting inside the page
        movieurl = re.findall("\"/title/.*?\"", str(container))[0].replace('"',"")
        movieurls.append('https://www.imdb.com' + str(movieurl))




movies = pd.DataFrame({'movie':titles,
                        'url':movieurls,
                       'year':years,
                       'time_minute':time,
                       'genres':genres,
                       'imdb_rating':imdb_ratings,
                       'plot':plots,
                       'cast':casts,
                       'image':images,
                       })

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

