# sem

![test](https://img.shields.io/badge/Tests-Passing-32CD32)
[![fastapi](https://img.shields.io/badge/FastAPI-FF0000)](https://github.com/tiangolo/fastapi)
[![sqlalchemy](https://img.shields.io/badge/SQLAlchemy-FF0000)](https://github.com/sqlalchemy/sqlalchemy)
[![postgresql](https://img.shields.io/badge/PostgreSQL-FF0000)](https://github.com/postgres/postgres)
[![testing](https://img.shields.io/badge/testing-pytest-blue)](https://github.com/pytest-dev/pytest)
[![pylint](https://img.shields.io/badge/linting-pylint-blue)](https://github.com/pylint-dev/pylint)
[![black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![poetry](https://img.shields.io/badge/build-poetry-blue)](https://github.com/python-poetry/poetry)
[![docker](https://img.shields.io/badge/deployment-docker-blue)](https://github.com/docker)
[![mkdocs](https://img.shields.io/badge/documentation-mkdocs-blue)](https://github.com/mkdocs/mkdocs)




## Local installation

### Installation and dependencies

The system is predisposed for local installation via the
`poetry` python package manager. The

```bash
$ poetry install
```

command, ran in the root directory, will use the local
`pyconfig.toml` and `poetry.lock` files to install the
dependencies.

### Running

The server can be executed running the commands

```bash
$ poetry run python3 -m modules.main
```

or

```bash
$ make run
```

Its interface can be accessed at the URL

<http://127.0.0.1:8000>

The server requires an active instance of POSTGRESQL to
be running on the system, and to be listening at its
default address <http://localhost:5432>.

### CLI

Once an instance of the server is running, a
command-line interface can be executed as

```bash
$ poetry run python3 -im modules.cli
```

or

```bash
$ make cli
```

**Relative documentation will be added.**

### Testing

Local testing can be performed by running

```bash
$ SEM_TEST=1 poetry run python3 -m pytest -x -s -v .
```

or

```bash
$ make test
```

An instance of the server will be started and then
stopped autonomously by the test client (with the same
POSTGRESQL requirement).




## Documentation

Documentation on the server API can be obtained running
the server at the URLs

- <http://127.0.0.1:8000/redoc>
- <http://127.0.0.1:8000/docs>

(the former is advised, due to better integration with
existing docstrings).

Documentation on server internals and schemas can be
generated and served via `mkdocs`, as

```bash
$ poetry run mkdocs build
$ poetry run mkdocs serve
```

or

```bash
$ make docs
```

after which it will be available at the URL

<http://127.0.0.1:8001>

(note the non-standard `8001` port, to allow
simultaneous browsing with the API documentation).
