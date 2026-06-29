import pandas as pd

lan_df = pd.read_csv("Data/world_language.csv")
languages = lan_df.name.tolist()

de_skill_df = pd.read_excel("Data/FinalGermanSkills.xlsx", engine="openpyxl")
# de_nlp = models.nlp_de_sm
de_skills = de_skill_df.skills.tolist()

# en_nlp = models.nlp_en_sm  # need to pass
en_skill_df = pd.read_excel("Data/FinalEnglishSkills.xlsx", engine="openpyxl")
en_skills = en_skill_df.skills.tolist()  # need to pass
