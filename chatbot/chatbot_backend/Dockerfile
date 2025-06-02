FROM python:3.10-slim

WORKDIR /chatbot_backend

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9999

CMD ["python", "backend.py"]