from django.http import HttpResponse, JsonResponse, Http404, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt 
from django.shortcuts import get_object_or_404
from .models import Movie
from lxml import etree
import os

from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from .models import WatchedMovie , Comment

MOVIE_SCHEMA_PATH = os.path.join(settings.BASE_DIR, 'schemas', 'movie_schema.xsd')

# --- XML Yardımcı Fonksiyonları ---
def validate_xml_with_xsd(xml_string_bytes, xsd_path):
    """Gelen XML byte string'ini XSD'ye göre doğrular."""
    try:
        xsd_doc = etree.parse(xsd_path)
        xmlschema = etree.XMLSchema(xsd_doc)
        xml_doc_to_validate = etree.fromstring(xml_string_bytes) 
        xmlschema.assertValid(xml_doc_to_validate)
        return True, None, xml_doc_to_validate 
    except etree.DocumentInvalid as e:
        return False, f"XML does not conform to XSD: {str(e)}", None
    except etree.XMLSyntaxError as e:
        return False, f"Invalid XML syntax: {str(e)}", None
    except Exception as e:
        return False, f"An unexpected error occurred during XSD validation: {str(e)}", None

def movie_to_xml_etree(movie_obj):
    """Django Movie nesnesini lxml etree Element'ine dönüştürür."""
    root = etree.Element("movie", id=str(movie_obj.movie_id)) # movie_id modelde CharField
    etree.SubElement(root, "title").text = movie_obj.title
    if movie_obj.year:
        etree.SubElement(root, "year").text = str(movie_obj.year)
    if movie_obj.director:
        etree.SubElement(root, "director").text = movie_obj.director
    

    if movie_obj.plot:
        plot_el = etree.SubElement(root, "plot")
        plot_el.text = etree.CDATA(movie_obj.plot)
    if movie_obj.poster_url:
        etree.SubElement(root, "posterUrl").text = movie_obj.poster_url
    if movie_obj.rating is not None: # None kontrolü önemli
        etree.SubElement(root, "rating").text = str(movie_obj.rating)
    
  
    return root

def xml_response(element_tree, status_code=200):
    """lxml etree Element'ini Django HttpResponse'a dönüştürür."""
    xml_string = etree.tostring(element_tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    return HttpResponse(xml_string, content_type='application/xml', status=status_code)

def error_xml_response(message, status_code=400):
    """Hata mesajı için XML HttpResponse oluşturur."""
    root = etree.Element("error")
    etree.SubElement(root, "message").text = message
    return xml_response(root, status_code=status_code)


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication]) 
def movie_list_create_view(request):
    """
    GET: Tüm filmlerin listesini XML olarak döner.
    POST: Yeni bir film oluşturur (gelen XML verisi ile).
    """
    if request.method == 'GET':
        movies = Movie.objects.all()
        root = etree.Element("movies")
        for movie_obj in movies:
            movie_element = etree.Element("movie", id=str(movie_obj.movie_id))
            etree.SubElement(movie_element, "title").text = movie_obj.title
            root.append(movie_element)
        return xml_response(root)

    elif request.method == 'POST':
        if not request.user.is_staff: # is_staff veya is_superuser kontrolü
            return error_xml_response("You do not have permission to perform this action.", status_code=403)
        
        is_valid_xml, error_msg, xml_doc = validate_xml_with_xsd(request.body, MOVIE_SCHEMA_PATH)
        if not is_valid_xml:
            return error_xml_response(error_msg, status_code=400)

        try:
            movie_id = xml_doc.get('id') 
            title = xml_doc.findtext('title')
            year_str = xml_doc.findtext('year')
            year = int(year_str) if year_str and year_str.isdigit() else None
            director=xml_doc.findtext('director')
            plot=xml_doc.findtext('plot')
            poster_url=xml_doc.findtext('posterUrl')
            rating_str = xml_doc.findtext('rating')
            rating = float(rating_str) if rating_str else None
            
            if not movie_id or not title:
                return error_xml_response("Movie ID and Title are required.", status_code=400)

            if Movie.objects.filter(movie_id=movie_id).exists():
                return error_xml_response(f"Movie with id {movie_id} already exists.", status_code=409)

            movie_obj = Movie.objects.create(
                movie_id=movie_id,
                title=title,
                year=year,
                director=director,
                plot=plot,
                poster_url=poster_url,
                rating=rating
            )
            return xml_response(movie_to_xml_etree(movie_obj), status_code=201)
        except Exception as e:
            return error_xml_response(f"Error processing XML data: {str(e)}", status_code=500)
    
    return error_xml_response("Method Not Allowed", status_code=405)


