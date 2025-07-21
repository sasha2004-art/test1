# Используем официальный образ python:3.10-slim
FROM python:3.10-slim

# Устанавливаем рабочую директорию /app
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё остальное содержимое проекта
COPY . .

# Открываем порт 5000
EXPOSE 5000

# Запускаем Flask-приложение с хостом 0.0.0.0
CMD ["flask", "run", "--host=0.0.0.0"]
