.PHONY: test install lint docker-up docker-up-db docker-down docker-build migrate frontend-install frontend-test

install:
	cd backend && pip install -r requirements.txt

frontend-install:
	cd frontend && npm install

test:
	cd backend && python -m pytest -v

frontend-test:
	cd frontend && npm test

lint:
	cd backend && python -m flake8 app/ tests/ --max-line-length=120

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-up-db:
	docker compose up -d mysql

docker-down:
	docker compose down

migrate:
	cd backend && alembic upgrade head
