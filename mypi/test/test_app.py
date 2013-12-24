from __future__ import print_function
import unittest

from sqlalchemy.orm import Session
from mock import create_autospec

from mypi.core import App


class MyPiAppTestCase(unittest.TestCase):

    def setUp(self):
        self.session = create_autospec(Session)
        self.app = App(self.session)

    def test_example(self):
        self.fail("no tests implemented yet!")
