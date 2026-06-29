import os
import pickle
import re
import requests
from langdetect import detect
import spacy

class DatasetLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_datasets()
        return cls._instance

    def load_datasets(self):
        base_dir = os.getcwd()
        self.loc_patterns_swiss = self.lazy_load_pickle(
            os.path.join(base_dir, "ExtractInfo/data/loc_patterns_swiss.pkl"))
        self.cities = self.lazy_load_pickle(os.path.join(base_dir, "ExtractInfo/data/cities.pkl"))
        self.skill_pattern_german = self.lazy_load_pickle(
            os.path.join(base_dir, "ExtractInfo/data/GermanSkillPattern.pkl"))
        self.skill_pattern_english = self.lazy_load_pickle(
            os.path.join(base_dir, "ExtractInfo/data/EnglishSkillPattern.pkl"))

    def lazy_load_pickle(self, file_path):
        try:
            with open(file_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return None

    @classmethod
    def get_loc_patterns_swiss(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance.loc_patterns_swiss

    @classmethod
    def get_cities(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance.cities

    @classmethod
    def get_skill_pattern_german(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance.skill_pattern_german

    @classmethod
    def get_skill_pattern_english(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance.skill_pattern_english


# Usage
loc_patterns_swiss = DatasetLoader.get_loc_patterns_swiss()
cities = DatasetLoader.get_cities()
skill_pattern_german = DatasetLoader.get_skill_pattern_german()
skill_pattern_english = DatasetLoader.get_skill_pattern_english()


def en_core_web_sm(texts):
    url = "https://spacy.jobdesk.com/analyze/en_core_web_sm"
    response = requests.get(url, params={"text": texts})
    if response.status_code == 200:
        datas = response.json()
        return datas
    return None


def de_core_news_sm(texts):
    url = "https://spacy.jobdesk.com/analyze/de_core_news_sm"
    response = requests.get(url, params={"text": texts})
    if response.status_code == 200:
        datas = response.json()
        return datas
    return None


def de_core_news_md(texts):
    url = "https://spacy.jobdesk.com/analyze/de_core_news_md"
    response = requests.post(url, params={"text": texts})
    if response.status_code == 200:
        datas = response.json()
        return datas
    return None


def extract_name(text):
    text = text.strip()
    clean = en_core_web_sm(text)
    skill_list = []
    person = ""
    for token in clean[0]:
        if token['entity'] == 'PERSON':
            if person:
                person += " " + token['text']
            else:
                person = token['text']
    if person:
        skill_list.append(person)
    # return "".join(skill_list)
    return None


nlp_de = spacy.load("de_core_news_md")
nlp_en = spacy.load("en_core_web_sm")
stop_words_de = set(nlp_de.Defaults.stop_words)
stop_words_en = set(nlp_en.Defaults.stop_words)


# def extract_name(text: str) -> str:
#     """
#     - If the text is empty, return `None`.
#     - Otherwise, use spaCy to extract all entities of type `PER` (person) that are at least two words
#     long and all words are titles.
#     - Return the last such entity
#
#     :param text: the text to extract the name from
#     :type text: str
#     :return: The name of the person who is being mentioned in the text.
#     """
#     if text.strip() == "":
#         return None
#     doc = nlp_de(text)
#     ents = [
#         e.text
#         for e in doc.ents
#         if e.label_ == "PER"
#            and len(e.text.split()) >= 2
#            and all(word.istitle() for word in e.text.split())
#     ]
#     try:
#         name = ents[-1]
#         name_words = name.split()
#         if len(name_words) > 2:
#             return name_words[0] + " " + name_words[1]
#         else:
#             return name
#     except IndexError:
#         return None


def extract_number(text):
    cleaned = re.sub(r"[^\w+]", "", text)
    pattern = r"(?:\+)?\d{9,11}"
    try:
        matches = re.findall(pattern, cleaned)
        return matches[-1]
    except IndexError:
        return "None"


def extract_location(loc_text):
    if loc_text.strip() == "":
        return None
    loc = []
    doc = en_core_web_sm(loc_text)
    for single in doc[0]:
        if single['entity'] == "GPE" and single['label'] == "B":
            loc.append(single["text"])
    if len(loc) > 0:
        return loc[-1]
    return loc


def extract_email(text):
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    try:
        matches = list(re.finditer(email_regex, text))
        for match in reversed(matches):
            return match.group()
    except IndexError:
        return "None"


def detect_lang(text: str) -> str:
    langCode = detect(text[0:2000])
    return langCode


def extract_german_skills(text):
    doc = de_core_news_sm(text)
    tokens, stop_words = doc
    noun_chunks = []
    current_chunk = []
    for token in tokens:
        if token['pos'] in {'NOUN', 'PROPN', 'ADJ'}:
            current_chunk.append(token['text'])
        else:
            if current_chunk:
                noun_chunks.append(" ".join(current_chunk))
                current_chunk = []
    if current_chunk:
        noun_chunks.append(" ".join(current_chunk))
    final = list(set(noun_chunks))
    return final[:30]


def extract_english_skills(text):
    doc = en_core_web_sm(text)
    tokens, stop_words = doc
    noun_chunks = []
    current_chunk = []
    for token in tokens:
        if token['pos'] in {'NOUN', 'PROPN', 'ADJ'}:
            current_chunk.append(token['text'])
        else:
            if current_chunk:
                noun_chunks.append(" ".join(current_chunk))
                current_chunk = []
    if current_chunk:
        noun_chunks.append(" ".join(current_chunk))
    final = list(set(noun_chunks))
    return final[:30]


# def extract_german_skills(text):
#     doc = nlp_de(text)
#     noun_chunks = []
#     current_chunk = []
#     for token in doc:
#         if token.pos_ in {'NOUN', 'PROPN', 'ADJ'}:
#             current_chunk.append(token.text)
#         else:
#             if current_chunk:
#                 noun_chunks.append(" ".join(current_chunk))
#                 current_chunk = []
#     if current_chunk:
#         noun_chunks.append(" ".join(current_chunk))
#     final = list(set(noun_chunks))
#     return final[:30]


# def extract_english_skills(text):
#     doc = nlp_en(text)
#     noun_chunks = []
#     current_chunk = []
#     for token in doc:
#         if token.pos_ in {'NOUN', 'PROPN', 'ADJ'}:
#             current_chunk.append(token.text)
#         else:
#             if current_chunk:
#                 noun_chunks.append(" ".join(current_chunk))
#                 current_chunk = []
#     if current_chunk:
#         noun_chunks.append(" ".join(current_chunk))
#     final = list(set(noun_chunks))
#     return final[:30]


def extract_skills(text):
    langCode = detect_lang(text)
    if langCode == "de":
        return extract_german_skills(text)
    else:
        # langCode == "en"
        return extract_english_skills(text)
    # else:
    #     return None
