FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app/src
ENV API_PORT=8181

EXPOSE 8181

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8181"]
