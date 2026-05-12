FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN useradd --create-home --uid 10001 --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

ENV PYTHONPATH=/app/src
ENV MCP_PORT=8051

EXPOSE 8051

USER appuser

CMD ["python", "-m", "mcp_server.server"]
