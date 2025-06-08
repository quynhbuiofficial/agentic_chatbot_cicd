from elasticsearch_ne import HybridSearch
from config import INDEX_NAME_HYBRID, INDEX_NAME_LEGAL
import asyncio
from duckduckgo_search import AsyncDDGS
import wikipedia
from utils import get_es_client
from dotenv import load_dotenv
load_dotenv()
import re

from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Multi-Agent MCP")

@mcp.tool()
async def get_tma_information(search_query: str):
    """
    Tìm kiếm các thông tin về công ty TMA.
    """
    search_results = await hybrid_search_class.hybrid_search(search_query=search_query, top_k=3, INDEX_NAME=INDEX_NAME_HYBRID)
    final_results = [item["content"] for item in search_results]
    retrieval_context = "\n".join(final_results)
    return retrieval_context

@mcp.tool()
async def get_legal_information(full_question: str):
    """
    Tìm kiếm các thông tin về pháp luật.
    """
    search_results = await hybrid_search_class.hybrid_search(search_query=full_question, top_k=1, INDEX_NAME=INDEX_NAME_LEGAL)
    response = ''
    for item in search_results:
        khoan_content = item['khoan']
        if re.match(r'^\d{1,2}\.\s.*', khoan_content):
            khoan_name = khoan_content.split('.', 1)[0].strip() 
        else:
            khoan_name = '_'

        dieu_name = item['dieu']
        response += f'Câu trả lời là: `Tại **khoản {khoan_name.lower()} {dieu_name.lower()}** Luật An Ninh Mạng 2018, đã quy định cụ thể thông tin trên.`'
    return response


async def asearch(word, max_results: int = 2):
    async with AsyncDDGS() as ddgs:
        return await ddgs.atext(word, max_results=max_results)

@mcp.tool()
async def duckduck_search_tool(question: str):
    """
    Hữu ích khi tìm kiếm thông tin mới, trên mạng thông qua DuckDuckGo.
    """
    question = [w.strip() for w in question.split(",")] 
    tasks = [asearch(w, 2) for w in question]
    results = await asyncio.gather(*tasks)
    items = [item['body'] for result in results for item in result]
    results = "\n".join(items)
    return results

@mcp.tool()
def wiki_search_tool(search_query: str):
    """
    Hữu ích khi tra cứu thông tin về các khái niệm, quốc gia, và tôn giáo từ Wikipedia.
    """
    wikipedia.set_lang("vi")
    try:
        summary = wikipedia.summary(search_query, sentences=17)
        print(summary)
        return summary
    except wikipedia.exceptions.PageError:
        print("Không tìm thấy bài viết với tiêu đề đã cho.")
        return "Không tìm thấy bài viết với tiêu đề đã cho."
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Có nhiều kết quả phù hợp: {e.options}")


if __name__ == "__main__":
    import uvicorn
    print("[LOG]: Connect to ElasticSearch for tools")
    es = get_es_client(max_retries=2, sleep_time=1)
    print("[LOG]: DONE")
    hybrid_search_class = HybridSearch(es=es)
    uvicorn.run(mcp.sse_app(), host='127.0.0.1', port=1234)

# async def main():
#     print("GGGG")
#     a = await get_tma_information("TMA có bao nhiêu cơ sở?")
#     print("CCCCCCCC: ", a)

# import asyncio
# if __name__ == '__main__':
#     es = get_es_client(max_retries=2, sleep_time=1)
#     hybrid_search_class = HybridSearch(es=es)   
#     asyncio.run(main())

