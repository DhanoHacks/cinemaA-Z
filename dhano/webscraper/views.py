from django.shortcuts import render
from django.http import HttpResponse

from .models import MovieData, List

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
    sim = []
    for s in m.similar:
        if len(MovieData.objects.filter(name=s))>0:
            sim.append({"mname":s,"mid":MovieData.objects.filter(name=s)[0].id})
        else:
            sim.append({"mname":s,"mid":"notfound"})
    print(sim)
    if response.method == "POST" :
        if response.POST.get("watched"):
            watched = List.objects.get(type="watched")
            items = watched.items_set.all().filter(text=m.name, user=response.user)
            if len(items) == 0:
                watched.items_set.create(text = m.name, user=response.user)
            elif len(items) == 1:
                items[0].delete()

        elif response.POST.get("like"):
            liked = List.objects.get(type="liked")
            items = liked.items_set.all().filter(text=m.name, user=response.user)
            if len(items) == 0:
                liked.items_set.create(text = m.name, user=response.user)
            elif len(items) == 1:
                items[0].delete()
        elif response.POST.get("watchlist"):
            watchlist = List.objects.get(type="watchlist")
            items = watchlist.items_set.all().filter(text=m.name, user=response.user)
            if len(items) == 0:
                watchlist.items_set.create(text = m.name, user=response.user)
            elif len(items) == 1:
                items[0].delete()
    return render(response, "webscraper/movie.html", {"m":m,"sim":sim})

def save(response):
    # return save_tvshow(response)
    # Getting English translated titles from the movies
    headers = {'Accept-Language': 'en-US, en;q=0.5'}

    f=int(open("done_movie.txt","r").read())
    #pages = np.arange(1,1001,50)
    count=0

    # Storing each of the urls of 50 movies 
    while f<1001 and count<1:
        # Getting the contents from the each url
        page = requests.get('https://www.imdb.com/search/title/?groups=top_1000&start=' + str(f) + '&ref_=adv_nxt',headers=headers)
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
        f+=50
        count+=1
        open("done_movie.txt","w").write(str(f))
    return HttpResponse(f"Finished Scraping Movies {f-50*count} - {f-1}")


def save_tvshow(response):
    
    # Getting English translated titles from the movies
    headers = {'Accept-Language': 'en-US, en;q=0.5'}

    f=int(open("done_tvseries.txt","r").read())
    count = 0
    before = f
    #pages = np.arange(1,1001,50)

    # Storing each of the urls of 50 movies 
    while f<1001 and count<1:
        # Getting the contents from the each url
        page = requests.get('https://www.imdb.com/search/title/?count50&start='+ str(f) + '&num_votes=1000,&sort=num_votes,desc&title_type=tv_series', headers=headers)
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
            rotten_tomato_url = "https://www.rottentomatoes.com/tv/" + str(re.sub("[^a-z^0-9^_]","",name.lower().replace("-"," ").replace(" ","_")))
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

            language = ["English",]

            if len(re.findall("\"ratingValue\":\".*?\"",str(soup1)))==0:
                rotten_tomato_rating = "-"
            else:
                rotten_tomato_rating = int(re.findall("\"ratingValue\":\".*?\"",str(soup1))[0].replace('"ratingValue":',"").replace('"',''))

            #metacritic url

            sleep(randint(3,5))
            metacritic_url = "https://www.metacritic.com/tv/" + re.sub("[^a-z^0-9^-]","",str(name.lower().replace("-"," ").replace(" ","-")))
            user_agent = {'User-agent': 'Mozilla/5.0'}
            metacritic_page  = requests.get(metacritic_url,headers = user_agent)
            soup2 = BeautifulSoup(metacritic_page.text, 'html.parser')

            # print(soup2.prettify())
            if len(soup2.find_all('span', class_="metascore_w header_size tvshow positive"))==0:
                metascore = "-"
            else:
                metascore = soup2.find_all('span', class_="metascore_w header_size tvshow positive")[0]
                metascore=metascore.text

            if len(MovieData.objects.filter(name=name))==0:
                m = MovieData(name=name,site_link={"imdb":movieurl,"rotten_tomatoes":rotten_tomato_url,"metacritic":metacritic_url}
                ,rating={"imdb":imdb,"rotten_tomatoes":rotten_tomato_rating,"metacritic":metascore},plot=plot
                ,language=language,similar=similar_for_movie
                ,year_of_release=year,duration=runtime,genre=genre.split(", "),cast=stars
                ,reviews=review_for_one_movie,platform=platform_for_one_movie,image_url=imageurl)
                m.save()
        f+=50
        count+=1
    open("done_tvseries.txt","w").write(str(f))
    return HttpResponse(f"Finished Scraping Movies {before} - {f-1}")


