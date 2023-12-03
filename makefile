cli:
	poetry run python3 -im modules.cli

run:
	poetry run python3 -m modules.main

test:
	poetry run python3 -m pytest -x -s -v .
