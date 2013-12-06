from sqlalchemy import create_engine
from logging.config import fileConfig

from config_resolver import Config

from alembic import context

config = context.config
fileConfig(config.config_file_name)
target_metadata = None


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    cfg = Config('exhuma', 'mypi', version='1.0')
    url = cfg.get('sqlalchemy', 'url')
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    cfg = Config('exhuma', 'mypi', version='1.0')
    engine = create_engine(cfg.get('sqlalchemy', 'url'))

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
