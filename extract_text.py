# import os
# import boto3
# import numpy as np
#
#
# os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
# textract = boto3.client("textract")
#
#
# def get_nid_text(image_file: np.ndarray) -> str:
#     """
#     It takes an image file, converts it to bytes, and then uses the AWS Textract API to extract the text
#     from the image
#
#     :param image_file: The image file that we want to extract text from
#     :type image_file: np.ndarray
#     :return: A string of text
#     """
#
#     image_bytes = image_file.tobytes()
#     response = textract.detect_document_text(Document={"Bytes": image_bytes})
#     nid_text = ""
#     for block in response["Blocks"]:
#         if block["BlockType"] == "LINE":
#             nid_text += block["Text"] + " "
#     return nid_text
