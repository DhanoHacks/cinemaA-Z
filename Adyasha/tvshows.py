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
showurls = []
reviews = []
platforms = []
similar_shows = []
languages = []
rotten_tomato_ratings = []
metascores = []
metacritic_urls = []
rotten_tomato_urls = []


# Getting English translated titles from the shows
headers = {'Accept-Language': 'en-US, en;q=0.5'}

pages = np.arange(1,2,50)
pages

# Storing each of the urls of 50 shows 
for page in pages:
    # Getting the contents from the each url
    page = requests.get('https://www.imdb.com/search/title/?count50&start='+ str(page) + '&num_votes=1000,&sort=num_votes,desc&title_type=tv_series', headers=headers)
    
    soup = bs(page.text, 'html.parser')
    # Aiming the part of the html we want to get the information from
    show_div = soup.find_all('div', class_='lister-item mode-advanced')
    
    # Controling the loop’s rate by pausing the execution of the loop for a specified amount of time
    # Waiting time between requests for a number between 2-10 seconds
    # IMP - this helped us resolve the issue of captcha
    sleep(randint(2,10))
    
    for container in show_div[1:2]:
        # Scraping the show's name
        name = container.h3.a.text
        titles.append(name)
        
        # Scraping the show's year
        year = container.h3.find('span', class_='lister-item-year').text
        years.append(year)
        
        # Scraping the show's length
        runtime = container.find('span', class_='runtime').text if container.p.find('span', class_='runtime') else '-'
        time.append(runtime)

        # Scraping the show's genre
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
        
#         #Getting inside the page
        showurl = re.findall("\"/title/.*?\"", str(container))[1].replace('"',"")
        url = 'https://www.imdb.com' + str(showurl)
        showurls.append(url)

        sleep(randint(3,10))
        insidepage = requests.Session().get(url + "reviews?sort=0&ratingFilter=10")
        soup1 = bs(insidepage.text, 'html.parser')

#         # print(soup1.text)

        review_for_one_show = []
        review_div = soup1.find_all('div' , class_="text show-more__control")
        for review in review_div[0:5]:

            review_for_one_show.append(review.text)

        insidepage = requests.Session().get(url + "reviews?sort=0&ratingFilter=3")
        soup1 = bs(insidepage.text, 'html.parser')
        review_div = soup1.find_all('div' , class_="text show-more__control")
        for review in review_div[0:5]:
            review_for_one_show.append(review.text.replace("\\",""))


        reviews.append(review_for_one_show)


        #Rotten tomatoes url

        sleep(randint(3,10))
        rotten_tomato_url = "https://www.rottentomatoes.com/m/" + str(name.lower().replace(" ","_")) 
        rotten_tomato_urls.append(rotten_tomato_url)
        rotten_tomato_page = requests.Session().get(rotten_tomato_url)
        soup1 = bs(rotten_tomato_page.text, 'html.parser')
        print(rotten_tomato_url)
        # print(soup1.prettify())

        platform_for_one_show = []
        where_to_watch = soup1.find_all('where-to-watch-meta')
        for place in where_to_watch:
            platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
            platform_for_one_show.append(platform)

        platforms.append(platform_for_one_show)

        similar_for_show = []
        similar = soup1.find_all('span' , class_="p--small")
        for elem in similar:
            similar_for_show.append(elem.text.replace('"',""))
        similar_shows.append(similar_for_show)

        # language = soup1.find_all('div',class_="meta-value")[2]
        # languages.append(language.text.rstrip())

        # rotten_tomato_rating = int(re.findall("\"ratingValue\":\".*?\"",str(soup1))[0].replace('"ratingValue":',"").replace('"',''))
        # rotten_tomato_ratings.append(rotten_tomato_rating)

        #metacritic url

        sleep(randint(3,5))
        metacritic_url = "https://www.metacritic.com/tv/" + str(name.lower().replace(" ","-"))
        metacritic_urls.append(metacritic_url)
        print(metacritic_url)
        user_agent = {'User-agent': 'Mozilla/5.0'}
        metacritic_page  = requests.get(metacritic_url,headers = user_agent)
        soup2 = bs(metacritic_page.text, 'html.parser')

        print(soup2.prettify())
        metascore = soup2.find_all('span', class_="metascore_w header_size tvshow positive")[0]
        metascores.append(metascore.text)



# shows = pd.DataFrame({'show':titles,
#                         'url':showurls,
#                        'year':years,
#                        'time_minute':time,
#                        'genres':genres,
#                        'imdb_rating':imdb_ratings,
#                        'plot':plots,
#                        'cast':casts,
#                        'image':images,
#                        'reviews':reviews,
#                        'platform':platforms,
#                        'similar shows':similar_shows,
#                        'language':languages,
#                        'Tomatometer':rotten_tomato_ratings,
#                        'rotten tomato url':rotten_tomato_urls,
#                        'metacrtic url':metacritic_urls,
#                         'Metascore':metascores,
#                        })

# shows.head()



# shows.dtypes



# # Cleaning 'year' column
# shows['year'] = shows['year'].str.extract('(\d+)').astype(int)
# shows.head(3)

# # Cleaning 'time_minute' column
# shows['time_minute'] = shows['time_minute'].str.extract('(\d+)').astype(int)
# shows.head(3)


# shows.dtypes



# shows



# shows.to_csv('shows.csv')

