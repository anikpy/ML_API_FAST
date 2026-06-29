# """
# Searches Skill based on JobTitle
# """
#
# from elasticsearch import Elasticsearch
# from typing import List
#
#
# def get_skill(data: List[str]) -> List[str]:
#     """
#     It takes a list of job titles, searches for them in the Elasticsearch index, and returns a list of
#     job skills
#     :param data: list of job titles
#     :return: A list of lists of job skills
#     """
#
#     # jobcat = []
#     for jobtitle_ in data:
#         # Connect to the Elasticsearch client
#         es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
#
#         # Define the query
#         query = {
#             "query": {
#                 "match": {
#                     "jobtitle": {
#                         "query": jobtitle_,
#                         "analyzer": "standard",
#                         "fuzziness": 2,
#                         "max_expansions": 50,
#                         "prefix_length": 0,
#                         "fuzzy_transpositions": True,
#                     }
#                 }
#             }
#         }
#
#         # Execute the search
#         results = es.search(index="skill-index", body=query)
#
#         # Get the first matching document
#         qs = results["hits"]["hits"][0]
#
#         # Append the job categories to the list
#         skill = qs["_source"]["skill"]
#         skillList = list(skill.split(","))
#         strippedSkillList = list(map(str.strip, skillList))
#
#         return strippedSkillList
