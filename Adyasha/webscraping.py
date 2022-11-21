from requests import Session
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import sys


with Session() as s:
   
    site = s.get("https://www.imdb.com/title/")
    bs_content = bs(site.content, "html.parser")
    print(bs_content.prettify())
    content = bs_content.find_all("script",type="application/ld+json")
    print(content)
    x = re.findall("{.*}", str(content))
    print(x)
    items = x[0].split(",")
    res = {}
    count = 0
    res["cast"] = []
    for i in range (len(items)):
        # print(item)
        if '"image"' in items[i]:
            res["image"] = items[i].split("\":\"")[1].replace('"',"")
        if '"dateCreated"' in items[i]:
            res["year of release"] = items[i].split("\":\"")[1].split("-")[0]
        if '"genre"' in items[i]:
            res["genre"] = []
            res["genre"].append(items[i].split("\":[")[1].replace('"',""))
            while("]" not in items[i]):
                i = i+1
                if("]" in items[i]):
                    res["genre"].append(items[i].replace('"',"").replace("]",""))
                else:
                    res["genre"].append(items[i].replace('"',""))
        if '"name"' in items[i] and '"url"' in items[i-1]:
            if(count == 0):
                res["Movie"] = items[i].split("\":\"")[1].replace('"',"")
                items[i] = ""
                count = 1
            else:
                res["cast"].append(items[i].split("\":\"")[1].replace("}","").replace('"',"").replace("]",""))
        if '"ratingValue"' in items[i]:
            res["rating"]  = items[i].split("\":")[1].replace("}","")
        if '"description"' in items[i]:
            res["plot"] = items[i].split("\":\"")[1].replace('"',"")

    for i in res:        
        print(i,":",res[i])
        # parameter.append(item.split("\":\"")[0])
        # value.append(item.split(":")[0])
        # print(item.split(":"))
    # res = dict(map(lambda i,j : (i,j) , parameter,value))
    # print(res)
          


# list.append(items)
 
# printing movie details with its rating.
# for movie in list:
#     print(movie['place'], '-', movie['movie_title'], '('+movie['year'] +
#         ') -', 'Starring:', movie['star_cast'], movie['rating'])
 
 
# ##.......##
# df = pd.DataFrame(list)
# df.to_csv('imdb_top_250_movies.csv',index=False)
