import fabric.api as fab


@fab.task
def develop():
    """
    Create a development environment
    """
    fab.local('virtualenv .env')
    fab.local('./.env/bin/pip install -e .')
    fab.local('./.env/bin/alembic upgrade head')
