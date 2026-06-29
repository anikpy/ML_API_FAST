import re
from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, Response
from ExtractInfo.extract_info import extract_skills, extract_name, extract_number, extract_email, \
    extract_location, nlp_de, nlp_en
from applicationmatching_functions import text_cleaner_skills, score_generator_text, EnglishAlgorithm, en_skills, \
    languages, GermanAlgorithm, doc_to_text, pdf_to_text, score_generator_object, professional_exp_scoring
from files_of_applicationmatching import de_skills
from isofinder_functions import clean_html, tag_remover, data_quality_maintainer, detect_lang, location_acronyms, \
    vn_loc_modification, get_ad_location_vn, GetAdLocation, zip_df, is_executive_lis, is_apprenticeship_lis, \
    is_student_lis, not_executive_lis, geo_locator
from profilematchingapi_functions import ProfileMatchingAlgorithm, etag_id, ex, eskills_set, ey, eunique_tag, \
    SkillSuggestionAlgorithm, english_data, gertag_id, gerx, gery, gerunique_tag, gerskills_set
from profilepricingapi_functions import profile_info, education_rating, professional_exp_rating, viewer_info
from skillMatchSearch.normal_search import get_similar_skills, skills_data
from subcatSearch.clean_input import clean_title
from subcatSearch.subcat_search import get_categories, subcat_data
from vacancymatching_functions import VacancyMatchingAlgorithm, gerskills, extract_skill_clean_con
import face_recognition
import cv2
from deep_translator import GoogleTranslator
from langdetect import detect
from googletrans import Translator
from bs4 import BeautifulSoup
import numpy as np
from vision_ai_functions import draw_face_detection
import logging

app = FastAPI()


@app.post('/GetJobAdInfo/lang_detector')
async def lang_detector(request: Request):
    lang = await request.json()
    if lang is None or len(lang) == 0:
        raise HTTPException(status_code=400, detail="Please provide text")
    try:
        langs = lang['LangText']
        lang_code = detect(langs[:2000])
        return {
            "LangCode": lang_code,
        }
    except Exception as e:
        return {"LangCode": "None", "error": str(e)}


@app.post("/GetJobAdInfo/refactor_ad")
async def refactor_ad(request: Request):
    ad = await request.json()

    if not ad:
        raise HTTPException(status_code=400, detail="Empty Content, please send requests with some valid data")

    # Cleaning HTML content
    clean_con = clean_html(ad["CleanContent"])
    clean_con = clean_con.replace("\n", "")
    clean_con = clean_con.replace("\\", "")
    clean_con = clean_con.strip()
    rawdata = tag_remover(str(ad["RawContent"]))
    ad["RawContent"] = data_quality_maintainer(rawdata)
    # ad["CleanContent"] = clean_con
    lang = detect_lang(
        ad["CleanContent"]
    )
    if lang is not None and len(lang) == 2:
        ad["SourceLangCode"] = lang

    acro_loc_list = ad["JobLocation"].strip().split(" ")
    acrolen = [x for x in acro_loc_list if len(x) == 2]
    if len(acro_loc_list) == len(acrolen):
        try:
            ad["JobLocation"] = location_acronyms[acro_loc_list[0].lower()]
        except KeyError:
            ad["JobLocation"] = location_acronyms[acro_loc_list[1].lower()]
        except:
            pass

    if ad["JobLocation"] == " " or ad["JobLocation"] == "":
        return JSONResponse(ad)  # if job location is null then no need to process

    if lang == "vi":  # vietnam
        ad["JobLocation"] = vn_loc_modification(ad["JobLocation"])
        ad = get_ad_location_vn(ad)
    else:
        ad = GetAdLocation(ad)

    # * Executive job project
    input_job_title = ad["JobTitle"].encode("utf8").decode("utf8")
    stripped_job_title = re.sub(r"[^\w\s]", "", input_job_title).strip()
    job_title = " " + stripped_job_title.lower() + " "
    is_ex = False
    for title in not_executive_lis:
        if title in job_title:
            ad["IsExecutiveJob"] = False
            is_ex = True
            break
    if not is_ex:
        for title in is_executive_lis:
            if title in job_title:
                ad["IsExecutiveJob"] = True
                break
        else:
            ad["IsExecutiveJob"] = False

    # * ApprenticeshipJobUpdated
    is_apprenticeship_lis_clean = [
        file.replace("*", "").lower() for file in is_apprenticeship_lis
    ]  # cleaned * and lowered the keywords
    for (
            title
    ) in (
            is_apprenticeship_lis_clean
    ):  # checking if title is in cleaned keywords
        if title in job_title:
            ad["IsApprenticeshipJob"] = True
            break
        else:
            ad["IsaApprenticeshipJob"] = False

    # * StudentJobUpdated
    is_student_lis_clean = [
        file.replace("*", "").lower() for file in is_student_lis
    ]  # cleaned * and lowered the keywords
    for (
            title
    ) in is_student_lis_clean:  # checking if title is in cleaned keywords
        if title in job_title:
            ad["IsStudentJob"] = True
            break
        else:
            ad["IsStudentJob"] = False

    try:
        cleaned_title = clean_title([input_job_title])
        for single in cleaned_title:
            subcategories = get_categories(single, subcat_data)
            ad["JobSubCategories"] = subcategories
    except Exception as e:
        ad["JobSubCategories"] = ["No Match"]

    try:
        ContactInfo = {}
        ContactInfo["Name"] = None
        ContactInfo["CompanyName"] = ad.get("CompanyName", "")
        ContactInfo["PhoneNumber"] = ad.get("JobContactPhone")
        ContactInfo["Email"] = ad.get("JobContactEmails")
        ContactInfo["Location"] = None
        ad["ContactInfo"] = ContactInfo
    except Exception as e:
        pass

    try:
        cln_title = clean_title([input_job_title])
        for single in cln_title:
            ad['Skills'] = get_similar_skills(single, skills_data)
    except Exception as e:
        ad["Skills"] = None

    try:
        ad["ExtractedSkills"] = extract_skills(clean_con)
    except Exception:
        ad["ExtractedSkills"] = None

    return JSONResponse(ad)


