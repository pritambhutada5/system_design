import joblib
from src.logger import logger
from pathlib import Path


class MovieRecommender:
    def __init__(self, ):
        """ Loads Movie Recommendation System """
        logger.info("Loading Movie Recommendation System")
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent
        models_path = f"{project_root}/data/processed/"
        self.movies = joblib.load(f"{models_path}movie_list.pkl")
        self.similarity = joblib.load(f"{models_path}similarity_matrix.pkl")

    def recommend(self, movie_title):
        """
        Returns a list of recommended movie titles.
        """
        # 1. Find the index of the movie
        # We use .values[0] to get the actual integer index safely
        try:
            movie_index = self.movies[self.movies['title'] == movie_title].index[0]
        except IndexError:
            return ["Movie not found in database"]

        distances = self.similarity[movie_index]

        movies_list = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:6]

        recommendations = []
        for i in movies_list:
            row = self.movies.iloc[i[0]]
            recommendations.append((row['title'], row['movie_id']))

        return recommendations


if __name__ == "__main__":
    rec = MovieRecommender()
    logger.info(rec.recommend('Batman Begins'))
