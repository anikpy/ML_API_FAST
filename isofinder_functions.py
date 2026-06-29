import copy
import lxml
from lxml.html.clean import Cleaner
import pandas as pd
import lxml.html.clean
from bs4 import BeautifulSoup
import locationtagger
from geopy.geocoders import Nominatim
import traceback
from langdetect import detect, DetectorFactory
from lxml.html.clean import Cleaner
import re
import lxml.html
import lxml.html.clean
import requests


# # Lazy loading function for Excel files
# def lazy_load_parquet(file_path):
#     try:
#         return pd.read_parquet(file_path)
#     except Exception as e:
#         print(f"Error loading file {file_path}: {e}")
#         return None
#
#
# def get_zip_df():
#     return lazy_load_parquet("Data/switz_postal_code.parquet")
#
#
# def get_region_df():
#     return lazy_load_parquet("Data/switz_region.parquet")
#
#
# def get_is_executive_df():
#     lst = lazy_load_parquet("Data/keywordsForExecutive.parquet")
#     return [item for sublist in lst.values.tolist() for item in sublist]
#
#
# def get_not_executive_df():
#     df = lazy_load_parquet("Data/keywordsForNotExecutive.parquet")
#     return [item for sublist in df.values.tolist() for item in sublist]
#
#
# def get_sector_df():
#     return lazy_load_parquet("Data/JobSectorDataset.parquet")
#
#
# def get_job_categories_df():
#     return lazy_load_parquet("Data/JobCategories.parquet")
#
#
# def get_is_apprenticeship_df():
#     df = lazy_load_parquet("Data/keywordsForApprenticeship.parquet")
#     return [item for sublist in df.values.tolist() for item in sublist]
#
#
# def get_is_student_df():
#     df = lazy_load_parquet("Data/keywordsForStudent.parquet")
#     return [item for sublist in df.values.tolist() for item in sublist]
#
#
# def get_label_cat_df():
#     return lazy_load_parquet("Data/JobLabelCategoryDataset.parquet")
#
#
# def get_title_cat_df():
#     return lazy_load_parquet("Data/Cleanjobcategorydata.parquet")
#
#
# zip_df = get_zip_df()
# region_df = get_region_df()
# is_executive_lis = get_is_executive_df()
# not_executive_lis = get_not_executive_df()
# sector_df = get_sector_df()
# job_categories_df = get_job_categories_df()
# is_apprenticeship_lis = get_is_apprenticeship_df()
# is_student_lis = get_is_student_df()
# label_cat_df = get_label_cat_df()
# title_cat_df = get_title_cat_df()

class DatasetLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_datasets()
        return cls._instance

    def load_datasets(self):
        self.zip_df = self.lazy_load_parquet("Data/switz_postal_code.parquet")
        self.region_df = self.lazy_load_parquet("Data/switz_region.parquet")
        self.is_executive_lis = self.get_is_executive_df()
        self.not_executive_lis = self.get_not_executive_df()
        self.sector_df = self.lazy_load_parquet("Data/JobSectorDataset.parquet")
        self.job_categories_df = self.lazy_load_parquet("Data/JobCategories.parquet")
        self.is_apprenticeship_lis = self.get_is_apprenticeship_df()
        self.is_student_lis = self.get_is_student_df()
        self.label_cat_df = self.lazy_load_parquet("Data/JobLabelCategoryDataset.parquet")
        self.title_cat_df = self.lazy_load_parquet("Data/Cleanjobcategorydata.parquet")

    def lazy_load_parquet(self, file_path):
        try:
            return pd.read_parquet(file_path)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return None

    def get_is_executive_df(self):
        lst = self.lazy_load_parquet("Data/keywordsForExecutive.parquet")
        return [item for sublist in lst.values.tolist() for item in sublist]

    def get_not_executive_df(self):
        df = self.lazy_load_parquet("Data/keywordsForNotExecutive.parquet")
        return [item for sublist in df.values.tolist() for item in sublist]

    def get_is_apprenticeship_df(self):
        df = self.lazy_load_parquet("Data/keywordsForApprenticeship.parquet")
        return [item for sublist in df.values.tolist() for item in sublist]

    def get_is_student_df(self):
        df = self.lazy_load_parquet("Data/keywordsForStudent.parquet")
        return [item for sublist in df.values.tolist() for item in sublist]

    def get_zip_df(self):
        return self.zip_df

    def get_region_df(self):
        return self.region_df

    def get_sector_df(self):
        return self.sector_df

    def get_job_categories_df(self):
        return self.job_categories_df

    def get_label_cat_df(self):
        return self.label_cat_df

    def get_title_cat_df(self):
        return self.title_cat_df


