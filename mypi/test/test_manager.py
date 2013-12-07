from unittest import TestCase

from mock import create_autospec, patch, MagicMock
from sqlalchemy.orm.session import Session

from mypi.manager import (
    UserManager,
    ReleaseManager,
    PackageManager,
    FileManager)
from mypi import db


class TestUserManager(TestCase):

    def setUp(self):
        self.session = create_autospec(Session)
        self.manager = UserManager(self.session)

    @patch('mypi.manager.md5')
    def test_by_auth(self, md5):
        self.manager.by_auth('john.doe@example.com', 'awwyisss')
        self.session.query.assert_called_with(db.User)
        md5.assert_called_with('awwyisss')
        self.assertTrue(md5().hexdigest.called,
                        "md5.hexdigest was not called!")

    def test_by_email(self):
        self.manager.by_email('john.doe@example.com')
        print self.session.get_bind.mock_calls
        self.session.query.assert_called_with(db.User)
        md5.assert_called_with('awwyisss')
        self.assertTrue(md5().hexdigest.called,
                        "md5.hexdigest was not called!")
