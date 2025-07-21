#!/bin/bash
set -e # Выход при первой ошибке

echo "--- Formatting check with black ---"
black --check .

echo "--- Linting with flake8 ---"
flake8 .

echo "--- Running tests with pytest ---"
pytest

echo "--- Verification PASSED ---"
