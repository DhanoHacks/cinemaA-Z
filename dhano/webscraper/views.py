"""Stores all views/functions involved in the webscraper app
"""

from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import MovieData, List, Items

import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import re

def temp(response):
    """Redirects to home page
    """
    return redirect('/home/')

def index(response,id):
    """Renders the movie page corresponding to the id

    :param id: id of the movie
    :type id: int
    """
    m = MovieData.objects.get(id=id)
    #generating similar movies
    sim = []
    for s in m.similar:
        if len(MovieData.objects.filter(name=s))>0:
            sim.append({"mname":s,"mid":MovieData.objects.filter(name=s)[0].id})
        else:
            sim.append({"mname":s,"mid":"notfound"})

    #updating watched, watchlist, and liked status depending on whether user click on the buttons
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
    #Passing variable to know if the movie is in a particular list or not
    if response.user.is_authenticated:
        myuser = response.user
        movie = m.name
        watched = List.objects.get(type="watched").items_set.all().filter(text = movie, user = myuser)
        watchlist = List.objects.get(type="watchlist").items_set.all().filter(text = movie, user = myuser)
        liked = List.objects.get(type="liked").items_set.all().filter(text = movie, user = myuser)
        return render(response, "webscraper/movie.html", {"m":m,"sim":sim, "watched":len(watched), "watchlist":len(watchlist),"liked":len(liked)})
    else:
        return render(response, "webscraper/movie.html", {"m":m,"sim":sim})

def save_movies(response):
    """Scrapes movies from top 1000 list, in multiples of 50"""

    # Getting English translated titles from the movies
    headers = {'Accept-Language': 'en-US, en;q=0.5'}

    # File storing the number of movies which have already been scraped
    f=int(open("done_movie.txt","r").read())
    before=f
    # Variable which models how many multiples of 50 we want to scrape
    count=0

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
            # Scraping the movie's name
            name = container.h3.a.text
            
            # Scraping the movie's year
            year = int(re.search("[0-9]+",container.h3.find('span', class_='lister-item-year').text).group(0))
            
            # Scraping the movie's length
            runtime = int(re.search("[0-9]+",container.find('span', class_='runtime').text).group(0)) if container.p.find('span', class_='runtime') else 0

            # Scraping the movie's genre
            genre = container.find('span', class_='genre').text.strip()

            # Scraping the IMDb rating
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

            #Scraping the good reviews
            review_for_one_movie = {"good_reviews":[],"bad_reviews":[]}
            review_div = soup1.find_all('div' , class_="text show-more__control")
            for review in review_div[0:5]:
                review_for_one_movie["good_reviews"].append(review.text)
            #Scraping the bad reviews
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

            #Scraping the movie platforms
            platform_for_one_movie = []
            where_to_watch = soup1.find_all('where-to-watch-meta')
            for place in where_to_watch:
                platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
                platform_for_one_movie.append(platform)

            #Scraping similar movies and tv shows
            similar_for_movie = []
            s1 = soup1.find_all("tiles-carousel-responsive-item")
            for elem in s1:
                similar_for_movie.append(elem.find_all("span")[0].text)
            #If the following quantity is < 3, that means that the movie link was incorrect, we retry with a different link
            if len(soup1.find_all('div',class_="meta-value"))<3:
                sleep(randint(3,10))
                rotten_tomato_url = "https://www.rottentomatoes.com/m/" + str(re.sub("[^a-z^0-9^_]","",name.lower().replace("-"," ").replace(" ","_")))
                rotten_tomato_page = requests.Session().get(rotten_tomato_url)
                soup1 = BeautifulSoup(rotten_tomato_page.text, 'html.parser')

                #Scraping the movie platforms
                platform_for_one_movie = []
                where_to_watch = soup1.find_all('where-to-watch-meta')
                for place in where_to_watch:
                    platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
                    platform_for_one_movie.append(platform)

                #Scraping similar movies
                similar_for_movie = []
                s1 = soup1.find_all("tiles-carousel-responsive-item")
                for elem in s1:
                    similar_for_movie.append(elem.find_all("span")[0].text)
            
            #If movie is unavailable on rotten tomatoes, we skip the movie
            if len(soup1.find_all('div',class_="meta-value"))<3:
                continue
            
            #Scraping the languages for movie
            language = soup1.find_all('div',class_="meta-value")[2]

            #Scraping the rotten tomatoes rating for movie
            if len(re.findall("\"ratingValue\":\".*?\"",str(soup1)))==0:
                rotten_tomato_rating = "-" #No rating on rotten tomatoes
            else:
                rotten_tomato_rating = int(re.findall("\"ratingValue\":\".*?\"",str(soup1))[0].replace('"ratingValue":',"").replace('"',''))

            #metacritic url

            sleep(randint(3,5))
            metacritic_url = "https://www.metacritic.com/movie/" + re.sub("[^a-z^0-9^-]","",str(name.lower().replace("-"," ").replace(" ","-")))
            user_agent = {'User-agent': 'Mozilla/5.0'}
            metacritic_page  = requests.get(metacritic_url,headers = user_agent)
            soup2 = BeautifulSoup(metacritic_page.text, 'html.parser')

            #Scraping the Metascore for movie
            if len(soup2.find_all('span', class_="metascore_w header_size movie positive"))==0:
                metascore = "-" #No rating on rotten tomatoes
            else:
                metascore = soup2.find_all('span', class_="metascore_w header_size movie positive")[0]
                metascore=metascore.text

            #Storing the movie if it isnt already stored in the database
            if len(MovieData.objects.filter(name=name))==0:
                m = MovieData(name=name,site_link={"imdb":movieurl,"rotten_tomatoes":rotten_tomato_url,"metacritic":metacritic_url}
                ,rating={"imdb":imdb,"rotten_tomatoes":rotten_tomato_rating,"metacritic":metascore},plot=plot
                ,language=language.text.rstrip().split(", "),similar=similar_for_movie
                ,year_of_release=year,duration=runtime,genre=genre.split(", "),cast=stars
                ,reviews=review_for_one_movie,platform=platform_for_one_movie,image_url=imageurl)
            
                m.save()
        f+=50
        count+=1
        open("done_movie.txt","w").write(str(f)) #Updating the file
    return HttpResponse(f"Finished Scraping {before} - {f-1}") #Just for confirmation


