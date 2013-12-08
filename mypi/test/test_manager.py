from hashlib import md5
from datetime import datetime
from unittest import TestCase, skip
from os import unlink

from mock import create_autospec, patch, MagicMock
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config_resolver import Config

from mypi.manager import (
    UserManager,
    ReleaseManager,
    PackageManager,
    FileManager)
from mypi import db


def upgrade_db():
    import os
    import alembic.config
    from alembic import command
    os.environ['EXHUMA_MYPI_FILENAME'] = 'test.ini'
    alembic_cfg = alembic.config.Config('alembic.ini')
    command.upgrade(alembic_cfg, 'head')
    os.environ['EXHUMA_MYPI_FILENAME'] = ''


class TestUserManager(TestCase):

    @classmethod
    def setUpClass(cls):
        upgrade_db()
        cfg = Config('exhuma', 'mypi', filename='test.ini')
        cls.engine = create_engine(cfg.get('sqlalchemy', 'url'))
        cls.conn = cls.engine.connect()

    @classmethod
    def tearDownClass(cls):
        unlink('test.db')
        cls.conn.close()

    def setUp(self):
        Session = sessionmaker(bind=self.engine)

        self.conn.execute('INSERT INTO user ('
                          'email, password, full_name, verified, '
                          'verification_token, verification_token_exires, '
                          'inserted, updated ) VALUES ('
                          '?, ?, ?, ?, ?, ?, ?, ?)',
                          (
                              'jane.doe@example.com',
                              md5('foobar').hexdigest(),
                              'Jane Doe',
                              True,
                              'verif_token',
                              datetime.now(),
                              datetime.now(),
                              datetime.now()))

        self.session = Session(bind=self.conn)
        self.manager = UserManager(self.session)

    def tearDown(self):
        self.conn.execute('DELETE FROM user')

    @skip('not yet implemented')
    @patch('mypi.manager.md5')
    def test_by_auth(self, md5):
        self.manager.by_auth('john.doe@example.com', 'awwyisss')
        self.session.query.assert_called_with(db.User)
        md5.assert_called_with('awwyisss')
        self.assertTrue(md5().hexdigest.called,
                        "md5.hexdigest was not called!")

    @skip('not yet implemented')
    @patch('mypi.manager.md5')
    def test_by_email(self, md5):
        self.manager.by_email('john.doe@example.com')
        print self.session.get_bind.mock_calls
        self.session.query.assert_called_with(db.User)
        md5.assert_called_with('awwyisss')
        self.assertTrue(md5().hexdigest.called,
                        "md5.hexdigest was not called!")

    def test_get_or_add_existing(self):
        user = self.manager.get_or_add('jane.doe@example.com')
        self.assertEqual(user.email, 'jane.doe@example.com')
        self.assertEqual(user.full_name, 'Jane Doe')
        self.assertEqual(user.password, md5('foobar').hexdigest())

    def test_get_or_add_new(self):
        user = self.manager.get_or_add(email='john.doe@example.com',
                                       passwd='foo',
                                       name='John Doe')
        self.session.commit()
        self.assertEqual(user.email, 'john.doe@example.com')
        self.assertEqual(user.full_name, 'John Doe')
        self.assertEqual(user.password, md5('foo').hexdigest())
        res = self.conn.execute('select full_name, password from user where '
                                'email=?',
                                ('john.doe@example.com',))
        fname, pwd = res.fetchone()
        self.assertEqual(fname, 'John Doe')
        self.assertEqual(pwd, md5('foo').hexdigest())
        res = self.conn.execute('select count(*) from user')
        self.assertEqual(res.scalar(), 2)