# Usage
loader = DatasetLoader()
zip_df = loader.get_zip_df()
region_df = loader.get_region_df()
is_executive_lis = loader.get_is_executive_df()
not_executive_lis = loader.get_not_executive_df()
sector_df = loader.get_sector_df()
job_categories_df = loader.get_job_categories_df()
is_apprenticeship_lis = loader.get_is_apprenticeship_df()
is_student_lis = loader.get_is_student_df()
label_cat_df = loader.get_label_cat_df()
title_cat_df = loader.get_title_cat_df()

DetectorFactory.seed = 0

location_acronyms = {
    "nw": "nidwalden",
    "be": "bern",
    "BE": "bern/berne",
    "zh": "zürich",
    "lu": "luzern",
    "ur": "uri",
    "sz": "schwyz",
    "gl": "glarus",
    "zg": "zug",
    "fr": "freiburg",
    "FR": "baden-württemberg",
    "so": "solothurn",
    "bl": "basel",
    "BS": "basel-stadt",
    "bs": "basel",
    "sh": "schaffhausen",
    "ar": "appenzell",
    "ai": "appenzell",
    "AI": "appenzell innerrhoden",
    "sg": "sankt gallen",
    "gr": "graubunden",
    "ag": "aargau",
    "tg": "thurgau",
    "ti": "ticino",
    "vd": "vaud",
    "vs": "valais",
    "GR": "graubünden/grischun/grigioni",
    "ne": "neuchatel",
    "NE": "neuchâtel",
    "ge": "geneva",
    "GE": "genève",
    "ju": "jura",
    "ow": "obwalden sarnen",
    "ow": "obwalden",
    "ch": "switzerland",
    "FR": "fribourg/freiburg",
}
location_key_abre = list(location_acronyms.keys())
location_value = list(location_acronyms.values())


def clean_html(text):
    try:
        text = text.replace("<<", "").replace(">>", "").replace("&nbsp", "").replace("\xa0", "")
        doc = lxml.html.fromstring(text)
        cleaner = lxml.html.clean.Cleaner(style=True)
        doc = cleaner.clean_html(doc)
        text = doc.text_content()
        RE_WSPACE = re.compile(r"\s+", re.IGNORECASE)
        RE_TAGS = re.compile(r"<[^>]+>")
        text = re.sub(RE_TAGS, " ", text)
        text = re.sub(RE_WSPACE, " ", text)
        text = text.replace("&nbsp", "")
        text = text.replace("\xa0", "")
        return text.strip(" ")
    except:
        return text


# Define the cache
# def geo_locator(query):
#     try:
#         loc_list = []
#         if query is None or query == "" or query.strip() == "":
#             return None
#         else:
#             query = query.split("/")[-1]
#             query = query.replace(" ", "+")
#             app = Nominatim(user_agent="anik")
#             loc = app.geocode(query, addressdetails=True)
#             loc_list.append(loc.raw)
#             return loc_list
#     except Exception as e:
#         print(f"Nominatim is not working: {e}")

def geo_locator(query):
    try:
        query = query.split("/")[-1]
        query = query.replace(" ", "+")
        url = f"https://nomin.jobdesk.com/nominatim/search.php?addressdetails=1&q={query}&format=json&limit=1"
        response = requests.get(url)
        if response.status_code == 200:
            loc = response.json()
            return loc
    except Exception as e:
        print(f"Nominatim is not working: {e}")

# def geo_locator(query):
#     try:
#         if query is None or query.strip() == "":
#             return None
#         query = query.split("/")[-1]
#         query = query.replace(" ", "+")
#         url = f"https://nomin.jobdesk.com/search.php?addressdetails=1&q={query}&format=json&limit=1"
#         response = requests.get(url)
#         if response.status_code == 200:
#             return response.json()
#     except Exception as e:
#         print(f"Nominatim is not working: {e}")


