# predict.py

import pandas as pd
import numpy as np
from joblib import load

# Cargar el modelo y los objetos necesarios
print("Cargando el modelo y los codificadores...")
model = load('models/based_on_budget/movie_success_model_xgb.joblib')
encoder_actor = load('models/based_on_budget/encoder_actor.joblib')
encoder_actress = load('models/based_on_budget/encoder_actress.joblib')
encoder_genre = load('models/based_on_budget/encoder_genre.joblib')
scaler = load('models/based_on_budget/scaler.joblib')
print("Modelo y codificadores cargados.\n")

# Función para predecir el éxito de una película
def predict_movie_success(actor, actress, genre, budget):
    # Convertir las entradas de texto a valores numéricos
    actor_encoded = encoder_actor.transform([actor])[0]
    actress_encoded = encoder_actress.transform([actress])[0]
    genre_encoded = encoder_genre.transform([genre])[0]
    
    # Normalizar el presupuesto
    budget_scaled = scaler.transform([[budget, 0]])[0][0]  # Cambiar para que tenga 2 características (presupuesto, recaudación ficticia de 0)
    
    # Crear el vector de características para la predicción
    X_new = np.array([[actor_encoded, actress_encoded, genre_encoded, budget_scaled]])
    
    # Realizar la predicción
    prediction = model.predict(X_new)
    
    # Interpretar el resultado
    if prediction == 1:
        return "ÉXITO"
    else:
        return "FRACASO"
