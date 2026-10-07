FROM python:3.11-slim

# Evita geração de arquivos .pyc e força flush imediato de stdout/stderr para o Cloud Logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalação de dependências em camada cacheada
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Criação de usuário não-root
RUN useradd -m -u 1000 appuser
USER appuser

# Copia o código da aplicação
COPY main.py .

CMD ["python", "main.py"]