def get_ad_location_vn(ad):
    try:
        if ad is None or "JobLocation" not in ad or ad["JobLocation"] is None:
            return ad

        loc_res = geo_locator(ad["JobLocation"])
        if not loc_res:
            return ad

        loc_data = loc_res[0]
        address = loc_data.get("address", {})
        loc = None

        for addr_type in ["place", "town", "city", "suburb", "region", "village"]:
            if addr_type in address:
                loc = address[addr_type]
                if addr_type in ["town", "city", "suburb"]:
                    ad["JobLocationCity"] = loc

                break

        if "state" in address:
            state = address["state"]
            ad["JobLocationLocality"] = state
            try:
                location_index = location_value.index(state.lower())
                ad["JobLocationState"] = location_key_abre[location_index].upper()
            except ValueError:
                ad["JobLocationState"] = state.upper()

        if "country" in address:
            ad["JobLocationCountry"] = address["country"]
            loc = address["country"]

        if "country_code" in address:
            ad["JobLocationCountryCode"] = address["country_code"]
            ad["JobLocationText"] = ad["JobLocation"]
            ad["JobLocation"] = loc

        post_code = zip_df.loc[zip_df.Location == ad.get("JobLocationText", "").lower(), "PostCode"].values.tolist()
        ad["JobLocationPostalCode"] = str(post_code[0]) if post_code else None

        if ad["JobLocationPostalCode"] is None and "postcode" in address:
            ad["JobLocationPostalCode"] = str(address["postcode"])

        region_lis = []

        if "JobLocationState" in ad:
            region = region_df.loc[region_df.Value == ad["JobLocationState"].upper(), "RegionCode"].tolist()
            region_lis.append(region[0]) if region else None

        if ad["JobLocationPostalCode"] is not None:
            region = region_df.loc[region_df.Value == ad["JobLocationPostalCode"], "RegionCode"].tolist()
            region_lis.append(region[0]) if region else None

        if "JobLocation" in ad:
            loca = ad["JobLocation"].upper()
            region = region_df.loc[region_df.Value == loca, "RegionCode"].tolist()
            region_lis.append(region[0]) if region else None

        ad["GeoLat"] = loc_data["lat"]
        ad["GeoLong"] = loc_data["lon"]
        ad["JobLocationRegions"] = list(set(region_lis))

        ad["JobTitle"] = clean_html(ad["JobTitle"])
        ad["CompanyName"] = clean_html(ad.get("CompanyName", ""))

    except Exception as e:
        print(traceback.format_exc())

    return ad


def detect_lang(content):
    try:
        if content is None or content == "":
            return None
        return detect(content[0:2000])
    except Exception as e:
        print(traceback.format_exc())
        return None


def location_tagger_tr(text):
    if not isinstance(text, str):  # Check if text is a string
        return ""
    if text == "" or text == " ":
        text = "MehdiHasanBal"
    else:
        text = text
    text = re.sub(r"\([^()]*\)", "", text)
    text = text.strip(" ")
    copy_text = text
    # text = GoogleTranslator(source='auto', target='en').translate(text)
    place_entity = locationtagger.find_locations(text=text)
    country = place_entity.countries
    regions = place_entity.regions
    city = place_entity.cities
    country_name = ""
    city_name = ""
    region_name = ""
    if len(country) > 0:
        country_name = country[0]
    elif len(regions) > 0:
        city_name = regions[0]
        region_name = regions[0]
    elif len(city) > 0:
        city_name = city[0]
    else:
        country_name = ""
        splited = copy_text.split(" ")
        if len(splited) == 1:
            city_name = copy_text
        if len(splited) > 1:
            city_name = splited[-1]
    location = region_name + " " + city_name + " " + country_name
    return location.strip(" ")


def vn_loc_modification(loc_text):
    if not isinstance(loc_text, str):  # Check if loc_text is a string
        return ""
    not_dupli_loc = list()
    loc_text = re.sub(r"\([^()]*\)", "", clean_html(loc_text))
    loc_text = "".join([x for x in loc_text if not x.isdigit()])
    [not_dupli_loc.append(x) for x in loc_text.split(" ") if x not in not_dupli_loc]
    loc_text = " ".join(not_dupli_loc)
    loc_text = re.sub(" +", " ", loc_text)
    loc_text = loc_text.strip(" ")
    lis = loc_text.split(",")
    if len(lis) == 1:
        loc_text = " ".join(loc_text.split(" ")[-4:])
    else:
        loc_text = " ".join(lis[-2:])
    return loc_text


