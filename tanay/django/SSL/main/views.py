from django.shortcuts import render
from django.http import HttpResponse
from .models import ToDoList, Item

# Create your views here.

def index(response, id):
    my_dict = {}#To be used instead pf name:ls.name for multiple variables mainly
    ls = ToDoList.objects.get(id = id)
    return render(response, "main/base.html", {"name":ls.name})

def home(response):
    return render(response, "main/home.html", {"name":"test"})