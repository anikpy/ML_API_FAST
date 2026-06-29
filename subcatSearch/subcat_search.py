import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class DatasetLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_datasets()
        return cls._instance

    def load_datasets(self):
        current_dir = os.getcwd()
        file_path = f"{current_dir}/subcatSearch/data/basic_cleaned.csv"
        self.subcat_data = self.lazy_load_csv(file_path)

    def lazy_load_csv(self, file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return None

    def get_subcat_data(self):
        return self.subcat_data


# Usage
loader = DatasetLoader()
subcat_data = loader.get_subcat_data()


def preprocess_text(text):
    text = text.lower()
    return text


def get_cosine_similarity_matrix(job_title, job_titles):
    vectorizer = TfidfVectorizer(preprocessor=preprocess_text)
    job_titles_vec = vectorizer.fit_transform(job_titles)
    job_title_vec = vectorizer.transform([job_title])
    similarity_matrix = cosine_similarity(job_title_vec, job_titles_vec)
    return similarity_matrix


def get_categories(job_title, datasets, threshold=0.3):
    datasets = datasets.dropna(subset=['jobtitle'])
    job_titles = datasets['jobtitle'].tolist()
    similarity_matrix = get_cosine_similarity_matrix(job_title, job_titles)
    similar_indices = np.where(similarity_matrix[0] >= threshold)[0]
    if len(similar_indices) > 0:
        subcategories = datasets.iloc[similar_indices]['jobsubcategories'].str.strip("[]").str.strip("'")
        subcategory_freq = subcategories.value_counts()
        max_subcategory = subcategory_freq.idxmax()
        return [max_subcategory.strip()]
    else:
        return None 
