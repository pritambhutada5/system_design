import joblib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from src.logger import logger


def build_and_save_model(df: pd.DataFrame, save_path):
    """
    1. Vectorizes the tags
    2. Computes Cosine Similarity
    3. Saves the Matrix and the DataFrame to disk
    """
    logger.info("Vectorizing data...")
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(df['tags']).toarray()

    logger.info("Calculating similarity matrix...")
    similarity = cosine_similarity(vectors)

    logger.info(f"Saving artifacts to {save_path}...")
    joblib.dump(df, f"{save_path}movie_list.pkl")
    joblib.dump(similarity, f"{save_path}similarity_matrix.pkl")

    logger.info("Model built and saved successfully!")


if __name__ == "__main__":
    # run this file directly to 'train' the model
    from src.ingestion import load_data, process_features
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    RAW_DATA_PATH = project_root / "data" / "raw"
    SAVE_PATH = f"{project_root}/data/processed/"

    raw_df = load_data(f"{RAW_DATA_PATH}/tmdb_5000_movies.csv",
                       f"{RAW_DATA_PATH}/tmdb_5000_credits.csv")

    final_df = process_features(raw_df)

    build_and_save_model(final_df, SAVE_PATH)
