import pandas as pd
import numpy as np
from joblib import load
from sklearn.preprocessing import LabelEncoder
import random
from predict_scores import predict_movie_success_scores
# Cargar el dataset y el modelo
df = pd.read_csv('dataset.csv')

# Cargar el modelo entrenado
model = load('models/based_on_scores/movie_success_model_xgb.joblib')
encoder_actor = load('models/based_on_scores/encoder_actor.joblib')
encoder_actress = load('models/based_on_scores/encoder_actress.joblib')
encoder_genre = load('models/based_on_scores/encoder_genre.joblib')

# Función para predecir el éxito de una película

# Función para recomendar actores, actrices, géneros y presupuesto
def recommend_successful_movie(user_actor=None, user_actress=None, user_genre=None, user_budget=None):
    # Filtramos solo las películas que fueron exitosas
    successful_movies = df[df['success'] == 1]
    
    # Si el usuario no ha proporcionado un actor, sugerimos el más común entre las películas exitosas
    if user_actor is None:
        actor_successful_avg = successful_movies.groupby('actor').size().sort_values(ascending=False)
        recommended_actor = encoder_actor.inverse_transform(actor_successful_avg.index[0:50])  # Top 3 actores más comunes
    else:
        recommended_actor = [user_actor]  # Si el usuario ya ha proporcionado un actor, lo usamos directamente
    
    # Si el usuario no ha proporcionado una actriz, sugerimos la más común entre las películas exitosas
    if user_actress is None:
        actress_successful_avg = successful_movies.groupby('actress').size().sort_values(ascending=False)
        recommended_actress = []
        
        # Filtrar actrices que están presentes en el encoder
        for actress in actress_successful_avg.index[0:3]:
            if actress in encoder_actress.classes_:
                recommended_actress.append(actress)
        
        # Si alguna actriz no está en el encoder, asignamos la más común entre las que sí están
        if not recommended_actress:
            recommended_actress = encoder_actress.inverse_transform(encoder_actress.classes_[0:50])
    else:
        recommended_actress = [user_actress]  # Si el usuario ya ha proporcionado una actriz, lo usamos directamente
    
    # **Nuevo código para evitar repetir actores y actrices con el mismo nombre:**
    # Filtrar actores y actrices que tienen el mismo nombre
    if user_actor and user_actress and user_actor == user_actress:
        # Si el actor y la actriz son el mismo, excluir el actor o la actriz
        recommended_actor = [actor for actor in recommended_actor if actor != user_actor]
        recommended_actress = [actress for actress in recommended_actress if actress != user_actress]
        
        # Si después de eliminar queda vacío, tomamos el siguiente mejor
        if not recommended_actor:
            recommended_actor = encoder_actor.inverse_transform(actor_successful_avg.index[1:2])  # Tomamos el siguiente mejor actor
        if not recommended_actress:
            recommended_actress = encoder_actress.inverse_transform(actress_successful_avg.index[1:2])  # Tomamos la siguiente mejor actriz
    
    # Si el usuario no ha proporcionado un género, sugerimos el más común entre las películas exitosas
    if user_genre is None:
        genre_successful_avg = successful_movies.groupby('genre').size().sort_values(ascending=False)
        recommended_genre = []
        
        # Filtrar géneros que están presentes en el encoder
        for genre in genre_successful_avg.index[0:3]:
            if genre in encoder_genre.classes_:
                recommended_genre.append(genre)
        
        # Si algún género no está en el encoder, asignamos el más común entre los que sí están
        if not recommended_genre:
            recommended_genre = encoder_genre.inverse_transform(encoder_genre.classes_[0:3])
    else:
        recommended_genre = [user_genre]  # Si el usuario ya ha proporcionado un género, lo usamos directamente
    
    # Si el usuario no ha proporcionado un presupuesto, sugerimos el presupuesto promedio de las películas exitosas
    if user_budget is None:
        avg_budget_successful = successful_movies['budget'].mean()
        recommended_budget = avg_budget_successful  # Sugerimos el presupuesto promedio de las películas exitosas
    else:
        recommended_budget = user_budget  # Si el usuario ya ha proporcionado un presupuesto, lo usamos directamente
    
    # Ahora, para cada combinación posible de los valores proporcionados o sugeridos, calculamos el éxito
    recommendations = []
    
    # Generar todas las combinaciones posibles para actor, actriz, género, y presupuesto
    for actor in recommended_actor:
        for actress in recommended_actress:
            # Asegurarse de que el actor y la actriz no sean la misma persona
            if actor != actress:
                # Predicción de éxito con el presupuesto
                success = predict_movie_success_scores(actor, actress, user_genre, recommended_budget)
                
                # Solo agregamos la recomendación si es exitosa
                if success == 1:
                    recommendations.append({
                        "actor": actor,
                        "actress": actress,
                        "genre": user_genre,
                        "budget": recommended_budget,
                        "predicted_success": "ÉXITO"
                    })
    
    # Si hay recomendaciones exitosas, seleccionamos una aleatoria
    if recommendations:
        selected_rec = random.choice(recommendations)
        return("Recomendación para asegurar el éxito de la película:")
        return(f"Actor: {selected_rec['actor']}, Actriz: {selected_rec['actress']}, Género: {selected_rec['genre']}, "
              f"Presupuesto: {selected_rec['budget']:.2f} millones, Predicción: {selected_rec['predicted_success']}")
    else:
        return("No se generaron recomendaciones exitosas basadas en los parámetros dados.")

