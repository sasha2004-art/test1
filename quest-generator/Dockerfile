# quest-generator/Dockerfile

# Используем официальный образ python:3.10-slim
FROM python:3.10-slim

# Устанавливаем рабочую директорию /app
WORKDIR /app

# ---- НОВОЕ ИЗМЕНЕНИЕ ----
# Обновляем инструменты сборки Python перед установкой зависимостей
# Это решает проблему с 'distutils'
RUN pip install --upgrade pip setuptools wheel
# -------------------------

# Копируем requirements.txt и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё остальное содержимое проекта
COPY . .

# Указываем Flask, где находится наше приложение
ENV FLASK_APP=backend/app.py

# Открываем порт 5000
EXPOSE 5000

# Запускаем Flask-приложение с хостом 0.0.0.0
CMD ["flask", "run", "--host=0.0.0.0"]
