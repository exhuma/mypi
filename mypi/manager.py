from logging import getLogger

from .db import User, Package, Release, File, hashfunc

LOG = getLogger(__name__)


class Manager(object):

    def __init__(self, session):
        self._session = session


class UserManager(Manager):
    """
    Manages user entities.

    :param session: A database session.
    :param hashfunc: A function used to hash user passwords.
    """

    def __init__(self, session, hashfunc=hashfunc):
        super(UserManager, self).__init__(session)
        self._hashfunc = hashfunc

    def by_auth(self, email, passwd):
        """
        Find users by email & password.

        :return: A user entity.
        """
        q = self._session.query(User)
        q = q.filter(User.email == email)
        # TODO: add salt
        q = q.filter(User.password == self._hashfunc(passwd))
        return q.first()

    def by_email(self, email):
        """
        Find a user by e-mail.

        :return: A user entity.
        """
        q = self._session.query(User)
        q = q.filter(User.email == email)
        return q.first()

    def get_or_add(self, email, passwd=None, name=None):
        """
        Return a user entity. If the user does not yet exist, create a new
        one and return it.
        """
        q = self._session.query(User)
        q = q.filter(User.email == email)
        user = q.first()
        if user:
            return user

        # TODO: add salt
        user = User(email, self._hashfunc(passwd), name)
        self._session.add(user)
        return user


class ReleaseManager(Manager):
    """
    Manages Release entities.
    """

    def get(self, author_email, name, version):
        """
        Get a release by author, name and version

        :return: a Release or None
        """
        q = self._session.query(Release)
        q = q.filter(Release.author_email == author_email)
        q = q.filter(Release.package == name)
        q = q.filter(Release.version == version)
        rel = q.first()
        return rel

    def get_or_add(self, author_email, name, version):
        """
        Get a release by author, name and version. If it does not exist, create
        it and return the created instance.
        """

        rel = Release(author_email, name, version)
        self._session.add(rel)
        return rel

    def create(self, email, name, version):
        """
        Create a new release and return the entity.
        """
        rel = Release(
            email,
            name,
            version)
        self._session.add(rel)
        return rel


class PackageManager(Manager):
    """
    Manages Package entities.
    """

    def get_or_add(self, name):
        """
        Return a package reference. If the package does not yet exist, create a
        new one and return that one
        """
        q = self._session.query(Package)
        q = q.filter(Package.name == name)
        proj = q.first()
        if proj:
            return proj

        proj = Package(name)
        self._session.add(proj)
        return proj

    def get(self, name):
        """
        Return a package reference
        """
        q = self._session.query(Package)
        q = q.filter(Package.name == name)
        proj = q.first()
        return proj

    def all(self):
        """
        Return a list of packages
        """
        q = self._session.query(Package)
        q = q.order_by(Package.name)
        return q


class FileManager(Manager):
    """
    Manages File instances.
    """

    def find(self, package, md5_digest):
        """
        Finds a file by package and MD5-digest
        """
        q = self._session.query(File)
        q = q.filter(File.package == package)
        q = q.filter(File.md5_digest == md5_digest)
        return q.first()

    def find_by_filename(self, package, filename):
        """
        Finds a file by filename
        """
        q = self._session.query(File)
        q = q.filter(File.package == package)
        q = q.filter(File.filename == filename)
        return q.first()

    def create(self, name, email, version, filename, md5_digest):
        """
        Creates a new file entity.
        """
        entity = File(name, email, version, filename, md5_digest)
        self._session.add(entity)
        return entity
