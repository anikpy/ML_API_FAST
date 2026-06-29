# from elasticsearch import Elasticsearch
#
# # creating the connection
# es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
#
# es.indices.create(
#     index="skill-index",
#     body={
#         "settings": {"number_of_shards": 1, "number_of_replicas": 0},
#         "mappings": {
#             "properties": {
#                 "jobtitle": {"type": "text", "analyzer": "standard"},
#                 "skill": {"type": "text"},
#             }
#         },
#     },
# )
