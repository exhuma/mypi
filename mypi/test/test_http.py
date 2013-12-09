from __future__ import print_function
import unittest
from cStringIO import StringIO

from config_resolver import Config

from mypi import App


@unittest.skip('test not yet implemented')
class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        main_app = App(Config('exhuma', 'mypi', filename='test.ini'))
        main_app.config['TESTING'] = True
        self.manager = main_app.manager
        self.app = main_app.test_client()

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
        response = self.app.post('/', {
            ':action': '<some_action>'
        })
        self.assertEqual(
            response.status_code,
            501)

    def test_get_non_existing_package(self):
        response = self.app.get('/somepackage')
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
        response = self.app.get('/simple/mybadpackage')
        self.assertEqual(response.status_code,
                         404)

    def test_simple_pkg_alias(self):
        response = self.app.get('/simple/mypackage')
        response2 = self.app.get('/simple/mypackage/')
        self.assertEqual(response.text,
                         response2.text)

    def test_upload(self):
        response = self.app.post('/', data={
            'file': (StringIO('file_content'), 'test.txt'),
            ':action': 'upload'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'OK')
        self.manager.file_manager.create.assert_called_with(
            'data', 'test.txt')

    def test_duplicate_upload(self):
        self.app.post('/', data={
            'file': (StringIO('file_content'), 'test.txt'),
            ':action': 'upload'
        })
        response = self.app.post('/', data={
            'file': (StringIO('file_content'), 'test.txt'),
            ':action': 'upload'
        })
        self.assertEqual(response.status_code, 409)
        self.assertIn(response.text.lower(), 'exists')

    def test_submit(self):
        self.app.port('/', {
            ':action': 'submit',
            'foo': 'bar'})
        self.manager.release_manager.register.assert_called_with(
            foo='bar')