# apps for vision_ai


@app.post("/vision_ai/human_face")
async def detect_human_face(ProfileImage: UploadFile = File(...)) -> JSONResponse:
    try:
        profile_image = await ProfileImage.read()
        if not profile_image:
            raise HTTPException(status_code=400, detail="ProfileImage is empty")

        profile_image_temp = np.asarray(bytearray(profile_image), dtype="uint8")
        profile_image_temp = cv2.imdecode(profile_image_temp, cv2.IMREAD_COLOR)
        profile_image_temp = cv2.cvtColor(profile_image_temp, cv2.COLOR_BGR2RGB)
        profile_image_locations = face_recognition.face_locations(profile_image_temp)

        if len(profile_image_locations) == 0:
            predictions = {"HumanFace": "False"}
        else:
            if draw_face_detection(profile_image_temp):
                predictions = {"HumanFace": "False"}
            else:
                predictions = {"HumanFace": "True"}

        return JSONResponse(content=predictions)

    except Exception as e:
        predictions = {"HumanFace": None}
        return JSONResponse(content=predictions)


@app.post("/vacancy/en_vacancy")
async def en_vacancy(request: Request):
    data = await request.json()
    if data is not None:
        job_title = data.get("JobTitle", "")
        job_content = data.get("JobContent", "")
        source_uid = data.get("SourceUID", "")
        if not job_title and not job_content:
            return {"error": "Empty string", "message": "Empty string is given"}
        else:
            try:
                if job_title is None and job_content is None:
                    predictions = {"Message": "Both field are none"}
                    return JSONResponse(predictions)
                else:
                    en_algo = VacancyMatchingAlgorithm()
                    en_algo.fit(
                        tag_id=etag_id,
                        x=ex,
                        y=ey,
                        skills=eskills_set,
                        nlp=nlp_en,
                        unique_tag=eunique_tag,
                    )
                    if job_title is None or job_title == " " or job_title == "":
                        job_title = " "
                    else:
                        if detect_lang(job_title) != "en":
                            job_title = GoogleTranslator(
                                source="auto", target="en"
                            ).translate(job_title)
                        job_title = en_algo.clean_text(job_title)
                    if job_content is None or job_content == " " or job_content == "":
                        skills = " "
                    else:
                        if detect_lang(job_content) != "en":
                            job_content = GoogleTranslator(
                                source="auto", target="en"
                            ).translate(job_content[:4990])
                        job_content = en_algo.clean_text(job_content)
                        # skills = en_algo.extract_skills(job_content)
                        skills = "".join(extract_skill_clean_con(job_content))
                    combine_text = job_title + " " + skills + " " + job_title

                    # combine_text_tokens = sent_tokenize(combine_text)

                    profe, tag_id, score = en_algo.pred(combine_text)
                    del en_algo
                    predictions = {
                        "Profession": profe,
                        "TagId": tag_id,
                        "Score": round(score * 100, 2),
                    }
                    return JSONResponse(predictions)
            except Exception as e:
                predictions = {"error": "2", "message": str(e)}
                return JSONResponse(predictions)


