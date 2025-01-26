import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import timedelta

# Configuración
API_KEY = "20c4b27df6202262cc6bd7418d428594"
BASE_URL = "https://api.themoviedb.org/3"
PAGES_TO_FETCH = 2000  # Número de páginas a obtener
MAX_WORKERS = 10  # Hilos paralelos
REQUEST_DELAY = 0.1  # Segundos entre peticiones para evitar rate limiting
RETRY_ATTEMPTS = 3  # Intentos por petición fallida

# Estadísticas de seguimiento
stats = {
    'total_pages': 0,
    'movies_fetched': 0,
    'movies_processed': 0,
    'api_errors': 0,
    'processing_errors': 0,
    'success_rate': 0.0
}

def fetch_with_retry(url, max_retries=RETRY_ATTEMPTS):
    """Función con reintentos para peticiones HTTP"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                print(f"Rate limit alcanzado. Reintentando después de {retry_after} segundos...")
                time.sleep(retry_after)
            else:
                print(f"Error HTTP {response.status_code} en intento {attempt + 1}")
                time.sleep(2 ** attempt)
        except Exception as e:
            print(f"Error de conexión: {str(e)}")
            time.sleep(5)
    return None

def fetch_movies(page):
    """Obtiene películas populares de una página específica con manejo de errores"""
    print(f"\n📥 Obteniendo página {page}/{PAGES_TO_FETCH}...")
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=es-ES&page={page}"
    data = fetch_with_retry(url)
    
    if data and 'results' in data:
        stats['total_pages'] += 1
        movies = data['results']
        stats['movies_fetched'] += len(movies)
        print(f"✅ Página {page} obtenida: {len(movies)} películas")
        return movies
    else:
        stats['api_errors'] += 1
        print(f"❌ Fallo al obtener página {page}")
        return []

def process_movie(movie):
    """Procesa una película obteniendo detalles y créditos"""
    try:
        movie_id = movie.get("id")
        title = movie.get("title", "Desconocido").strip()
        
        # Obtener detalles con reintentos
        details = fetch_with_retry(f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=es-ES")
        credits = fetch_with_retry(f"{BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}&language=es-ES")
        
        if not details or not credits:
            return None

        # Extracción de datos
        budget = details.get("budget", 0)
        revenue = details.get("revenue", 0)
        genres = details.get("genres", [])
        imdb_score = details.get("vote_average", 0.0)
        genre = genres[0]["name"] if genres else "Desconocido"

        # Manejo del reparto
        cast = credits.get("cast", [])
        actor = next((p["name"] for p in cast if p["gender"] == 2), "Desconocido")
        actress = next((p["name"] for p in cast if p["gender"] == 1), "Desconocido")

        # Cálculo de éxito
        success = 1 if (revenue > budget and budget > 0) else 0

        stats['movies_processed'] += 1
        print(f"🎬 Procesada: {title} | Presupuesto: ${budget:,} | Éxito: {success}")
        
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
        stats['processing_errors'] += 1
        print(f"❌ Error procesando {title}: {str(e)}")
        return None

def generate_dataset():
    """Función principal para generar el dataset"""
    print("\n🚀 Iniciando generación de dataset...")
    start_time = time.time()
    movies_data = []
    
    # Paso 1: Obtener todas las páginas
    print(f"\n📡 Obteniendo {PAGES_TO_FETCH} páginas de películas...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_page = {executor.submit(fetch_movies, page): page for page in range(1, PAGES_TO_FETCH + 1)}
        
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                movies = future.result()
                if movies:
                    # Paso 2: Procesar películas en paralelo
                    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as processor:
                        processed = processor.map(process_movie, movies)
                        movies_data.extend([m for m in processed if m])
                        time.sleep(REQUEST_DELAY)  # Controlar tasa de peticiones
            except Exception as e:
                print(f"Error procesando página {page}: {str(e)}")
    
    # Paso 3: Crear y guardar el dataset
    print("\n💾 Guardando dataset...")
    df = pd.DataFrame(movies_data)
    df.to_csv("dataset.csv", index=False)
    
    # Estadísticas finales
    stats['success_rate'] = df['success'].mean() * 100 if not df.empty else 0
    elapsed = time.time() - start_time
    
    print("\n📊 Resumen final:")
    print(f"• Tiempo total: {timedelta(seconds=elapsed)}")
    print(f"• Páginas obtenidas: {stats['total_pages']}/{PAGES_TO_FETCH}")
    print(f"• Películas procesadas: {stats['movies_processed']}")
    print(f"• Tasa de éxito: {stats['success_rate']:.2f}%")
    print(f"• Errores API: {stats['api_errors']}")
    print(f"• Errores procesamiento: {stats['processing_errors']}")
    print(f"\n✅ Dataset generado con {len(df)} películas!")

if __name__ == "__main__":
    generate_dataset()