def save_tvshows(response):
    """Scrapes tv shows from top 1000 list, in multiples of 50"""
    # Getting English translated titles from the tv shows
    headers = {'Accept-Language': 'en-US, en;q=0.5'}

    # File storing the number of tv shows which have already been scraped
    f=int(open("done_tvseries.txt","r").read())
    before = f
    # Variable which models how many multiples of 50 we want to scrape
    count = 0

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
            # Scraping the tv show's name
            name = container.h3.a.text
            
            # Scraping the tv show's year
            year = int(re.search("[0-9]+",container.h3.find('span', class_='lister-item-year').text).group(0))
            
            # Scraping the tv show's length
            runtime = int(re.search("[0-9]+",container.find('span', class_='runtime').text).group(0)) if container.p.find('span', class_='runtime') else 0

            # Scraping the tv show's genre
            genre = container.find('span', class_='genre').text.strip()

            # Scraping the IMDb rating
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

            #Scraping the good reviews
            review_for_one_movie = {"good_reviews":[],"bad_reviews":[]}
            review_div = soup1.find_all('div' , class_="text show-more__control")
            for review in review_div[0:5]:
                review_for_one_movie["good_reviews"].append(review.text)
            #Scraping the bad reviews
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

            #Scraping the platforms on which we can watch
            platform_for_one_movie = []
            where_to_watch = soup1.find_all('where-to-watch-meta')
            for place in where_to_watch:
                platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
                platform_for_one_movie.append(platform)

            #Scraping similar movies and tv shows
            similar_for_movie = []
            s1 = soup1.find_all("tiles-carousel-responsive-item")
            for elem in s1:
                similar_for_movie.append(elem.find_all("span")[0].text)

            #Scraping language
            language = ["English",]

            #Scraping rotten tomatoes rating
            if len(re.findall("\"ratingValue\":\".*?\"",str(soup1)))==0:
                rotten_tomato_rating = "-" #Not rated on rotten tomatoes
            else:
                rotten_tomato_rating = int(re.findall("\"ratingValue\":\".*?\"",str(soup1))[0].replace('"ratingValue":',"").replace('"',''))

            #metacritic url

            sleep(randint(3,5))
            metacritic_url = "https://www.metacritic.com/tv/" + re.sub("[^a-z^0-9^-]","",str(name.lower().replace("-"," ").replace(" ","-")))
            user_agent = {'User-agent': 'Mozilla/5.0'}
            metacritic_page  = requests.get(metacritic_url,headers = user_agent)
            soup2 = BeautifulSoup(metacritic_page.text, 'html.parser')

            #Scraping metascore
            if len(soup2.find_all('span', class_="metascore_w header_size tvshow positive"))==0:
                metascore = "-" #Tv show not rated on metacritic
            else:
                metascore = soup2.find_all('span', class_="metascore_w header_size tvshow positive")[0]
                metascore=metascore.text

            #Storing the tv show if it doesnt already exist in the database
            if len(MovieData.objects.filter(name=name))==0:
                m = MovieData(name=name,site_link={"imdb":movieurl,"rotten_tomatoes":rotten_tomato_url,"metacritic":metacritic_url}
                ,rating={"imdb":imdb,"rotten_tomatoes":rotten_tomato_rating,"metacritic":metascore},plot=plot
                ,language=language,similar=similar_for_movie
                ,year_of_release=year,duration=runtime,genre=genre.split(", "),cast=stars
                ,reviews=review_for_one_movie,platform=platform_for_one_movie,image_url=imageurl)
                m.save()
        f+=50
        count+=1
        open("done_tvseries.txt","w").write(str(f)) #Updating the file
    return HttpResponse(f"Finished Scraping {before} - {f-1}") #Just for confirmation