@api_view(['GET', 'PUT', 'DELETE']) # 1. Hangi HTTP metodlarına izin verileceğini belirt
# 2. Kimlik doğrulama ve yetkilendirme sınıflarını tanımla
@authentication_classes([TokenAuthentication]) 
# @permission_classes([IsAuthenticated]) # Şimdilik bunu daha esnek yapalım
def movie_detail_view(request, movie_id):
    """
    GET: Herkes erişebilir.
    PUT/DELETE: Sadece admin yetkisine sahip (is_staff=True) kullanıcılar erişebilir.
    """
    # get_object_or_404 Django'nun standart bir aracıdır, DRF ile de uyumlu çalışır
    movie_obj = get_object_or_404(Movie, pk=movie_id)

    # --- GET İsteği ---
    # Herkesin film detayını görmesine izin verelim.
    if request.method == 'GET':
        return xml_response(movie_to_xml_etree(movie_obj))

    # --- PUT veya DELETE İstekleri (Kimlik Doğrulama ve Yetkilendirme Gerekli) ---
    
    # 3. İsteği yapan kullanıcının kimliğini kontrol et
    if not request.user.is_authenticated:
        return error_xml_response("Authentication credentials were not provided.", status_code=401) # Unauthorized

    # 4. İsteği yapan kullanıcının yetkisini (rolünü) kontrol et
    if not request.user.is_staff: # Django'da admin kullanıcıları 'staff' olarak işaretlenir
        return error_xml_response("You do not have permission to perform this action.", status_code=403) # Forbidden
    

    # Eğer kullanıcı kimliğini ve yetkisini geçtiyse, işlemlere devam et:
    if request.method == 'PUT':
        if request.content_type != 'application/xml':
            return error_xml_response("Content-Type must be application/xml", status_code=415)

        is_valid_xml, error_msg, xml_doc = validate_xml_with_xsd(request.body, MOVIE_SCHEMA_PATH)
        if not is_valid_xml:
            return error_xml_response(error_msg, status_code=400)
        
        try:
            # XML'den güncellenecek verileri al
            movie_obj.title = xml_doc.findtext('title', default=movie_obj.title)
            year_str = xml_doc.findtext('year')
            movie_obj.year = int(year_str) if year_str and year_str.isdigit() else movie_obj.year
            # ... diğer alanları da güncelle ...
            movie_obj.save()
            return xml_response(movie_to_xml_etree(movie_obj))
        except Exception as e:
            return error_xml_response(f"Error updating movie data: {str(e)}", status_code=500)

    elif request.method == 'DELETE':
        try:
            movie_obj.delete()
            success_xml = etree.Element("success")
            etree.SubElement(success_xml, "message").text = f"Movie with id {movie_id} deleted successfully."
            # DELETE başarılı olduğunda genellikle boş bir yanıt (204) döndürülür.
            # İstemcinin bir mesaja ihtiyacı varsa 200 OK ile de döndürülebilir.
            return xml_response(success_xml, status_code=200) 
        except Exception as e:
            return error_xml_response(f"Error deleting movie: {str(e)}", status_code=500)


# Helper fonksiyonu: Kullanıcı nesnesini XML'e dönüştür
def user_to_xml_etree(user_obj):
    root = etree.Element("user", id=str(user_obj.id))
    etree.SubElement(root, "username").text = user_obj.username
    etree.SubElement(root, "email").text = user_obj.email
    etree.SubElement(root, "first_name").text = user_obj.first_name
    etree.SubElement(root, "last_name").text = user_obj.last_name
    return root

