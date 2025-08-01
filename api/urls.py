from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


app_name = 'api' 

urlpatterns = [

    # --- Authentication Endpoints ---
    path('auth/register/', views.register_user_view, name='register-user'), # kullanıcı kayıt endpointi
    path('auth/login/', obtain_auth_token, name='api-token-auth'), # kullanıcı giriş endpointi


    # Bir kullanıcının izlenenler listesini yönetmek için
    path('watchedlist/', views.watched_list_view, name='watched-list'),
    #  URL'yi /users/{user_id}/watchedlist/ gibi yapmak yerine /watchedlist/ yapıyoruz çünkü kimin istek attığını zaten request.user'dan (token sayesinde) bileceğiz. Bu daha güvenli ve RESTful bir yaklaşımdır.

    # XSLT dönüşümü için HTML sayfası sunan URL
    path('html/movies/<str:movie_id>/', views.movie_detail_html_view, name='movie-detail-html'),
    path('html/movies/', views.movie_list_html_view, name='movie-list-html'),

    # --- Movie  Endpoints (XML API) ---
    # Bir filme ait yorumları listelemek ve yeni yorum eklemek için
    path('movies/<str:movie_id>/comments/', views.comment_list_create_view, name='comment-list-create'),
    # Filmleri listelemek ve yeni film eklemek için (POST)
    path('movies/', views.movie_list_create_view, name='movie-list-create'),
    # Belirli bir filmi getirmek( GET), güncellemek (PUT), silmek (DELETE) için
    path('movies/<str:movie_id>/', views.movie_detail_view, name='movie-detail'),


    # TMDB'den film içe aktarmak için
    path('import/movie/', views.import_movie_from_tmdb_view, name='import-movie'),
]

    


