from unittest.util import _MAX_LENGTH
from django.db import models

class MovieData(models.Model):
    name = models.CharField(max_length=80)
    site_link = models.CharField(max_length=200)
    duration = models.IntegerField()
    rating = models.IntegerField()
    summary = models.CharField(max_length=1000)

    def __str__(self):
        return self.name