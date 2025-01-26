from flask import Flask, request, render_template, jsonify
import joblib
import pandas as pd
from predict_scores import predict_movie_success_scores
from predict import predict_movie_success
from recomendations import MovieRecommender

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    user_data = {
        'actor': request.form['actor'],
        'actress': request.form['actress'],
        'genre': request.form['genre'],
        'budget': float(request.form['budget'])
    }

    # Obtener predicciones
    probability_scores = predict_movie_success_scores(
        user_data['actor'],
        user_data['actress'],
        user_data['genre'],
        user_data['budget']
    ) * 100
    
    success = predict_movie_success(
        user_data['actor'],
        user_data['actress'],
        user_data['genre'],
        user_data['budget']
    )

    # Obtener recomendaciones y convertir a formato serializable
    recommender = MovieRecommender()
    raw_recommendations = recommender.recommend_by_genre_budget(user_data)
    
    # Convertir DataFrames a listas de diccionarios
    recommendations = {
        'genre': raw_recommendations['genre'],
        'budget_analysis': {
            'user_budget': raw_recommendations['budget_analysis']['user_budget'],
            'genre_avg_budget': raw_recommendations['budget_analysis']['genre_avg_budget'],
            'budget_status': raw_recommendations['budget_analysis']['budget_status'],
            'budget_range': raw_recommendations['budget_analysis']['budget_range']
        },
        'top_actors': raw_recommendations['top_actors'].reset_index().rename(columns={'index': 'actor'}).to_dict('records'),
        'top_actresses': raw_recommendations['top_actresses'].reset_index().rename(columns={'index': 'actress'}).to_dict('records'),
        'budget_deviation': raw_recommendations['budget_deviation']
    }

    return jsonify({
        'probability': probability_scores,
        'success': success,
        'recommendations': recommendations
    })

if __name__ == '__main__':
    app.run(debug=True)