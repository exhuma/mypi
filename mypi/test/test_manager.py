from textwrap import dedent
from hashlib import md5
from datetime import datetime
from unittest import TestCase
from os import unlink

from mock import create_autospec
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config_resolver import Config

from mypi.manager import (
    UserManager,
    ReleaseManager,
    PackageManager,
    FileManager)


def setUpModule():
    upgrade_db()


def tearDownModule():
    unlink('test.db')


def upgrade_db():
    import logging
    import os
    import alembic.config
    from alembic import command
    os.environ['EXHUMA_MYPI_FILENAME'] = 'test.ini'
    alembic_cfg = alembic.config.Config('alembic.ini')

    handlers = logging.getLogger().handlers
    orig_andlers = handlers[:]
    while handlers:
        handlers.pop()
    command.upgrade(alembic_cfg, 'head')
    for handler in orig_andlers:
        handlers.append(handler)

    os.environ['EXHUMA_MYPI_FILENAME'] = ''


class TestUserManager(TestCase):

    @classmethod
    def setUpClass(cls):
        cfg = Config('exhuma', 'mypi', filename='test.ini')
        cls.engine = create_engine(cfg.get('sqlalchemy', 'url'))
        cls.conn = cls.engine.connect()

    @classmethod
    def tearDownClass(cls):
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

    def test_by_auth(self):
        result = self.manager.by_auth('jane.doe@example.com', 'foobar')
        self.assertEqual(result.email, 'jane.doe@example.com')
        self.assertEqual(result.password, self.manager._hashfunc('foobar'))
        self.assertEqual(result.full_name, 'Jane Doe')
        self.assertEqual(result.verified, True)

    def test_by_wrong_auth(self):
        result = self.manager.by_auth('jane.doe@example.com', 'wrongpw')
        self.assertEqual(result, None)

    def test_by_email(self):
        user = self.manager.by_email('jane.doe@example.com')
        self.assertEqual(
            user.password,
            md5('foobar').hexdigest()
        )

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


class TestReleaseManager(TestCase):

    @classmethod
    def setUpClass(cls):
        cfg = Config('exhuma', 'mypi', filename='test.ini')
        cls.engine = create_engine(cfg.get('sqlalchemy', 'url'))
        cls.conn = cls.engine.connect()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        self.now = datetime.now()
        self.conn.execute(dedent(
            '''\
            INSERT INTO release (
                package,
                license,
                metadata_version,
                home_page,
                author_email,
                download_url,
                summary,
                version,
                platform,
                description,
                inserted,
                updated
            ) VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )'''), (
                'thepackage',
                'somelicense',
                '1.0',
                'http://some.url',
                'john.doe@example.com',
                'http://some.url/bar.tar.gz',
                'this is some project',
                '1.0',
                'linux',
                'long desc',
                self.now,
                self.now
            ))

        Session = sessionmaker(bind=self.engine)
        self.session = Session(bind=self.conn)
        self.manager = ReleaseManager(self.session)

    def tearDown(self):
        self.conn.execute('DELETE FROM release')

    def test_get(self):
        release = self.manager.get('john.doe@example.com',
                                   'thepackage',
                                   '1.0')

        expected = {
            'package': 'thepackage',
            'license': 'somelicense',
            'metadata_version': '1.0',
            'home_page': 'http://some.url',
            'author_email': 'john.doe@example.com',
            'download_url': 'http://some.url/bar.tar.gz',
            'summary': 'this is some project',
            'version': '1.0',
            'platform': 'linux',
            'description': 'long desc',
            'inserted': self.now,
            'updated': self.now
        }

        result = {
            'package': release.package,
            'license': release.license,
            'metadata_version': release.metadata_version,
            'home_page': release.home_page,
            'author_email': release.author_email,
            'download_url': release.download_url,
            'summary': release.summary,
            'version': release.version,
            'platform': release.platform,
            'description': release.description,
            'inserted': release.inserted,
            'updated': release.updated
        }

        self.assertEqual(expected, result)

    def test_get_or_add(self):
        release = self.manager.get_or_add(
            'jane.doe@example.com',
            'other_release',
            '2.0')
        self.session.commit()
        res = self.conn.execute('select count(*) from release')
        self.assertEqual(res.scalar(), 2)

        expected = {
            'package': 'other_release',
            'author_email': 'jane.doe@example.com',
            'version': '2.0',
        }

        result = {
            'package': release.package,
            'author_email': release.author_email,
            'version': release.version,
        }

        self.assertEqual(expected, result)


    def test_create(self):
        release = self.manager.create(email, name, version)
        self.fail()
