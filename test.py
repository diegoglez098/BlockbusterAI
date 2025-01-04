from predict import predict_movie_success
from predict_scores import predict_movie_success_scores
from recomendator import recommend_successful_movie

actor = "Leonardo DiCaprio"
actress = "Margot Robbie"
genre = "Comedia"
budget = 100000000

# Predecir el éxito basado en el presupuesto
result_budget = predict_movie_success(actor, actress, genre, budget)

# Predecir el éxito basado en las puntuaciones
result_scores = predict_movie_success_scores(actor, actress, genre, budget) * 100

recommend = recommend_successful_movie(actor, actress, genre, budget)

print(f"Predicción basada en presupuesto: {result_budget}")
print(f"Posibilidad de éxito basada en puntuaciones: {result_scores}" + "%")
print(recommend)