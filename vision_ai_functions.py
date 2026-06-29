import keras
# from tensorflow import keras
import numpy as np
import cv2
import re
import itertools
import face_recognition
import warnings
import easyocr
from keras.models import load_model

# reader = easyocr.Reader(["en"])
#
# model = keras.models.load_model("NID_Detector_CNN.h5")
# warnings.filterwarnings("ignore", category=FutureWarning)
# month_names = [
#     "jan",
#     "feb",
#     "mar",
#     "apr",
#     "may",
#     "jun",
#     "jul",
#     "aug",
#     "sept",
#     "oct",
#     "nov",
#     "dec",
#     "january",
#     "february",
#     "march",
#     "april",
#     "may",
#     "jun",
#     "july",
#     "august",
#     "september",
#     "october",
#     "november",
#     "december",
# ]
# classes = ["BD Analog", "BD Hand", "BD passport", "BD  Smart", "CH ID", "CH Passport"]
#
#
# def text_type_contact(text):
#     contact_exist = False
#     contact_list = text.split()
#     start = 0
#     stride = 1
#     founded_index = list()
#     input_length = len(contact_list)
#     kernel_size = 3
#     target_list = [
#         "gmail",
#         "email",
#         "hotmail",
#         "yahoo",
#         "com",
#         "dot",
#         "@",
#         "at",
#         "(.)",
#         ".",
#     ]
#     for i in range(0, input_length - kernel_size + 1):
#         target_found = 0
#         end = start + kernel_size
#         temp_lis = list()
#         for j in range(start, end):
#             if contact_list[j].lower() in target_list:
#                 target_found += 1
#             temp_lis.append(j)
#         if target_found > 1:
#             founded_index.append(temp_lis)
#         start += stride
#     final_list = set(list(itertools.chain(*founded_index)))
#     for i in final_list:
#         contact_list[i] = "*"
#     for i in range(0, len(contact_list)):
#         large_count = 0
#         if (
#                 len(contact_list[i]) >= 8
#         ):  # less the number is more the accurate and slower is
#             for k in target_list:
#                 if contact_list[i].find(k) > -1:
#                     large_count += 1
#             if large_count > 2:
#                 # contact_list[i] = "****"
#                 contact_exist = True
#         else:
#             pass
#     text = " ".join([x for x in contact_list])
#     text = re.sub("(?<=\*) (?=\*)", "", text)  ##
#     return text, contact_exist
#
#
# def profile_filtering(summary):
#     contact_exist = False
#     numbs = [
#         "zero",
#         "one",
#         "two",
#         "three",
#         "four",
#         "five",
#         "six",
#         "seven",
#         "eight",
#         "nine",
#     ]
#     phone_special_char = ["-", "+", "(", ")"]
#     integer = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#     tem_text = ""
#     for ind, val in enumerate(summary.split()):
#         val = val.lower()
#         if val in numbs:
#             tem_text = tem_text + " " + str(numbs.index(val))
#         else:
#             tem_text = tem_text + " " + str(val)
#     summary = re.sub("(?<=\d) (?=\d)", "", tem_text)
#     # phone number
#     for i in summary.split(" "):
#         try:
#             phone_num = re.search(
#                 r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{3})",
#                 i,
#             ).group()
#             if i.find(str(phone_num)) >= 0:
#                 ex_phone = i
#                 phone_rep = "".join(
#                     [
#                         str(word)
#                         for word in ex_phone
#                         if word.isdigit() or word in phone_special_char
#                     ]
#                 )
#                 summary = summary.replace(phone_rep, "****")
#                 contact_exist = True
#         except:
#             continue
#     r = re.compile(r"[\w\.-]+@[\w\.-]+")
#     email_rep = r.findall(summary)
#     try:
#         for mail in email_rep:
#             summary = summary.replace(mail, "****")
#             contact_exist = True
#     except:
#         pass
#     urls = re.findall("(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+", summary)
#     try:
#         for url in urls:
#             summary = summary.replace(url, "****")
#             contact_exist = True
#     except:
#         pass
#     r = re.compile(r"\B\#\w+")
#     reference_rep = r.findall(summary)
#     print(reference_rep)
#     try:
#         for reference in reference_rep:
#             print(reference)
#             summary = summary.replace(reference, "****")
#             contact_exist = True
#     except:
#         pass
#
#     # number to text conversion
#     tem_text = ""
#     sumlist = summary.split()
#     for ind, val in enumerate(sumlist):
#         val = val.lower()
#         try:
#             val = int(val)
#             if (val in integer and val < 10) and (
#                     sumlist[ind + 1] not in month_names
#             ):  # may couse error
#                 tem_text = tem_text + " " + str(numbs[int(val)])
#             else:
#                 tem_text = tem_text + " " + str(val)
#         except:
#             tem_text = tem_text + " " + str(val)
#     summary = re.sub("  +", " ", tem_text).strip()
#     return summary, contact_exist
#
#
# def name_cleaner(name):
#     # remove any digits
#     clean_input = re.sub("\d+", "", name)
#     # removes any non-word or non-whitespace character
#     clean_input = re.sub(r"[^\w\s]", "", clean_input)
#     # removes extra spaces
#     clean_input = re.sub(" +", " ", clean_input)
#     # lowered, and removed trailing and leading whitespaces
#     # last returns LIST OF WORDS
#     return clean_input.lower().strip().split(" ")
#
#
# def img_text_cleaner(text_extracted):
#     clean_input = re.sub("\d+", "", text_extracted)  # remove digit
#     clean_input = re.sub(r"[^\w\s]", "", clean_input)
#     clean_input = clean_input.replace("\n", " ")
#     clean_input = re.sub(" +", " ", clean_input)
#     return clean_input.strip().split(" ")
#
#
# def nid_detection(image):
#     """
#     a fucntion that takes an image as input and returns a tuple containing
#     a boolean value and a string. The function appears to use a machine learning
#     model to classify the input image into one of
#     three categories: "analog", "hand", or "smart".
#     """
#
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # arrange format as per keras
#     image = cv2.resize(image, (224, 224))
#     image = np.array(image) / 255
#     image = np.expand_dims(image, axis=0)
#     classes = ["analog", "hand", "smart"]
#     prediction = model.predict(image)
#     max_ind = np.argmax(prediction)
#     del image
#     if classes[max_ind] == "analog" or classes[max_ind] == "smart":
#         return True, classes[max_ind]
#     else:
#         return False, classes[max_ind]
#
#
# def find_nid_number(nid_text: str) -> str:
#     """
#     Returns NID number from nid text.
#
#     :param nid_text: The text that contains the NID number
#     :type nid_text: str
#     :return: The NID number is being returned.
#     """
#
#     pattern = r"\d{3} \d{3} \d{4}|\d{10}"
#     match = re.search(pattern, nid_text)
#
#     if match:
#         # If the regex matches, print the entire match
#         nid_number = match.group()
#         nid_number = nid_number.replace(" ", "")
#         return nid_number
#     else:
#         # If there is no match, print a message
#         return "No match found."
#
#
# def face_cropper(image):
#     """
#     takes an image as an input and returns a cropped version of the image
#     containing only the face. Uses FaceRecognition Library! output is resized to
#     224*224 pixels.
#     """
#
#     image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
#     face_locations = face_recognition.face_locations(image)
#     for face_location in face_locations:
#         top, right, bottom, left = face_location
#         face_image = image[top:bottom, left:right]
#         face_image = cv2.fastNlMeansDenoisingColored(face_image, None, 8, 8, 8, 8)
#         face_image = cv2.cvtColor(np.array(face_image), cv2.COLOR_BGR2RGB)
#         face_image = cv2.resize(face_image, (224, 224), interpolation=cv2.INTER_AREA)
#         return face_image


# model = load_model("drawingFaceDetector.h5")
Model = None


def get_draw_model():
    global Model
    if Model is None:
        Model = load_model("drawingFaceDetector.h5")
    return Model


def draw_face_detection(image):
    model = get_draw_model()
    image = cv2.resize(image, (224, 224))
    image = np.array(image) / 255
    image = np.expand_dims(image, axis=0)
    classes = ["Colorful Drawing", "Drawing face", "Real face"]
    prediction = model.predict(image)
    max_ind = np.argmax(prediction)
    del image
    if classes[max_ind] == "Colorful Drawing" or classes[max_ind] == "Drawing face":
        return True
    else:
        return False
