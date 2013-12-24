from __future__ import print_function
import unittest
from cStringIO import StringIO
from hashlib import md5

from config_resolver import Config
from sqlalchemy.orm import Session
from mock import create_autospec

from mypi.server import create_app


# TODO: The tests should simply test if the proper methods in mypi.core.App are
# called which is tested elsewhere!


class MyPiHTTPTestCase(unittest.TestCase):

    def setUp(self):
        config = Config('exhuma', 'mypi', filename='test.ini')
        self.session = create_autospec(Session)
        flask_instance = create_app(config, self.session)
        flask_instance.config['TESTING'] = True
        self.app = flask_instance.test_client()

    def tearDown(self):
        pass

    def test_root_alias_package(self):
        response = self.app.get('/package/')
        response2 = self.app.get('/')
        self.assertEqual(response.text,
                         response2.text)

    def test_root(self):
        response = self.app.get('/')
        for name in expected_packages:
            self.assertIn(name, response.text)

    def test_post_root(self):
        response = self.app.post('/', data={
            ':action': '<some_action>'
        })
        self.assertEqual(
            response.status_code,
            501)

    def test_get_non_existing_package(self):
        response = self.app.get('/somepackage/')
        self.assertEqual(
            response.status_code,
            404)

    def test_get_package(self):
        response = self.app.get('/mypackage/')
        for rel in releases:
            self.assertIn('rel.version', response.text)
            self.assertIn('rel.platform', response.text)
            self.assertIn('rel.license', response.text)
            self.assertIn('rel.author.full_name', response.text)
            self.assertIn('rel.updated', response.text)
            for file_ in rel.files:
                self.assertIn('file.filename', response.text)

    def test_get_package_alias(self):
        response = self.app.get('/mypackage/')
        response2 = self.app.get('/package/mypackage/')
        self.assertEqual(response.text,
                         response2.text)

    def test_download(self):
        response = self.app.get('/download/mypackage/myfilename/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers,
            {'Content-Type': 'application/x-gzip',
             'Content-Disposition': 'attachement; filename=myfilename'})
        self.assertEqual(response.data, 'filecontent')

    def test_non_existing_download(self):
        response = self.app.get('/download/mypackage/mybadfilename/')
        self.assertEqual(
            response.status_code,
            404)

    def test_simple_index(self):
        response = self.app.get('/simple/')
        for pkg in expected_pack_links:
            self.assertIn(pkg, response.data)

    def test_simple_pkg(self):
        response = self.app.get('/simple/mypackage')
        for rel in releases:
            self.assertIn('rel.version', response.text)
            self.assertIn('rel.platform', response.text)
            self.assertIn('rel.license', response.text)
            self.assertIn('rel.author.full_name', response.text)
            self.assertIn('rel.updated', response.text)
            for file_ in rel.files:
                self.assertIn('file.filename', response.text)

    def test_simple_non_existing_pkg(self):
        response = self.app.get('/simple/mybadpackage/')
        self.assertEqual(response.status_code,
                         404)

    def test_simple_pkg_alias(self):
        response = self.app.get('/simple/mypackage')
        response2 = self.app.get('/simple/mypackage/')
        self.assertEqual(response.text,
                         response2.text)

    @unittest.skip("md5 not properly calculated")
    def test_upload(self):
        response = self.app.post('/', data={
            'content': (StringIO('file_content'), 'test.txt'),
            ':action': 'file_upload',
            'author_email': '',
            'comment': '',
            'filetype': '',
            'md5_digest': md5('file content').hexdigest(),
            'name': '',
            'protcol_version': '',
            'pyversion': '',
            'version': '',
            'author_email': '',
            'name': '',
            'version': ''
        })
        print(self.session.mock_calls)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'OK')
        self.main_app._file_manager.create.assert_called_with(
            'data', 'test.txt')
        self.fail('not all submitted data is tested')

    @unittest.skip("non error")
    def test_duplicate_upload(self):
        self.app.post('/', data={
            'content': (StringIO('file_content'), 'test.txt'),
            ':action': 'file_upload'
        })
        response = self.app.post('/', data={
            'content': (StringIO('file_content'), 'test.txt'),
            ':action': 'file_upload'
        })

        self.assertEqual(response.status_code, 409)
        self.assertIn(response.text.lower(), 'exists')

    def test_submit(self):
        self.app.post('/', data={
            ':action': 'submit',
            'foo': 'bar'})
        self.main_app._release_manager.register.assert_called_with(
            foo='bar')
