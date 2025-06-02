from sentence_transformers import SentenceTransformer
import torch
torch.classes.__path__ = []

from elasticsearch import Elasticsearch

class HybridSearch:
    def __init__(self, es: Elasticsearch):
        print("[LOG]: HYBRID SEARCH")
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        #VietNamese embedding: https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2?library=sentence-transformers
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2").to(device)
        self.es = es
        print("[LOG]: DONE")

    async def lexical_search_hybrid(self, search_query: str, top_k: int, INDEX_NAME):
        """
            Hàm thực hiện lexical search.
        """
        if INDEX_NAME == 'data_law':
            query = {
                "multi_match": {
                    "query": search_query,
                    "fields": ['khoan']  
                }
            }
        else:
            query = {
                "multi_match": {
                    "query": search_query,
                    "fields": ['content', 'title']  
                }
            }
        results = self.es.search(
            index=INDEX_NAME,
            body={
                "query": query,
                "_source": {"excludes": ["embedding_field"]},                   # Loại bỏ "embedding_field" khỏi results search
                "size": top_k
            }
        )
        hits = results['hits']['hits']
        max_bm25_score = max([hit["_score"] for hit in hits], default=1.0)
        for hit in hits:
            hit['_normalized_score'] = hit['_score'] / max_bm25_score
        
        print('\n\nLEXICAL: ', len(hits))
        print('\n\nLEXICAL: ', hits)
        return hits
    
    async def semantic_search_hybrid(self, search_query: str, top_k: int, INDEX_NAME):
        """
            Hàm thực hiện Semantic search.
        """
        query = {
            "knn": {
                "field": "embedding_field",
                "query_vector": self.model.encode(search_query),
                "k": 10_000
            }
        }
        results = self.es.search(
            index=INDEX_NAME,
            body={
                "query": query,
                "_source": {"excludes": ["embedding_field"]},                   # Loại bỏ "embedding_field" khỏi results search
                "size": top_k
            }
        )
        hits = results['hits']['hits']
        max_semantic_score = max([hit["_score"] for hit in hits], default=1.0)      # cosine
        for hit in hits:
            hit['_normalized_score'] = hit['_score'] / max_semantic_score   

        # print('SEMANTIC: ', hits)
        return hits
    
    def reciprocal_rank_fusion(self, lexical_hits, semantic_hits, k=60, top_k=4):
        """
            Hàm thực hiện tổng hợp kết của của 2 phương pháp lexical search và semantic search bằng thuật toán rrf.
        """
        rrf_score = {}          # Lưu các doc và tổng điểm khi tính rrf trên từng kiểu search
        for rank, hit in enumerate(lexical_hits, start=1):
            doc_id = hit["_id"]
            score = 1 / (k + rank)
            if doc_id in rrf_score:
                rrf_score[doc_id]['rrf_score'] += score
                rrf_score[doc_id]['lexical_score'] += hit['_normalized_score']
            else:
                rrf_score[doc_id] = {
                    "dieu": hit['_source'].get('dieu', 'N/A'),
                    "khoan": hit['_source'].get('khoan', 'N/A'),
                    "content": hit['_source']['content'],
                    'semantic_score': 0,
                    'lexical_score': hit['_normalized_score'],
                    'rrf_score': score
                }

        for rank, hit in enumerate(semantic_hits, start=1):
            doc_id = hit["_id"]
            score = 1 / (k + rank)
            if doc_id in rrf_score:
                rrf_score[doc_id]['rrf_score'] += score
                rrf_score[doc_id]['semantic_score'] += hit['_normalized_score']
            else:
                rrf_score[doc_id] = {
                    "dieu": hit['_source'].get('dieu', 'N/A'),
                    "khoan": hit['_source'].get('khoan', 'N/A'),
                    "content": hit['_source']['content'],
                    'lexical_score': 0,
                    'semantic_score': hit['_normalized_score'],
                    'rrf_score': score
                }
        
        sorted_results = sorted(rrf_score.values(), key=lambda x: x['rrf_score'], reverse=True)
        final_results = sorted_results[:top_k]
        return final_results
    
    async def hybrid_search(self, search_query: str, top_k: int = 4, INDEX_NAME: str = None):
        """
            input:
                search_query: str | Câu query của người dùng được dùng làm search query để truy vấn.
                top_k: int = 4  | Số lượng tối đa kết quả truy vấn trả về.
                INDEX_NAME: str = None  | tên của index elasticsearch để thực hiện truy vấn trên index đó.
            output:
                combined_results: str | kết quả truy vấn chính xác nhất sau khi đươc tổng hợp từ 2 phương pháp trên.
        """
        lexical_hits = await self.lexical_search_hybrid(search_query, top_k=top_k, INDEX_NAME=INDEX_NAME)
        semantic_hits = await self.semantic_search_hybrid(search_query, top_k=top_k, INDEX_NAME=INDEX_NAME)
        combined_results = self.reciprocal_rank_fusion(lexical_hits=lexical_hits, semantic_hits=semantic_hits, k=60, top_k=top_k)
        print("[LOG] SERCH COMPLETE -- 1 combined_results: ", combined_results)
        return combined_results if combined_results else ['No results found']
    

# if __name__ == "__main__":
#     print("GO")
#     INDEX_NAME = 'data_law'
#     INDEX_NAME_HYBRID = 'tma_hybrid'
#     import asyncio
#     from utils import get_es_client
#     es = get_es_client()
#     search = HybridSearch(es=es)
#     asyncio.run(search.hybrid_search("TMA có bao nhiêu cơ sở?", top_k=3, INDEX_NAME=INDEX_NAME_HYBRID))
    