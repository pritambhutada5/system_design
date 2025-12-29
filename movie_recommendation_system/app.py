import os
import streamlit as st
import requests
from dotenv import load_dotenv
from src.recommender import MovieRecommender
load_dotenv()

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

TMDB_BEARER_TOKEN = os.getenv("TMDB_BEARER_TOKEN")


def fetch_poster(movie_id):
    """
    Fetches the poster URL from TMDB API.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_BEARER_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return "https://via.placeholder.com/500x750?text=No+Image"  # Fallback image
    except Exception:
        return "https://via.placeholder.com/500x750?text=Error"


def set_custom_style():
    st.markdown(
        """
        <style>
        .stApp { background-color: #0E1117; }
        h1, h2, h3, p, label { color: white !important; }
        .stSelectbox label { color: #FF4B4B !important; font-size: 1.2rem; }
        .stButton > button {
            background: linear-gradient(45deg, #FF4B4B, #FF914D);
            color: white; border: none; padding: 0.6rem 2rem;
            border-radius: 10px; font-weight: bold; width: 100%;
        }
        .stButton > button:hover { transform: translateY(-2px); }
        /* Style for the movie titles under posters */
        .caption { text-align: center; font-weight: bold; margin-top: 5px; color: #ddd;}
        </style>
        """,
        unsafe_allow_html=True
    )


set_custom_style()
st.title("🎬 Movie Recommendation System")


@st.cache_resource
def load_recommender():
    return MovieRecommender()


try:
    recommender = load_recommender()
    movie_list = recommender.movies['title'].values
    selected_movie = st.selectbox("Select a movie you like:", movie_list)

    if st.button('Show Recommendations'):
        with st.spinner('Fetching recommendations and posters...'):
            recommendations = recommender.recommend(selected_movie)

            cols = st.columns(5)

            for idx, (title, movie_id) in enumerate(recommendations):
                with cols[idx]:
                    poster_url = fetch_poster(movie_id)
                    st.image(poster_url, width='stretch')
                    st.markdown(f"<div class='caption'>{title}</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"An error occurred: {e}")
