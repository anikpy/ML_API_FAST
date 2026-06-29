import pandas as pd
import os
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
        base_dir = os.getcwd()
        file_path = f"{base_dir}/skillMatchSearch/data/title-skill.csv"
        self.skills_data = self.lazy_load_csv(file_path)

    def lazy_load_csv(self, file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return None

    def get_skills_data(self):
        return self.skills_data


# Usage
loader = DatasetLoader()
skills_data = loader.get_skills_data()


def get_cosine_similarity_matrix(job_title, job_titles, vectorizer=None):
    if vectorizer is None:
        vectorizer = TfidfVectorizer().fit(job_titles)
    job_title_vec = vectorizer.transform([job_title])
    job_titles_vec = vectorizer.transform(job_titles)
    similarity_matrix = cosine_similarity(job_title_vec, job_titles_vec)
    return similarity_matrix, vectorizer


def get_similar_skills(job_title, datasets, top_n=20):
    datasets = datasets.dropna(subset=['jobtitle']).drop_duplicates(subset=['jobtitle'])
    job_titles = datasets['jobtitle'].tolist()
    similarity_matrix, vectorizer = get_cosine_similarity_matrix(job_title, job_titles)
    similar_indices = np.argsort(similarity_matrix[0])[::-1][:top_n]
    similar_skills = []
    for index in similar_indices:
        skills = datasets.iloc[index]['skill'].split(',')
        similar_skills.extend([skill.strip() for skill in skills])
    return list(set(similar_skills))[:top_n]

