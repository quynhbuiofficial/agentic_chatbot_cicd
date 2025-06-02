FROM python:3.10-slim

WORKDIR /mcp_server_manager

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 1234

CMD ["python", "server.py"] 