from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    files = Table('file', meta, autoload=True)
    filename = Column('filename', Unicode)
    filename.create(files)

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    files = Table('file', meta, autoload=True)
    files.c.filename.drop()
