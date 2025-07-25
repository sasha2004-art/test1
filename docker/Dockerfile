FROM public.ecr.aws/docker/library/python:3.10-slim

RUN python -m pip install --upgrade pip setuptools

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Добавляем /app в PYTHONPATH, чтобы импорты работали из любого места
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PATH="/root/.local/bin:${PATH}"

COPY app/ .

EXPOSE 5000

CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "main:app"]