# predict.py
import pandas as pd
from joblib import load

def predict_movie_success(actor, actress, genre, budget):
    try:
        # Cargar el pipeline completo
        model = load('models/based_on_budget/model.pkl')
        
        # Crear DataFrame con la estructura esperada
        input_data = pd.DataFrame([{
            'actor': str(actor),
            'actress': str(actress),
            'genre': str(genre),
            'budget': float(budget)
        }])
        
        # Asegurar tipos de datos
        input_data = input_data.astype({
            'actor': 'object',
            'actress': 'object',
            'genre': 'object',
            'budget': 'float64'
        })
        
        # Obtener probabilidades de predicción
        proba = model.predict_proba(input_data)[0]
        success_prob = round(proba[1] * 100, 2)  # Probabilidad de éxito (clase 1)
        
        # Obtener predicción binaria
        prediction = model.predict(input_data)[0]
        
        # Devolver resultado con porcentaje
        result = "ÉXITO" if prediction == 1 else "FRACASO"
        return f"{success_prob}%"
    
    except Exception as e:
        return f"Error: {str(e)}"

# Ejemplo de uso
if __name__ == "__main__":
    ejemplo = {
        'actor': "Tom Hanks",
        'actress': "Meryl Streep",
        'genre': "Drama",
        'budget': 100000000
    }
    
    resultado = predict_movie_success(
        ejemplo['actor'],
        ejemplo['actress'],
        ejemplo['genre'],
        ejemplo['budget']
    )
    
    print(f"Predicción: {resultado}")