def search_page_view(response):
    query = response.GET.get("q")
    movies = MovieData.objects.filter(name__contains=query)
    if len(movies)>0:
        return render(response,"webscraper/searchpage.html",{"list_of_movies":movies})
    else:
        # Getting English translated titles from the movies
        headers = {'Accept-Language': 'en-US, en;q=0.5'}
        with requests.Session() as s:
            movie_name = query.replace(" ","%20")
            sleep(randint(3,10))
            movieurl = 'https://www.imdb.com/search/title/?title='+ movie_name+'&sort=num_votes,desc'
            page = requests.get(movieurl)
            
            soup = BeautifulSoup(page.text, 'html.parser')

            movie_div = soup.find_all('div', class_='lister-item mode-advanced')
            sleep(randint(2,10))
            a=0
            movies=[]
            while a<len(movie_div) and a<2:
                a+=1
                container = movie_div[a]
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
                    movies.append(m)

            b=0
            while b<len(movie_div) and b<2:
                b+=1
                container=movie_div[b]
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
                rotten_tomato_url = "https://www.rottentomatoes.com/tv/" + str(re.sub("[^a-z^0-9^_]","",name.lower().replace("-"," ").replace(" ","_")))
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

                language = ["English",]

                if len(re.findall("\"ratingValue\":\".*?\"",str(soup1)))==0:
                    rotten_tomato_rating = "-"
                else:
                    rotten_tomato_rating = int(re.findall("\"ratingValue\":\".*?\"",str(soup1))[0].replace('"ratingValue":',"").replace('"',''))

                #metacritic url

                sleep(randint(3,5))
                metacritic_url = "https://www.metacritic.com/tv/" + re.sub("[^a-z^0-9^-]","",str(name.lower().replace("-"," ").replace(" ","-")))
                user_agent = {'User-agent': 'Mozilla/5.0'}
                metacritic_page  = requests.get(metacritic_url,headers = user_agent)
                soup2 = BeautifulSoup(metacritic_page.text, 'html.parser')

                # print(soup2.prettify())
                if len(soup2.find_all('span', class_="metascore_w header_size tvshow positive"))==0:
                    metascore = "-"
                else:
                    metascore = soup2.find_all('span', class_="metascore_w header_size tvshow positive")[0]
                    metascore=metascore.text

                if len(MovieData.objects.filter(name=name))==0:
                    m = MovieData(name=name,site_link={"imdb":movieurl,"rotten_tomatoes":rotten_tomato_url,"metacritic":metacritic_url}
                    ,rating={"imdb":imdb,"rotten_tomatoes":rotten_tomato_rating,"metacritic":metascore},plot=plot
                    ,language=language,similar=similar_for_movie
                    ,year_of_release=year,duration=runtime,genre=genre.split(", "),cast=stars
                    ,reviews=review_for_one_movie,platform=platform_for_one_movie,image_url=imageurl)
                    m.save()
                    movies.append(m)
            if len(movies)>0:
                return render(response,"webscraper/searchpage.html",{"list_of_movies":movies})
            else:
                return render(response, "webscraper/error.html")


def home(response):
    if not List.objects.filter(type="watched").exists():
        watched = List(type = "watched")
        watched.save()
    if not List.objects.filter(type="watchlist").exists():
        watchlist = List(type="watchlist")
        watchlist.save()
    if not List.objects.filter(type="liked").exists():
        liked = List(type="liked")
        liked.save()

    list = List.objects.get(type="watched").items_set.filter(user=response.user.id).order_by('-id')
    watched = [MovieData.objects.get(name=movie.text) for movie in list]
    list = List.objects.get(type="watchlist").items_set.filter(user=response.user.id).order_by('-id')
    watchlist = [MovieData.objects.get(name=movie.text) for movie in list]
    list = List.objects.get(type="liked").items_set.filter(user=response.user.id).order_by('-id')
    liked = [MovieData.objects.get(name=movie.text) for movie in list]
    top10 = MovieData.objects.all().order_by('-rating__imdb')[0:10]


    sim_movie_names = []
    recommended = []
    for movie in liked:
        for sim_movie in movie.similar:
            if sim_movie not in sim_movie_names:
                sim_movie_names.append(sim_movie)
    for movie_name in sim_movie_names:
        f=MovieData.objects.filter(name=movie_name)
        if len(f)>0 and f[0] not in watched:
            recommended.append(f[0])

    return render(response, "webscraper/index.html"
    , {"top10":top10, "recommended":recommended[0:8], "watched":watched[0:8], "watchlist":watchlist[0:8], "liked":liked[0:8], "lengthwl":len(watchlist), "lengthwtd":len(watched), "lenlik":len(liked), "lenrec":len(recommended)})
