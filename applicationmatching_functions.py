import math
from collections import Counter
from datetime import date
import re
import lxml.html
import lxml.html.clean
import datetime
import pandas as pd
import fitz
from langdetect import detect, DetectorFactory, LangDetectException
import docx2txt

from ExtractInfo.extract_info import nlp_de, nlp_en

en_skill_df = pd.read_excel("Data/FinalEnglishSkills.xlsx", engine="openpyxl")
en_skills = en_skill_df.skills.tolist()
lan_df = pd.read_csv("Data/world_language.csv")
languages = lan_df.name.tolist()
WORD = re.compile(r"\w+")


def time_gen(inp_date):
    inp_date = inp_date.strip()
    if inp_date == "Currently Working":
        current_time = datetime.datetime.now()
        year, month, day = str(current_time).split(" ")[0].split("-")
    else:
        inp_date = inp_date.split("T")[0]
        inp_date = inp_date.split("-")
        year, month, day = inp_date
    return int(year), int(month), int(day)


def professional_exp_scoring(in_pro):
    root_score = 0
    for i in in_pro:
        exp, from_date, to_date = i.values()
        if to_date == " " or to_date == "" or to_date is None:
            to_date = "Currently Working"
        if from_date == " " or from_date == "" or from_date is None:
            from_date = "Currently Working"
            to_date = "Currently Working"
        year1, month1, day1 = time_gen(from_date)  # need to pass tuple
        year2, month2, day2 = time_gen(to_date)
        d0 = date(year1, month1, day1)
        d1 = date(year2, month2, day2)
        try:
            total_day = int(str(d1 - d0).split(" ")[0])
        except:
            total_day = 0
        total_score = 0  # fixed by us based
        base_score = 2
        if 180 >= total_day > 0:
            total_score = total_score + base_score + 2
        elif 180 < total_day >= 240:
            total_score = total_score + base_score + 4
        elif 240 < total_day >= 480:
            total_score = total_score + base_score + 6
        else:
            total_score = total_score + base_score
        root_score = root_score + total_score
    return root_score


