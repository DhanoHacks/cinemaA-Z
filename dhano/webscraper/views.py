from django.shortcuts import render
from django.http import HttpResponse

from .models import MovieData

import numpy as np
import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import re

def temp(response):
    return HttpResponse("<h1><a href='/register'> Register </a> <br> <a href='/login'> Login </a></h1>")

def index(response,id):
    m = MovieData.objects.get(id=id)
    return render(response, "webscraper/movie.html", {"m":m})

def save(response):

    # Getting English translated titles from the movies
    headers = {'Accept-Language': 'en-US, en;q=0.5'}

    f=int(open("done.txt","r").read())
    #pages = np.arange(1,1001,50)
    page=f

    # Storing each of the urls of 50 movies 
    if page<1001:
        # Getting the contents from the each url
        page = requests.get('https://www.imdb.com/search/title/?groups=top_1000&start=' + str(page) + '&ref_=adv_nxt',headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        
        # Aiming the part of the html we want to get the information from
        movie_div = soup.find_all('div', class_='lister-item mode-advanced')
        
        # Controling the loop’s rate by pausing the execution of the loop for a specified amount of time
        # Waiting time between requests for a number between 2-10 seconds
        # IMP - this helped us resolve the issue of captcha
        sleep(randint(2,10))
        
        for container in movie_div:
            #print(container)
            # Scraping the movie's name
            name = container.h3.a.text
            
            # Scraping the movie's year
            year = int(re.search("[0-9]+",container.h3.find('span', class_='lister-item-year').text).group(0))
            
            # Scraping the movie's length
            runtime = int(re.search("[0-9]+",container.find('span', class_='runtime').text).group(0)) if container.p.find('span', class_='runtime') else 0

            # Scraping the movie's genre
            genre = container.find('span', class_='genre').text.strip()

            # Scraping the rating
            imdb = float(container.strong.text)

            # Scraping the plot
            plot = container.find_all('p', class_='text-muted')[1].text.lstrip().rstrip()

            # Scraping the cast
            castlist = container.find_all('a')
            stars = []
            for cast in castlist[13:len(castlist)-1]:

                stars.append(cast.text)

            #Scraping the image url
            imageurl = re.findall("https:.*?_V1_", str(container))[0]+".jpg"

            #Getting inside the page
            movieurl = 'https://www.imdb.com' + str(re.findall("\"/title/.*?\"", str(container))[0].replace('"',""))

            sleep(randint(3,10))
            insidepage = requests.Session().get(movieurl + "reviews?sort=0&ratingFilter=10")
            soup1 = BeautifulSoup(insidepage.text, 'html.parser')

            # print(soup1.text)

            review_for_one_movie = {"good_reviews":[],"bad_reviews":[]}
            review_div = soup1.find_all('div' , class_="text show-more__control")
            for review in review_div[0:5]:
                review_for_one_movie["good_reviews"].append(review.text)

            insidepage = requests.Session().get(movieurl + "reviews?sort=0&ratingFilter=3")
            soup1 = BeautifulSoup(insidepage.text, 'html.parser')
            review_div = soup1.find_all('div' , class_="text show-more__control")
            for review in review_div[0:5]:
                review_for_one_movie["bad_reviews"].append(review.text.replace("\\",""))


            #Rotten tomatoes url

            sleep(randint(3,10))
            rotten_tomato_url = "https://www.rottentomatoes.com/m/" + str(re.sub("[^a-z^0-9^_]","",name.lower().replace("-"," ").replace(" ","_"))) + "_" + str(year)
            rotten_tomato_page = requests.Session().get(rotten_tomato_url)
            soup1 = BeautifulSoup(rotten_tomato_page.text, 'html.parser')

            # print(soup1.prettify())

            platform_for_one_movie = []
            where_to_watch = soup1.find_all('where-to-watch-meta')
            for place in where_to_watch:
                platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
                platform_for_one_movie.append(platform)


            similar_for_movie = []
            s1 = soup1.find_all("tiles-carousel-responsive-item")
            for elem in s1:
                similar_for_movie.append(elem.find_all("span")[0].text)

            if len(soup1.find_all('div',class_="meta-value"))<3:
                sleep(randint(3,10))
                rotten_tomato_url = "https://www.rottentomatoes.com/m/" + str(re.sub("[^a-z^0-9^_]","",name.lower().replace("-"," ").replace(" ","_")))
                rotten_tomato_page = requests.Session().get(rotten_tomato_url)
                soup1 = BeautifulSoup(rotten_tomato_page.text, 'html.parser')

                # print(soup1.prettify())

                platform_for_one_movie = []
                where_to_watch = soup1.find_all('where-to-watch-meta')
                for place in where_to_watch:
                    platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
                    platform_for_one_movie.append(platform)


                similar_for_movie = []
                s1 = soup1.find_all("tiles-carousel-responsive-item")
                for elem in s1:
                    similar_for_movie.append(elem.find_all("span")[0].text)
            
            if len(soup1.find_all('div',class_="meta-value"))<3:
                continue
            
            language = soup1.find_all('div',class_="meta-value")[2]

            if len(re.findall("\"ratingValue\":\".*?\"",str(soup1)))==0:
                rotten_tomato_rating = "-"
            else:
                rotten_tomato_rating = int(re.findall("\"ratingValue\":\".*?\"",str(soup1))[0].replace('"ratingValue":',"").replace('"',''))

            #metacritic url

            sleep(randint(3,5))
            metacritic_url = "https://www.metacritic.com/movie/" + re.sub("[^a-z^0-9^-]","",str(name.lower().replace("-"," ").replace(" ","-")))
            user_agent = {'User-agent': 'Mozilla/5.0'}
            metacritic_page  = requests.get(metacritic_url,headers = user_agent)
            soup2 = BeautifulSoup(metacritic_page.text, 'html.parser')

            # print(soup2.prettify())
            if len(soup2.find_all('span', class_="metascore_w header_size movie positive"))==0:
                metascore = "-"
            else:
                metascore = soup2.find_all('span', class_="metascore_w header_size movie positive")[0]
                metascore=metascore.text

            if len(MovieData.objects.filter(name=name))==0:
                m = MovieData(name=name,site_link={"imdb":movieurl,"rotten_tomatoes":rotten_tomato_url,"metacritic":metacritic_url}
                ,rating={"imdb":imdb,"rotten_tomatoes":rotten_tomato_rating,"metacritic":metascore},plot=plot
                ,language=language.text.rstrip().split(", "),similar=similar_for_movie
                ,year_of_release=year,duration=runtime,genre=genre.split(", "),cast=stars
                ,reviews=review_for_one_movie,platform=platform_for_one_movie,image_url=imageurl)
                m.save()
    open("done.txt","w").write(str(f+50))
    return HttpResponse(f"Finished Scraping Movies {f} - {f+49}")

def search_results_view(response):
    query = response.GET.get("q")
    movie = MovieData.objects.filter(name__contains=query)
    if len(movie)>0:
        return render(response, "webscraper/movie.html", {"m":movie[0]})
    else:
        # Getting English translated titles from the movies
        headers = {'Accept-Language': 'en-US, en;q=0.5'}
        with requests.Session() as s:
            movie_name = query.replace(" ","%20")
            sleep(randint(3,10))
            movieurl = 'https://www.imdb.com/search/title/?title='+ movie_name
            page = requests.get(movieurl)
            
            soup = BeautifulSoup(page.text, 'html.parser')

            movie_div = soup.find_all('div', class_='lister-item mode-advanced')
            sleep(randint(2,10))
            
            if len(movie_div) != 0:
                container = movie_div[0:1]
                #print(container)
                # Scraping the movie's name
                name = container.h3.a.text
            
                # Scraping the movie's year
                year = int(re.search("[0-9]+",container.h3.find('span', class_='lister-item-year').text).group(0))
                
                # Scraping the movie's length
                runtime = int(re.search("[0-9]+",container.find('span', class_='runtime').text).group(0)) if container.p.find('span', class_='runtime') else 0

                # Scraping the movie's genre
                genre = container.find('span', class_='genre').text.strip()

                # Scraping the rating
                imdb = float(container.strong.text)

                # Scraping the plot
                plot = container.find_all('p', class_='text-muted')[1].text.lstrip().rstrip()

                # Scraping the cast
                castlist = container.find_all('a')
                stars = []
                for cast in castlist[13:len(castlist)-1]:

                    stars.append(cast.text)

                #Scraping the image url
                imageurl = re.findall("https:.*?_V1_", str(container))[0]+".jpg"

                #Getting inside the page
                movieurl = 'https://www.imdb.com' + str(re.findall("\"/title/.*?\"", str(container))[0].replace('"',""))

                sleep(randint(3,10))
                insidepage = requests.Session().get(movieurl + "reviews?sort=0&ratingFilter=10")
                soup1 = BeautifulSoup(insidepage.text, 'html.parser')

                # print(soup1.text)

                review_for_one_movie = {"good_reviews":[],"bad_reviews":[]}
                review_div = soup1.find_all('div' , class_="text show-more__control")
                for review in review_div[0:5]:
                    review_for_one_movie["good_reviews"].append(review.text)

                insidepage = requests.Session().get(movieurl + "reviews?sort=0&ratingFilter=3")
                soup1 = BeautifulSoup(insidepage.text, 'html.parser')
                review_div = soup1.find_all('div' , class_="text show-more__control")
                for review in review_div[0:5]:
                    review_for_one_movie["bad_reviews"].append(review.text.replace("\\",""))


                #Rotten tomatoes url

                sleep(randint(3,10))
                rotten_tomato_url = "https://www.rottentomatoes.com/m/" + str(re.sub("[^a-z^0-9^_]","",name.lower().replace("-"," ").replace(" ","_"))) + "_" + str(year)
                rotten_tomato_page = requests.Session().get(rotten_tomato_url)
                soup1 = BeautifulSoup(rotten_tomato_page.text, 'html.parser')

                # print(soup1.prettify())

                platform_for_one_movie = []
                where_to_watch = soup1.find_all('where-to-watch-meta')
                for place in where_to_watch:
                    platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
                    platform_for_one_movie.append(platform)


                similar_for_movie = []
                s1 = soup1.find_all("tiles-carousel-responsive-item")
                for elem in s1:
                    similar_for_movie.append(elem.find_all("span")[0].text)

                if len(soup1.find_all('div',class_="meta-value"))<3:
                    sleep(randint(3,10))
                    rotten_tomato_url = "https://www.rottentomatoes.com/m/" + str(re.sub("[^a-z^0-9^_]","",name.lower().replace("-"," ").replace(" ","_")))
                    rotten_tomato_page = requests.Session().get(rotten_tomato_url)
                    soup1 = BeautifulSoup(rotten_tomato_page.text, 'html.parser')

                    # print(soup1.prettify())

                    platform_for_one_movie = []
                    where_to_watch = soup1.find_all('where-to-watch-meta')
                    for place in where_to_watch:
                        platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
                        platform_for_one_movie.append(platform)


                    similar_for_movie = []
                    s1 = soup1.find_all("tiles-carousel-responsive-item")
                    for elem in s1:
                        similar_for_movie.append(elem.find_all("span")[0].text)
                
                if len(soup1.find_all('div',class_="meta-value"))<3:
                    return render(response, "webscraper/error.html")
                
                language = soup1.find_all('div',class_="meta-value")[2]

                if len(re.findall("\"ratingValue\":\".*?\"",str(soup1)))==0:
                    rotten_tomato_rating = "-"
                else:
                    rotten_tomato_rating = int(re.findall("\"ratingValue\":\".*?\"",str(soup1))[0].replace('"ratingValue":',"").replace('"',''))

                #metacritic url

                sleep(randint(3,5))
                metacritic_url = "https://www.metacritic.com/movie/" + re.sub("[^a-z^0-9^-]","",str(name.lower().replace("-"," ").replace(" ","-")))
                user_agent = {'User-agent': 'Mozilla/5.0'}
                metacritic_page  = requests.get(metacritic_url,headers = user_agent)
                soup2 = BeautifulSoup(metacritic_page.text, 'html.parser')

                # print(soup2.prettify())
                if len(soup2.find_all('span', class_="metascore_w header_size movie positive"))==0:
                    metascore = "-"
                else:
                    metascore = soup2.find_all('span', class_="metascore_w header_size movie positive")[0]
                    metascore=metascore.text

                if len(MovieData.objects.filter(name=name))==0:
                    m = MovieData(name=name,site_link={"imdb":movieurl,"rotten_tomatoes":rotten_tomato_url,"metacritic":metacritic_url}
                    ,rating={"imdb":imdb,"rotten_tomatoes":rotten_tomato_rating,"metacritic":metascore},plot=plot
                    ,language=language.text.rstrip().split(", "),similar=similar_for_movie
                    ,year_of_release=year,duration=runtime,genre=genre.split(", "),cast=stars
                    ,reviews=review_for_one_movie,platform=platform_for_one_movie,image_url=imageurl)
                    m.save()
                    return render(response, "webscraper/movie.html", {"m":m})
            else:
                return render(response, "webscraper/error.html")


def home(response):
    return render(response, "webscraper/index.html", {})

def watched(response):
    print(response.user)