import re
import traceback
import pandas as pd
from langdetect import detect
from ExtractInfo.extract_info import nlp_en

gerskill_df = pd.read_excel("Data/FinalGermanSkills.xlsx", engine="openpyxl")
gerskills = gerskill_df.skills.tolist()

eskill_df = pd.read_excel("Data/FinalEnglishSkills.xlsx", engine="openpyxl")
eskills_set = eskill_df.skills.tolist()


def detect_lang(content):
    try:
        if content is None or content == "":
            return None
        return detect(content[0:200])
    except Exception as e:
        print(traceback.format_exc())
        return None


def tokenize(text):
    return re.findall(r"\b\w+\b", text)


def extract_skill_clean_con(text):
    doc = nlp_en(text)
    noun_chunks = []
    current_chunk = []
    for token in doc:
        if token.pos_ in {'NOUN', 'PROPN', 'ADJ'}:
            current_chunk.append(token.text)
        else:
            if current_chunk:
                noun_chunks.append(" ".join(current_chunk))
                current_chunk = []
    if current_chunk:
        noun_chunks.append(" ".join(current_chunk))
    final = list(set(noun_chunks))
    return final[:30]


class VacancyMatchingAlgorithm:
    import re
    from collections import Counter as Counter
    import math as math

    WORD = re.compile(r"\w+")

    def __init__(self):
        self.counter_list = list()
        self.y_dependent = list()
        self.tag_id = list()
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
        # nlp_text = self.nlp(" ".join([x.capitalize() for x in text.split(" ")]))
        # tokens = [token.text for token in nlp_text if not token.is_stop]
        # skillset = []
        # for token in tokens:
        #     token = token.lower().strip()
        #     if token in self.skill_df:
        #         if token not in skillset:
        #             skillset.append(token)
        # for token in nlp_text.noun_chunks:
        #     token = token.text.lower().strip()
        #     if token in self.skill_df:
        #         if token not in skillset:
        #             skillset.append(token)
        # req_skills = [i.lower() for i in set([i.lower() for i in skillset])]
        # return " ".join(req_skills)
        doc = nlp_en(text)
        noun_chunks = []
        current_chunk = []
        for token in doc:
            if token.pos_ in {'NOUN', 'PROPN', 'ADJ'}:
                current_chunk.append(token.text)
            else:
                if current_chunk:
                    noun_chunks.append(" ".join(current_chunk))
                    current_chunk = []
        if current_chunk:
            noun_chunks.append(" ".join(current_chunk))
        final = list(set(noun_chunks))
        return final[:30]

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

    def fit(self, tag_id, y, x, skills, nlp, unique_tag):
        self.tag_id = tag_id
        self.y_dependent = y[:]
        self.x_inde = x[:]
        self.nlp = nlp
        self.skill_df = skills
        self.unique_tag = unique_tag
        for i in x:
            self.counter_list.append(self.Counter(self.WORD.findall(i)))

    def pred(self, x):
        temp_list = list()
        self.get_cosine(x)
        u_tag = self.unique_tag[self.max_index]
        temp_list.append(u_tag)
        temp_list.append(self.tag_id[self.max_index])
        return self.y_dependent[self.max_index], temp_list, self.max_score
