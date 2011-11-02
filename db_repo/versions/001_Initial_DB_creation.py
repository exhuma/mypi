from sqlalchemy import *
from migrate import *

metadata = MetaData()

users_table = Table(
    'user', metadata,
    Column('email', String, primary_key=True),
    Column('password', String),
    )

projects_table = Table(
    'project', metadata,
    Column('name', String),
    Column('author_email', String, ForeignKey('user.email')),
    PrimaryKeyConstraint('name', 'author_email')
    )

release_table = Table(
    'release', metadata,
    Column('project', String),
    Column('license', String),
    Column('metadata_version', String),
    Column('author', String),
    Column('author_email', String, ForeignKey('user.email')),
    Column('home_page', String),
    Column('download_url', String),
    Column('summary', String),
    Column('version', String),
    Column('platform', String),
    Column('description', String),
    PrimaryKeyConstraint('project', 'author_email', 'version'),
    ForeignKeyConstraint(('project', 'author_email'),
                         ('project.name', 'project.author_email')),
    )


def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    users_table.create()
    projects_table.create()
    release_table.create()


def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    release_table.drop()
    projects_table.drop()
    users_table.drop()
