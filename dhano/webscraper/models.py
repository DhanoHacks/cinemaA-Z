from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User

class MovieData(models.Model):
    """Class for storing movies inside the database

    Functions and methods:
        - ``__str__``
    
    :param name: Name of the movie
    :type name: models.CharField()
    :param site_link: Links to IMDb, Rotten Tomatoes, and Metacritic pages of the movie
    :type site_link: models.JSONField()
    :param rating: Ratings on  IMDb, Rotten Tomatoes, and Metacritic for the movie
    :type rating: models.JSONField()
    :param plot: Short description of the movie plot
    :type plot: models.CharField()
    :param language: Languages the movie is available in
    :type language: models.JSONField()
    :param similar: Movies similar to this one
    :type similar: models.JSONField()
    :param year_of_release: Year of release of the movie
    :type year_of_release: models.IntegerField()
    :param duration: Duration in minutes of the movie
    :type duration: models.InegerField()
    :param genre: Genres in which the movie belongs
    :type genre: models.JSONField()
    :param cast: Cast of the movie
    :type cast: models.JSONField()
    :param reviews: Reviews (5 good and 5 bad) for the movie
    :type reviews: models.JSONField()
    :param platform: Platforms on which user can watch the movie
    :type platform: models.JSONField()
    :param image_url: Link to movie poster
    :type image_url: models.CharField()
    """
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
        """String conversion method

        :return: Name of the movie
        :rtype: str
        """
        return self.name
class List(models.Model):
    """Class for storing three types of lists (watched, watchlist, liked) for every user
    
    Functions and methods:
        - ``__str__``

    :param type: Type of content which the list stores, can be watched, watchlist, liked
    :type type: models.CharField()
    """
    type = models.CharField(max_length=20)

    def __str__(self):
        """String conversion method

        :return: Type of content stored in list
        :rtype: str
        """
        return  self.type

class Items(models.Model):
    """Class for storing a single movie in a single List for a single User

    Functions and methods:
        - ``__str__``

    :param list: List of which this item is a part of
    :type list: models.ForeignKey(List)
    :param user: User in whose list this movie exists
    :type user: models.ForeignKey(User)
    :param text: Text storing name of the movie corresponding to this object
    :type text: models.CharField()
    """
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    text = models.CharField(max_length=200)
    
    def __str__(self):
        """String conversion method

        :return: Name of the movie corresponding to this object
        :rtype: str
        """
        return self.text
