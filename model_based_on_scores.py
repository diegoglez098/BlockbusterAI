import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Cargar el dataset
df = pd.read_csv('dataset.csv')

# One-Hot Encoding para las variables categóricas
df_encoded = pd.get_dummies(df, columns=['actor', 'actress', 'genre'])
print("Dataset codificado")
# Dividir el dataset en características y etiqueta
X = df_encoded.drop(columns=['title', 'success', 'revenue', 'imdb_score'])
y = (df['imdb_score'] >= 7).astype(int)  # Supongamos que éxito es una puntuación de IMDb >= 7

# División en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("Creando modelo...")
# Crear el modelo
model = RandomForestClassifier(n_estimators=1000, random_state=42)
print("Entrenando modelo...")
# Entrenar el modelo
model.fit(X_train, y_train)

# Crear el directorio para guardar el modelo si no existe
os.makedirs('models/based_on_scores', exist_ok=True)

# Guardar el modelo entrenado
joblib.dump(model, 'models/based_on_scores/model.pkl')
print("Modelo guardado en 'models/based_on_scores/model.pkl'")
