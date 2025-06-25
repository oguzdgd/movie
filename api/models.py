from django.db import models
from django.contrib.auth.models import User

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


class WatchedMovie(models.Model):
    # Bu model, bir User ile bir Movie arasında bir bağlantı kurar.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watched_list')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watched_by_users')
    watched_date = models.DateField(auto_now_add=True) # Eklendiği tarihi otomatik olarak kaydeder
    user_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True) 
    
    class Meta:
        # Bir kullanıcının aynı filmi listesine birden fazla kez eklemesini engelle
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} watched {self.movie.title}"