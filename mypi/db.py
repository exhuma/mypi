from hashlib import md5

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    ForeignKey,
    PrimaryKeyConstraint,
    ForeignKeyConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, backref, relationship


engine = create_engine('sqlite:///dev.db', echo=True)
Base = declarative_base()
Session = scoped_session(sessionmaker(bind=engine))


class User(Base):
    __tablename__ = 'user'

    email = Column(String, primary_key=True)
    password = Column(String)
    
    @classmethod
    def by_auth(self, sess, email, passwd):
        q = sess.query(User)
        q = q.filter(User.email == email)
        q = q.filter(User.password == md5(passwd).hexdigest())
        return q.first()

    def __init__(self, email, passwd):
        self.email = email
        self.passwd = md5(passwd).hexdigest() #TODO: add salt


class Project(Base):
    __tablename__ = 'project'
    __table_args__ = (
        PrimaryKeyConstraint('name', 'author_email'),
        {}
    )

    name = Column(String, primary_key=True)
    author_email = Column(String, ForeignKey('user.email'))

    @classmethod
    def get(self, session, email, name):
        """
        Return a project reference. If the project does not yet exist, create a
        new one and return that one
        """
        q = session.query(Project)
        q = q.filter(Project.author_email == email)
        q = q.filter(Project.name == name)
        proj = q.first()
        if proj:
            return proj

        proj = Project(name, email)
        session.add(proj)
        return proj

    def __init__(self, name, email):
        self.name = name
        self.author_email = email


class Release(Base):
    __tablename__ = 'release'
    __table_args__ = (
        PrimaryKeyConstraint('project', 'author_email', 'version'),
        ForeignKeyConstraint(('project', 'author_email'),
                             ('project.name', 'project.author_email')),
        {}
    )

    project = Column(String)
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

    @classmethod
    def get(self, session, author_email, name, version):

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
        proj = Project.get(session, data['author_email'], data['name'])

        release = Release.get(session,
            data['author_email'],
            data['name'],
            data['version'])

        release.license = data["license"]
        release.metadata_version = data["metadata_version"]
        release.home_page = data["home_page"]
        release.download_url = data["download_url"]
        release.summary = data["summary"]
        release.platform = data["platform"]
        release.description = data["description"]

        ##    data["author"], TODO: do sth. with this field?
        return release

    def __init__(self, author_email, project, version):
        self.author_email = author_email
        self.project = project
        self.version = version

class File(Base):
    __tablename__ = "file"
    __table_args__ = (
        PrimaryKeyConstraint('project', 'author_email', 'version', 'md5_digest'),
        ForeignKeyConstraint(('project', 'author_email', 'version'),
                         ('release.project', 'release.author_email', 'release.version')),
        {}
    )

    @classmethod
    def add_meta(self, session, data):

        # ensure the release exists
        Release.get(session, data['author_email'], data['name'], data['version'])

        file = File(data["name"], data["author_email"], data["version"], data["md5_digest"])

        file.comment = data["comment"]
        file.filetype = data["filetype"]
        file.pyversion = data["pyversion"]
        file.protcol_version = data["protcol_version"]

        session.add(file)

    def __init__(self, project, author_email, version, md5_digest):
        self.project = project
        self.author_email = author_email
        self.version = version
        self.md5_digest = md5_digest

    project = Column(String)
    author_email = Column(String)
    version = Column(String)
    md5_digest = Column(String(32))
    comment = Column(String)
    filetype = Column(String)
    pyversion = Column(String)
    protcol_version = Column(Integer)

