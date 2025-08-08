FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

 # Non-root user for security
RUN useradd -m -u 10001 appuser && \
    apt-get update && apt-get install -y --no-install-recommends tini ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

 # Install dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

 # Copy code
COPY backend/app /app/app

 # Port exposure (default 8000 internal)
EXPOSE 8000

USER appuser
ENTRYPOINT ["/usr/bin/tini", "--"]

 # Direct Uvicorn (simple and effective)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
