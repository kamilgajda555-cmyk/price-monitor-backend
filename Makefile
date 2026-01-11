.PHONY: help build up down restart logs clean install test

help:
	@echo "Price Monitor - Makefile Commands"
	@echo "=================================="
	@echo "make build      - Build Docker containers"
	@echo "make up         - Start all services"
	@echo "make down       - Stop all services"
	@echo "make restart    - Restart all services"
	@echo "make logs       - Show logs"
	@echo "make clean      - Remove all containers and volumes"
	@echo "make install    - First time setup"
	@echo "make test       - Run tests"
	@echo "make backup     - Backup database"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

install: build up
	@echo "Waiting for services to start..."
	@sleep 10
	@echo "Creating admin user..."
	docker-compose exec -T backend python -c "from app.models.database import SessionLocal; from app.models.models import User; from app.api.auth import get_password_hash; db = SessionLocal(); user = User(email='admin@example.com', hashed_password=get_password_hash('admin123'), full_name='Admin', is_superuser=True); db.add(user); db.commit(); print('Admin user created')"
	@echo "Installation complete!"
	@echo "Access the application at http://localhost"
	@echo "Login: admin@example.com / admin123"

test:
	docker-compose exec backend pytest

backup:
	@mkdir -p backups
	docker-compose exec db pg_dump -U priceuser pricedb > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created in backups/"

restore:
	@read -p "Enter backup file path: " backup_file; \
	docker-compose exec -T db psql -U priceuser pricedb < $$backup_file
