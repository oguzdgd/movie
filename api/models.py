from django.db import models

class Movie(models.Model):
    movie_id = models.CharField(max_length=50, unique=True, primary_key=True) 
    title = models.CharField(max_length=255)
    year = models.IntegerField(null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    plot = models.TextField(null=True, blank=True)
    poster_url = models.URLField(max_length=500, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return self.title
