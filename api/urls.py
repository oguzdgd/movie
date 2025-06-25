from django.urls import path
from . import views


app_name = 'api' 

urlpatterns = [
    # Filmleri listelemek ve yeni film eklemek için (POST)
    path('movies/', views.movie_list_create_view, name='movie-list-create'),
    
    # Belirli bir filmi getirmek, güncellemek (PUT), silmek (DELETE) için
    path('movies/<str:movie_id>/', views.movie_detail_view, name='movie-detail'),
    
]

