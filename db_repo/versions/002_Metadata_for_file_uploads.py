from sqlalchemy import *
from migrate import *

metadata = MetaData()

files_table = Table(
    'file', metadata,
    Column('project', String),
    Column('author_email', String),
    Column('version', String),
    Column('md5_digest', String(32)),

    Column('comment', String),
    Column('filetype', String),
    Column('pyversion', String),
    Column('protcol_version', Integer),

    PrimaryKeyConstraint('project', 'author_email', 'version', 'md5_digest'),
    ForeignKeyConstraint(('project', 'author_email', 'version'),
                         ('release.project', 'release.author_email', 'release.version')),
    )


def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    release_table = Table( 'release', metadata, autoload = True)
    files_table.create()


def downgrade(migrate_engine):
    files_table.drop()
