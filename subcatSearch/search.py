#
# from elasticsearch import Elasticsearch
# import ast
# from typing import List
#
#
# def get_categories(data: List[str]) -> List[str]:
#     """
#     It takes a list of job titles, searches for them in the Elasticsearch index, and returns a list of
#     job categories
#     :param data: list of job titles
#     :return: A list of lists of job categories
#     """
#     es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
#
#     # jobcat = []
#
#     index_name = "jobindex"
#
#     if not es.indices.exists(index=index_name):
#         mapping = {
#             "mappings": {
#                 "properties": {
#                     "jobtitle": {"type": "text"},
#                     "jobsubcategories": {"type": "text"}
#                 }
#             }
#         }
#         es.indices.create(index=index_name, body=mapping)
#
#     job_categories = []
#     for jobtitle_ in data:
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
#         results = es.search(index="jobindex", body=query)
#         # Get the first matching document
#         qs = results["hits"]["hits"][0]
#
#         # Append the job categories to the list
#         data = qs["_source"]["jobsubcategories"]
#         data = ast.literal_eval(data)
#     return data

# from elasticsearch import Elasticsearch
# import ast
# from typing import List
#
#
# def get_categories(data: List[str]) -> List[str]:
#     """
#     It takes a list of job titles, searches for them in the Elasticsearch index, and returns a list of
#     job categories
#     :param data: list of job titles
#     :return: A list of lists of job categories
#     """
#     es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
#
#     index_name = "jobindex"
#
#     if not es.indices.exists(index=index_name):
#         # Define the mapping for your index
#         mapping = {
#             "mappings": {
#                 "properties": {
#                     "jobtitle": {"type": "text"},
#                     "jobsubcategories": {"type": "text"}
#                 }
#             }
#         }
#
#         # Create the index with the specified mapping
#         es.indices.create(index=index_name, body=mapping)
#
#         print(f"Index '{index_name}' created successfully.")
#
#     job_categories = []  # Use a different variable to accumulate job categories
#
#     for jobtitle_ in data:
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
#         results = es.search(index=index_name, body=query)
#         print(results)
#
#         # Check if there are hits in the results
#         if "hits" in results and "hits" in results["hits"] and results["hits"]["hits"]:
#             # Get the first matching document
#             first_hit = results["hits"]["hits"][0]
#
#             # Append the job categories to the list
#             job_subcategories = first_hit["_source"]["jobsubcategories"]
#             job_subcategories = ast.literal_eval(job_subcategories)
#             job_categories.extend(job_subcategories)
#
#     return job_categories

