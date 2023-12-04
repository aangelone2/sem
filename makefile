cli:
	poetry run python3 -im modules.cli

run:
	poetry run python3 -m modules.main

test:
	SEM_TEST=1 poetry run python3 -m pytest -x -s -v .
