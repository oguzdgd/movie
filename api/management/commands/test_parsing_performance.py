import os
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from lxml import etree

class Command(BaseCommand):
    help = 'Compares the performance of DOM-style vs event-driven (iterparse) XML parsing on a large file.'

    def handle(self, *args, **options):
        xml_file_path = os.path.join(settings.BASE_DIR, 'data', 'large_movies.xml')
        if not os.path.exists(xml_file_path):
            self.stdout.write(self.style.ERROR("large_movies.xml not found. Please run generate_large_xml.py first."))
            return

        # --- 1. DOM-Style Parsing (Tüm dosyayı belleğe yükle) ---
        self.stdout.write(self.style.WARNING("--- Testing DOM-style parsing (etree.parse) ---"))
        start_time = time.time()
        
        try:
            tree = etree.parse(xml_file_path)
            root = tree.getroot()
            movie_count_dom = len(root.findall('movie'))
            end_time = time.time()
            
            self.stdout.write(self.style.SUCCESS(f"Finished in {end_time - start_time:.4f} seconds."))
            self.stdout.write(f"Found {movie_count_dom} movies.")
            # Bu noktada, tüm XML ağacı bellektedir.
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))

        self.stdout.write("-" * 50)

        # --- 2. Event-Driven/Pull Parsing (iterparse - dosyayı satır satır oku) ---
        self.stdout.write(self.style.WARNING("--- Testing event-driven parsing (etree.iterparse) ---"))
        start_time = time.time()
        
        movie_count_iter = 0
        try:
            # iterparse ile 'end' olaylarını (bir etiket kapandığında) dinle
            # Sadece 'movie' etiketleri bittiğinde ilgileniyoruz
            context = etree.iterparse(xml_file_path, events=('end',), tag='movie')
            
            for event, elem in context:
                movie_count_iter += 1
                # Belleği boşaltmak için elemanı temizle
                elem.clear()
                # Kök elemanın referansını da temizle
                while elem.getprevious() is not None:
                    del elem.getparent()[0]

            del context
            end_time = time.time()

            self.stdout.write(self.style.SUCCESS(f"Finished in {end_time - start_time:.4f} seconds."))
            self.stdout.write(f"Found {movie_count_iter} movies.")
            # Bu noktada, XML ağacının çok küçük bir kısmı bellekte tutulmuştur.
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))