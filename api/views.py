from django.http import HttpResponse, JsonResponse, Http404, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt 
from django.shortcuts import get_object_or_404
from .models import Movie
from lxml import etree
import os
from django.conf import settings

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


@csrf_exempt
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
        if request.content_type != 'application/xml':
            return error_xml_response("Content-Type must be application/xml", status_code=415)
        
        is_valid_xml, error_msg, xml_doc = validate_xml_with_xsd(request.body, MOVIE_SCHEMA_PATH)
        if not is_valid_xml:
            return error_xml_response(error_msg, status_code=400)

        try:
            # DOĞRU YOL: xml_doc zaten kök elemanıdır.
            # YANLIŞ: movie_id = xml_doc.getroot().get('id') 
            movie_id = xml_doc.get('id') # .getroot() kaldırıldı.

            # Diğer alanlar için de aynı şekilde .getroot() olmadan devam edin.
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

@csrf_exempt
def movie_detail_view(request, movie_id):
    """
    GET: Belirli bir filmin detaylarını XML olarak döner.
    PUT: Belirli bir filmi günceller (gelen XML verisi ile).
    DELETE: Belirli bir filmi siler.
    """
    movie_obj = get_object_or_404(Movie, pk=movie_id) # pk=movie_id doğru olmalı (modeldeki primary key)

    if request.method == 'GET':
        return xml_response(movie_to_xml_etree(movie_obj))

    elif request.method == 'PUT':
        if request.content_type != 'application/xml':
            return error_xml_response("Content-Type must be application/xml", status_code=415)

        is_valid_xml, error_msg, xml_doc = validate_xml_with_xsd(request.body, MOVIE_SCHEMA_PATH)
        if not is_valid_xml:
            return error_xml_response(error_msg, status_code=400)
        
        try:
            # XML'den güncellenecek verileri al
            # Sadece gönderilen alanları güncellemek daha iyi olabilir (PATCH mantığı)
            # ama PUT genellikle tüm kaynağı değiştirmeyi hedefler.
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
            return xml_response(success_xml, status_code=204) # No Content
        except Exception as e:
            return error_xml_response(f"Error deleting movie: {str(e)}", status_code=500)

    return error_xml_response("Method Not Allowed", status_code=405)