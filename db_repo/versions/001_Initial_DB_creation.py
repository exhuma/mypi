from sqlalchemy import *
from migrate import *

metadata = MetaData()

projects_table = Table(
    'project', metadata,
    Column('name', String, primary_key=True),
    Column('inserted', DateTime, nullable=False, default=func.now()),
    Column('updated', DateTime, nullable=False, default=func.now())
    )

users_table = Table(
    'user', metadata,
    Column('email', String, primary_key=True),
    Column('password', String),
    Column('inserted', DateTime, nullable=False, default=func.now()),
    Column('updated', DateTime, nullable=False, default=func.now())
    )

release_table = Table(
    'release', metadata,
    Column('project', String, ForeignKey('project.name')),
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
    Column('inserted', DateTime, nullable=False, default=func.now()),
    Column('updated', DateTime, nullable=False, default=func.now()),
    PrimaryKeyConstraint('project', 'author_email', 'version'),
    )

files_table = Table(
    'file', metadata,
    Column('project', String),
    Column('author_email', String),
    Column('version', String),
    Column('md5_digest', String(32)),

    Column('filename', Unicode),
    Column('comment', String),
    Column('filetype', String),
    Column('pyversion', String),
    Column('protcol_version', Integer),

    Column('inserted', DateTime, nullable=False, default=func.now()),
    Column('updated', DateTime, nullable=False, default=func.now()),

    PrimaryKeyConstraint('project', 'author_email', 'version', 'md5_digest'),
    ForeignKeyConstraint(('project', 'author_email', 'version'),
                         ('release.project', 'release.author_email', 'release.version')),
    )


def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    users_table.create()
    projects_table.create()
    release_table.create()
    files_table.create()


def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    files_table.drop()
    release_table.drop()
    projects_table.drop()
    users_table.drop()
