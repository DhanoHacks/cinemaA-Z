"""URLs and their corresponding views stored here
"""

from django.urls import path
from . import views

urlpatterns = [
    path("<int:id>", views.index, name="index"),
    path("search/", views.search_page_view, name="search_page"),
    path("save-movies", views.save_movies, name="save-movies"),
    path("save-tvshows", views.save_tvshows, name="save-tvshows"),
    path("home/", views.home, name="home"),
    path("", views.temp, name="temp"),
]