def tag_remover(text):
    try:
        soup = BeautifulSoup(text, "lxml")
        for a in soup.findAll("a"):
            a.replaceWithChildren()
        for a in soup.findAll("i"):
            a.replaceWithChildren()
        for empty in soup.find_all():
            if len(empty.get_text(strip=True)) == 0:
                empty.extract()
        for s in soup.select("select"):
            s.extract()
        return str(soup)
    except:
        return text


def data_quality_maintainer(text):
    try:
        text2 = str(text)
        text2 = text2.replace("&ZeroWidthSpace;", " ")
        text2 = text2.replace("&amp;ZeroWidthSpace;", " ")
        css_seletor = [
            ".class",
            ":active",
            "::after",
            "::before",
            ":checked",
            ":default",
            ":disabled",
            ":empty",
            "::selection",
            ":root",
            "::marker",
            "::placeholder",
            "::marker",
        ]
        image_tag = re.compile(r"<img.*?/>")
        text2 = re.sub(image_tag, "", text2)
        iframe_starting_tag = re.compile(r"<iframe.*?>")
        text2 = re.sub(iframe_starting_tag, "", text2)
        iframe_ending_tag = re.compile(r"</iframe.*?>")
        text2 = re.sub(iframe_ending_tag, "", text2)
        input_tag = re.compile(r"<input.*?>")
        text2 = re.sub(input_tag, "", text2)
        text2 = re.sub(" +", " ", text2)
        text2 = list(text2)
        for ind, val in enumerate(text2):
            if val == "n":
                try:
                    space = text2[ind + 1] == " "
                    left_angle = text2[ind - 1] == ">"
                except:
                    space = False
                    left_angle = False
            else:
                continue
            if space == True and left_angle == True:
                del text2[ind]

        text2 = " ".join(
            [x for x in ("".join(text2).split(" ")) if x.strip() not in css_seletor]
        )
        text2 = text2.replace("#ffffff", "")
        text2 = text2.replace(" t ", "")
        text2 = Cleaner(style=True).clean_html(text2)
        return text2
    except:
        return text


def GetDefaultLocationData(ad):
    try:
        if ad is None or "JobLocation" not in ad or ad["JobLocation"] is None:
            return ad

        region_lis = []
        if ad["JobLocation"]:
            try:
                region = region_df.loc[region_df.Value == ad["JobLocation"], "RegionCode"].tolist()
                region_lis.extend(region)
            except Exception as e:
                print("Error occurred during region lookup: %s", e)

        ad["JobLocationRegions"] = list(set(region_lis))
    except Exception as e:
        print("An error occurred: %s", e)

    ad["JobLocationText"] = ad.get("JobLocation", "")
    ad["JobLocationCountryCode"] = ad.get("SourceCountry", "")
    return ad


