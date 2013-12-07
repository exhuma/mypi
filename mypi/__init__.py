import logging
from hashlib import md5

from .manager import (
    UserManager,
    FileManager,
    PackageManager,
    ReleaseManager)


LOG = logging.getLogger(__name__)


class App(object):

    def __init__(self, session):
        self._user_manager = UserManager(session)
        self._file_manager = FileManager(session)
        self._package_manager = PackageManager(session)
        self._release_manager = ReleaseManager(session)

    def register_release(self, data):
        """
        Takes metadata sent by "setup.py register" to create a new release.

        Returns the new release instance.
        """

        #first, we need a package reference to attach this relase to...
        package = self._package_manager.get_or_add(data['name'])

        # now let's see if we have a matching user, and if he/she may write to
        # this package
        user = self._user_manager.get_or_add(data['author_email'],
                                             name=data['author'])

        if user in package.users:
            # TODO: Check access rights and bail out on denial
            pass
        else:
            # This package does not have any users assigned (it's most likely
            # a new one. Add the sending user the the mappings
            # TODO: add the proper privilege bitmask (GRANT_READ & GRANT_WRITE) to this as well.
            package.users.append(user)

        release = self._release_manager.get(
            data['author_email'],
            data['name'],
            data['version'])

        if not release:
            release = self._release_manager.create(
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

        return release

    def upload(self, data, filename, fileobj):
        """
        This method takes a dictionary of data as sent by "setup.py upload" to
        create new files.
        """

        # ensure the release exists
        rel = self._release_manager.get(
            data['author_email'],
            data['name'],
            data['version'])
        if not rel:
            raise ValueError("Release for this file does not exist yet! "
                             "Please register it first!")

        file_ = self._file_manager.create(
            data["name"],
            data["author_email"],
            data["version"],
            filename,
            data["md5_digest"])

        file_.comment = data["comment"]
        file_.filetype = data["filetype"]
        file_.pyversion = data["pyversion"]
        file_.protcol_version = data["protcol_version"]

        file_data = fileobj.read()
        file_.data = file_data
        file_digest = md5(file_data).hexdigest()

        LOG.debug('MD5: %s', file_digest)
        if file_.md5_digest != file_digest:
            raise ValueError("md5 checksum error")
