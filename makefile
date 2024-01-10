.PHONY: docker docs

docker-cli:
	docker compose run server python -im modules.cli

docker:
	docker compose up --build

docker-test:
	SEM_TEST=1 docker compose up --build

cli:
	poetry run python3 -im modules.cli

run:
	poetry run python3 -m modules.main

test:
	poetry run python3 -m pytest --ignore=sem-db-data/ -x -s -v .

requirements:
	poetry run pip freeze | grep -v '^-e' > docker/requirements.txt

docs:
	poetry run mkdocs build
	poetry run mkdocs serve