class EnglishAlgorithm:
    def __init__(self):
        self.counter_list = []
        self.similarity_score = []
        self.skill_df = []
        self.languages = []

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

    def get_cosine(self, vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        denominator = math.sqrt(sum([vec1[x] ** 2 for x in vec1])) * math.sqrt(sum([vec2[x] ** 2 for x in vec2]))
        return float(numerator) / denominator if denominator else 0.0

    def jaccard_similarity(self, doc1, doc2):
        words_doc1 = set(doc1.lower().split())
        words_doc2 = set(doc2.lower().split())
        intersection = words_doc1.intersection(words_doc2)
        union = words_doc1.union(words_doc2)
        return float(len(intersection)) / len(union)

    def text_to_vector(self, text):
        WORD = re.compile(r"\w+")
        words = WORD.findall(text)
        return Counter(words)

    def extract_skills(self, text, decision):
        # doc = en_core_web_sm(text)
        # tokens, stop_words = doc
        # noun_chunks = []
        # current_chunk = []
        # langset = []
        # for token in tokens:
        #     if token['pos'] in {'NOUN', 'PROPN', 'ADJ'}:
        #         current_chunk.append(token['text'])
        #     else:
        #         if current_chunk:
        #             noun_chunks.append(" ".join(current_chunk))
        #             current_chunk = []
        # if current_chunk:
        #     noun_chunks.append(" ".join(current_chunk))
        # final = list(set(noun_chunks))
        # for lang in final:
        #     langset.append(lang)
        # return " ".join(final), langset
        doc = nlp_de(text)
        noun_chunks = []
        current_chunk = []
        langset = []
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
        for lang in final:
            langset.append(lang)
        return final[:30], langset

    def fit(self, skills_df, languages):
        self.skill_df = skills_df
        self.languages = languages


class GermanAlgorithm:
    WORD = re.compile(r"\w+")

    def __init__(self):
        self.counter_list = []
        self.similarity_score = []
        self.skill_df = []
        self.nlp = None
        self.languages = None

    def german_clean_text(self, text):
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

    def extract_skills(self, text, decision):
        # doc = de_core_news_md(text)
        # tokens, stop_words = doc
        # noun_chunks = []
        # current_chunk = []
        # langset = []
        # for token in tokens:
        #     if token['pos'] in {'NOUN', 'PROPN', 'ADJ'}:
        #         current_chunk.append(token['text'])
        #     else:
        #         if current_chunk:
        #             noun_chunks.append(" ".join(current_chunk))
        #             current_chunk = []
        # if current_chunk:
        #     noun_chunks.append(" ".join(current_chunk))
        # final = list(set(noun_chunks))
        # for lang in final:
        #     langset.append(lang)
        # return " ".join(final), langset
        doc = nlp_en(text)
        noun_chunks = []
        current_chunk = []
        langset = []
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
        for lang in final:
            langset.append(lang)
        return final[:30], langset

    def get_cosine(self, vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        denominator = math.sqrt(sum([vec1[x] ** 2 for x in vec1])) * math.sqrt(sum([vec2[x] ** 2 for x in vec2]))
        return float(numerator) / denominator if denominator else 0.0

    def text_to_vector(self, text):
        words = self.WORD.findall(text)
        return Counter(words)

    def fit(self, skills_df, language):
        self.skill_df = skills_df
        self.languages = language


# functions for application matching api


def single_char_checker(text):
    count = 0
    text_lis = text.split(" ")[:100]
    if len(text_lis) == 100:
        measurement = 70
    else:
        measurement = abs(len(text_lis) - 30)
    for x in text_lis:
        if len(x) == 1:
            count += 1
    if count >= measurement:
        return True
    else:
        return False


def doc_to_text(m):
    temp = docx2txt.process(m)
    resume_text = [line.replace("\t", " ") for line in temp.split("\n") if line]
    text = " ".join(resume_text)
    return text


def pdf_to_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")  # open document
    raw_text = ""
    for page in doc:
        raw_text = raw_text + " " + str(page.get_text())
    if single_char_checker(raw_text):
        raw_text = raw_text.replace(" ", "")
        raw_text = raw_text.replace(".", "")
        raw_text = raw_text.replace(",", ", ")
    full_string = re.sub(r"\n+", ". ", raw_text)
    full_string = full_string.replace("\r", ". ")
    full_string = full_string.replace("\t", " ")
    full_string = re.sub(r"\uf0b7", " ", full_string)
    full_string = re.sub(r"\(cid:\d{0,2}\)", " ", full_string)
    full_string = re.sub(r"• ", " ", full_string)
    doc.close()
    return full_string


def language_detect(content):
    # try:
    #     if not content:
    #         return "en"
    #     detected_lang = detect(content[:2000])
    #     return detected_lang if detected_lang in ["en", "de"] else "en"
    # except LangDetectException:
    #     return "en"
    try:
        if content is None or content == "":
            return None
        return detect(content[0:2000])
    except Exception as e:
        return None


def score_generator_text(score_text_algo, profile_info, vacancy_info, weight):
    profile_info_temp = set(profile_info)
    vacancy_info_temp = set(vacancy_info)
    matched_skills = " ".join([x for x in profile_info_temp if x in vacancy_info_temp])
    vacancy_skills = " ".join(vacancy_info_temp)
    matched_skills = score_text_algo.text_to_vector(matched_skills)
    vacancy_skills = score_text_algo.text_to_vector(vacancy_skills)
    cosine_score = round(
        score_text_algo.get_cosine(matched_skills, vacancy_skills) * 100, 2
    )

    ##### force logic ####
    matched_len = len(matched_skills)
    vacancy_len = len(vacancy_info_temp)
    # print('vacency len', len(vacancy_info_temp))
    # single_ratio = matched_len / vacancy_len
    # if single_ratio > 0.70:
    #     single_ratio = 0.70
    extra_skills = len(profile_info_temp) - matched_len
    # print('extra skills 1: ', extra_skills)
    # print(weight)
    if weight > 0:
        extra_score = weight * extra_skills
        # print(extra_score)
    else:
        extra_score = 0
    if extra_skills > vacancy_len:
        extra_skills = vacancy_len
        # print('extra skills 2 ',extra_skills)
    cosine = cosine_score + extra_score
    if cosine > 100:
        cosine = 100
    return cosine


def score_generator_object(score_text_algo, profile_info, vacancy_info):
    profile_info_temp = set(profile_info)
    vacancy_info_temp = set(vacancy_info)
    matched_skills = " ".join([x for x in profile_info_temp if x in vacancy_info_temp])
    vacancy_skills = " ".join(vacancy_info_temp)
    # print("Matched skills", matched_skills)
    matched_skills = score_text_algo.text_to_vector(matched_skills)
    vacancy_skills = score_text_algo.text_to_vector(vacancy_skills)
    cosine_score = round(
        score_text_algo.get_cosine(matched_skills, vacancy_skills) * 100, 2
    )

    ##### force logic ####
    matched_len = len(matched_skills)
    # print('matched len',matched_len)
    vacancy_len = len(vacancy_info_temp)
    single_ratio = (matched_len / vacancy_len) + 0.25
    # print('single Ratio:',single_ratio)
    extra_skills = len(profile_info_temp) - matched_len
    # print('extra skills 1: ', extra_skills)
    if extra_skills > vacancy_len:
        extra_skills = vacancy_len
        # print('extra skills 2 ',extra_skills)
    if extra_skills < 0:
        extra_skills = 0
    if single_ratio > 0.70:
        single_ratio = 0.70
    cosine = cosine_score + (single_ratio * extra_skills)
    if cosine > 70:
        cosine = 70
    return cosine


def text_cleaner_skills(text):
    text = re.sub("\W+", " ", text)
    text = re.sub("  +", "", text)
    decision_list = [x for x in text.split(" ") if len(x) > 30]
    if len(decision_list) > 0:
        decision = True
    else:
        decision = False
    return decision, text
