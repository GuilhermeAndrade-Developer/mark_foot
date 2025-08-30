# Makefile for Mark Foot Test Service

.PHONY: help build up down test test-unit test-integration test-auth test-api clean logs shell

# Default target
help:
	@echo "Mark Foot Test Service Commands:"
	@echo ""
	@echo "  build           Build the test service container"
	@echo "  up              Start test service and dependencies"
	@echo "  down            Stop test service and dependencies"
	@echo "  test            Run all tests"
	@echo "  test-unit       Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-auth       Run authentication tests only"
	@echo "  test-api        Run API tests only"
	@echo "  test-coverage   Run tests with coverage report"
	@echo "  test-parallel   Run tests in parallel"
	@echo "  clean           Clean up containers and volumes"
	@echo "  logs            Show container logs"
	@echo "  shell           Open shell in test container"
	@echo ""

# Build the test service
build:
	docker-compose -f docker-compose.test.yml build

# Start services
up:
	docker-compose -f docker-compose.test.yml up -d test-db test-redis
	@echo "Waiting for database to be ready..."
	@sleep 10

# Stop services
down:
	docker-compose -f docker-compose.test.yml down

# Run all tests
test: up
	docker-compose -f docker-compose.test.yml run --rm test-service python -m pytest -v

# Run unit tests
test-unit: up
	docker-compose -f docker-compose.test.yml run --rm test-service python -m pytest -v -m unit unit/

# Run integration tests
test-integration: up
	docker-compose -f docker-compose.test.yml run --rm test-service python -m pytest -v -m integration integration/

# Run auth tests
test-auth: up
	docker-compose -f docker-compose.test.yml run --rm test-service python -m pytest -v -m auth auth/

# Run API tests
test-api: up
	docker-compose -f docker-compose.test.yml run --rm test-service python -m pytest -v -m api

# Run tests with coverage
test-coverage: up
	docker-compose -f docker-compose.test.yml run --rm test-service python -m pytest -v --cov=. --cov-report=html --cov-report=term-missing

# Run tests in parallel
test-parallel: up
	docker-compose -f docker-compose.test.yml run --rm test-service python -m pytest -v -n auto

# Clean up
clean:
	docker-compose -f docker-compose.test.yml down -v
	docker system prune -f

# Show logs
logs:
	docker-compose -f docker-compose.test.yml logs -f

# Open shell in test container
shell: up
	docker-compose -f docker-compose.test.yml run --rm test-service bash

# Quick test (no dependencies)
test-quick:
	python -m pytest -v --tb=short