# def GetAdLocation(ad):
#     try:
#         prohibited_locations = ["Carrière", "Rue", "Gare", "Laufen", "Suisse", "TBD", "Global", "International",
#                                 "Corporate", "Hechtackerstrasse", "l'Industrie", "chemin des Aulx", "Horgen",
#                                 "Not Specified", "Milan", "Fahweidstrasse", "Grossraum", "Bezirke"]
#
#         ignored_words = ["wing", "location", "Railway", "Station", "chem", "des", "sports", "chemin", "des", "aulx",
#                          "forel", "l'industrie", "reckenholz", "road", "deutschschweiz", "not", "specified", "any",
#                          "region", "home", "based", "unavailable", "anywhere", "in", "others", "other", "tbd",
#                          "global", "international", "corporate", "not specified", "milan", "false", "false",
#                          "Address", "Cor.", "3rd", "Ave.", "MEZ", "bis", "dahin"]
#
#         allowed_words = ["Bienne", "romande", "St. Gallen", "Dorking", "Süßen", "Chur", "St. Moritz",
#                          "Plan-les-Ouates"]
#
#         if "JobLocation" in ad:
#             loc_text = re.sub(r"\([^()]*\)", "", clean_html(ad["JobLocation"]))
#             loc = copy.deepcopy(loc_text)
#
#             if any(ele in loc_text for ele in allowed_words):
#                 resultwords = " ".join([word for word in loc.split(" ") if word.lower() not in ignored_words])
#                 loc_text = resultwords.strip(" ")
#                 loc_res = geo_locator(loc_text)
#
#             elif not any(ele in loc.replace("!@#$%^&*()[]{};:,./<>?\|`~-=_+", " ") for ele in prohibited_locations):
#                 resultwords = " ".join([word for word in re.split(r"\W+", loc)
#                                         if word.lower().strip(" ") not in ignored_words and len(word) > 2])
#                 loc_text = resultwords.strip(" ")
#                 loc_res = geo_locator(loc_text)
#
#             else:
#                 resultwords = [word for word in re.split("\W+", loc)
#                                if word.lower().strip(" ") not in ignored_words and len(word) > 2]
#                 loc_text = " ".join(resultwords)
#                 loc_text = loc_text.strip(" ")
#                 location = location_tagger_tr(loc_text)
#                 if len(location) == 0:
#                     location = " ".join([x for x in loc.split(" ") if x not in prohibited_locations])
#                     location = location_tagger_tr(location)
#                 loc_res = geo_locator(location)
#
#             if loc_res:
#                 loc_data = loc_res[0]
#                 if loc_data and "address" in loc_data:
#                     address = loc_data["address"]
#                     loc = None
#
#                     if address:
#                         for key in ["place", "town", "city", "suburb", "region", "village"]:
#                             if key in address:
#                                 loc = address[key]
#                                 if key in ["town", "city", "suburb"]:
#                                     ad["JobLocationCity"] = loc
#                                 break
#
#                         if "state" in address:
#                             ad["JobLocationLocality"] = address["state"]
#                             try:
#                                 location_index = location_value.index(address["state"].lower())
#                                 state_abbreviation = location_key_abre[location_index]
#                                 ad["JobLocationState"] = state_abbreviation.upper()
#                             except ValueError:
#                                 ad["JobLocationState"] = address["state"]
#
#                             if not loc:
#                                 loc = address["state"]
#
#                         if "country" in address:
#                             ad["JobLocationCountry"] = address["country"]
#                             if not loc:
#                                 loc = address["country"]
#
#                         if "country_code" in address:
#                             ad["JobLocationCountryCode"] = address["country_code"]
#                             ad["JobLocationText"] = ad["JobLocation"]
#                             ad["JobLocation"] = loc
#
#                         try:
#                             post_code = zip_df.loc[zip_df.Location == ad["JobLocationText"].lower()]
#                             ad["JobLocationPostalCode"] = str(list(post_code.PostCode)[0])
#                         except Exception:
#                             ad["JobLocationPostalCode"] = None
#
#                         if not ad["JobLocationPostalCode"]:
#                             ad["JobLocationPostalCode"] = str(address.get("postcode", None))
#
#                     region_lis = []
#
#                     if "JobLocationState" in ad:
#                         try:
#                             region = region_df.loc[region_df.Value == ad["JobLocationState"], "RegionCode"].tolist()
#                             region_lis.append(region[0])
#                         except Exception:
#                             pass
#
#                     if ad["JobLocationPostalCode"]:
#                         try:
#                             region = region_df.loc[region_df.Value == ad["JobLocationPostalCode"], "RegionCode"].tolist()
#                             region_lis.append(region[0])
#                         except Exception:
#                             pass
#
#                     if "JobLocation" in ad:
#                         try:
#                             region = region_df.loc[region_df.Value == ad["JobLocation"], "RegionCode"].tolist()
#                             region_lis.append(region[0])
#                         except Exception:
#                             pass
#
#                     ad["GeoLat"] = loc_data.get("lat", None)
#                     ad["GeoLong"] = loc_data.get("lon", None)
#                     ad["JobLocationRegions"] = list(set(region_lis))
#
#         else:
#             ad = GetDefaultLocationData(ad)
#
#     except Exception as e:
#         print(traceback.format_exc())
#     return ad

def process_location_text(loc_text, ignored_words, prohibited_locations, allowed_words):
    loc = copy.deepcopy(loc_text)

    if any(ele in loc_text for ele in allowed_words):
        resultwords = " ".join([word for word in loc.split(" ") if word.lower() not in ignored_words])
        loc_text = resultwords.strip(" ")
    elif not any(ele in loc.replace("!@#$%^&*()[]{};:,./<>?\|`~-=_+", " ") for ele in prohibited_locations):
        resultwords = " ".join([word for word in re.split(r"\W+", loc)
                                if word.lower().strip(" ") not in ignored_words and len(word) > 2])
        loc_text = resultwords.strip(" ")
    else:
        resultwords = [word for word in re.split("\W+", loc)
                       if word.lower().strip(" ") not in ignored_words and len(word) > 2]
        loc_text = " ".join(resultwords)
        loc_text = loc_text.strip(" ")

    return loc_text


