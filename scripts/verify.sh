#!/bin/bash
set -e # Выход при первой ошибке

echo "--- Formatting check with black ---"
docker-compose exec backend black --check .

echo "--- Linting with flake8 ---"
docker-compose exec backend flake8 .

echo "--- Running tests with pytest ---"
docker-compose exec backend pytest

echo "--- Verification PASSED ---"
