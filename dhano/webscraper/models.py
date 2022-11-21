from unittest.util import _MAX_LENGTH
from django.db import models

class MovieData(models.Model):
    name = models.CharField(max_length=80)
    site_link = models.CharField(max_length=200)
    
    rating = models.FloatField()
    plot = models.CharField(max_length=1000)
    language = models.JSONField()
    similar = models.JSONField()
    year_of_release = models.IntegerField()
    duration = models.IntegerField()
    genre = models.JSONField()
    cast = models.JSONField()
    reviews = models.JSONField()
    platform = models.JSONField()

    def __str__(self):
        return self.name