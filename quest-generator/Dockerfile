FROM python:3.10-slim

RUN apt-get update && apt-get install -y build-essential cmake

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=backend/app.py

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]