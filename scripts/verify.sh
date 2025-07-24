set -e 

echo "--- 1. Formatting check with black ---"
docker-compose -f docker/docker-compose.yml exec web black --check .

echo "--- 2. Linting with flake8 ---"
docker-compose -f docker/docker-compose.yml exec web flake8 . --count --ignore=E501,F401 --show-source --statistics

echo "--- 3. Fast type checking with pyright ---"
docker-compose -f docker/docker-compose.yml exec web pyright

echo "--- 4. Dependency security check with pip-audit ---"
docker-compose -f docker/docker-compose.yml exec web pip-audit

echo "--- 5. Security analysis with bandit ---"
docker-compose -f docker/docker-compose.yml exec web bandit -r . -x ./tests

echo "--- 6. Advanced static analysis with semgrep ---"
docker-compose -f docker/docker-compose.yml exec web semgrep scan --config "p/python" --metrics=off --verbose

echo "--- 7. Running tests and checking coverage ---"
docker-compose -f docker/docker-compose.yml exec web python -m pytest --cov=main --cov=services --cov-report=term-missing --cov-fail-under=90 /tests

echo ""
echo "✅ ✅ ✅ ALL CHECKS PASSED ✅ ✅ ✅"
