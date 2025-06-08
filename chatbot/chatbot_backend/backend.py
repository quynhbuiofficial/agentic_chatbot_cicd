from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from chatbot_client import ChatBot
from pdf_manager import pdf_parser_nodes_index
from utils import get_es_client

app = FastAPI(title="Multi-agent-chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173"],
    # allow_origins=["http://chatbot_frontend:5173"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

es = get_es_client(max_retries=2, sleep_time=1)
multi_agent_chatbot = ChatBot(es=es)

class Request(BaseModel):
    prompt: str
    session_id_choiced: Optional[str] = ''
    tmp_file_path: Optional[str] = ''

@app.post("/chat")
async def chat(request: Request):
    responses = await multi_agent_chatbot.get_response(request.prompt, request.session_id_choiced, request.tmp_file_path)
    return responses

class Request_pdf(BaseModel):
    tmp_file_path: str

@app.post('/parser_index')
def parser_index(file: UploadFile):
    tmp_file_path = f"/tmp/{file.filename}"
    with open(tmp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print("\n\n📄 Đã nhận file và lưu tại:", tmp_file_path)

    pdf_parser_nodes_index(tmp_file_path=tmp_file_path, es=es)

    return tmp_file_path

@app.get("/")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9999)