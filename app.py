from flask import Flask, request, render_template, jsonify
import joblib
import pandas as pd
from predict_scores import predict_movie_success_scores
from predict import predict_movie_success

# Crear una instancia de Flask
app = Flask(__name__)

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar la predicción
@app.route('/predict', methods=['POST'])
def predict():
    actor = request.form['actor']
    actress = request.form['actress']
    genre = request.form['genre']
    budget = float(request.form['budget'])
    
    probability_scores = predict_movie_success_scores(actor, actress, genre, budget) * 100
    sucess = predict_movie_success(actor, actress, genre, budget)
    return jsonify({'probability': probability_scores, 'success': sucess})

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
