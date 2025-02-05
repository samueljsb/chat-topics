# Chat Topics

## Development

This project uses [`uv`](https://docs.astral.sh/uv/)
for dependency management.
To start developing this project,
install `uv`
and run

```shell
uv sync --all-groups
. .venv/bin/activate
```

Alternatively,
if you don't want to install `uv` for your whole system,
run

```shell
python3.13 -mvenv .venv
. .venv/bin/activate
python -mpip install uv
uv sync --all-groups
```

The project management commands
are then available from `nox`.
Running `nox`
will run the linting and testing tools.
They can be run individually
by specifying which tool you want to run:

- `nox -s lint` will run [`pre-commit`](https://pre-commit.com),
  which will run all of the linters.
- `nox -s mypy` will run the type checker.
- `nox -s test` will run the tests.

For local development,
there are some commands to run the project.

- `nox -s venv` will synchronise the requirements
  installed in the local virtual environment.
- `nox -s run` will run the website.