def search_page_view(response):
    """Searches user query within the database, if it doesnt exist, scrapes atmost
    2 movies and 2 tv shows online, and displays search results
    """
    query = response.GET.get("q")
    movies = MovieData.objects.filter(name__contains=query)
    if len(movies)>0: #Found the query within the database
        return render(response,"webscraper/searchpage.html",{"list_of_movies":movies})
    else:
        # Getting English translated titles from the movies
        headers = {'Accept-Language': 'en-US, en;q=0.5'}
        with requests.Session() as s:
            movie_name = query.replace(" ","%20")
            sleep(randint(3,10))
            #Scraping results from IMDb search page for movies
            movieurl = 'https://www.imdb.com/search/title/?title='+ movie_name+'&sort=num_votes,desc'
            page = requests.get(movieurl)
            
            soup = BeautifulSoup(page.text, 'html.parser')

            movie_div = soup.find_all('div', class_='lister-item mode-advanced')
            sleep(randint(2,10))
            a=0
            movies=[]
            while a<len(movie_div) and a<2: #Scrapes atmost 2 movies
                a+=1
                container = movie_div[a]
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

                #Scraping good reviews
                review_for_one_movie = {"good_reviews":[],"bad_reviews":[]}
                review_div = soup1.find_all('div' , class_="text show-more__control")
                for review in review_div[0:5]:
                    review_for_one_movie["good_reviews"].append(review.text)
                #Scraping bad reviews
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

                #Scraping platforms on which we can view the movie
                platform_for_one_movie = []
                where_to_watch = soup1.find_all('where-to-watch-meta')
                for place in where_to_watch:
                    platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
                    platform_for_one_movie.append(platform)

                #Scraping similar movies and tv shows
                similar_for_movie = []
                s1 = soup1.find_all("tiles-carousel-responsive-item")
                for elem in s1:
                    similar_for_movie.append(elem.find_all("span")[0].text)

                if len(soup1.find_all('div',class_="meta-value"))<3: #if this happens, original rotten tomatoes movie link was incorrect
                    sleep(randint(3,10))
                    #new movie url
                    rotten_tomato_url = "https://www.rottentomatoes.com/m/" + str(re.sub("[^a-z^0-9^_]","",name.lower().replace("-"," ").replace(" ","_")))
                    rotten_tomato_page = requests.Session().get(rotten_tomato_url)
                    soup1 = BeautifulSoup(rotten_tomato_page.text, 'html.parser')

                    #Scraping platforms on which we can view the movie
                    platform_for_one_movie = []
                    where_to_watch = soup1.find_all('where-to-watch-meta')
                    for place in where_to_watch:
                        platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
                        platform_for_one_movie.append(platform)

                    #Scraping similar movies and tv shows
                    similar_for_movie = []
                    s1 = soup1.find_all("tiles-carousel-responsive-item")
                    for elem in s1:
                        similar_for_movie.append(elem.find_all("span")[0].text)
                
                if len(soup1.find_all('div',class_="meta-value"))<3: #if it happens again, movie doesnt exist on rotten tomatoes
                    continue
                
                #Scraping the languages movie is available in
                language = soup1.find_all('div',class_="meta-value")[2]

                #Scraping the rotten tomatoes rating
                if len(re.findall("\"ratingValue\":\".*?\"",str(soup1)))==0:
                    rotten_tomato_rating = "-" #Movie not rated on rotten tomatoes
                else:
                    rotten_tomato_rating = int(re.findall("\"ratingValue\":\".*?\"",str(soup1))[0].replace('"ratingValue":',"").replace('"',''))

                #metacritic url

                sleep(randint(3,5))
                metacritic_url = "https://www.metacritic.com/movie/" + re.sub("[^a-z^0-9^-]","",str(name.lower().replace("-"," ").replace(" ","-")))
                user_agent = {'User-agent': 'Mozilla/5.0'}
                metacritic_page  = requests.get(metacritic_url,headers = user_agent)
                soup2 = BeautifulSoup(metacritic_page.text, 'html.parser')

                #Scraping the metascore
                if len(soup2.find_all('span', class_="metascore_w header_size movie positive"))==0:
                    metascore = "-" #Movie not rated on metacritic
                else:
                    metascore = soup2.find_all('span', class_="metascore_w header_size movie positive")[0]
                    metascore=metascore.text

                #Storing the movie in the database
                if len(MovieData.objects.filter(name=name))==0:
                    m = MovieData(name=name,site_link={"imdb":movieurl,"rotten_tomatoes":rotten_tomato_url,"metacritic":metacritic_url}
                    ,rating={"imdb":imdb,"rotten_tomatoes":rotten_tomato_rating,"metacritic":metascore},plot=plot
                    ,language=language.text.rstrip().split(", "),similar=similar_for_movie
                    ,year_of_release=year,duration=runtime,genre=genre.split(", "),cast=stars
                    ,reviews=review_for_one_movie,platform=platform_for_one_movie,image_url=imageurl)
                    m.save()
                    movies.append(m)

            b=0
            while b<len(movie_div) and b<2: #Scrapes atmost 2 movies
                b+=1
                container=movie_div[b]
                # Scraping the tv show's name
                name = container.h3.a.text
                
                # Scraping the tv show's year
                year = int(re.search("[0-9]+",container.h3.find('span', class_='lister-item-year').text).group(0))
                
                # Scraping the tv show's length
                runtime = int(re.search("[0-9]+",container.find('span', class_='runtime').text).group(0)) if container.p.find('span', class_='runtime') else 0

                # Scraping the tv show's genre
                genre = container.find('span', class_='genre').text.strip()

                # Scraping the IMDb rating
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

                #Scraping the good reviews
                review_for_one_movie = {"good_reviews":[],"bad_reviews":[]}
                review_div = soup1.find_all('div' , class_="text show-more__control")
                for review in review_div[0:5]:
                    review_for_one_movie["good_reviews"].append(review.text)
                #Scraping the bad reviews
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

                #Scraping platforms on which we can view the movie
                platform_for_one_movie = []
                where_to_watch = soup1.find_all('where-to-watch-meta')
                for place in where_to_watch:
                    platform = re.findall("\".*?\"", str(place))[0].replace('"',"")
                    platform_for_one_movie.append(platform)

                #Scraping similar movies and tv shows
                similar_for_movie = []
                s1 = soup1.find_all("tiles-carousel-responsive-item")
                for elem in s1:
                    similar_for_movie.append(elem.find_all("span")[0].text)

                #Scraping the tv show language
                language = ["English",]

                #Scraping the rotten tomatoes rating
                if len(re.findall("\"ratingValue\":\".*?\"",str(soup1)))==0:
                    rotten_tomato_rating = "-" #Tv show not yet rated on rotten tomatoes
                else:
                    rotten_tomato_rating = int(re.findall("\"ratingValue\":\".*?\"",str(soup1))[0].replace('"ratingValue":',"").replace('"',''))

                #metacritic url

                sleep(randint(3,5))
                metacritic_url = "https://www.metacritic.com/tv/" + re.sub("[^a-z^0-9^-]","",str(name.lower().replace("-"," ").replace(" ","-")))
                user_agent = {'User-agent': 'Mozilla/5.0'}
                metacritic_page  = requests.get(metacritic_url,headers = user_agent)
                soup2 = BeautifulSoup(metacritic_page.text, 'html.parser')

                #Scraping the metascore
                if len(soup2.find_all('span', class_="metascore_w header_size tvshow positive"))==0:
                    metascore = "-" #TV show not yet rated on metacritic
                else:
                    metascore = soup2.find_all('span', class_="metascore_w header_size tvshow positive")[0]
                    metascore=metascore.text

                #Stores the tv show in the database
                if len(MovieData.objects.filter(name=name))==0:
                    m = MovieData(name=name,site_link={"imdb":movieurl,"rotten_tomatoes":rotten_tomato_url,"metacritic":metacritic_url}
                    ,rating={"imdb":imdb,"rotten_tomatoes":rotten_tomato_rating,"metacritic":metascore},plot=plot
                    ,language=language,similar=similar_for_movie
                    ,year_of_release=year,duration=runtime,genre=genre.split(", "),cast=stars
                    ,reviews=review_for_one_movie,platform=platform_for_one_movie,image_url=imageurl)
                    m.save()
                    movies.append(m)
            if len(movies)>0: #Render search page displaying all search results
                return render(response,"webscraper/searchpage.html",{"list_of_movies":movies})
            else: #No search results returned
                return render(response, "webscraper/error.html")


