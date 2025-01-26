# train_model.py (versión mejorada)
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

print("Iniciando el programa...")

# 1. Cargar el dataset
print("Cargando el dataset...")
df = pd.read_csv('dataset.csv')
print(f"Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas.\n")

# 2. Definir características y target
print("Preparando características...")
# Eliminar columnas no relevantes
df = df.drop(columns=['title', 'revenue','imdb_score'])

# Separar características y target
X = df.drop(columns=['success'])
y = df['success']

# 3. Preprocesamiento avanzado
print("Creando pipeline de preprocesamiento...")

# Identificar columnas por tipo
categorical_cols = ['actor', 'actress', 'genre']
numeric_cols = X.select_dtypes(include=np.number).columns.tolist()
numeric_cols = [col for col in numeric_cols if col not in ['success']]

# Transformadores numéricos y categóricos
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))])

# Preprocesador completo
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_cols),
        ('cat', categorical_transformer, categorical_cols)])

# 4. Pipeline completo con modelo
print("Construyendo pipeline completo...")
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(
        n_estimators=1000,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1))
])

# 5. Dividir datos
print("Dividiendo en train-test...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42,
    stratify=y  # Mantener distribución de clases
)

# 6. Entrenamiento
print("Entrenando modelo...")
model.fit(X_train, y_train)

# 7. Evaluación
print("\nEvaluación del modelo:")
y_pred = model.predict(X_test)
print(f"Exactitud: {accuracy_score(y_test, y_pred):.4f}")
print("Reporte completo:")
print(classification_report(y_test, y_pred))

# 8. Guardar componentes
print("\nGuardando artefactos...")
os.makedirs('models/based_on_budget', exist_ok=True)

# Guardar modelo completo
joblib.dump(model, 'models/based_on_budget/model.pkl')

# Guardar preprocesador por separado
joblib.dump(preprocessor, 'models/based_on_budget/preprocessor.pkl')

print("Proceso completado exitosamente!")