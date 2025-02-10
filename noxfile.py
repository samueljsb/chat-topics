from collections.abc import Collection

import nox

PYTHON = '3.13'

nox.options.sessions = ['lint', 'mypy', 'test']
nox.options.reuse_existing_virtualenvs = True


def _install_python_dependencies(
    session: nox.Session, groups: Collection[str] = ()
) -> None:
    group_args: tuple[str, ...] = ()
    for group in groups:
        group_args += ('--group', group)

    session.install('uv')
    session.run(
        'uv', 'sync', '--quiet', *group_args,
        # to avoid a warning about not matching the
        # "project environment path `.venv`"
        env={'UV_PROJECT_ENVIRONMENT': session.virtualenv.location},
    )  # fmt: skip


@nox.session(python=PYTHON)
def compile_requirements(session: nox.Session) -> None:
    session.install('uv')
    session.run(
        'uv',
        'lock',
        # to avoid a warning about not matching the
        # "project environment path `.venv`"
        env={'UV_PROJECT_ENVIRONMENT': session.virtualenv.location},
    )


@nox.session(python=PYTHON)
def lint(session: nox.Session) -> None:
    session.install('pre-commit')
    session.run('pre-commit', 'run', '--all-files')


@nox.session(python=PYTHON)
def mypy(session: nox.Session) -> None:
    _install_python_dependencies(session, ('mypy', 'test'))
    session.run('mypy', 'chat_topics', 'tests', *session.posargs)


@nox.session(python=PYTHON)
def test(session: nox.Session) -> None:
    _install_python_dependencies(session, ('test',))

    session.run('coverage', 'erase')
    session.run('coverage', 'run', '-m', 'pytest', *session.posargs)
    session.run('coverage', 'report')


# Local dev
# =========


@nox.session(python=PYTHON)
def venv(session: nox.Session) -> None:
    """Create/sync a virtual environment in `.venv/`."""
    session.install('uv')
    session.run(
        'uv', 'sync', '--all-groups',
        env={'UV_PROJECT_ENVIRONMENT': '.venv'},
    )  # fmt: skip


@nox.session(python=PYTHON)
def run(session: nox.Session) -> None:
    """Run the website app."""
    _install_python_dependencies(session)
    session.run(
        'uvicorn',
        '--reload',
        '--factory', 'chat_topics.website.app:create_app',
    )  # fmt: skip
