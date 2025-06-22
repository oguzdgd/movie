import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from lxml import etree
from api.models import Movie

class Command(BaseCommand):
    help = 'Loads movies from XML files in data/movies/ into the database, validating against XSD.'

    def handle(self, *args, **options):
        movies_data_path = os.path.join(settings.BASE_DIR, 'data', 'movies')
        schema_path = os.path.join(settings.BASE_DIR, 'schemas', 'movie_schema.xsd')

        if not os.path.exists(movies_data_path):
            raise CommandError(f"Movies data path does not exist: {movies_data_path}")
        if not os.path.exists(schema_path):
            raise CommandError(f"Movie XSD schema path does not exist: {schema_path}")

        try:
            xsd_doc = etree.parse(schema_path)
            xmlschema = etree.XMLSchema(xsd_doc)
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded XSD schema from {schema_path}"))
        except Exception as e:
            raise CommandError(f"Failed to parse XSD schema: {e}")

        loaded_count = 0
        updated_count = 0
        error_count = 0

        for filename in os.listdir(movies_data_path):
            if filename.endswith(".xml"):
                file_path = os.path.join(movies_data_path, filename)
                self.stdout.write(f"Processing file: {filename}...")
                try:
                    xml_doc = etree.parse(file_path)
                    # XSD ile doğrulama
                    xmlschema.assertValid(xml_doc) 
                    self.stdout.write(self.style.SUCCESS(f"  > XML is valid according to XSD."))

                    # Veriyi çekme
                    movie_id = xml_doc.getroot().get('id')
                    title = xml_doc.findtext('title')
                    year_str = xml_doc.findtext('year')
                    year = int(year_str) if year_str else None
                    director = xml_doc.findtext('director')
                    plot = xml_doc.findtext('plot') 
                    poster_url = xml_doc.findtext('posterUrl')
                    rating_str = xml_doc.findtext('rating')
                    rating = float(rating_str) if rating_str else None
                    
                 
                    genres_list = [genre.text for genre in xml_doc.xpath('//genres/genre')]
                    actors_list = [actor.text for actor in xml_doc.xpath('//actors/actor')]
                    
                    # Django modeline kaydetme veya güncelleme
                    movie_obj, created = Movie.objects.update_or_create(
                        movie_id=movie_id,
                        defaults={
                            'title': title,
                            'year': year,
                            'director': director,
                            'plot': plot,
                            'poster_url': poster_url,
                            'rating': rating,
                        }
                    )

                    if created:
                        loaded_count += 1
                        self.stdout.write(self.style.SUCCESS(f"  > Movie '{title}' created in database."))
                    else:
                        updated_count += 1
                        self.stdout.write(self.style.WARNING(f"  > Movie '{title}' updated in database."))

                except etree.DocumentInvalid as e:
                    self.stderr.write(self.style.ERROR(f"  > XML validation error in {filename}: {e}"))
                    error_count += 1
                except etree.XMLSyntaxError as e:
                    self.stderr.write(self.style.ERROR(f"  > XML syntax error in {filename}: {e}"))
                    error_count += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"  > An error occurred processing {filename}: {e}"))
                    error_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"\nFinished processing. Loaded: {loaded_count}, Updated: {updated_count}, Errors: {error_count}"))