import pandas as pd
import ast
from typing import List, Union
from nltk.stem.porter import PorterStemmer
from pathlib import Path
from src.logger import logger

def load_data(movies_path: str, credits_path: str) -> pd.DataFrame:
    """
    Loads movies and credits datasets and merges them.
    """
    movies = pd.read_csv(movies_path)
    credits = pd.read_csv(credits_path)

    # Merge datasets
    # Note: 'title' is used here, but 'id' is often safer if available in both to avoid title duplicates
    df = movies.merge(credits, on='title')
    df = df[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
    df.dropna(inplace=True)
    return df


def _parse_list_column(text: str) -> List[str]:
    """Helper: Extracts 'name' from a stringified JSON list (for genres/keywords)."""
    try:
        data = ast.literal_eval(text)
        return [item['name'] for item in data]
    except (ValueError, SyntaxError):
        return []


def _stem_text(text):
    stemmer = PorterStemmer()
    y = []
    for i in text.split():
        y.append(stemmer.stem(i))
    return " ".join(y)


def _extract_top_cast(text: str, limit: int = 3) -> List[str]:
    """Helper: Extracts top N actors from the cast list."""
    try:
        data = ast.literal_eval(text)
        return [item['name'] for item in data][:limit]
    except (ValueError, SyntaxError):
        return []


def _fetch_director(text: str) -> List[str]:
    """Helper: Extracts the Director's name from the crew list."""
    try:
        data = ast.literal_eval(text)
        for item in data:
            if item.get('job') == 'Director':
                return [item['name']]  # Return as list for concatenation consistency
        return []
    except (ValueError, SyntaxError):
        return []


def _collapse_spaces(obj: Union[List[str], str]) -> List[str]:
    """
    Helper: Removes spaces from strings to create unique tags.
    e.g., "Science Fiction" -> "ScienceFiction"
    """
    if isinstance(obj, list):
        return [i.replace(" ", "") for i in obj]
    return []


def process_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Orchestrates the feature engineering pipeline.
    """
    # 1. Extract raw data from JSON columns
    df['genres'] = df['genres'].apply(_parse_list_column)
    df['keywords'] = df['keywords'].apply(_parse_list_column)
    df['cast'] = df['cast'].apply(_extract_top_cast)
    df['crew'] = df['crew'].apply(_fetch_director)

    df['overview'] = df['overview'].apply(lambda x: x.split() if isinstance(x, str) else [])

    cols_to_clean = ['genres', 'keywords', 'cast', 'crew']
    for col in cols_to_clean:
        df[col] = df[col].apply(_collapse_spaces)

    df['tags'] = df['overview'] + df['genres'] + df['keywords'] + df['cast'] + df['crew']

    new_df = df[['movie_id', 'title', 'tags']].copy()
    new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))
    new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())

    new_df['tags'] = new_df['tags'].apply(_stem_text)

    return new_df


if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    RAW_DATA_PATH = project_root / "data" / "raw"
    try:
        logger.info(f"Looking for data in: {RAW_DATA_PATH}")
        raw_df = load_data(
            RAW_DATA_PATH / "tmdb_5000_movies.csv",
            RAW_DATA_PATH / "tmdb_5000_credits.csv"
        )

        logger.info("Processing features...")
        final_df = process_features(raw_df)

        logger.info(f"Success! Processed {len(final_df)} movies.")
        logger.info(final_df.head(1)['tags'].values)

    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        logger.exception("Please check that your 'data/raw' folder exists in the project root.")