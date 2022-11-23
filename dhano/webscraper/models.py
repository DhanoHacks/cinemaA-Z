from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User

class MovieData(models.Model):
    name = models.CharField(max_length=80)
    site_link = models.JSONField()
    
    rating = models.JSONField()
    plot = models.CharField(max_length=1000)
    language = models.JSONField()
    similar = models.JSONField()
    year_of_release = models.IntegerField()
    duration = models.IntegerField()
    genre = models.JSONField()
    cast = models.JSONField()
    reviews = models.JSONField()
    platform = models.JSONField()
    image_url = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

class List(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20)

    def __str__(self):
        return  self.name

class Items(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    
    def __str__(self):
        return self.text
