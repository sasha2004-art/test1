#!/bin/bash
set -e # Выход при первой ошибке

echo "--- Formatting check with black ---"
docker-compose -f docker/docker-compose.yml exec web black --check .

echo "--- Linting with flake8 ---"
docker-compose -f docker/docker-compose.yml exec web flake8 . --count --ignore=E501,F401 --show-source --statistics

echo "--- Security check with bandit ---"
# Исключаем директорию с тестами из проверки безопасности
docker-compose -f docker/docker-compose.yml exec web bandit -r . -x ./tests

echo "--- Running tests with pytest ---"
# Используем 'python -m pytest', чтобы исправить пути импорта
docker-compose -f docker/docker-compose.yml exec web python -m pytest tests/

echo "--- ALL CHECKS PASSED ---"
