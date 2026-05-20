FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

# Run as non-root
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin reliquary \
 && chown -R reliquary:reliquary /app
USER reliquary

EXPOSE 8282

HEALTHCHECK --interval=10s --timeout=5s --retries=6 --start-period=20s \
  CMD curl -fsS http://localhost:8282/health || exit 1

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8282"]
