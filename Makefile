.PHONY: install install-dev install-prod install-all lint format type-check test test-cov check run run-prod clean

# Setup
install:
	python -m pip install -e .

install-dev:
	python -m pip install -e ".[dev]"

install-prod:
	if [ -f requirements.lock ]; then \
		python -m pip install -r requirements.lock; \
		python -m pip install -e .; \
	else \
		python -m pip install -e ".[prod]"; \
	fi

install-all:
	python -m pip install -e ".[all]"

# Development
lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

type-check:
	mypy .

test:
	pytest

test-cov:
	pytest --cov=database --cov=web --cov-report=term-missing --cov-report=html

check: test lint type-check

# Running
run:
	python web/app.py

run-prod:
	gunicorn --bind 0.0.0.0:5000 --workers 2 "web.app:create_app()"

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type f -name "coverage.xml" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
