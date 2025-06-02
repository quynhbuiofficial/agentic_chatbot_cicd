import os
from elasticsearch import Elasticsearch
import time
from pprint import pprint

def get_es_client(max_retries=2, sleep_time=1):
    """
        input: 
            max_retries: int | Số lần thực hiện kết nối với elasticSearch local
            sleep_time: int | Thời gian chờ sau khi mỗi lần kết nối hỏng
        output:
            es: Elasticsearch | đối tượng Elasticsearch giúp user thực hiện query
    """
    i = 0
    while i < max_retries:
        try:
            # es = Elasticsearch("http://localhost:9200")
            es = Elasticsearch(os.environ.get("ELASTICSEARCH_URL"))
            client_info = es.info()
            print("Connected to Elasticsearch! \n")
            pprint(client_info)
            return es
        except Exception:
            pprint('Could not connect to ElasticSearch, trying,,,,')
            time.sleep(sleep_time)
            i += 1
    raise ConnectionError("Failed to connect to Elasticsearch after multiple attempts.")

# get_es_client(max_retries=2, sleep_time=1)