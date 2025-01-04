import pandas as pd
import joblib

def predict_movie_success_scores(actor, actress, genre, budget):
    # Cargar el modelo entrenado
    model = joblib.load('models/based_on_scores/model.pkl')

    # Nuevos datos de entrada
    new_data = {'actor': [actor], 'actress': [actress], 'genre': [genre], 'budget': [budget]}
    new_df = pd.DataFrame(new_data)
    new_df_encoded = pd.get_dummies(new_df, columns=['actor', 'actress', 'genre'])

    # Cargar los datos originales para obtener las columnas correctas
    original_data = pd.read_csv('dataset.csv')
    original_encoded = pd.get_dummies(original_data, columns=['actor', 'actress', 'genre'])
    original_columns = original_encoded.drop(columns=['title', 'success', 'revenue', 'imdb_score']).columns

    # Asegurarse de que las columnas coincidan con las del modelo entrenado
    new_X = new_df_encoded.reindex(columns=original_columns, fill_value=0)

    # Calcular la probabilidad de éxito
    success_probability = model.predict_proba(new_X)[0][1]
    return success_probability

