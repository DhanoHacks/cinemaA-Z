import pandas as pd
import numpy as np
import requests
from requests import get
from bs4 import BeautifulSoup as bs
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
reviews = []
platforms = []
similar_movies = []
languages = []
rotten_tomato_ratings = []
metascore = []
metacritic_urls = []
rotten_tomato_urls = []


# Getting English translated titles from the movies
headers = {'Accept-Language': 'en-US, en;q=0.5'}

pages = np.arange(1,2,50)
pages

# Storing each of the urls of 50 movies 
for page in pages:
    # Getting the contents from the each url
    page = requests.get('https://www.imdb.com/search/title/?groups=top_1000&start=' + str(page) + '&ref_=adv_nxt', headers=headers)
    soup = bs(page.text, 'html.parser')
    
    # Aiming the part of the html we want to get the information from
    movie_div = soup.find_all('div', class_='lister-item mode-advanced')
    
    # Controling the loop’s rate by pausing the execution of the loop for a specified amount of time
    # Waiting time between requests for a number between 2-10 seconds
    # IMP - this helped us resolve the issue of captcha
    sleep(randint(2,10))
    
    for container in movie_div[1:2]:
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
        images.append(imageurl[0])
        
        #Getting inside the page
        movieurl = re.findall("\"/title/.*?\"", str(container))[1].replace('"',"")
        url = 'https://www.imdb.com' + str(movieurl)
        movieurls.append(url)

        sleep(randint(3,10))
        insidepage = requests.Session().get(url + "reviews?sort=0&ratingFilter=10")
        soup1 = bs(insidepage.text, 'html.parser')

        # print(soup1.text)

        review_for_one_movie = []
        review_div = soup1.find_all('div' , class_="text show-more__control")
        for review in review_div[0:5]:

            review_for_one_movie.append(review.text)

        insidepage = requests.Session().get(url + "reviews?sort=0&ratingFilter=3")
        soup1 = bs(insidepage.text, 'html.parser')
        review_div = soup1.find_all('div' , class_="text show-more__control")
        for review in review_div[0:5]:
            review_for_one_movie.append(review.text.replace("\\",""))


        reviews.append(review_for_one_movie)


        #Rotten tomatoes url

        sleep(randint(3,10))
        rotten_tomato_url = "https://www.rottentomatoes.com/m/" + str(name.lower().replace(" ","_")) + "_" + str(year).replace("(","").replace(")","")
        rotten_tomato_urls.append(rotten_tomato_url)
        rotten_tomato_page = requests.Session().get(rotten_tomato_url)
        soup1 = bs(rotten_tomato_page.text, 'html.parser')

        # print(soup1.prettify())

        platform_for_one_movie = []
        where_to_watch = soup1.find_all('where-to-watch-meta')
        for place in where_to_watch:
            platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
            platform_for_one_movie.append(platform)

        platforms.append(platform_for_one_movie)

        similar_for_movie = []
        similar = soup1.find_all('span' , class_="p--small")
        for elem in similar:
            similar_for_movie.append(elem.text.replace('"',""))
        similar_movies.append(similar_for_movie)

        language = soup1.find_all('div',class_="meta-value")[2]
        languages.append(language.text.rstrip())

        rotten_tomato_rating = int(re.findall("\"ratingValue\":\".*?\"",str(soup1))[0].replace('"ratingValue":',"").replace('"',''))
        rotten_tomato_ratings.append(rotten_tomato_rating)

        #metacritic url

        sleep(randint(3,10))
        metacritic_url = "https://www.metacritic.com/movie/" + str(name.lower().replace(" ","-"))
        metacritic_urls.append(metacritic_url)
        # metacritic_page = requests.Session().get(metacritic_url)
        # soup2 = bs(metacritic_page.text, 'html.parser')

        # print(soup2.prettify())



movies = pd.DataFrame({'movie':titles,
                        'url':movieurls,
                       'year':years,
                       'time_minute':time,
                       'genres':genres,
                       'imdb_rating':imdb_ratings,
                       'plot':plots,
                       'cast':casts,
                       'image':images,
                       'reviews':reviews,
                       'platform':platforms,
                       'similar movies':similar_movies,
                       'language':languages,
                       'Tomatometer':rotten_tomato_ratings,
                       'rotten tomato url':rotten_tomato_urls,
                       'metacrtic url':metacritic_urls,
                    #    'Metascore':metascore,
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

