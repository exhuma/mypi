from hashlib import md5
from os import getcwd
import logging
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Unicode,
    Integer,
    ForeignKey,
    DateTime,
    PrimaryKeyConstraint,
    ForeignKeyConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship


engine = create_engine('sqlite:///dev.db', echo=True)
Base = declarative_base()
Session = scoped_session(sessionmaker(bind=engine))
LOG = logging.getLogger(__name__)


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


class Project(Base):
    __tablename__ = 'project'

    name = Column(String, primary_key=True)
    inserted = Column(DateTime, nullable=False, default=datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.now)

    releases = relationship('Release', lazy="joined")

    @classmethod
    def get_or_add(self, session, name):
        """
        Return a project reference. If the project does not yet exist, create a
        new one and return that one
        """
        q = session.query(Project)
        q = q.filter(Project.name == name)
        proj = q.first()
        if proj:
            return proj

        proj = Project(name)
        session.add(proj)
        return proj

    @classmethod
    def get(self, session, name):
        """
        Return a project reference
        """
        q = session.query(Project)
        q = q.filter(Project.name == name)
        proj = q.first()
        return proj

    @classmethod
    def all(self, session):
        """
        Return a list of projects
        """
        q = session.query(Project)
        q = q.order_by(Project.name)
        return q

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):

        if not isinstance(other, Project):
            return False

        return other.name == self.name and other.author_email == self.author_email


class User(Base):
    __tablename__ = 'user'

    email = Column(String, primary_key=True)
    password = Column(String)
    inserted = Column(DateTime, nullable=False, default=datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.now)

    @classmethod
    def by_auth(self, sess, email, passwd):
        q = sess.query(User)
        q = q.filter(User.email == email)
        q = q.filter(User.password == md5(passwd).hexdigest())
        return q.first()

    def __init__(self, email, passwd):
        self.email = email
        self.passwd = md5(passwd).hexdigest() #TODO: add salt

    def __eq__(self, other):

        if not isinstance(other, User):
            return False

        return self.email == other.email


class Release(Base):
    __tablename__ = 'release'
    __table_args__ = (
        PrimaryKeyConstraint('project', 'author_email', 'version'),
        {}
    )

    files = relationship('File')

    project = Column(String, ForeignKey('project.name'))
    license = Column(String)
    metadata_version = Column(String)
    author = Column(String)
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
        q = q.filter(Release.project == name)
        q = q.filter(Release.version == version)
        rel = q.first()
        return rel

    @classmethod
    def get_or_add(self, session, author_email, name, version):

        # ensure the project exists
        Project.get(session, author_email, name)

        q = session.query(Release)
        q = q.filter(Release.author_email == author_email)
        q = q.filter(Release.project == name)
        q = q.filter(Release.version == version)
        rel = q.first()
        if rel:
            raise ValueError("Duplicate release! We already have a release "
                             "for this project by this author and version!")

        rel = Release(author_email, name, version)

        session.add(rel)
        return rel

    @classmethod
    def add(self, session, data):
        proj = Project.get_or_add(session, data['name'])

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

        ##    data["author"], TODO: do sth. with this field?
        return release

    @classmethod
    def register(self):
        """
        Registers a new project release.
        If the project does not yet exist, it will be created automatically
        """
        pass

    def __init__(self, author_email, project, version):
        self.author_email = author_email
        self.project = project
        self.version = version

    def __eq__(self, other):

        if not isinstance(other, Release):
            return False

        return (self.project == other.project
            and self.author_email == other.author_email
            and self.version == other.version)


class File(Base):
    __tablename__ = "file"
    __table_args__ = (
        PrimaryKeyConstraint('project', 'author_email', 'version', 'md5_digest'),
        ForeignKeyConstraint(('project', 'author_email', 'version'),
                         ('release.project', 'release.author_email', 'release.version')),
        {}
    )

    project = Column(String)
    author_email = Column(String)
    version = Column(String)
    md5_digest = Column(String(32))
    comment = Column(String)
    filetype = Column(String)
    pyversion = Column(String)
    filename = Column(Unicode)
    protcol_version = Column(Integer)
    inserted = Column(DateTime, nullable=False, default=datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.now)


    @classmethod
    def add(self, session, data, filename):

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

        session.add(file)

    @classmethod
    def find(self, session, project, md5):
        """
        Finds a file by project and MD5-digest
        """
        q = session.query(File)
        q = q.filter(File.project == project)
        q = q.filter(File.md5_digest == md5)
        return q.first()

    @classmethod
    def find_by_filename(self, session, project, filename):
        """
        Finds a file by filename
        """
        q = session.query(File)
        q = q.filter(File.project == project)
        q = q.filter(File.filename == filename)
        return q.first()

    def __init__(self, project, author_email, version, filename, md5_digest):
        self.project = project
        self.author_email = author_email
        self.version = version
        self.filename = filename
        self.md5_digest = md5_digest

    def __eq__(self, other):

        if not isinstance(other, Release):
            return False

        return (self.project == other.project
            and self.author_email == other.author_email
            and self.version == other.version
            and self.md5_digest == other.md5_digest)
