migrate:
	sudo docker compose run --rm app python manage.py migrate

createsuperuser:
	sudo docker compose run --rm app python manage.py createsuperuser --noinput