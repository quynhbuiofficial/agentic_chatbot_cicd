from elasticsearch import Elasticsearch
from tqdm import tqdm
from pprint import pprint
import json
import torch
from sentence_transformers import SentenceTransformer
from typing import List

class IndexData:
    def __init__(self, es: Elasticsearch):
        print("[LOG]: INDEX DATA")
        self.es = es
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2").to(device)
        

    def index_data(self, documents: list[dict], INDEX_NAME: str):
        """
            input:
                documents: list[dict] | chứa thông tin các nodes vừa mới parser từ pdf sang doc và chunking.
                INDEX_NAME: str |
        """
        _ = self._delete_index(INDEX_NAME=INDEX_NAME)
        _ = self._create_index(INDEX_NAME=INDEX_NAME)
        _ = self._insert_documents(documents=documents, INDEX_NAME=INDEX_NAME)
        # count_response = es.count(index=INDEX_NAME_PDF)
        # print("Số tài liệu trong index:", count_response["count"])
    
    def _delete_index(self, INDEX_NAME: str):
        self.es.indices.delete(index=INDEX_NAME, ignore_unavailable=True)

    def _create_index(self, INDEX_NAME: str):
        """
            input:
                self, INDEX_NAME | 
            main:
                hàm thực hiện tạo indices, để có thể truyền các docs vào elsearch 1 cách chính xác các trường dữ liệu.

        """
        return self.es.indices.create(
            index=INDEX_NAME,
            body = {
                "mappings": {
                    "properties":{
                        "embedding_field":{
                            "type": "dense_vector"
                        }
                    }
                },
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "default": {                                # đặt default để esearch áp dụng tokenizer ngram lên tất cả các field.
                                "type": "custom",
                                'tokenizer': "n_gram_tokenizer",
                                "filter": ["lowercase"]                 # Chuyển thành chữ thường khi lưu + khi search chuyển truy vấn thành chữ thường https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-lowercase-tokenfilter.html
                            }
                        },
                        "tokenizer":{
                            "n_gram_tokenizer": {
                                "type": "edge_ngram",
                                "min_gram": 1,
                                "max_gram": 20,
                                "token_chars": ['letter', 'digit']
                            }
                        }
                    }
                }
            }
        )

    def _insert_documents(self, documents: List[dict], INDEX_NAME: str):
        """
            input:
                documents: list[dict] | chứa thông tin các nodes vừa mới parser từ pdf sang doc và chunking.
                INDEX_NAME: str |
            main:
                hàm thực hiện truyền các node vào elasticSearch bằng bulk.
        """
        if not self.es.indices.exists(index=INDEX_NAME):
            self._create_index(INDEX_NAME=INDEX_NAME)
        operations = []
        for doc in tqdm(documents, total=(len(documents)), desc='Indexing documents'):
            operations.append({'index': {'_index': INDEX_NAME}})
            operations.append({
                'title': doc['title'],
                'content': doc['content'],
                'collection_date': doc['collection_date'],
                "embedding_field": self.model.encode(doc['content'])
            })
        return self.es.bulk(operations=operations, refresh=True)

