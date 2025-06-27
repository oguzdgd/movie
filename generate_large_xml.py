import random

print("Generating large XML file...")
movie_count = 5000000

with open("data/large_movies.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<movies>\n')
    for i in range(movie_count):
        movie_id = f"gen_{i+1:06d}"
        title = f"Generated Movie {i+1}"
        year = random.randint(1980, 2024)
        rating = round(random.uniform(1.0, 10.0), 1)
        
        f.write(f'  <movie id="{movie_id}">\n')
        f.write(f'    <title>{title}</title>\n')
        f.write(f'    <year>{year}</year>\n')
        f.write(f'    <rating>{rating}</rating>\n')
        f.write(f'  </movie>\n')
    
    f.write('</movies>\n')

print(f"Generated data/large_movies.xml with {movie_count} movies.")