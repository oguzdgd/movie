# api/views.py



import os
from lxml import etree
from django.http import HttpResponse
from django.conf import settings

import requests

from .models import Movie, WatchedMovie, Comment
from .serializers import MovieSerializer, UserRegisterSerializer, UserSerializer, WatchedMovieSerializer, CommentSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

# --- AUTH VIEWS ---

@api_view(['POST'])
@permission_classes([AllowAny]) # Herkes kayıt olabilir
def register_user_view(request):
    """Creates a new user and returns their info along with a token."""
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        # Yanıtta token'ı da ekleyelim
        response_data = {
            'user': UserSerializer(user).data,
            'token': token.key
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- MOVIE VIEWS ---

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny]) # GET için herkese izin ver
def movie_list_create_view(request):
    """Lists all movies or creates a new one."""
    if request.method == 'GET':
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Sadece adminler yeni film ekleyebilir
        if not request.user.is_staff:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AllowAny])
def movie_list_html_view(request):
    """
    Tüm filmlerin listesini XSLT ile HTML'e dönüştürerek sunar.
    """
    try:
        movies = Movie.objects.all()
        
        # 1. Tüm filmleri bir XML ağacına dönüştür
        root = etree.Element("movies")
        for movie_obj in movies:
            movie_element = etree.Element("movie", id=str(movie_obj.movie_id))
            etree.SubElement(movie_element, "title").text = movie_obj.title
            root.append(movie_element)
        

        html_result = apply_xslt_transform(root, 'movies_list_to_html.xsl')
        
        return HttpResponse(html_result, content_type='text/html')

    except Exception as e:
        return HttpResponse(f"<h1>An error occurred.</h1><p>{e}</p>", status=500)



