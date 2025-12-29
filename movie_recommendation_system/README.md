```markdown
# 🎬 Movie Recommendation System (PoC)

A Content-Based Movie Recommendation System built with Python, Scikit-Learn, and Streamlit. This project implements a **Retrieval-based architecture** inspired by production recommendation systems (e.g. Netflix/YouTube)

## 📌 Overview

This application suggests movies based on similarities in their plot, genre, cast, and crew. It solves the "Cold Start" problem for items by analyzing metadata rather than user interaction history.

**Key Features:**
*   **Data Pipeline:** Automated ingestion and cleaning of TMDB 5000 datasets.
*   **Vectorization:** Uses `CountVectorizer` to convert text metadata into vector space.
*   **Similarity Engine:** Calculates Cosine Similarity to find the closest matches.
*   **Interactive UI:** A dark-themed Streamlit dashboard with real-time movie posters.
*   **Logging:** Centralized logging for tracking pipeline execution.

---

## 🏗️ System Architecture

This PoC mimics a Two-Stage Recommendation Architecture (specifically the **Retrieval Layer**):

1.  **Ingestion Layer (`src/ingestion.py`)**:
    *   Loads raw CSVs (Movies & Credits).
    *   Parses JSON columns (Cast, Crew, Keywords).
    *   Stems text using `PorterStemmer` and creates a tag for each movie.

2.  **Model Training (`src/models.py`)**:
    *   Converts text tags into vectors (5000-dimensional space).
    *   Computes a 4800x4800 Similarity Matrix.
    *   Saves artifacts (`.pkl` files) for low-latency inference.

3.  **Serving Layer (`app.py` & `src/recommender.py`)**:
    *   Loads the pre-computed matrix.
    *   Fetches movie posters via TMDB API.
    *   Renders results in a Streamlit web app.

---

## 📂 Project Structure

```text
movie_recommendation_system/
├── .env                  # Environment variables (TMDB Token)
├── .gitignore            # Files to ignore (e.g., venv, __pycache__)
├── app.py                # Streamlit Dashboard (Frontend)
├── requirements.txt      # Project Dependencies
├── README.md             # Documentation
├── data/
│   ├── raw/              # TMDB CSV files
│   └── processed/        # Generated .pkl models
├── logs/                 # Execution logs
└── src/
    ├── __init__.py
    ├── ingestion.py      # ETL Pipeline: Cleaning & Preprocessing
    ├── models.py         # ML Pipeline: Vectorization & Training
    ├── recommender.py    # Inference Logic
    └── logger.py         # Centralized Logging Config
```

---

## 🚀 Getting Started

### 1. Prerequisites
*   Python 3.11 or higher
*   TMDB API Read Access Token (for fetching posters)

### 2. Installation

Clone the repository and install dependencies:

```
# Clone the repo
git clone <your-repo-url>
cd movie_recommendation_system

# Create Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Libraries
pip install -r requirements.txt
```

### 3. Data Setup
1.  Download the dataset from [Kaggle (TMDB 5000 Movie Dataset)](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata).
2.  Place `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` inside `data/raw/`.

### 4. Build the Model
Run the pipeline to process data and generate the similarity matrix:

```
# Run ingestion and training
Note: The model files are too large for GitHub. After cloning, please run python src/models.py to generate the necessary .pkl files locally.

```bash
python src/models.py
```

```
*Check `logs/` to see the training progress.*

### 5. Run the Application
Start the Streamlit server:

```
streamlit run app.py
```

---

## ⚙️ Configuration

To enable movie posters, open `app.py` and replace the token placeholder:

```
# app.py
TMDB_BEARER_TOKEN = "Fetch Token From .env file"
```

---

## 🧠 Technical Details

### Why CountVectorizer?
We use `CountVectorizer` instead of TF-IDF because in movie metadata, frequency doesn't necessarily mean less importance. If an actor appears often (e.g., "Robert Downey Jr."), it is a strong signal for grouping movies, not a stop word to be down-weighted.

### Similarity Metric
We use **Cosine Similarity** over Euclidean Distance because we care about the *angle* between vectors (content overlap), not the magnitude (length of description).

---

## 🔮 Future Improvements
*   **Hybrid Filtering:** Combine this content-based approach with Collaborative Filtering (User-Item interactions).
*   **Vector Database:** Migrate from local `.pkl` files to a Vector DB (Pinecone/Milvus) for scalability.
*   **FastAPI Backend:** Decouple the UI from the logic by serving recommendations via a REST API.

---

## 📝 License
This project is open-source.
```
