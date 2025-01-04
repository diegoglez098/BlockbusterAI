import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time  # Importar para medir el tiempo de ejecución

# Clave de API de TMDb
API_KEY = "20c4b27df6202262cc6bd7418d428594"
BASE_URL = "https://api.themoviedb.org/3"
PAGES_TO_FETCH = 2000  # Número de páginas de películas populares a consultar (20 películas por página)


# Función para obtener películas populares
def fetch_movies(page=1):
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=es-ES&page={page}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        return []

# Función para obtener detalles y créditos de una película y procesarlos
def process_movie(movie):
    movie_id = movie.get("id")
    title = movie.get("title", "Desconocido")
    try:
        details = fetch_movie_details(movie_id)
        credits = fetch_movie_credits(movie_id)
        if not details or not credits:
            return None

        # Obtener datos principales
        budget = details.get("budget", 0)
        revenue = details.get("revenue", 0)
        genres = details.get("genres", [])
        imdb_score = details.get("vote_average", 0.0)
        genre = genres[0]["name"] if genres else "Desconocido"

        # Obtener actores y actrices principales
        cast = credits.get("cast", [])
        actor = cast[0]["name"] if len(cast) > 0 else "Desconocido"
        actress = cast[1]["name"] if len(cast) > 1 else "Desconocido"

        # Determinar éxito (1 = éxito, 0 = fracaso)
        success = 1 if revenue > budget else 0

        print(f"Procesada: {title}")

        return {
            "title": title,
            "actor": actor,
            "actress": actress,
            "genre": genre,
            "budget": budget,
            "revenue": revenue,
            "imdb_score": imdb_score,
            "success": success
        }
    except Exception as e:
        print(f"Error procesando {title}: {e}")
        return None

def fetch_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=es-ES"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def fetch_movie_credits(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}&language=es-ES"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Medir tiempo de inicio
start_time = time.time()

# Generar dataset con hilos
movies_data = []
pages_to_fetch = PAGES_TO_FETCH  # Número de páginas de películas populares a consultar (20 películas por página)

all_movies = []
for page in range(1, pages_to_fetch + 1):
    all_movies.extend(fetch_movies(page=page))

# Usar hilos para procesar las películas en paralelo
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(process_movie, all_movies)

# Filtrar resultados válidos
movies_data = [movie for movie in results if movie is not None]

# Crear DataFrame
df_movies = pd.DataFrame(movies_data)

# Guardar como CSV
file_path = "dataset.csv"
df_movies.to_csv(file_path, index=False)

# Medir tiempo de finalización
end_time = time.time()
elapsed_time = end_time - start_time

print(f"Dataset guardado en {file_path}")
print(f"El proceso completo tardó {elapsed_time:.2f} segundos.")