def GetAdLocation(ad):
    try:
        prohibited_locations = ["Carrière", "Rue", "Gare", "Laufen", "Suisse", "TBD", "Global", "International",
                                "Corporate", "Hechtackerstrasse", "l'Industrie", "chemin des Aulx", "Horgen",
                                "Not Specified", "Milan", "Fahweidstrasse", "Grossraum", "Bezirke"]

        ignored_words = ["wing", "location", "Railway", "Station", "chem", "des", "sports", "chemin", "des", "aulx",
                         "forel", "l'industrie", "reckenholz", "road", "deutschschweiz", "not", "specified", "any",
                         "region", "home", "based", "unavailable", "anywhere", "in", "others", "other", "tbd",
                         "global", "international", "corporate", "not specified", "milan", "false", "false",
                         "Address", "Cor.", "3rd", "Ave.", "MEZ", "bis", "dahin"]

        allowed_words = ["Bienne", "romande", "St. Gallen", "Dorking", "Süßen", "Chur", "St. Moritz",
                         "Plan-les-Ouates"]

        if "JobLocation" in ad:
            loc_text = re.sub(r"\([^()]*\)", "", clean_html(ad["JobLocation"]))

            loc_text = process_location_text(loc_text, ignored_words, prohibited_locations, allowed_words)

            loc_res = geo_locator(loc_text)

            if loc_res:
                loc_data = loc_res[0]
                if loc_data and "address" in loc_data:
                    address = loc_data["address"]
                    loc = None

                    if address:
                        for key in ["place", "town", "city", "suburb", "region", "village"]:
                            if key in address:
                                loc = address[key]
                                if key in ["town", "city", "suburb"]:
                                    ad["JobLocationCity"] = loc
                                break

                        if "state" in address:
                            ad["JobLocationLocality"] = address["state"]
                            try:
                                location_index = location_value.index(address["state"].lower())
                                state_abbreviation = location_key_abre[location_index]
                                ad["JobLocationState"] = state_abbreviation.upper()
                            except ValueError:
                                ad["JobLocationState"] = address["state"]

                            if not loc:
                                loc = address["state"]

                        if "country" in address:
                            ad["JobLocationCountry"] = address["country"]
                            if not loc:
                                loc = address["country"]

                        if "country_code" in address:
                            ad["JobLocationCountryCode"] = address["country_code"]
                            ad["JobLocationText"] = ad["JobLocation"]
                            ad["JobLocation"] = loc

                        try:
                            post_code = zip_df.loc[zip_df.Location == ad["JobLocationText"].lower()]
                            ad["JobLocationPostalCode"] = str(list(post_code.PostCode)[0])
                        except Exception:
                            ad["JobLocationPostalCode"] = None

                        if not ad["JobLocationPostalCode"]:
                            ad["JobLocationPostalCode"] = str(address.get("postcode", None))

                    region_lis = []

                    if "JobLocationState" in ad:
                        try:
                            region = region_df.loc[region_df.Value == ad["JobLocationState"], "RegionCode"].tolist()
                            region_lis.append(region[0])
                        except Exception:
                            pass

                    if ad["JobLocationPostalCode"]:
                        try:
                            region = region_df.loc[region_df.Value == ad["JobLocationPostalCode"], "RegionCode"].tolist()
                            region_lis.append(region[0])
                        except Exception:
                            pass

                    if "JobLocation" in ad:
                        try:
                            region = region_df.loc[region_df.Value == ad["JobLocation"], "RegionCode"].tolist()
                            region_lis.append(region[0])
                        except Exception:
                            pass

                    ad["GeoLat"] = loc_data.get("lat", None)
                    ad["GeoLong"] = loc_data.get("lon", None)
                    ad["JobLocationRegions"] = list(set(region_lis))

        else:
            ad = GetDefaultLocationData(ad)

    except Exception as e:
        print(traceback.format_exc())
    return ad

