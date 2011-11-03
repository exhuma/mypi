from os import unlink
import unittest

from migrate.versioning.api import upgrade, db_version, version_control
from migrate.exceptions import DatabaseNotControlledError

from mypi import db

DB_FILE = 'test.db'
URI = 'sqlite:///%s' % DB_FILE
REPO = 'db_repo'

def create_db():
    """
    Creates the test DB
    """
    try:
        db_version(URI, REPO)
    except DatabaseNotControlledError:
        version_control(URI, REPO)

    upgrade(URI, REPO)

def drop_db():
    """
    Removes the test DB
    """
    unlink(DB_FILE)


class TestProjectManagement(unittest.TestCase):

    def setUp(self):
        db.rebind(URI)
        create_db()
        self.session = db.Session()
        self.session.expire_on_commit = False

    def tearDown(self):
        self.session.close()
        drop_db()

    def testCreate(self):
        p = db.Project('test', 'john@example.com')
        self.session.add(p)
        self.session.commit()

        s2 = db.Session()
        x = s2.query(db.Project).all()[0]
        self.assertEqual(x, p)

    def testUniqueness(self):
        "ensures no duplicates can be entered to the DB"
        from sqlalchemy.exc import IntegrityError
        p = db.Project('test', 'john@example.com')
        dupe = db.Project('test', 'john@example.com')
        self.session.add(p)
        self.session.add(dupe)
        self.assertRaises(IntegrityError, self.session.commit)

class TestInterface(unittest.TestCase):

    def setUp(self):
        db.rebind(URI)
        create_db()
        self.session = db.Session()
        self.session.expire_on_commit = False

        # Add one example release
        data = {}
        data['author_email'] = "john@example.com"
        data['name'] = "proj1"
        data['version'] = "1.0"
        data["license"] = "BSD"
        data["metadata_version"] = "1"
        data["home_page"] = "UNKNOWN"
        data["download_url"] = "UNKNOWN"
        data["summary"] = "bla"
        data["platform"] = "linux"
        data["description"] = "Hello World!"
        #rel = db.Release.add(self.session, data)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        drop_db()

    def testRegister(self):
        data = {}
        data['author_email'] = "jane@example.com"
        data['name'] = "proj2"
        data['version'] = "1.0"
        data["license"] = "BSD"
        data["metadata_version"] = "1"
        data["home_page"] = "UNKNOWN"
        data["download_url"] = "UNKNOWN"
        data["summary"] = "bla"
        data["platform"] = "linux"
        data["description"] = "Hello World!"
        rel = db.Release.add(self.session, data)
        self.session.commit()

        self.assertTrue(rel)

    def testUploadWithoutMetadata(self):
        """
        Ensures that we are blocking uploads without having metadata from a
        previous "register" action.
        """

        data = dict(
            author_email = "john@example.com",
            name = "proj1",
            version = "1.0",
            md5_digest = "1234",
            comment = "bla",
            filetype = "bdist_dumb",
            pyversion = "2.7",
            protcol_version = "1",
            )

        self.assertRaises(ValueError, db.File.add, self.session, data)

def main():
    """
    The main method
    """
    create_db()
    drop_db()

if __name__ == '__main__':
    unittest.main()

