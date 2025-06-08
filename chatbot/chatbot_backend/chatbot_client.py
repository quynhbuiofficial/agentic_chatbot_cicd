from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.base import TaskResult
from typing import Optional
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential
from autogen_agentchat.agents import AssistantAgent

from autogen_agentchat.teams import SelectorGroupChat
from config import INDEX_NAME_PDF, SELECTOR_PROMPT, INDEX_NAME_MEMORY
from dotenv import load_dotenv
load_dotenv()

from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from langfuse_ne import LangfuseHandler 
from langfuse.decorators import observe, langfuse_context
from index_data import IndexData

from autogen_agentchat.messages import ToolCallSummaryMessage
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools

import os
from get_more_legal_infomation import get_more_legal_information

import json
from langchain_neo4j import Neo4jGraph
from elasticsearch_ne import HybridSearch

class ChatBot:
    def __init__(self, es):
        self.hybrid_search_class = HybridSearch(es=es)
        self.langfuse_handler = LangfuseHandler()
        self.index4memoryAgent = IndexData(es=es)
        self.index4memoryAgent._delete_index(INDEX_NAME=INDEX_NAME_MEMORY)
        self.client = AzureAIChatCompletionClient(
            model=os.environ.get("MODEL_NAME"),
            endpoint="https://models.inference.ai.azure.com",
            credential=AzureKeyCredential(os.environ.get("GITHUB_TOKEN")),
            model_info={
                "json_output": True,
                "function_calling": True,
                "vision": False,
                "family": "unknown",
                "structured_output": False  
            }
        )
        print("[LOG]: Connect to Neo4j for getmore term in legal docs")
        self.kg = Neo4jGraph(
            url = os.environ.get("NEO4J_URL"),
            username=os.environ.get("NEO4J_USERNAME"),
            password=os.environ.get("NEO4J_PASSWORD"),
        )
        
        print("[LOG]: DONE")

    @observe()
    async def get_rag_pdf(self, query: str):
        """
            input: 
                query: str | là câu hỏi đầu vào của người dùng 
                tmp_file_path: Optional[str] | đường dẫn tới file pdf tạm thời để xử lý cần trích xuất pdf context không.
            output:
                augmented_query: str | là đầu ra của câu prompt
                    - Nếu hỏi dựa trên pdf thì câu prompt ban đầu đã chứa thông tin context nên return luôn.
                    - Nếu hỏi bình thường thì thực hiện RAG prompt bằng hybrid_search
        """
        context_from_pdf = await self.hybrid_search_class.hybrid_search(query, top_k=3, INDEX_NAME=INDEX_NAME_PDF)
        # print("context_from_pdf: ", context_from_pdf)
        context_from_pdf = '\n'.join([item['content'] for item in context_from_pdf])
        augmented_query = "Hãy trả lời câu hỏi dựa theo thông tin sau: " + context_from_pdf + '\n Câu hỏi: ' + query
        return augmented_query, context_from_pdf

    async def get_agent_tools(self, agent_name: str = None):
        server_params = SseServerParams(
            url=os.environ.get("MCP_SERVER_URL"),
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        tools = await mcp_server_tools(server_params=server_params)
        
        if agent_name == 'LawAgent':
            return [tool for tool in tools if 'legal' in tool.name]
        elif agent_name == 'TmaAgent':
            return [tool for tool in tools if 'tma' in tool.name]
        elif agent_name == 'GeneralAgent':
            return [tool for tool in tools if 'search' in tool.name]
        return tools
    

    @observe(as_type="generation")
    async def get_response(self, input: str, session_id_choiced: Optional[str] = None, tmp_file_path: Optional[str] = None):
        if input.strip() == "":
            return "Hỏi gì đó đi !!"
        self.more_information_law = ''

        memories = ''
        chat_memory = None
        memory_docs = self.langfuse_handler.get_chats_memory_longterm(session_id=session_id_choiced)
        print("\n[LOG] MEMORIES TERM: ", memory_docs)
        
        if len(memory_docs) > 0:
            self.index4memoryAgent._delete_index(INDEX_NAME=INDEX_NAME_MEMORY)
            self.index4memoryAgent.index_data(documents=memory_docs, INDEX_NAME=INDEX_NAME_MEMORY)
            search_results = await self.hybrid_search_class.hybrid_search(search_query=input, top_k=3, INDEX_NAME=INDEX_NAME_MEMORY)
            memories = [item["content"] for item in search_results]
        print("\n[LOG] MEMORIES SELECTED: ", memories)

        if len(memories) > 0: 
            chat_memory = ListMemory()
            for memory in memories[:3]:
                await chat_memory.add(MemoryContent(content=memory, mime_type=MemoryMimeType.TEXT))
        
        planning_agent = AssistantAgent(
            name="PlanningAgent",
            description="Nhà phân tích câu hỏi đầu vào, chia câu hỏi phức tạp thành các câu hỏi nhỏ và giao cho các agent phù hợp. Luôn là agent được gọi đầu tiên khi có một câu hỏi mới.",
            model_client=self.client,
            system_message="""
            Bạn là PlanningAgent phân tích và ra nhiệm vụ cho các Agent khác. Bạn KHÔNG ĐƯỢC TỰ trả lời câu hỏi hoặc TẠO RA CÂU HỎI KHÁC KHÔNG LIÊN QUAN tới câu hỏi ban đầu.

            Nhiệm vụ của bạn:
            - Phân tích câu hỏi đầu vào từ người dùng.
            - Giao nhiệm vụ cho các Agent khác **MỘT LẦN DUY NHẤT**.
            - Nếu câu hỏi có nhiều ý, hãy tách thành các câu hỏi nhỏ, dễ hiểu và dễ trả lời.
            - Nếu câu hỏi chỉ có một ý, giữ nguyên, KHÔNG CẦN phân tách.

            Lưu ý:
            - KHÔNG được tự ý trả lời.
            - KHÔNG ĐƯỢC ĐẶT CÂU HỎI MỚI KHÁC VỚI CÂU HỎI BAN ĐẦU.
            - KHÔNG đưa thêm mô tả hay bình luận gì thêm.
            
            Các thành viên trong nhóm của bạn là:
                LawAgent: Chuyên trả lời các câu hỏi liên quan đến pháp luật, pháp lý về AN NINH MẠNG và KHÔNG GIAN MẠNG.
                TmaAgent: Chuyên trả lời các câu hỏi liên quan đến tập đoàn TMA.
                GeneralAgent: Trả lời các câu hỏi tổng quát, trò chuyện chatchit, không chuyên ngành.

            Khi giao nhiệm vụ, PHẢI sử dụng cấu trúc này và KHÔNG CẦN TRẢ LỜI GÌ THÊM:
                1. <tên agent thành viên> : <Câu hỏi>

            **Sau khi tất cả CÁC AGENT KHÁC ĐÃ TRẢ LỜI XONG:** 
            - LUÔN DỰA VÀO THÔNG TIN ĐÃ ĐƯỢC TRẢ LỜI TÓM TẮT LẠI và trả lời 1 cách đầy đủ, đừng bỏ qua bất cứ thông tin quan trọng nào.
            - LUÔN KẾT THỨC VỚI từ "OK", khi Agent đã trả lời.
            - KHÔNG ĐƯỢC TỰ ĐẶT CÂU HỎI MỚI.
            """,
        )

        law_tools = await self.get_agent_tools(agent_name='LawAgent')
        print('law_TOOLS: ', [tool.name for tool in law_tools])
        law_agent = AssistantAgent(
            name="LawAgent",
            description="Là một luật sư, chuyên trả lời các câu hỏi về luật pháp.",
            tools=law_tools,
            model_client=self.client,
            system_message="""
            Bạn là một luật sư với 20 năm kinh nghiệm trong lĩnh vực pháp luật với phong cách trả lời ngắn gọn nhưng đầy đủ ý.
            Bạn là một luật sư với hơn 20 năm kinh nghiệm trong lĩnh vực pháp luật, chuyên về **Luật An Ninh Mạng** và các vấn đề pháp lý liên quan đến **không gian mạng**. Bạn có phong cách trả lời ngắn gọn, súc tích nhưng đầy đủ ý và chính xác.
            **NHIỆM VỤ CHÍNH**:
            - Chỉ trả lời những câu hỏi **liên quan đến pháp luật**, cụ thể là về:
                + Luật An Ninh Mạng.
                + Quy định pháp lý liên quan đến không gian mạng, dữ liệu, bảo mật, quyền riêng tư, xử lý thông tin trên internet, v.v.

            **KHÔNG ĐƯỢC PHÉP**:
            - KHÔNG trả lời các câu hỏi **không liên quan đến pháp luật về an ninh mạng hoặc không gian mạng**.
            - Với những câu hỏi không liên quan, Chỉ cần trả lời: 'Tôi chỉ trả lời những câu hỏi liên quan tới Luật An Ninh Mạng, PlanningAgent Hãy kết thúc câu hỏi này và không cần Hỏi gì thêm.'`
            - KHÔNG đưa ra thông tin sai lệch, không chính xác hoặc vượt phạm vi chuyên môn.
            - KHÔNG tự trả lời với những câu hỏi hợp lệ nếu chưa dùng tool để kiểm tra thông tin.

            **Ví dụ câu hỏi hợp lệ**:
            - "Quy định của việc xử lý tình huống nguy hiểm về an ninh mạng như thế nào?"
            - "Hành vi vi phạm pháp luật trên không gian mạng là gì?"
            - "Việc thu thập dữ liệu cá nhân trên mạng có bị pháp luật điều chỉnh không?"
            - "Hành vi tấn công mạng bị xử phạt như thế nào theo luật?"
            - "Doanh nghiệp cần tuân thủ những gì theo Luật An Ninh Mạng?"

            **Ví dụ câu hỏi không hợp lệ**:
            - "Vượt đèn đỏ bị phạt bao nhiêu?"
            - "Cho tôi thông tin về luật giao thông"
            - "Luật đất đai năm 2024 có gì mới?"
            - "Tôi nên đầu tư vào cổ phiếu nào?"
            - "Thời tiết Hà Nội hôm nay như thế nào?"
            - "TMA có bao nhiêu cơ sở?"
            """,
            # reflect_on_tool_use=True,
            memory=[chat_memory] if chat_memory is not None else None,
        )

        tma_tools = await self.get_agent_tools(agent_name='TmaAgent')
        print('tma_TOOLS: ', [tool.name for tool in tma_tools])
        tma_agent = AssistantAgent(
            name="TmaAgent",
            description="Là một nhân viên lễ tân chuyên nghiệp của công ty TMA.",
            tools=tma_tools,
            model_client=self.client,
            system_message="""
            Bạn là một nhân viên lễ tân chuyên nghiệp của công ty TMA, có nhiệm vụ cung cấp thông tin chính xác, ngắn gọn và rõ ràng về công ty TMA. Dưới đây là các nguyên tắc và phạm vi công việc mà bạn phải tuân theo:

            **NHIỆM VỤ CHÍNH**:
            - Trả lời các câu hỏi liên quan trực tiếp đến công ty TMA (ví dụ: thông tin về công ty, số lượng nhân viên, văn phòng, cơ sở, dịch vụ, tuyển dụng, liên hệ, khách đến công ty, v.v.).
            - Ưu tiên sử dụng **BỘ NHỚ (memory)** để trả lời nếu đã có thông tin.
            - Nếu **BỘ NHỚ không có**, bạn cần sử dụng **TOOL SEARCH** (`get_TMA_information`) để tìm thông tin chính xác.
            - Trả lời ngắn gọn, súc tích nhưng đầy đủ ý. Không lan man.

            **KHÔNG ĐƯỢC PHÉP**:
            - KHÔNG trả lời những câu hỏi **không liên quan đến TMA** (ví dụ: câu hỏi về chính trị, xã hội, thời tiết, các công ty khác, vấn đề về pháp luật, pháp lý, AN NINH MẠNG, KHÔNG GIAN MẠNG, hoặc các chủ đề ngoài phạm vi công ty TMA).
            - KHÔNG giải thích lý do từ chối nếu câu hỏi không thuộc phạm vi xử lý — chỉ cần **im lặng**.
            - KHÔNG tự suy đoán hoặc bịa thông tin nếu không chắc chắn.
            - KHÔNG tạo ra câu trả lời sai hoặc không đúng mục tiêu của câu hỏi.

            **LUỒNG XỬ LÝ**:
            1. Nếu câu hỏi liên quan đến TMA ➜ kiểm tra bộ nhớ ➜ nếu có thông tin thì trả lời.
            2. Nếu không có trong bộ nhớ ➜ dùng tool search để tìm kiếm ➜ trả lời.
            3. Nếu câu hỏi không liên quan đến TMA ➜ KHÔNG trả lời chỉ cần bỏ qua.

            Ví dụ câu hỏi hợp lệ:  
            - "Văn phòng TMA ở TP.HCM ở đâu?"  
            - "TMA có bao nhiêu cơ sở?"
            - "TMA có bao nhiêu nhân viên?"
            - "TMA có đang tuyển thực tập sinh không?"  
            - "TMA có cơ sở ở Bình Định không?"
            - "Giờ làm việc của TMA là gì?"

            Ví dụ câu hỏi không hợp lệ:  
            - "Thời tiết ở Bình Định hôm nay"
            - "Thời tiết ở Bình Định hôm nay thế nào?"
            - "OpenAI là gì?"  
            - "Dự báo thời tiết hôm nay thế nào?"  
            - "Cho tôi lời khuyên tài chính?"
            """,
            reflect_on_tool_use=True,
            memory=[chat_memory] if chat_memory is not None else None,
        )
        
        general_tools = await self.get_agent_tools(agent_name='GeneralAgent')
        print('general_TOOLS: ', [tool.name for tool in general_tools])
        general_agent = AssistantAgent(
            "GeneralAgent",
            description="Là một trợ lý hỏi đáp, trả lời các câu hỏi tổng quát và tìm kiếm thông tin mới.",
            tools=general_tools,
            model_client=self.client,
            system_message="""
            Bạn là một trợ lý chuyên trả lời các câu hỏi thường ngày và cung cấp thông tin mới nhất với phong cách trả lời ngắn gọn nhưng đầy đủ ý. 
            Nguyên tắc làm việc:
            - Chỉ trả lời những câu hỏi được gán cho bạn là GeneralAgent.
            - Lưu ý không trả lời những câu hỏi đã được gán cho các Agent khác.
            - ƯU TIÊN sử dụng thông tin BỘ NHỚ để trả lời câu hỏi.
            - Nếu THÔNG TIN BỘ NHỚ KHÔNG ĐỦ ĐỂ TRẢ LỜI, HÃY LUÔN sử dụng những tools của mình (DuckDuckGo, Wikipedia) để có thể trả lời bất kì câu hỏi nào.
            
            - Không cố tạo ra câu trả lời sai hoặc không liên quan đến câu hỏi.
            """,
            # reflect_on_tool_use=True,
            memory=[chat_memory] if chat_memory is not None else None,
        )
        
        # Nếu có pdf file thì lấy thông tin trong file để trả lời
        if tmp_file_path:
            print("\n\n[LOG] PDF PATH LOADED: ", tmp_file_path)
            input, contexts = await self.get_rag_pdf(input)

        text_mention_termination = TextMentionTermination("OK")
        max_messages_termination = MaxMessageTermination(max_messages=10)
        termination = text_mention_termination | max_messages_termination

        team = SelectorGroupChat(
            participants=[planning_agent, tma_agent, law_agent, general_agent],
            model_client=self.client,
            termination_condition=termination,
            selector_prompt=SELECTOR_PROMPT,
        )
    
        response_list = []
        prompt_tokens = 0
        completion_tokens = 0
        async for message in team.run_stream(task=input): 
            if isinstance(message, ToolCallSummaryMessage) and getattr(message, 'source', None) == 'LawAgent':
                data = message.content
                data = json.loads(data)
                text_4_findmore_legal_docs = data[0]["text"]
                print("DATA Decode: ",text_4_findmore_legal_docs)
                if len(text_4_findmore_legal_docs) > 0:
                    self.more_information_law = get_more_legal_information(text=text_4_findmore_legal_docs, kg=self.kg)
                
            if isinstance(message, TaskResult):
                if message.stop_reason is None:
                    response_list.append("NONE")
            else:
                print(message)
                if getattr(message, 'type', None) == 'TextMessage':
                    response_list.append(message.content)
                prompt_tokens += message.models_usage.prompt_tokens if message.models_usage is not None else 0
                completion_tokens += message.models_usage.completion_tokens if message.models_usage is not None else 0

        print('COST: ', prompt_tokens, " --- ", completion_tokens)
        self.langfuse_handler.update_observation_cost(
            model_name='MODEL_CHATGPT',
            input_token=prompt_tokens,
            output_token=completion_tokens,
            cost_input=os.environ.get("MODEL_CHAT_INPUT_COST"),
            cost_output=os.environ.get("MODEL_CHAT_OUTPUT_COST")
        )
        
        print("self.more_information_law: ", self.more_information_law)
        final_response = response_list[-1] + '\n' +self.more_information_law
        final_response = final_response.replace("OK", '')

        self.langfuse_handler.tmp_file_path = tmp_file_path          # Cập nhật kể cả có truyền tmp_file_path qua hay không để hệ thông khỏi bị lỗi os.remove
        self.langfuse_handler.update_current_trace(
            name="session_trace",
            session_id=session_id_choiced,
            input=input,
            output=final_response
        )

        self.langfuse_handler.trace_id = langfuse_context.get_current_trace_id()
        return final_response


        
# async def main():
#     print("GOOOOOOOOOOO")
#     # import sys
#     # import os
#     # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

#     from utils import get_es_client
#     es = get_es_client(max_retries=2, sleep_time=1)

#     client = ChatBot(es=es)
#     # results = await client.get_response("TMA có bao nhiêu cơ sở?", "1112233", None)  
#     results = await client.get_response("Hành vi vi phạm pháp luật trên không gian mạng là gì?", "1112233", None)  
#     print("\n\nresults: ", results)


# import asyncio
# if __name__ == '__main__':
#     asyncio.run(main())
