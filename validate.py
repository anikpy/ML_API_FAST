import re
import datefinder


def date_validate(input_date: str, nid_text: str) -> bool:
    """
    It takes a date in the format of dd/mm/yyyy and a string of text and returns True if the date is
    found in the text

    :param input_date: The date that you want to validate
    :type input_date: str
    :param nid_text: The text of the NID card
    :type nid_text: str
    :return: True or False
    """

    dd, mm, yyyy = 0, 0, 0
    matched_dates = list(datefinder.find_dates(nid_text))
    dd, mm, yyyy = str(input_date).split("/")
    input_date_con = yyyy + "-" + mm + "-" + dd
    input_date = list(datefinder.find_dates(str(input_date_con)))[0]

    if input_date in matched_dates:
        return True
    else:
        return False


def name_validate(name: str, nid_text: str):
    """
    It takes a name and a text, and returns True if the name is found in the text, and False if it is
    not

    :param name: The name of the person whose NID you want to validate
    :type name: str
    :param nid_text: The text of the NID
    :type nid_text: str
    :return: True or False
    """

    pattern = re.compile(name, re.IGNORECASE)
    match = pattern.search(nid_text)

    if match:
        return True
    else:
        return False


def nid_num_validate(extracted_nid_num: str, input_nid_num: str) -> bool:
    """
    Takes extracted_nid_num and input_nid_num, returns True if matches.

    :param extracted_nid_num: The NID number extracted from the image
    :type extracted_nid_num: str
    :param input_nid_num: The NID number that the user has entered
    :type input_nid_num: str
    :return: True or False
    """
    if extracted_nid_num == input_nid_num:
        return True
    else:
        return False