def home(response):
    """Home page of the project, displays current top 10 movies,
    and the watched, liked, and watchlist movies and tv shows for the user.
    Also displays recommended movies based on the movies similar to the
    user's liked movies which havent been watched by user yet
    """

    #Initialized empty lists for each type, if not existing
    if not List.objects.filter(type="watched").exists():
        watched = List(type = "watched")
        watched.save()
    if not List.objects.filter(type="watchlist").exists():
        watchlist = List(type="watchlist")
        watchlist.save()
    if not List.objects.filter(type="liked").exists():
        liked = List(type="liked")
        liked.save()

    #Generate liked, watched, and watchlist lists of movies
    list = List.objects.get(type="watched").items_set.filter(user=response.user.id).order_by('-id')
    watched = [MovieData.objects.get(name=movie.text) for movie in list]
    list = List.objects.get(type="watchlist").items_set.filter(user=response.user.id).order_by('-id')
    watchlist = [MovieData.objects.get(name=movie.text) for movie in list]
    list = List.objects.get(type="liked").items_set.filter(user=response.user.id).order_by('-id')
    liked = [MovieData.objects.get(name=movie.text) for movie in list]
    top10 = MovieData.objects.all().order_by('-rating__imdb')[0:10]

    #Generate recommened movies based on movies similar to user's liked movies
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

    return render(response, "webscraper/index.html" #Renders home page
    , {"top10":top10, "recommended":recommended, "watched":watched, "watchlist":watchlist, "liked":liked, "lengthwl":len(watchlist), "lengthwtd":len(watched), "lenlik":len(liked), "lenrec":len(recommended)})