@app.post("/vacancy/de_vacancy")
async def de_vacancy(request: Request):
    data = await request.json()
    if data is not None:
        job_title = data.get("JobTitle", "")
        job_content = data.get("JobContent", "")
        source_uid = data.get("SourceUID", "")
        if not job_title and not job_content:
            return {"error": "Empty string", "message": "Empty string is given"}
        else:
            try:
                if job_title is None and job_content is None:
                    predictions = {"error": "1", "message": "Both field are null"}
                    return JSONResponse(predictions)
                else:
                    de_algo = VacancyMatchingAlgorithm()
                    de_algo.fit(
                        tag_id=gertag_id,
                        x=gerx,
                        y=gery,
                        skills=gerskills,
                        nlp=nlp_de,
                        unique_tag=gerunique_tag,
                    )
                    if job_content is None or job_content == " " or job_content == "":
                        skills = " "
                    else:
                        skills = "".join(extract_skill_clean_con(job_content))
                    if job_title is None or job_title == " " or job_content == "":
                        job_title = " "
                    gcombine_text = de_algo.german_clean_text(
                        job_title + " " + skills + " " + job_title
                    )
                    gprofe, gtag_id, gscore = de_algo.pred(gcombine_text)
                    del de_algo
                    predictions = {
                        "Profession": gprofe,
                        "TagId": gtag_id,
                        "Score": round(gscore * 100, 2),
                    }
                    return JSONResponse(predictions)
            except Exception as e:
                predictions = {"error": "2", "message": str(e)}
            return JSONResponse(predictions)


@app.post("/scoring/score_by_cv")
async def score_finder_cv(request: Request):
    data = await request.form()
    ignored_word = ["developer"]
    vacancy_title = data.get("VacancyTitle", None)
    vacancy_text = data.get("VacancyText", None)
    file = data["CV"]

    file_name = file.filename
    try:
        if file_name.endswith(".pdf") or file_name.endswith(".PDF"):
            profile_text = pdf_to_text(file.file)
        elif file_name.endswith(".doc"):
            html = file.file.read().decode("latin-1")
            soup = BeautifulSoup(html, "html.parser")
            profile_text = soup.get_text()
            profile_text = re.sub("\W+", " ", profile_text)
            profile_text = re.sub(r"\s", " ", profile_text)
            profile_text = re.sub("[^a-zA-Z0-9]+", " ", profile_text)
            profile_text = " ".join([x for x in profile_text.split(" ") if len(x) > 1])
            profile_text = profile_text.replace("QJ", "")
            profile_text = profile_text.replace("OJ", "")
            profile_text = profile_text.replace("CJ", "")
            profile_text = profile_text.replace("PJ", "")
            print(profile_text)
        else:
            profile_text = doc_to_text(file)
    except Exception as e:
        profile_text = "No text"

    if (profile_text == " " or profile_text is None) or (
            vacancy_text == " " or vacancy_text is None
    ):
        predictions = {"score": 0}
        return JSONResponse(content=predictions)
    else:
        try:
            fields = [profile_text, vacancy_text, vacancy_title]
            if not None in fields:
                profile_text = profile_text.lower()
                vacancy_text = vacancy_text.lower()
                vacancy_title = vacancy_title.lower()
                vacancy_title = " ".join(
                    x for x in vacancy_title.split() if x not in ignored_word
                )
                vacancy_title = re.sub(r"[^\w\s]", "", vacancy_title)
                if (
                        detect_lang(profile_text) == "en"
                        and detect_lang(vacancy_text) == "en"
                ):
                    score_text_algo = EnglishAlgorithm()
                    score_text_algo.fit(en_skills, languages)
                elif (
                        detect_lang(profile_text) == "de"
                        and detect_lang(vacancy_text) == "de"
                ):
                    score_text_algo = GermanAlgorithm()
                    score_text_algo.fit(de_skills, languages)
                else:
                    translator = Translator()
                    profile_text = translator.translate(profile_text[:4990], src="auto", dest="en").text
                    vacancy_text = translator.translate(vacancy_text[:4990], src="auto", dest="en").text
                    score_text_algo = EnglishAlgorithm()
                    score_text_algo.fit(en_skills, languages)
                matched_word = 0
                vacancy_title_list = vacancy_title.split(" ")
                for word in vacancy_title_list:
                    if word in profile_text:
                        matched_word += 1
                if matched_word == 1:
                    weight = 0.30
                elif matched_word == 2:
                    weight = 0.45
                elif matched_word >= 3:
                    weight = 0.65
                else:
                    weight = 0
                decision_pro, profile_text = text_cleaner_skills(profile_text)
                decision_vac, vacancy_text = text_cleaner_skills(vacancy_text)
                profile_skill, pro_lang = score_text_algo.extract_skills(
                    profile_text, decision_pro
                )
                vacancy_skill, van_lang = score_text_algo.extract_skills(
                    vacancy_text, decision_vac
                )
                cosine = score_generator_text(
                    score_text_algo, profile_skill, vacancy_skill, weight
                )
                predictions = {"score": round(cosine, 2)}
                return JSONResponse(content=predictions)
            else:
                predictions = {"score": 0}
        except Exception as e:
            predictions = {"error": "2", "message": str(e)}
        return JSONResponse(content=predictions)


