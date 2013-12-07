from __future__ import print_function
from textwrap import dedent
import fabric.api as fab
import fabric.colors as clr


CONFIG_TEMPLATE = dedent(
    """\
    [meta]
    version = 1.0

    [sqlalchemy]
    url={db_url}
    """)


@fab.task
def develop():
    """
    Create a development environment
    """
    fab.local('[ -d .env ] || virtualenv .env')
    fab.local('mkdir -p .exhuma/mypi')
    db_url = fab.prompt(clr.white('Database URL:', bold=True),
                        default='sqlite:///dev.db')
    dev_conf_name = '.exhuma/mypi/app.ini'
    with open(dev_conf_name, 'w') as fp:
        fp.write(CONFIG_TEMPLATE.format(db_url=db_url))
        print(clr.white('Development config saved to ', bold=True) +
              clr.green(dev_conf_name))
    print(clr.white('Installing project into development environment...',
                    bold=True))
    fab.local('./.env/bin/pip install -e .')
    fab.execute(upgrade_local_db)


@fab.task
def upgrade_local_db():
    """
    Upgrades the development database to the latest alembic revision
    """
    print(clr.white('Upgrading database...', bold=True))
    fab.local('./.env/bin/alembic upgrade head')
