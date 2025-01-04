# train_model.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score
from joblib import dump

print("Iniciando el programa...")

# 1. Cargar el dataset
print("Cargando el dataset...")
df = pd.read_csv('dataset.csv')
print(f"Dataset cargado con {len(df)} filas y {len(df.columns)} columnas.\n")

# 2. Preprocesar datos
print("Preprocesando los datos...")

# Imputar valores faltantes si es necesario
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

# Convertir variables categóricas a numéricas
print("Convirtiendo columnas categóricas a numéricas...")
label_encoders = {}
for col in ['actor', 'actress', 'genre']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le
    print(f"Columna '{col}' convertida a valores numéricos.\n")

# Escalar presupuesto y recaudación
print("Normalizando presupuesto y recaudación...")
scaler = StandardScaler()
df[['budget', 'revenue']] = scaler.fit_transform(df[['budget', 'revenue']])
print("Normalización completada.\n")

# 3. Dividir el dataset en características (X) y etiqueta (y)
print("Dividiendo el dataset en características (X) y etiquetas (y)...")
X = df[['actor', 'actress', 'genre', 'budget']]  # Usamos las 4 características
y = df['success']  # Éxito (1) o no (0)
print(f"X contiene {X.shape[1]} características y {X.shape[0]} ejemplos.\n")

# 4. Dividir en datos de entrenamiento y prueba
print("Dividiendo datos en entrenamiento y prueba...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Datos de entrenamiento: {X_train.shape[0]} ejemplos.\nDatos de prueba: {X_test.shape[0]} ejemplos.\n")

# 5. Crear y entrenar el modelo
print("Creando y entrenando el modelo XGBoost...")
model = XGBClassifier(eval_metric='logloss', use_label_encoder=False, random_state=42)
model.fit(X_train, y_train)
print("Modelo entrenado.\n")

# 6. Evaluar el modelo
print("Evaluando el modelo...")
y_pred = model.predict(X_test)
print(f"Precisión del modelo: {accuracy_score(y_test, y_pred):.2f}\n")
print("Reporte de clasificación:\n", classification_report(y_test, y_pred))

# 7. Guardar el modelo y los codificadores
print("Guardando el modelo y los codificadores...")
dump(model, "models/based_on_budget/movie_success_model_xgb.joblib")
dump(label_encoders['actor'], "models/based_on_budget/encoder_actor.joblib")
dump(label_encoders['actress'], "models/based_on_budget/encoder_actress.joblib")
dump(label_encoders['genre'], "models/based_on_budget/encoder_genre.joblib")
dump(scaler, "models/based_on_budget/scaler.joblib")
print("Modelo y codificadores guardados exitosamente.")
