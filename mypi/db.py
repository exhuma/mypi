from hashlib import md5
from os import getcwd
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
from sqlalchemy.exc import IntegrityError


engine = create_engine('sqlite:///dev.db', echo=True)
Base = declarative_base()
Session = scoped_session(sessionmaker(bind=engine))
LOG = logging.getLogger(__name__)

# Bit-fields for package <-> user rights
GRANT_READ = 1
GRANT_WRITE = 2

def rebind(uri, echo=False):
    """
    Rebinds the session to a new SqlAlchemy URI.

    .. warning: After calling this all remaining session will still be using
                the old connection! Consider re-opening them!
    """
    global Session
    LOG.debug('Rebinding to {0}. CWD={1}'.format(
        uri, getcwd()
        ))
    engine = create_engine(uri)
    if echo:
        engine.echo = True
    Session = scoped_session(sessionmaker(bind=engine))

package_auth = Table(
    'package_auth', Base.metadata,
    Column('user', String, ForeignKey('user.email')),
    Column('package', String, ForeignKey('package.name')),
    Column('grant_mask', Integer,
        doc="Bitmask defining the rights granted to this user for this project"),
    PrimaryKeyConstraint('user', 'package'),
    #doc="Defines access rights to packages for users"
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

    @classmethod
    def by_auth(self, sess, email, passwd):
        q = sess.query(User)
        q = q.filter(User.email == email)
        q = q.filter(User.password == md5(passwd).hexdigest())
        return q.first()

    @classmethod
    def by_email(self, sess, email):
        q = sess.query(User)
        q = q.filter(User.email == email)
        return q.first()

    @classmethod
    def get_or_add(self, session, email, passwd=None, name=None):
        """
        Return a user reference. If the user does not yet exist, create a new
        one and return it
        """
        q = session.query(User)
        q = q.filter(User.email == email)
        user = q.first()
        if user:
            return user

        user = User(email, passwd, name)
        session.add(user)
        return user

    def __init__(self, email, passwd=None, name=None):
        self.email = email
        if passwd:
            self.passwd = md5(passwd).hexdigest() #TODO: add salt
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

    @classmethod
    def get(self, session, author_email, name, version):
        q = session.query(Release)
        q = q.filter(Release.author_email == author_email)
        q = q.filter(Release.package == name)
        q = q.filter(Release.version == version)
        rel = q.first()
        return rel

    @classmethod
    def get_or_add(self, session, author_email, name, version):

        # ensure the package exists
        Package.get(session, author_email, name)

        q = session.query(Release)
        q = q.filter(Release.author_email == author_email)
        q = q.filter(Release.package == name)
        q = q.filter(Release.version == version)
        rel = q.first()
        if rel:
            raise ValueError("Duplicate release! We already have a release "
                             "for this package by this author and version!")

        rel = Release(author_email, name, version)

        session.add(rel)
        return rel

    @classmethod
    def register(self, session, data):
        """
        Takes metadata sent by "setup.py register" to create a new release
        """

        #first, we need a package reference to attach this relase to...
        package = Package.get_or_add(session, data['name'])

        # now let's see if we have a matching user, and if he/she may write to
        # this package
        user = User.get_or_add(session, data['author_email'], name=data['author'])

        if user in package.users:
            # TODO: Check access rights and bail out on denial
            pass
        else:
            # This package does not have any users assigned (it's most likely
            # a new one. Add the sending user the the mappings
            # TODO: add the proper privilege bitmask (GRANT_READ & GRANT_WRITE) to this as well.
            package.users.append(user)

        release = Release.get(session,
            data['author_email'],
            data['name'],
            data['version'])

        if not release:
            release = Release(
                data['author_email'],
                data['name'],
                data['version'])
            session.add(release)

        release.license = data["license"]
        release.metadata_version = data["metadata_version"]
        release.home_page = data["home_page"]
        release.download_url = data["download_url"]
        release.summary = data["summary"]
        release.platform = data["platform"]
        release.description = data["description"]

        return release

    def __init__(self, author_email, package, version):
        self.author_email = author_email
        self.package = package
        self.version = version

    def __eq__(self, other):

        if not isinstance(other, Release):
            return False

        return (self.package == other.package
            and self.author_email == other.author_email
            and self.version == other.version)


class Package(Base):
    __tablename__ = 'package'

    name = Column(String, primary_key=True)
    inserted = Column(DateTime, nullable=False, default=datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.now)

    users = relationship("User", secondary=package_auth, backref="packages")
    releases = relationship('Release', order_by=Release.updated.desc())

    @classmethod
    def get_or_add(self, session, name):
        """
        Return a package reference. If the package does not yet exist, create a
        new one and return that one
        """
        q = session.query(Package)
        q = q.filter(Package.name == name)
        proj = q.first()
        if proj:
            return proj

        proj = Package(name)
        session.add(proj)
        return proj

    @classmethod
    def get(self, session, name):
        """
        Return a package reference
        """
        q = session.query(Package)
        q = q.filter(Package.name == name)
        proj = q.first()
        return proj

    @classmethod
    def all(self, session):
        """
        Return a list of packages
        """
        q = session.query(Package)
        q = q.order_by(Package.name)
        return q

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):

        if not isinstance(other, Package):
            return False

        return other.name == self.name and other.author_email == self.author_email


class File(Base):
    __tablename__ = "file"
    __table_args__ = (
        PrimaryKeyConstraint('package', 'version', 'md5_digest'),
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


    @classmethod
    def upload(self, session, data, filename, fileobj):
        """
        This method takes a dictionary of data as sent by "setup.py upload" to
        create new files.
        """

        # ensure the release exists
        rel = Release.get(session, data['author_email'], data['name'], data['version'])
        if not rel:
            raise ValueError("Release for this file does not exist yet! "
                    "Please register it first!")

        file = File(data["name"], data["author_email"], data["version"],
                filename, data["md5_digest"])

        file.comment = data["comment"]
        file.filetype = data["filetype"]
        file.pyversion = data["pyversion"]
        file.protcol_version = data["protcol_version"]
        # TODO: verify MD5sum
        file.data = fileobj.read()

        session.add(file)

    @classmethod
    def find(self, session, package, md5):
        """
        Finds a file by package and MD5-digest
        """
        q = session.query(File)
        q = q.filter(File.package == package)
        q = q.filter(File.md5_digest == md5)
        return q.first()

    @classmethod
    def find_by_filename(self, session, package, filename):
        """
        Finds a file by filename
        """
        q = session.query(File)
        q = q.filter(File.package == package)
        q = q.filter(File.filename == filename)
        return q.first()

    def __init__(self, package, author_email, version, filename, md5_digest):
        self.package = package
        self.author_email = author_email
        self.version = version
        self.filename = filename
        self.md5_digest = md5_digest

    def __eq__(self, other):

        if not isinstance(other, Release):
            return False

        return (self.package == other.package
            and self.author_email == other.author_email
            and self.version == other.version
            and self.md5_digest == other.md5_digest)
