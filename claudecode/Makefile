.PHONY: test install lint

install:
	cd backend && pip install -r requirements.txt

test:
	cd backend && python -m pytest -v

lint:
	cd backend && python -m flake8 app/ tests/ --max-line-length=120
