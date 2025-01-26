# recommendations.py
import pandas as pd
import numpy as np
from joblib import load

class MovieRecommender:
    def __init__(self):
        self.df = pd.read_csv('dataset.csv')
        self.budget_model = load('models/based_on_budget/model.pkl')
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Prepara los datos para análisis de recomendaciones por género"""
        # Calcular éxito promedio por género
        self.genre_stats = self.df.groupby('genre').agg({
            'success': 'mean',
            'budget': ['mean', 'std']
        })
        
    def recommend_by_genre_budget(self, user_data):
        """Genera recomendaciones específicas para el género y presupuesto del usuario"""
        target_genre = user_data['genre']
        user_budget = user_data['budget']
        
        # Filtrar dataset por género
        genre_df = self.df[self.df['genre'] == target_genre]
        
        # Calcular métricas clave
        budget_deviation = self._calculate_budget_deviation(genre_df, user_budget)
        actor_recommendations = self._get_genre_specific_recommendations(genre_df, 'actor', user_budget)
        actress_recommendations = self._get_genre_specific_recommendations(genre_df, 'actress', user_budget)
        
        # Preparar respuesta
        return {
            'genre': target_genre,
            'budget_analysis': self._analyze_budget(genre_df, user_budget),
            'top_actors': actor_recommendations,
            'top_actresses': actress_recommendations,
            'budget_deviation': budget_deviation
        }
    
    def _get_genre_specific_recommendations(self, genre_df, role, user_budget):
        """Genera recomendaciones para actores/actrices en el género específico"""
        recommendations = genre_df.groupby(role).agg({
            'success': 'mean',
            'budget': 'mean',
            'title': 'count'
        }).rename(columns={'title': 'movie_count'})
        
        # Filtrar y ordenar
        recommendations = recommendations[recommendations['movie_count'] >= 3]
        recommendations['budget_diff'] = abs(recommendations['budget'] - user_budget)
        
        return recommendations.sort_values(
            ['success', 'budget_diff'], 
            ascending=[False, True]
        ).head(5).reset_index()
        
    def _analyze_budget(self, genre_df, user_budget):
        """Analiza cómo se compara el presupuesto del usuario con datos históricos"""
        avg_budget = genre_df['budget'].mean()
        std_budget = genre_df['budget'].std()
        
        return {
            'user_budget': user_budget,
            'genre_avg_budget': avg_budget,
            'budget_range': {
                'low': avg_budget - std_budget,
                'high': avg_budget + std_budget
            },
            'budget_status': self._get_budget_status(user_budget, avg_budget, std_budget)
        }
    
    def _get_budget_status(self, user_budget, avg, std):
        """Clasifica el presupuesto del usuario"""
        if user_budget < avg - std:
            return "Presupuesto muy bajo para este género"
        elif user_budget > avg + std:
            return "Presupuesto muy alto para este género"
        else:
            return "Presupuesto dentro del rango típico"
    
    def _calculate_budget_deviation(self, genre_df, user_budget):
        """Calcula cuánto se desvía el presupuesto del usuario"""
        return (user_budget - genre_df['budget'].mean()) / genre_df['budget'].std()

    def print_recommendations(self, recommendations):
        """Muestra las recomendaciones de forma legible"""
        print(f"\n{' RECOMENDACIONES PARA ':^50}")
        print(f"Género: {recommendations['genre']}")
        print(f"\nPresupuesto introducido: ${recommendations['budget_analysis']['user_budget']:,.2f}")
        print(f"Presupuesto promedio en el género: ${recommendations['budget_analysis']['genre_avg_budget']:,.2f}")
        print(f"Estado del presupuesto: {recommendations['budget_analysis']['budget_status']}")
        
        print("\nTop Actores para este género y presupuesto:")
        for i, actor in enumerate(recommendations['top_actors'].itertuples(), 1):
            print(f"{i}. {actor.actor}")
            print(f"   Tasa de éxito: {actor.success:.1%}")
            print(f"   Presupuesto promedio: ${actor.budget:,.2f}")
            print(f"   Películas analizadas: {actor.movie_count}")
            
        print("\nTop Actrices para este género y presupuesto:")
        for i, actress in enumerate(recommendations['top_actresses'].itertuples(), 1):
            print(f"{i}. {actress.actress}")
            print(f"   Tasa de éxito: {actress.success:.1%}")
            print(f"   Presupuesto promedio: ${actress.budget:,.2f}")
            print(f"   Películas analizadas: {actress.movie_count}")

# Ejemplo de uso
if __name__ == "__main__":
    recommender = MovieRecommender()
    
    ejemplo = {
        'actor': "Tom Cruise",
        'actress': "Scarlett Johansson",
        'genre': "Acción",	
        'budget': 15000000
    }
    
    recs = recommender.recommend_by_genre_budget(ejemplo)
    recommender.print_recommendations(recs)