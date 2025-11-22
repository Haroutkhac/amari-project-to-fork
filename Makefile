.PHONY: help build up down logs restart clean dev prod

help:
	@echo "Document Processor - Docker Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build     - Build all Docker images"
	@echo "  make up        - Start all services (development)"
	@echo "  make down      - Stop all services"
	@echo "  make logs      - View logs from all services"
	@echo "  make restart   - Restart all services"
	@echo "  make clean     - Stop services and remove volumes"
	@echo "  make dev       - Start services in development mode"
	@echo "  make prod      - Start services in production mode"
	@echo "  make test      - Run tests in Docker container"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v
	docker system prune -f

dev:
	docker-compose up --build

prod:
	docker-compose -f docker-compose.prod.yml up -d --build

test:
	docker-compose run --rm backend pytest

backend-logs:
	docker-compose logs -f backend

frontend-logs:
	docker-compose logs -f frontend

backend-shell:
	docker-compose exec backend /bin/bash

frontend-shell:
	docker-compose exec frontend /bin/sh

