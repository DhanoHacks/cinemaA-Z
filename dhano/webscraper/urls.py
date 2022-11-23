from django.urls import path
from . import views

urlpatterns = [
    path("<int:id>", views.index, name="index"),
    path("search/", views.search_results_view, name="search_results"),
    path("save", views.save, name="save"),
    path("home/", views.home, name="home"),
    path("", views.temp, name="temp"),
    path("<int:id>", views.watched, name="addingWatched")
]