@csrf_exempt
def register_user_view(request):
    """
    POST: Yeni bir kullanıcı oluşturur (XML ile).
    """
    if request.method == 'POST':
        if request.content_type != 'application/xml':
            return error_xml_response("Content-Type must be application/xml", status_code=415)
        
        try:
            # Gelen XML'i ayrıştır
            xml_doc = etree.fromstring(request.body)
            
            # Gerekli alanları al (basit XSD veya manuel kontrol yapılabilir)
            username = xml_doc.findtext('username')
            email = xml_doc.findtext('email')
            password = xml_doc.findtext('password')

            if not username or not password or not email:
                return error_xml_response("Username, email, and password are required.", status_code=400)

            # Kullanıcı adının veya e-postanın zaten var olup olmadığını kontrol et
            if User.objects.filter(username=username).exists():
                return error_xml_response(f"Username '{username}' already exists.", status_code=409)
            if User.objects.filter(email=email).exists():
                return error_xml_response(f"Email '{email}' already exists.", status_code=409)

            # Yeni kullanıcıyı oluştur
            new_user = User.objects.create_user(username=username, email=email, password=password)
            
            # Kullanıcı için bir token oluştur
            token, created = Token.objects.get_or_create(user=new_user)
            
            # Başarılı yanıtı oluştur
            response_root = user_to_xml_etree(new_user)
            etree.SubElement(response_root, "message").text = "User created successfully."
            etree.SubElement(response_root, "token").text = token.key

            return xml_response(response_root, status_code=201)
        
        except etree.XMLSyntaxError:
            return error_xml_response("Invalid XML syntax.", status_code=400)
        except Exception as e:
            return error_xml_response(f"An unexpected error occurred: {str(e)}", status_code=500)
    
    return error_xml_response("Method Not Allowed", status_code=405)


# WATCHED MOVİE

def watched_movie_to_xml_etree(watched_movie_obj):
    """WatchedMovie nesnesini XML'e dönüştürür."""
    root = etree.Element("watchedMovie", movieId=str(watched_movie_obj.movie.movie_id))
    etree.SubElement(root, "title").text = watched_movie_obj.movie.title
    etree.SubElement(root, "watchedDate").text = str(watched_movie_obj.watched_date)
    if watched_movie_obj.user_rating:
        etree.SubElement(root, "userRating").text = str(watched_movie_obj.user_rating)
    return root

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) # Bu endpoint'e sadece giriş yapmış kullanıcılar erişebilir
def watched_list_view(request):
    """
    GET: Giriş yapmış kullanıcının izlenenler listesini döner.
    POST: Giriş yapmış kullanıcının izlenenler listesine yeni bir film ekler.
    """
    user = request.user 

    if request.method == 'GET':
        watched_movies = WatchedMovie.objects.filter(user=user).select_related('movie')
        root = etree.Element("watchedList", user=user.username)
        for item in watched_movies:
            root.append(watched_movie_to_xml_etree(item))
        return xml_response(root)

    elif request.method == 'POST':
        if request.content_type != 'application/xml':
            return error_xml_response("Content-Type must be application/xml", status_code=415)
        
        try:
            xml_doc = etree.fromstring(request.body)
            movie_id = xml_doc.findtext('movieId')
            user_rating_str = xml_doc.findtext('userRating')

            if not movie_id:
                return error_xml_response("movieId is required in the XML body.", status_code=400)
            
            # İlgili filmi veritabanından bul
            movie_to_add = get_object_or_404(Movie, pk=movie_id)
            
            # Zaten listede var mı kontrolü (modeldeki unique_together bunu zaten yapar ama ön kontrol iyi)
            if WatchedMovie.objects.filter(user=user, movie=movie_to_add).exists():
                return error_xml_response("This movie is already in your watched list.", status_code=409)

            # Yeni WatchedMovie nesnesi oluştur
            new_watched_item = WatchedMovie.objects.create(
                user=user,
                movie=movie_to_add,
                user_rating=float(user_rating_str) if user_rating_str else None
            )
            
            return xml_response(watched_movie_to_xml_etree(new_watched_item), status_code=201)

        except etree.XMLSyntaxError:
            return error_xml_response("Invalid XML syntax.", status_code=400)
        except Movie.DoesNotExist:
            return error_xml_response(f"Movie with id '{movie_id}' not found.", status_code=404)
        except Exception as e:
            # Veritabanı unique constraint hatasını yakalamak için
            if 'UNIQUE constraint' in str(e):
                 return error_xml_response("This movie is already in your watched list.", status_code=409)
            return error_xml_response(f"An error occurred: {str(e)}", status_code=500)
        

