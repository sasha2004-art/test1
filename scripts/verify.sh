#!/bin/bash
set -e # Выход при первой ошибке

echo "--- Formatting check with black ---"
docker-compose exec web black --check .

echo "--- Linting with flake8 ---"
docker-compose exec web flake8 .

echo "--- Running tests with pytest ---"
docker-compose exec web pytest

echo "--- Verification PASSED ---"