@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny]) # GET için herkese izin ver
def movie_detail_view(request, movie_id):
    """Retrieve, update or delete a movie instance."""
    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == 'GET':
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    # PUT ve DELETE için yetki kontrolü
    if not request.user.is_staff:
        return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = MovieSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- WATCHEDLIST VIEW ---

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) # Sadece giriş yapmış kullanıcılar erişebilir
def watched_list_view(request):
    """Retrieve or update the user's watched list."""
    if request.method == 'GET':
        watched_items = WatchedMovie.objects.filter(user=request.user)
        serializer = WatchedMovieSerializer(watched_items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Serializer'a hem datayı hem de user'ı vermek için context kullanıyoruz

        
        serializer = WatchedMovieSerializer(data=request.data)

        if WatchedMovie.objects.filter(user=request.user).exists():
            return Response({'error': 'This movie is already in your list.'}, status=status.HTTP_409_CONFLICT)
        if serializer.is_valid():
            # movie ID'sinin veritabanında var olup olmadığını kontrol et
            get_object_or_404(Movie, pk=request.data.get('movie'))
            serializer.save(user=request.user) # `user` alanını otomatik olarak doldur
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- COMMENT VIEW ---

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def comment_list_create_view(request, movie_id):
    """List comments for a movie or create a new one."""
    movie = get_object_or_404(Movie, pk=movie_id)
    
    if request.method == 'GET':
        comments = Comment.objects.filter(movie=movie)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, movie=movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# XSLT İLE HTML SUNAN VIEW

# ÖNEMLİ: Bu view'lar DRF'nin Response nesnesini değil, Django'nun standart
# HttpResponse nesnesini kullandığı için, DRF'nin standart XML renderer'ından
# etkilenmezler. O yüzden ayrı tutmakta sorun yok.
# Ayrıca manuel XML oluşturma mantığını kullandıkları için movie_to_xml_etree
# gibi eski bir yardımcı fonksiyona ihtiyaç duyacaklar. 

def movie_to_xml_etree_for_xslt(movie_obj):
    """Sadece XSLT için XML etree Element'i oluşturur."""
    root = etree.Element("movie", id=str(movie_obj.movie_id))
    etree.SubElement(root, "title").text = movie_obj.title
    if movie_obj.year:
        etree.SubElement(root, "year").text = str(movie_obj.year)
    if movie_obj.director:
        etree.SubElement(root, "director").text = movie_obj.director
    
    # TODO: Genre ve Actors alanlarını da buraya ekleyin
    
    if movie_obj.plot:
        plot_el = etree.SubElement(root, "plot")
        plot_el.text = etree.CDATA(movie_obj.plot)
    if movie_obj.poster_url:
        etree.SubElement(root, "posterUrl").text = movie_obj.poster_url
    if movie_obj.rating is not None:
        etree.SubElement(root, "rating").text = str(movie_obj.rating)
    
    return root


def apply_xslt_transform(xml_tree, xslt_filename):
    """Yardımcı fonksiyon: XML ağacına belirtilen XSLT'yi uygular ve HTML string'i döner."""
    try:
        xslt_path = os.path.join(settings.BASE_DIR, 'xslt', xslt_filename)
        xslt_tree = etree.parse(xslt_path)
        transform = etree.XSLT(xslt_tree)
        html_tree = transform(xml_tree)
        return etree.tostring(html_tree, pretty_print=True).decode('utf-8')
    except Exception as e:
        # Hatanın ne olduğunu daha net görmek için
        print(f"XSLT Transformation Error: {e}")
        raise

@api_view(['GET'])
@permission_classes([AllowAny])
def movie_list_html_view(request):
    """
    Tüm filmlerin listesini XSLT ile HTML'e dönüştürerek sunar.
    """
    try:
        movies = Movie.objects.all()
        root = etree.Element("movies")
        for movie_obj in movies:
            movie_element = etree.Element("movie", id=str(movie_obj.movie_id))
            etree.SubElement(movie_element, "title").text = movie_obj.title
            root.append(movie_element)
        
        html_result = apply_xslt_transform(root, 'movies_list_to_html.xsl')
        return HttpResponse(html_result, content_type='text/html')
    except Exception as e:
        return HttpResponse(f"<h1>An error occurred.</h1><p>{e}</p>", status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def movie_detail_html_view(request, movie_id):
    """
    Bir filmin XML verisini XSLT ile HTML'e dönüştürür ve tarayıcıda gösterir.
    """
    try:
        movie_obj = get_object_or_404(Movie, pk=movie_id)
        # XSLT için özel olarak oluşturduğumuz XML oluşturma fonksiyonunu kullanalım
        xml_tree = movie_to_xml_etree_for_xslt(movie_obj)
        html_result = apply_xslt_transform(xml_tree, 'movie_to_html.xsl')
        return HttpResponse(html_result, content_type='text/html')
    except Exception as e:
        return HttpResponse(f"<h1>An error occurred.</h1><p>{e}</p>", status=500)
    


#  TMDB IMPORT VIEW


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser]) # Sadece adminler film içe aktarabilsin
def import_movie_from_tmdb_view(request):
    """
    TMDB'den bir film arar ve veritabanına aktarır.
    İstek XML'i: <importRequest><title>Inception</title></importRequest>
    """
    # DRF'ye uygun hata yanıtı için kendi error_xml_response'umuzu kullanmayalım,
    # doğrudan Response nesnesi ile hata dönelim.
    if request.content_type != 'application/xml':
        return Response({'error': 'Content-Type must be application/xml'}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    
    try:
        xml_doc = etree.fromstring(request.body)
        movie_title_to_search = xml_doc.findtext('title')
        if not movie_title_to_search:
            return Response({'error': "A 'title' element is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. TMDB API'ye istek atma
        tmdb_api_key = settings.TMDB_API_KEY
        if not tmdb_api_key:
            return Response({'error': 'TMDB API key is not configured on the server.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={movie_title_to_search}"
        
        response = requests.get(search_url)
        response.raise_for_status() # Hata varsa exception fırlatır
        
        search_results = response.json()
        
        if not search_results.get('results'):
            return Response({'error': f"No movie found on TMDB with the title '{movie_title_to_search}'."}, status=status.HTTP_404_NOT_FOUND)
        
        tmdb_movie = search_results['results'][0]
        
        # ... (veri aktarma ve kaydetme mantığı aynı) ...
        tmdb_id = tmdb_movie.get('id')
        
        if Movie.objects.filter(movie_id=f"tmdb_{tmdb_id}").exists():
             return Response({'error': f"Movie '{tmdb_movie.get('title')}' already exists in the database."}, status=status.HTTP_409_CONFLICT)

        new_movie_id = f"tmdb_{tmdb_id}"
        new_movie = Movie.objects.create(
            movie_id=new_movie_id,
            title=tmdb_movie.get('title'),
            year=int(tmdb_movie.get('release_date', '0-0-0').split('-')[0]) if tmdb_movie.get('release_date') else None,
            plot=tmdb_movie.get('overview'),
            poster_url=f"https://image.tmdb.org/t/p/w500{tmdb_movie.get('poster_path')}" if tmdb_movie.get('poster_path') else None,
            rating=tmdb_movie.get('vote_average')
        )

        # Oluşturulan nesneyi MovieSerializer ile XML'e dönüştürerek döndür
        serializer = MovieSerializer(new_movie)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except requests.exceptions.HTTPError as e:
        return Response({'error': f"Error communicating with TMDB API: {e}"}, status=status.HTTP_502_BAD_GATEWAY)
    except requests.exceptions.RequestException as e:
        return Response({'error': f"A network error occurred: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except etree.XMLSyntaxError:
        return Response({'error': 'Invalid XML syntax.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)