FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --pre -U langchain
RUN pip install -r requirements.txt

COPY deepagents /tmp/deepagents
RUN pip install /tmp/deepagents

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
