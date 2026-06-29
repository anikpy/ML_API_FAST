# remove_punctutation
import re
import datetime
from datetime import date
import ast


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


def professional_exp_pricing(
        in_pro,
):  # professional exp contains (exp number(from date,to date)) expect like [name,dateFrom,dateTo] #Need to use for loop
    root_price = 0
    for i in in_pro:
        exp, from_date, to_date = i
        if (len(from_date) > 3) and (
                to_date == " " or to_date == "" or to_date == "null" or to_date == "Null"
        ):
            to_date = "Currently Working"
        if (
                to_date == " " or to_date == "" or to_date == "null" or to_date == "Null"
        ) and (
                from_date == " "
                or from_date == ""
                or from_date == "null"
                or from_date == "Null"
        ):
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
        total_price = 0  # fixed by us based
        base_price = 2
        if 180 >= total_day > 0:
            total_price = total_price + base_price + 2
        elif 180 < total_day >= 240:
            total_price = total_price + base_price + 4
        elif 240 < total_day >= 480:
            total_price = total_price + base_price + 6
        else:
            total_price = total_price + base_price
        root_price = root_price + total_price
    # print('professional price', root_price)
    return root_price


def skills_pricing(skills_list):  # listof_skills_name and ratting.
    base_price = 0.5
    skills_price = 0
    skill_rate_price = 0.20
    base_lenght = 5
    if len(skills_list) > base_lenght:
        for i in skills_list:  # skills_list contains skill name and ratting
            skills_price = skills_price + base_price + (int(i[1]) * skill_rate_price)
    if skills_price > 35:
        skills_price = 35
    # print('skill_price', skills_price)
    return skills_price


def language_pricing(lanlist):
    base_len = 1
    base_price = 0.50
    total_price = 0
    if len(lanlist) > base_len:
        total_price = base_price * (len(lanlist) - base_len)
    if total_price > 2:
        total_price = 2
    # print('lan price', total_price)
    return total_price


def edu_pricing(edu_list):
    base_len = 1
    base_price = 1.5
    total_price = 0
    if len(edu_list) > base_len:
        total_price = (len(edu_list) - base_len) * base_price
    if total_price > 15:
        total_price = 15
    # print('edu price', total_price)
    return total_price


def cer_pricing(cer_list):
    base_len = 1
    base_price = 1.5
    total_price = 0
    if len(cer_list) > base_len:
        total_price = (len(cer_list) - base_len) * base_price
    if total_price > 15:
        total_price = 15
    # print('certificate_price', total_price)
    return total_price


def job_match_pro(job_num, matching_score):
    base_price_pro = 1
    base_price_score = 0.05
    total_price = (base_price_pro * int(job_num)) + (
            base_price_score * float(matching_score)
    )
    return total_price


def num_of_view(view_num):
    base_price_view = 1
    return base_price_view * int(view_num)


def professional_exp_rating(
        in_pro,
):  # professional exp contains (exp number(from date,to date)) expect like [name,dateFrom,dateTo] #Need to use for loop
    all_exp_rating = list()
    total_day = 0
    for i in in_pro:
        exp, from_date, to_date = i.values()
        if from_date is None:
            from_date = "Currently Working"
        if to_date is None:
            to_date = "Currently Working"
        year1, month1, day1 = time_gen(from_date)  # need to pass tuple
        year2, month2, day2 = time_gen(to_date)
        d0 = date(year1, month1, day1)
        d1 = date(year2, month2, day2)
        try:
            total_day = d1 - d0
            total_day = total_day.days
        except:
            total_day = 0
        if total_day < 60 and total_day > 0:
            all_exp_rating.append(0.30)
        elif 60 <= total_day and total_day < 150:
            all_exp_rating.append(0.40)
        elif 150 <= total_day and total_day < 330:
            all_exp_rating.append(0.70)
        elif total_day >= 330:
            all_exp_rating.append(0.90)
        else:
            all_exp_rating.append(0)
    max_rating = max(all_exp_rating)
    if len(in_pro) >= 3:
        max_rating = max_rating + 0.20
    if max_rating > 0.90:
        max_rating = 0.90
    return max_rating, total_day


def clear_pun(text):
    text = re.sub(r"[^\w\s]", "", text)
    text = text.replace(" ", " ")
    return text.lower()


def education_rating(edu_list, exp_days):
    EDUCATION = [
        "ba",
        "ma",
        "msc",
        "bsc",
        "be",
        "bs",
        "me",
        "mba",
        "ms",
        "btech",
        "mtech",
        "bs",
        "ca",
        "bcom",
        "mcom",
        "phd",
        "mba",
        "bba",
        "graduate",
        "postgraduate",
        "masters",
        "bachelor",
        "university",
    ]
    modified_edu = list()
    no_edu_count = 0
    for edu in edu_list:
        # first_value = list(edu.values())[0]
        # second_value = list(edu.values())[1]

        first_value = edu[0]
        second_value = edu[1]

        if first_value is None:
            first_value = "NoEdu"
            no_edu_count += 1
        if second_value is None:
            second_value = "NoEdu"
            no_edu_count += 1
        modified_edu = (
                modified_edu
                + clear_pun(first_value).split(" ")
                + second_value.lower().split(" ")
        )
    found_edu = [x for x in modified_edu if x in EDUCATION]
    if len(found_edu) > 0 or exp_days > 1080:
        return 0.5
    elif len(edu_list) * 2 == no_edu_count:
        return 0
    else:
        return 0.30


def viewer_info(view_num, like_num, id_verified, phone_verified):
    if view_num > 100:
        view_num = 100
    if like_num > 50:
        like_num = 50
    view_rating = view_num * 0.004  # max = 0.40
    like_rating = like_num * 0.008  # max = 0.40
    id_rating = 0
    phone_rating = 0
    if id_verified:
        id_rating = 0.80
    if phone_verified:
        phone_rating = 0.20
    viewer_rating = view_rating + like_rating + id_rating + phone_rating
    if viewer_rating > 2.5:
        viewer_rating = 2.5
    return viewer_rating


def profile_info(
        skills_num, experience_rating, education_rating, language_num, certificate_num
):
    if skills_num > 10:
        skills_num = 10
    if language_num > 2:
        language_num = 2
    if certificate_num > 3:
        certificate_num = 3
    skills_rating = skills_num * 0.12  # max got 1.20
    language_rating = language_num * 0.15  # max got 0.30
    certificate_rating = certificate_num * 0.10  # max got 0.30
    if experience_rating == 0.90 and certificate_rating == 0.20:
        certificate_rating = 0.30
    profile_info_rating = (
            skills_rating
            + language_rating
            + certificate_rating
            + experience_rating
            + education_rating
    )
    if profile_info_rating > 3.2:
        profile_info_rating = 3.2
    return profile_info_rating
