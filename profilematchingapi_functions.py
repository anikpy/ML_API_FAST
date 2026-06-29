import json
import traceback
import pandas as pd
from langdetect import detect

eskill_df = pd.read_excel("Data/FinalEnglishSkills.xlsx", engine="openpyxl")
eskills_set = eskill_df.skills.tolist()

gerskill_df = pd.read_excel("Data/FinalGermanSkills.xlsx", engine="openpyxl")
gerskills_set = gerskill_df.skills.tolist()

english_data = "Data/englishdb.json"
with open(english_data, "r") as file:
    data = json.load(file)

# Extract data into lists
ex = [record["Combined"] for record in data]
ey = [record["CleanTitle"] for record in data]
etag_id = [record["SingleTag"] for record in data]
eunique_tag = [record["UniqueTag"] for record in data]

german_data = "Data/germandb.json"
with open(german_data, "r") as file:
    g_data = json.load(file)

gerx = [record["Combined"] for record in g_data]
gery = [record["CleanTitle"] for record in g_data]
gertag_id = [record["SingleTag"] for record in g_data]
gerunique_tag = [record["UniqueTag"] for record in g_data]


class ProfileMatchingAlgorithm:
    import re
    from collections import Counter as Counter
    import math as math

    WORD = re.compile(r"\w+")

    def __init__(self):
        self.counter_list = list()
        self.y_dependent = list()
        self.tag_id = list()
        self.similarity_score = list()
        self.x_inde = list()
        self.skill_df = ""
        self.nlp = None
        self.unique_tag = list()
        self.max_score = 0
        self.max_index = 0

    def clean_text(self, text, for_embedding=False):
        import re

        RE_WSPACE = re.compile(r"\s+", re.IGNORECASE)
        RE_TAGS = re.compile(r"<[^>]+>")
        RE_ASCII = re.compile(r"[^A-Za-zÀ-ž ]", re.IGNORECASE)
        RE_SINGLECHAR = re.compile(r"\b[A-Za-zÀ-ž]\b", re.IGNORECASE)
        if for_embedding:
            RE_ASCII = re.compile(r"[^A-Za-zÀ-ž,.!? ]", re.IGNORECASE)
            RE_SINGLECHAR = re.compile(r"\b[A-Za-zÀ-ž,.!?]\b", re.IGNORECASE)
        text = re.sub(RE_TAGS, " ", text)
        text = re.sub(RE_ASCII, " ", text)
        text = re.sub(RE_SINGLECHAR, " ", text)
        text = re.sub(RE_WSPACE, " ", text)
        return text.strip(" ").lower()

    def german_clean_text(self, text, for_embedding=False):
        import re
        import lxml.html
        import lxml.html.clean

        doc = lxml.html.fromstring(text)
        cleaner = lxml.html.clean.Cleaner(style=True)
        doc = cleaner.clean_html(doc)
        text = doc.text_content()
        RE_WSPACE = re.compile(r"\s+", re.IGNORECASE)
        RE_TAGS = re.compile(r"<[^>]+>")
        text = re.sub(RE_TAGS, " ", text)
        text = re.sub(RE_WSPACE, " ", text)
        text = text.replace("&nbsp", " ")
        text = text.replace("&amp", " ")
        text = re.sub("[\(\[].*?[\)\]]", " ", text)
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"[0-9]", " ", text)
        text = re.sub(" +", " ", text)
        text = text.lower()
        text = " ".join([x for x in text.split(" ") if len(x) > 1 and x != "in"])
        return text.strip(" ")

    def extract_skills(self, text):
        import numpy as np

        nlp_text = self.nlp(" ".join([x.capitalize() for x in text.split(" ")]))
        tokens = [token.text for token in nlp_text if not token.is_stop]
        skillset = []
        for token in tokens:
            token = token.lower().strip()
            if token in self.skill_df:
                if token not in skillset:
                    skillset.append(token)
        for token in nlp_text.noun_chunks:
            token = token.text.lower().strip()
            if token in self.skill_df:
                if token not in skillset:
                    skillset.append(token)
        req_skills = [i.lower() for i in set([i.lower() for i in skillset])]
        return " ".join(req_skills)

    def get_cosine(self, text):
        words = self.WORD.findall(text)
        vec2 = self.Counter(words)
        for ind, vec1 in enumerate(self.counter_list):
            intersection = set(vec1.keys()) & set(vec2.keys())
            numerator = sum([vec1[x] * vec2[x] for x in intersection])
            sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
            sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
            denominator = self.math.sqrt(sum1) * self.math.sqrt(sum2)
            if not denominator:
                continue
            else:
                gen_score = float(numerator) / denominator
                if gen_score > self.max_score:
                    self.max_score = gen_score
                    self.max_index = ind
                else:
                    continue

    def fit(self, tag_id, x, y, skills, nlp, unique_tag):
        self.tag_id = tag_id
        self.y_dependent = y[:]
        self.x_inde = x[:]
        self.nlp = nlp
        self.skill_df = skills
        self.unique_tag = unique_tag
        for i in x:
            self.counter_list.append(self.Counter(self.WORD.findall(i)))

    def pred(self, x):
        self.get_cosine(x)
        self.similarity_score = list()
        temp_list = list()
        u_tag = self.unique_tag[self.max_index]
        temp_list.append(u_tag)
        temp_list.append(self.tag_id[self.max_index])
        return self.y_dependent[self.max_index], temp_list, self.max_score


