import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from lxml import etree
from api.models import Movie 

class Command(BaseCommand):
    help = 'Loads movies from XML files in data/movies/ into the database, validating against XSD.'

    def handle(self, *args, **options):
        # Dosya yollarını settings.py'deki BASE_DIR'e göre dinamik olarak al
        movies_data_path = os.path.join(settings.BASE_DIR, 'data', 'movies')
        schema_path = os.path.join(settings.BASE_DIR, 'schemas', 'movie_schema.xsd')

        # Yolların var olup olmadığını kontrol et
        if not os.path.isdir(movies_data_path):
            raise CommandError(f"Movies data directory does not exist: {movies_data_path}")
        if not os.path.isfile(schema_path):
            raise CommandError(f"Movie XSD schema file does not exist: {schema_path}")

        # XSD şemasını bir kere yükle ve ayrıştır
        try:
            xsd_doc = etree.parse(schema_path)
            xmlschema = etree.XMLSchema(xsd_doc)
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded XSD schema from {schema_path}"))
        except Exception as e:
            raise CommandError(f"Failed to parse XSD schema: {e}")

        # İstatistikler için sayaçlar
        loaded_count = 0
        updated_count = 0
        error_count = 0

        self.stdout.write(f"Starting to process XML files from {movies_data_path}...")

        # data/movies klasöründeki tüm dosyaları gez
        for filename in os.listdir(movies_data_path):
            if filename.endswith(".xml"):
                file_path = os.path.join(movies_data_path, filename)
                self.stdout.write(f"--> Processing file: {filename}")
                
                try:
                    # XML dosyasını ayrıştır
                    xml_doc = etree.parse(file_path)
                    
                    # 1. XSD ile doğrulama yap
                    xmlschema.assertValid(xml_doc) # Hata varsa exception fırlatır
                    self.stdout.write(self.style.SUCCESS(f"  > XML is valid."))

                    # Kök elemanı al
                    root = xml_doc.getroot()

                    # 2. Veriyi çek
                    movie_id = root.get('id')
                    title = root.findtext('title')
                    year_str = root.findtext('year')
                    year = int(year_str) if year_str and year_str.isdigit() else None
                    
                    director = root.findtext('director')
                    plot = root.findtext('plot') # CDATA içeriği otomatik olarak alınır
                    poster_url = root.findtext('posterUrl')
                    rating_str = root.findtext('rating')
                    rating = float(rating_str) if rating_str else None
                    
                    if not movie_id or not title:
                        self.stderr.write(self.style.ERROR(f"  > Skipping file due to missing movie ID or title."))
                        error_count += 1
                        continue

                    # 3. Django modeline kaydetme veya güncelleme
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
                        self.stdout.write(self.style.SUCCESS(f"  > Created new movie in DB: '{title}'"))
                    else:
                        updated_count += 1
                        self.stdout.write(self.style.WARNING(f"  > Updated existing movie in DB: '{title}'"))

                except etree.DocumentInvalid as e:
                    self.stderr.write(self.style.ERROR(f"  > XML VALIDATION ERROR: {e}"))
                    error_count += 1
                except etree.XMLSyntaxError as e:
                    self.stderr.write(self.style.ERROR(f"  > XML SYNTAX ERROR: {e}"))
                    error_count += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"  > An unexpected error occurred: {e}"))
                    error_count += 1
        
        # Sonuçları raporla
        self.stdout.write(self.style.SUCCESS(
            f"\nFinished. {loaded_count} movies created, {updated_count} movies updated, {error_count} files failed."
        ))