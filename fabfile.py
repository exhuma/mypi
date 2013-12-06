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
    db_url = fab.prompt(clr.green('Database URL:'), default='sqlite:///dev.db')
    dev_conf_name = '.exhuma/mypi/app.ini'
    with open(dev_conf_name, 'w') as fp:
        fp.write(CONFIG_TEMPLATE.format(db_url=db_url))
        print(clr.green('Development config saved to ') +
              clr.yellow(dev_conf_name))
    print(clr.green('Installing project into development environment...'))
    fab.local('./.env/bin/pip install -e .')
    fab.execute(upgrade_local_db)


@fab.task
def upgrade_local_db():
    """
    Upgrades the development database to the latest alembic revision
    """
    print(clr.green('Upgrading database...'))
    fab.local('./.env/bin/alembic upgrade head')
