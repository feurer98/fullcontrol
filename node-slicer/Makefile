.PHONY: help dev up down logs clean test lint format

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

dev: ## Start development environment
	docker-compose up

up: ## Start services in background
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

clean: ## Clean up containers, volumes, and build artifacts
	docker-compose down -v
	rm -rf packages/frontend/node_modules
	rm -rf packages/frontend/dist
	rm -rf packages/backend/__pycache__
	rm -rf packages/backend/.pytest_cache

test: ## Run tests for frontend and backend
	cd packages/frontend && pnpm test
	cd packages/backend && python -m pytest

lint: ## Lint all code
	cd packages/frontend && pnpm lint
	cd packages/backend && ruff check .

format: ## Format all code
	cd packages/frontend && pnpm format
	cd packages/backend && black . && ruff check --fix .
