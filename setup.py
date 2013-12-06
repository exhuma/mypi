from setuptools import setup, find_packages
from setuptools.command.install import install
from os.path import join
from sys import prefix
import os

PACKAGE = "mypi"
NAME = "mypi"
DESCRIPTION = "Private Python Package Index"
AUTHOR = "Michel Albert"
AUTHOR_EMAIL = "michel@albert.lu"
VERSION = join(PACKAGE, 'version.txt').strip()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.rst").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    include_package_data=True,
    install_requires = [
      'Flask',
      'alembic',
      'SQLAlchemy',
      'config_resolver >=4.0, <5.0'
      ],
    packages=find_packages(exclude=["tests.*", "tests"]),
    data_files=[
        (join(prefix,'usr/share/docs/mypi/examples'),
        ['mod_wsgi/app.wsgi', 'mod_wsgi/example.apache.conf']),
        ],
)