@app.post("/scoring/score_finder_object")
async def score_finder_object(request: Request):
    try:
        data = await request.json()
        if data is None:
            raise HTTPException(status_code=400, detail="Input data is missing")

        vacancy_text = data.get("VacancyText", "")
        vacancy_title = data.get("VacancyTitle", "")
        vacancy_loc = data.get("VacancyLocation", "")
        profile_title = data.get("ProfileTitle", "")
        profile_lang = data.get("ProfileLang", [])
        profile_loc = data.get("ProfileLoc", "")
        profile_skill = data.get("ProfileSkills", [])
        pro_exp = data.get("ProExp", [])

        profile_skill = " ".join([x.lower() for x in profile_skill])
        profile_skill = profile_skill.replace(",", "")
        profile_skill = re.sub(r" +", " ", profile_skill)

        translator = Translator()
        if not vacancy_text:
            vacancy_text = "No text"

        vacancy_text_lang = detect_lang(vacancy_text)
        profile_skill_lang = detect_lang(profile_skill) if profile_skill else "en"

        if vacancy_text_lang == "en" and profile_skill_lang == "en":
            score_text_algo = EnglishAlgorithm()
            score_text_algo.fit(en_skills, languages)
        elif vacancy_text_lang == "de" and profile_skill_lang == "de":
            score_text_algo = GermanAlgorithm()
            score_text_algo.fit(de_skills, languages)
        else:
            try:
                if profile_skill and profile_skill_lang != "en":
                    profile_skill = translator.translate(profile_skill[:4990], dest='en').text
                if vacancy_text and vacancy_text_lang != "en":
                    vacancy_text = translator.translate(vacancy_text[:4990], dest='en').text
            except Exception as e:
                raise HTTPException(status_code=500, detail="Translation service failed")

            score_text_algo = EnglishAlgorithm()
            score_text_algo.fit(en_skills, languages)

        vacancy_skill, req_lang = score_text_algo.extract_skills(vacancy_text, False)
        skills_score = score_generator_object(score_text_algo, profile_skill, vacancy_skill)
        # print(skills_score)
        lan_base_score = 1
        matched_language = [x.lower() for x in profile_lang if x.lower() in req_lang]
        lan_score = (lan_base_score * len(matched_language)) * 1.1

        professional_score = professional_exp_scoring(pro_exp) * 1.5 if pro_exp else 0
        # print(professional_score)
        # Title matching score
        title_score = len(set(profile_title.lower().split()) & set(
            vacancy_title.lower().split())) * 1.1 if profile_title and vacancy_title else 0
        # print(title_score)
        # Location matching score
        location_score = len(set(profile_loc.lower().split()) & set(
            vacancy_loc.lower().split())) * 1.5 if profile_loc and vacancy_loc else 0
        # print(location_score)
        # Calculate other scores
        others_score = lan_score + title_score + location_score + professional_score

        # Cap the scores
        skills_score = min(skills_score, 70)
        others_score = min(others_score, 30)
        total_score = skills_score + others_score
        # print(skills_score)
        predictions = {"score": round(total_score, 2)}
        return JSONResponse(content=predictions)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