#XSLT  / HTML VİEWS

@api_view(['GET'])
@permission_classes([AllowAny]) # Herkesin HTML sayfasını görmesine izin ver
def movie_detail_html_view(request, movie_id):
    """
    Bir filmin XML verisini XSLT ile HTML'e dönüştürür ve tarayıcıda gösterir.
    """
    # 1. Veritabanından ilgili filmi al
    movie_obj = get_object_or_404(Movie, pk=movie_id)
    
    # 2. Film nesnesini XML etree'ye dönüştür
    xml_tree = movie_to_xml_etree(movie_obj)

    try:
        # 3. XSLT dosyasını yükle
        xslt_path = os.path.join(settings.BASE_DIR, 'xslt', 'movie_to_html.xsl')
        xslt_tree = etree.parse(xslt_path)
        transform = etree.XSLT(xslt_tree)
        
        # 4. XML verisine XSLT dönüşümünü uygula
        html_tree = transform(xml_tree)
        
        # 5. Sonucu HTML string'ine dönüştür
        html_result = etree.tostring(html_tree, pretty_print=True).decode('utf-8')
        
        # 6. HTML yanıtı olarak döndür
        return HttpResponse(html_result, content_type='text/html')

    except Exception as e:
        # Hata durumunda basit bir metin hatası döndür
        return HttpResponse(f"<h1>An error occurred during XSLT transformation.</h1><p>{e}</p>", status=500, content_type='text/html')
    


# YORUM 
def comment_to_xml_etree(comment_obj):
    """Comment nesnesini XML'e dönüştürür."""
    root = etree.Element("comment", id=str(comment_obj.id))
    etree.SubElement(root, "movieId").text = str(comment_obj.movie.movie_id)
    
    author_element = etree.SubElement(root, "author")
    author_element.set("id", str(comment_obj.author.id))
    author_element.text = comment_obj.author.username
    
    body_element = etree.SubElement(root, "body")
    body_element.text = etree.CDATA(comment_obj.body) # Yorum metni için CDATA önemli
    
    etree.SubElement(root, "createdAt").text = comment_obj.created_at.isoformat()
    return root


# --- API Görünümleri ---

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) # POST için kimlik doğrulaması gerekecek
def comment_list_create_view(request, movie_id):
    """
    GET: Belirli bir filme ait yorumları listeler. (Herkes erişebilir)
    POST: Belirli bir filme yeni bir yorum ekler. (Sadece giriş yapmış kullanıcılar)
    """
    # Yorumların ait olacağı filmi bul
    movie_obj = get_object_or_404(Movie, pk=movie_id)

    if request.method == 'GET':
        # @permission_classes'ı [AllowAny] yapmadığımız için GET de korumalı olacak.
        # GET'in herkese açık olmasını istiyorsak, izin kontrolünü view içinde yapmalıyız.
        # Şimdilik GET'in de korumalı kalması sorun değil.
        
        comments = movie_obj.comments.all().select_related('author') # Veritabanı sorgusunu optimize et
        root = etree.Element("comments", movieId=movie_id, movieTitle=movie_obj.title)
        
        for comment in comments:
            root.append(comment_to_xml_etree(comment))
        
        return xml_response(root)

    elif request.method == 'POST':
        # @permission_classes([IsAuthenticated]) sayesinde bu bloğa sadece
        # giriş yapmış kullanıcılar erişebilir.
        user = request.user
        
        if request.content_type != 'application/xml':
            return error_xml_response("Content-Type must be application/xml", status_code=415)
        
        try:
            xml_doc = etree.fromstring(request.body)
            comment_body = xml_doc.findtext('body')

            if not comment_body or not comment_body.strip():
                return error_xml_response("Comment body cannot be empty.", status_code=400)

            # Yeni yorumu oluştur
            new_comment = Comment.objects.create(
                movie=movie_obj,
                author=user,
                body=comment_body
            )

            # Başarılı yanıtı oluşturulan yorumun XML'i ile dön
            return xml_response(comment_to_xml_etree(new_comment), status_code=201)

        except etree.XMLSyntaxError:
            return error_xml_response("Invalid XML syntax.", status_code=400)
        except Exception as e:
            return error_xml_response(f"An error occurred: {str(e)}", status_code=500)
    
