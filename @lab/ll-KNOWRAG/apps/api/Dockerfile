FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium for Crawl4AI (browser-based crawling)
RUN playwright install --with-deps chromium || echo "Playwright install skipped (httpx fallback active)"

COPY src/ ./src/

RUN useradd --create-home --uid 10001 --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

ENV PYTHONPATH=/app/src
ENV API_PORT=8181

EXPOSE 8181

USER appuser

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8181"]
