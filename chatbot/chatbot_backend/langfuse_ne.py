from langfuse.decorators import langfuse_context
from langfuse import Langfuse
import os
from datetime import datetime
from langfuse.media import LangfuseMedia
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
import re 

class LangfuseHandler:
    def __init__(self):
        print("[LOG]: LANGFUSE")
        self.langfuse = Langfuse()
        self.is_newSession = True
        self.tmp_file_path = ''

        key = ''            #sq2k3
        llm = ChatOpenAI(api_key=key, model='gpt-4o-mini')
        emb = OpenAIEmbeddings(api_key=key, model='text-embedding-ada-002')
        # text-embedding-3-small
        # text-embedding-3-large
        self.trace_id = ''
        # self.chats_memory_short_term = []
        # verphu
        os.environ["LANGFUSE_PUBLIC_KEY"] = os.environ.get("LANGFUSE_PUBLIC_KEY")
        os.environ["LANGFUSE_SECRET_KEY"] = os.environ.get("LANGFUSE_SECRET_KEY")

        self.langfuse = Langfuse(
            secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
            public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
            host=os.environ.get("LANGFUSE_BASEURL"),
        )
    
    def get_chats_memory_longterm(self, session_id):

        traces = self.fetch_traces(session_id=session_id)
        documents_memory = []
        if len(traces) > 0:
            for trace in traces:
                if trace.input is not None and '?' not in trace.input:              # Không cần lưu câu hỏi người dùng trong memory
                    documents_memory.append(
                        {
                            'title': "Doc Memory From Session",
                            'content': trace.input,
                            'collection_date': str(datetime.today().strftime("%Y-%m-%d"))
                        }
                    )
                trace_output = (trace.output or "").strip()
                # print('trace_outputtrace_output: ', trace_output)
                if 'Luật An Ninh Mạng 2018' not in trace_output:
                    items = re.split(r'\.\s+|\.$|;\s*|\n+|:\n', trace_output)
                    for item in items:        # Vì thông tin lưu vào memory nên là 1 fact <=> 1 câu... https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/memory.html
                        if item.strip() and 'Luật An Ninh Mạng 2018' not in item: 
                            documents_memory.append(
                                {
                                    'title': "Doc Memory From Session",
                                    'content': item.strip(),
                                    'collection_date': str(datetime.today().strftime("%Y-%m-%d"))
                                }
                            )
        return documents_memory
        
    def fetch_traces(self, session_id: str):
        """
            input:
                session_id: str | Key của session muốn truy vấn.
            output:
                sorted_traces: list | danh sách các tracs được lấy về của session_id đó.
        """
        traces_response = self.langfuse.fetch_traces(session_id=session_id)
        traces = getattr(traces_response, "data", '')
        sorted_traces = sorted(traces, key=lambda x: x.timestamp)       # Sắp xếp lại các traces theo thứ tự thời gian các session
        return sorted_traces

    def fetch_sesions(self):
        """
            output:
                sorted_sessions: list | danh sách tất cả sessions của hôm nay.
        """
        today = datetime(datetime.now().year, datetime.now().month, datetime.now().day)  
        response = self.langfuse.fetch_sessions(
            from_timestamp=today,
            to_timestamp=datetime.now()
        )
        sessions = getattr(response, "data", '')
        sorted_sessions = sorted(sessions, key=lambda x: x.created_at, reverse=True)   # Sắp xếp lại các sessions theo thứ tự thời gian các session
        return sorted_sessions
    
    def update_current_trace(self, name, session_id, input, output):
        if self.tmp_file_path:
            # # Đọc nội dung file
            print("[LOG] PDF LOADED langfuse: ", self.tmp_file_path)
            with open(self.tmp_file_path, "rb") as f:
                file_bytes = f.read()
            wrapped_obj = LangfuseMedia(
                obj=file_bytes, content_bytes=file_bytes, content_type="application/pdf"
            )

            os.remove(self.tmp_file_path)
            langfuse_context.update_current_trace(
                name=name,
                session_id=session_id,
                input=input,
                output=output,
                metadata={
                    "context": wrapped_obj
                }
            )
        else:
            self.source_file_path = ''
            langfuse_context.update_current_trace(
                name=name,
                session_id=session_id,
                input=input,
                output=output,
            )

    def update_observation_cost(self, model_name, input_token, output_token, cost_input, cost_output):
        """
            Hàm cập nhật chi chí theo từng token của mỗi phiên truy vấn.
        """
        langfuse_context.update_current_observation(
            model=model_name,
            usage_details={
                "input": input_token,
                "output": output_token
            },
            cost_details={
                "input": float(input_token)* float(cost_input),
                "output":  float(output_token)* float(cost_output)
            }
        )