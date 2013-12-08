from hashlib import md5
import logging
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Table,
    Column,
    String,
    Unicode,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
    LargeBinary,
    PrimaryKeyConstraint,
    ForeignKeyConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship


engine = create_engine('sqlite:///dev.db', echo=True)
Base = declarative_base()
Session = scoped_session(sessionmaker(bind=engine))
LOG = logging.getLogger(__name__)

# Bit-fields for package <-> user rights
GRANT_READ = 1
GRANT_WRITE = 2


package_auth = Table(
    'package_auth', Base.metadata,
    Column('user', String, ForeignKey('user.email')),
    Column('package', String, ForeignKey('package.name')),
    Column('grant_mask', Integer,
           doc=("Bitmask defining the rights granted to this user for this "
                "project")),
    PrimaryKeyConstraint('user', 'package'),
    # doc="Defines access rights to packages for users"
)


class User(Base):
    __tablename__ = 'user'

    email = Column(String, primary_key=True)
    password = Column(String)
    full_name = Column(Unicode)
    verified = Column(Boolean)
    verification_token = Column(String)
    verification_token_exires = Column(DateTime)
    inserted = Column(DateTime, nullable=False, default=datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.now)

    def __init__(self, email, passwd=None, name=None):
        self.email = email
        if passwd:
            self.password = md5(passwd).hexdigest()  # TODO: add salt
        if name:
            self.full_name = name
        # TODO: Create verification-token and send verification-email
        # TODO: self.verification_token = ...
        # TODO: self.verification_token_exires = ...
        self.verified = False

    def __eq__(self, other):

        if not isinstance(other, User):
            return False

        return self.email == other.email


class Release(Base):
    __tablename__ = 'release'
    __table_args__ = (
        PrimaryKeyConstraint('package', 'version'),
        {}
    )

    files = relationship('File')
    author = relationship('User')

    package = Column(String, ForeignKey('package.name'))
    license = Column(String)
    metadata_version = Column(String)
    home_page = Column(String)
    author_email = Column(String, ForeignKey('user.email'))
    download_url = Column(String)
    summary = Column(String)
    version = Column(String)
    platform = Column(String)
    description = Column(String)
    inserted = Column(DateTime, nullable=False, default=datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.now)

    def __init__(self, author_email, package, version):
        self.author_email = author_email
        self.package = package
        self.version = version

    def __eq__(self, other):

        if not isinstance(other, Release):
            return False

        return (self.package == other.package and
                self.author_email == other.author_email and
                self.version == other.version)


class Package(Base):
    __tablename__ = 'package'

    name = Column(String, primary_key=True)
    inserted = Column(DateTime, nullable=False, default=datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.now)

    users = relationship("User", secondary=package_auth, backref="packages")
    releases = relationship('Release', order_by=Release.updated.desc())

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):

        if not isinstance(other, Package):
            return False

        return (other.name == self.name and
                other.author_email == self.author_email)


class File(Base):
    __tablename__ = "file"
    __table_args__ = (
        PrimaryKeyConstraint('package', 'version', 'filename'),
        ForeignKeyConstraint(('package', 'version'),
                             ('release.package', 'release.version')),
        {}
    )

    package = Column(String)
    author_email = Column(String)
    version = Column(String)
    md5_digest = Column(String(32))
    filename = Column(Unicode)
    comment = Column(String)
    filetype = Column(String)
    pyversion = Column(String)
    protcol_version = Column(Integer)
    data = Column(LargeBinary)
    inserted = Column(DateTime, nullable=False, default=datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.now)

    def __init__(self, package, author_email, version, filename, md5_digest):
        self.package = package
        self.author_email = author_email
        self.version = version
        self.filename = filename
        self.md5_digest = md5_digest

    def __eq__(self, other):

        if not isinstance(other, Release):
            return False

        return (self.package == other.package and
                self.author_email == other.author_email and
                self.version == other.version and
                self.md5_digest == other.md5_digest)
