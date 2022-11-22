from django.shortcuts import render
from django.http import HttpResponse
from .models import MovieData

def index(response):
    m = MovieData.objects.get(id=1)
    return render(response, "webscraper/movie.html", {"m":m})