FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Usuário não-root por segurança
RUN useradd -m -u 10001 appuser && \
    apt-get update && apt-get install -y --no-install-recommends tini ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia código
COPY backend/app /app/app

# Exposição de porta (padrão 8000 interno)
EXPOSE 8000

USER appuser
ENTRYPOINT ["/usr/bin/tini", "--"]

# Uvicorn direto (simples e eficaz)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