class SkillSuggestionAlgorithm:
    from collections import Counter
    import math
    import re

    WORD = re.compile(r"\w+")

    def __init__(self):
        self.skills = list()
        self.profile_title = list()
        self.counter_list = list()
        self.max_score = 0
        self.max_index = 0

    def clean_text(self, text, for_embedding=False):
        import re

        RE_WSPACE = re.compile(r"\s+", re.IGNORECASE)
        RE_TAGS = re.compile(r"<[^>]+>")
        RE_ASCII = re.compile(r"[^A-Za-zÀ-ž ]", re.IGNORECASE)
        RE_SINGLECHAR = re.compile(r"\b[A-Za-zÀ-ž]\b", re.IGNORECASE)
        if for_embedding:
            RE_ASCII = re.compile(r"[^A-Za-zÀ-ž,.!? ]", re.IGNORECASE)
            RE_SINGLECHAR = re.compile(r"\b[A-Za-zÀ-ž,.!?]\b", re.IGNORECASE)
        text = re.sub(RE_TAGS, " ", text)
        text = re.sub(RE_ASCII, " ", text)
        text = re.sub(RE_SINGLECHAR, " ", text)
        text = re.sub(RE_WSPACE, " ", text)
        return text.strip(" ").lower()

    def get_cosine(self, text):
        words = self.WORD.findall(text)
        vec2 = self.Counter(words)
        for ind, vec1 in enumerate(self.counter_list):
            intersection = set(vec1.keys()) & set(vec2.keys())
            numerator = sum([vec1[x] * vec2[x] for x in intersection])
            sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
            sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
            denominator = self.math.sqrt(sum1) * self.math.sqrt(sum2)
            if not denominator:
                pass
            else:
                gen_score = float(numerator) / denominator
                if gen_score > self.max_score:
                    self.max_score = gen_score
                    self.max_index = ind
                else:
                    pass

    def fit(self, title, skills):
        self.skills = skills
        self.profile_title = title
        for i in title:
            self.counter_list.append(
                self.Counter(self.WORD.findall(i))
            )  # try to change the logic when program will be fixed

    def pred(self, x):
        import re

        self.get_cosine(x)
        skills_set = self.skills[self.max_index]
        skills_set = re.sub(r"[^\w\s]", "", skills_set)
        title_len = len(self.profile_title[self.max_index].split())
        suggested_skills = skills_set.split(" ")[title_len:-title_len]
        return suggested_skills


def detect_lang(content):
    try:
        if content is None or content == "":
            return None
        return detect(content[0:2000])
    except Exception as e:
        print(traceback.format_exc())
        return None


