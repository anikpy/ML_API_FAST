# import csv
# import os
#
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk
#
# # Connect to the Elasticsearch cluster
# es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
# script_dir = os.path.dirname(os.path.abspath(__file__))
# # print(script_dir)
# csv_file_path = os.path.join(script_dir, "data/title-skill.csv")
#
# with open(csv_file_path, "r") as f:
#     reader = csv.DictReader(f)
#     bulk(es, reader, index="skill-index")
