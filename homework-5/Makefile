.PHONY: help migrate run freeze createsuperuser shell makemigrations test

help:
	@echo "Available commands:"
	@echo "  make migrate        - Run migrations"
	@echo "  make run            - Start development server"
	@echo "  make freeze         - Generate requirements.txt"
	@echo "  make createsuperuser - Create superuser"
	@echo "  make shell          - Open Django shell"
	@echo "  make makemigrations - Create migrations"
	@echo "  make test           - Run tests"

migrate:
	python manage.py migrate

run:
	python manage.py runserver

freeze:
	pip freeze > requirements.txt

createsuperuser:
	python manage.py createsuperuser

shell:
	python manage.py shell

makemigrations:
	python manage.py makemigrations
