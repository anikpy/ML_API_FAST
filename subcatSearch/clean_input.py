"""
Methods Clean input for Job Title
"""

# importing all the dependencies
import pandas as pd
from typing import List


def fix_type(df):
    """
    It converts the JobTitle column to a string.
    :param df: The dataframe you want to fix
    :return: A dataframe with the JobTitle column as a string.
    """

    df["JobTitle"] = df["JobTitle"].astype(str)
    return df


def clean_with_regex(df):
    """
    It removes all the text in brackets, all the text after a percentage sign, all the text after a
    slash, all the text after a dash, all the text after a colon, all the text after a dot, all the text
    after a quotation mark, all the text after a bullet point, all the text after the word "für", all
    the text after the word "am", all the text after the word "per", all the text after the word "oder",
    all the text after the word "eine", all the text after the word "ein", all the text after the word
    "einer", all the text after the word "einem", all the text after the word "eines", all the text
    after the word "einen", all the text after the word "eines", all the text after the word "ein", all
    the text after the word "ein", all the text after the word "ein",
    :param df: the dataframe to be cleaned
    :return: A dataframe with the cleaned job titles.
    """

    pattern = r"^(\(.*?\)|\[.*?\])"
    df["JobTitle"] = df["JobTitle"].str.replace(pattern, "", regex=True).str.strip()

    pattern = r"(\(.*?\)|\[.*?\]).*"
    df["JobTitle"] = df["JobTitle"].str.replace(pattern, "", regex=True).str.strip()

    pattern = r"((\d\d%? ?- ?)?\d\d\d? ?%|\d?\d%? ?[-à] ?).*"
    df["JobTitle"] = df["JobTitle"].str.replace(pattern, "", regex=True).str.strip()

    pattern = r"[\/*-:·]+ ?(in(nen)?|n|mann|r|frau|ne)\b"
    df["JobTitle"] = (
        df["JobTitle"].str.replace(pattern, "", regex=True, case=False).str.strip()
    )

    pattern = r"(\b[hfwmde]{1,2} ?[\/|] ?([hfwmde] ?[\/|] ?)?[hfwmde]{1,2}\b).*"
    df["JobTitle"] = (
        df["JobTitle"].str.replace(pattern, "", regex=True, case=False).str.strip()
    )

    pattern = r"(\bfür|[FH]{2}\b).*"
    df["JobTitle"] = (
        df["JobTitle"].str.replace(pattern, "", regex=True, case=False).str.strip()
    )

    pattern = r"[\W_]+$|^[\W_]+"
    df["JobTitle"] = df["JobTitle"].str.replace(pattern, "", regex=True).str.strip()

    pattern = r"\"|«|·"
    df["JobTitle"] = df["JobTitle"].str.replace(pattern, "", regex=True).str.strip()

    pattern = r"(\bein\*?e?\b)|(\bca\.*\b)|(\boder\b)|(\bcontract\b)"
    df["JobTitle"] = (
        df["JobTitle"].str.replace(pattern, "", regex=True, case=False).str.strip()
    )

    # pattern = r"(\bam|per\b).*"
    pattern = r"(\bam|\bper\b)[^\s]*\s*"

    df["JobTitle"] = df["JobTitle"].str.replace(pattern, "", regex=True).str.strip()

    return df


def clean_title(data: List[str]) -> List[str]:
    """
    1. Create a dataframe from the input data
    2. Fix the type of the dataframe
    3. Clean the dataframe with regex
    4. Return the cleaned data as a list
    :param data: a list of job titles
    :return: A list of strings
    """

    df = pd.DataFrame(data, columns=["JobTitle"])

    df = fix_type(df)
    df = clean_with_regex(df)
    cleaned = df["JobTitle"].tolist()
    return cleaned

